import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
env_path = root / ".env"
load_dotenv(env_path)


def connectDb():
    db_driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    db_server = os.getenv("DB_SERVER", "DESKTOP-DUBDQD2")
    db_name = os.getenv("DB_NAME", "Sales")
    db_trusted = os.getenv("DB_TRUSTED_CONNECTION", "yes")

    params = quote_plus(
        f"DRIVER={{{db_driver}}};"
        f"SERVER={db_server};"
        f"DATABASE={db_name};"
        f"Trusted_Connection={db_trusted};"
    )

    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    return engine


def dados():
    data_dir = Path(os.getenv("DATA_DIR", root / "createData" / "dados"))
    dfCompras = pd.read_csv(
        data_dir / "compras.csv",
        sep=',',
        decimal='.',
        parse_dates=['data'],
    )
    dfLojas = pd.read_csv(
        data_dir / "lojas.csv",
        sep=',',
        decimal='.',
    )
    dfProdutos = pd.read_csv(
        data_dir / "produtos.csv",
        sep=',',
        decimal='.',
    )
    return dfCompras, dfLojas, dfProdutos


def preparar_dados(dfCompras, dfLojas, dfProdutos):
    dfLojas = dfLojas.copy()
    dfLojas['id_loja'] = range(1, len(dfLojas) + 1)
    dfLojas = dfLojas[['id_loja', 'estado', 'cidade', 'vendedores']]

    dfProdutos = dfProdutos.copy()
    dfProdutos = dfProdutos.rename(columns={'id': 'id_produto'})
    dfProdutos['id_produto'] = dfProdutos['id_produto'].astype(int) + 1
    dfProdutos = dfProdutos[['id_produto', 'nome', 'preco']]

    loja_map = dict(zip(dfLojas['cidade'], dfLojas['id_loja']))
    produto_map = dict(zip(dfProdutos['nome'], dfProdutos['id_produto']))

    dfCompras = dfCompras.copy()
    dfCompras['data'] = pd.to_datetime(dfCompras['data'])
    dfCompras['id_loja'] = dfCompras['loja'].map(loja_map)
    dfCompras['id_produto'] = dfCompras['produto'].map(produto_map)
    dfCompras = dfCompras[
        [
            'data',
            'id_loja',
            'loja',
            'vendedor',
            'id_produto',
            'produto',
            'nome_cliente',
            'genero_cliente',
            'forma_pagamento',
        ]
    ]
    return dfCompras, dfLojas, dfProdutos
def limpar_tabelas(engine):
    """Apaga os dados existentes em Compras, Produtos e Lojas e reseta identity."""
    with engine.begin() as conn:
        # apagar compras primeiro por causa das FK
        conn.execute(text("DELETE FROM Compras"))
        # reset identity on Compras
        try:
            conn.execute(text("DBCC CHECKIDENT ('Compras', RESEED, 0)"))
        except Exception:
            # DBCC may require different permissions; ignore if fails
            pass
        conn.execute(text("DELETE FROM Produtos"))
        conn.execute(text("DELETE FROM Lojas"))


def inserindoDados(dfCompras, dfLojas, dfProdutos, engine, replace: bool = False):
    """Insere dados nas tabelas. Se replace=True, apaga os dados existentes primeiro."""
    if replace:
        limpar_tabelas(engine)

    # inserir na ordem: Lojas, Produtos, Compras
    dfLojas.to_sql(
        name="Lojas",
        con=engine,
        if_exists="append",
        index=False,
    )

    dfProdutos.to_sql(
        name="Produtos",
        con=engine,
        if_exists="append",
        index=False,
    )

    dfCompras.to_sql(
        name="Compras",
        con=engine,
        if_exists="append",
        index=False,
    )


def main():
    engine = connectDb()
    dfCompras, dfLojas, dfProdutos = dados()
    dfCompras, dfLojas, dfProdutos = preparar_dados(dfCompras, dfLojas, dfProdutos)

    print(f"Lojas: {len(dfLojas)} rows | Produtos: {len(dfProdutos)} rows | Compras: {len(dfCompras)} rows")
    print("Inserindo dados no banco de dados...")
    inserindoDados(dfCompras, dfLojas, dfProdutos, engine, replace=True)
    print("Carga concluída com sucesso.")


if __name__ == "__main__":
    main()