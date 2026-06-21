import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import names
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
env_path = root / ".env"
load_dotenv(env_path)

data_dir = Path(os.getenv("DATA_DIR", root / "createData" / "dados"))

def dicionarioDados():
    LOJAS = [
        {"estado" : "SP", "cidade": "São Paulo", 
        "vendedores": ["João", "Maria", "Pedro"]},
        {"estado" : "MG", "cidade": "Belo Horizonte", 
        "vendedores": ["Carlos", "Stephanie", "Carleto"]},
        {"estado" : "RJ", "cidade": "Rio de Janeiro", 
        "vendedores": ["Antônio", "Juliana", "Paulo"]},
        {"estado" : "SC", "cidade": "Florianópolis", 
        "vendedores": ["Eduardo", "Paola", "Rafaela"]},
        {"estado" : "RS", "cidade": "Porto Alegre", 
        "vendedores": ["Tiago", "Marta", "Lucas"]},
    ]

    PRODUTOS = [
        {"nome": "Galaxy", "id": "0", 'preco': 2000},
        {"nome": "iPhone", "id": "1", 'preco': 3000},
        {"nome": "iPad", "id": "2", 'preco': 2500},
        {"nome": "Android", "id": "3", 'preco': 2500},
        {"nome": "Dell", "id": "4", 'preco': 2500}
    ]

    FORMA_PAGAMENTO = ["Cartão de Crédito", "Boleto", "Pix", "Dinheiro"]
    GENEROS = ["Masculino", "Feminino", "Outro"]

    return LOJAS, PRODUTOS, FORMA_PAGAMENTO, GENEROS

def gerarDados(LOJAS, PRODUTOS, FORMA_PAGAMENTO, GENEROS, n=2000):
    compras = []
    for _ in range(n):
        loja = random.choice(LOJAS)
        vendedor = random.choice(loja["vendedores"])
        produto = random.choice(PRODUTOS)
        hora_compra = datetime.now() - timedelta(
            days = random.randint(1, 365),
            hours = random.randint(-5, 5),
            minutes = random.randint(-30, 30)
        )
        # escolher gênero/forma de pagamento e gerar nome
        genero_cliente = random.choice(GENEROS)
        forma_pagamento = random.choice(FORMA_PAGAMENTO)
        # mapear valores em português para o parâmetro esperado pela biblioteca `names`
        gender_map = {"Masculino": "male", "Feminino": "female", "Outro": None}
        gender_param = gender_map.get(genero_cliente)
        if gender_param:
            nome_cliente = names.get_full_name(gender=gender_param)
        else:
            nome_cliente = names.get_full_name()

        compras.append({
            "data": hora_compra,
            "id_compra": 0,
            "loja": loja["cidade"],
            "vendedor": vendedor,
            "produto": produto["nome"],
            "nome_cliente": nome_cliente,
            "genero_cliente": genero_cliente.replace("Masculino", "M").replace("Feminino", "F").replace("Outro", "O"),
            "forma_pagamento": forma_pagamento,
        })
    return compras  

def dataframes(compras, LOJAS, PRODUTOS, FORMA_PAGAMENTO, GENEROS):
    df_compras = pd.DataFrame(compras).set_index("data").sort_index()
    df_compras["id_compra"] = [i for i in range(len(df_compras))]

    df_lojas = pd.DataFrame(LOJAS)
    df_produtos = pd.DataFrame(PRODUTOS)

    return df_compras, df_lojas, df_produtos

def exportar(df_compras, df_lojas, df_produtos):
    # garantir diretório existe e exportar com a coluna de data
    data_dir.mkdir(parents=True, exist_ok=True)
    df_compras.reset_index(inplace=True)
    df_compras.to_csv(data_dir / "compras.csv", index=False)
    df_lojas.to_csv(data_dir / "lojas.csv", index=False)
    df_produtos.to_csv(data_dir / "produtos.csv", index=False)


if __name__ == "__main__":
    LOJAS, PRODUTOS, FORMA_PAGAMENTO, GENEROS = dicionarioDados()
    compras = gerarDados(LOJAS, PRODUTOS, FORMA_PAGAMENTO, GENEROS)
    df_compras, df_lojas, df_produtos = dataframes(compras, LOJAS, PRODUTOS, FORMA_PAGAMENTO, GENEROS)
    exportar(df_compras, df_lojas, df_produtos)