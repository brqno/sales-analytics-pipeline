import os
from pathlib import Path

import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
env_path = root / ".env"
load_dotenv(env_path)

st.set_page_config(page_title='Procedures SQL', layout='wide')

@st.cache_resource
def get_engine():
    db_driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    db_server = os.getenv("DB_SERVER", "DESKTOP-DUBDQD2")
    db_name = os.getenv("DB_NAME", "Sales")
    db_trusted = os.getenv("DB_TRUSTED_CONNECTION", "yes")

    params = quote_plus(
        f'DRIVER={{{db_driver}}};'
        f'SERVER={db_server};'
        f'DATABASE={db_name};'
        f'Trusted_Connection={db_trusted};'
    )
    return create_engine(f'mssql+pyodbc:///?odbc_connect={params}')


def run_procedure(proc_name: str, proc_params: dict | None = None) -> pd.DataFrame:
    if proc_params:
        param_list = ', '.join(f'@{key}=:{key}' for key in proc_params)
        sql = text(f'EXEC {proc_name} {param_list}')
    else:
        sql = text(f'EXEC {proc_name}')

    with get_engine().connect() as conn:
        return pd.read_sql_query(sql, conn, params=proc_params)


def execute_and_show(proc_name: str, params: dict | None):
    try:
        df = run_procedure(proc_name, params)
        st.success(f'Procedure `{proc_name}` executada com sucesso. Linhas retornadas: {len(df)}')

        # Rankings: mostrar gráfico acima da tabela
        if proc_name in {'rankingVendedores', 'rankingFormasPagamento', 'rankingProdutos', 'rankingGenero'}:
            # identificar coluna numérica e coluna categórica
            num_cols = df.select_dtypes(include=['number']).columns.tolist()
            if num_cols:
                numeric_col = num_cols[0]
            else:
                numeric_col = df.columns[0]

            cat_cols = [c for c in df.columns if c != numeric_col]
            category_col = cat_cols[0] if cat_cols else (df.columns[1] if len(df.columns) > 1 else df.columns[0])

            # lidar com nomes de coluna duplicados
            cols = list(df.columns)
            category_idx = next((i for i, c in enumerate(cols) if c == category_col), None)
            numeric_idx = next((i for i, c in enumerate(cols) if c == numeric_col), None)

            if category_idx is None or numeric_idx is None:
                st.error('Não foi possível identificar colunas para o gráfico.')
            else:
                chart_df = df.iloc[:, [category_idx, numeric_idx]].copy()
                chart_df.columns = ['category', 'value']
                chart_df = chart_df.groupby('category', as_index=False).sum()
                chart_df = chart_df.sort_values('value', ascending=False)

                chart = alt.Chart(chart_df).mark_bar().encode(
                    x=alt.X('value:Q', title=numeric_col),
                    y=alt.Y('category:N', sort=alt.EncodingSortField(field='value', order='descending'), title=category_col),
                    tooltip=['category', 'value']
                ).properties(height=420)

                st.altair_chart(chart, use_container_width=True)

        st.dataframe(df)
    except Exception as exc:
        st.error('Erro ao executar a procedure:')
        st.exception(exc)


st.title('Dashboard de Vendas!')
st.markdown('Dashboard de vendas com diversos filtros e análises.')

proc_names = [
    'filtroEstado',
    'comprasPorVendedor',
    'rankingVendedores',
    'rankingFormasPagamento',
    'rankingProdutos',
    'rankingGenero',
]

sellers = [
    'João', 'Lucas', 'Marta', 'Paulo', 'Carlos', 'Maria', 'Paola', 'Eduardo',
    'Juliana', 'Antônio', 'Carleto', 'Stephanie', 'Tiago', 'Pedro', 'Rafaela'
]

cities = [
    'São Paulo', 'Belo Horizonte', 'Rio de Janeiro', 'Florianópolis', 'Porto Alegre'
]

selected_proc = st.sidebar.selectbox('Selecione a análise', proc_names)

param_value = None
if selected_proc == 'filtroEstado':
    param_value = st.sidebar.selectbox('Escolha a loja (cidade)', [''] + cities, format_func=lambda x: x if x else '--- selecione ---')
elif selected_proc == 'comprasPorVendedor':
    param_value = st.sidebar.selectbox('Escolha o vendedor', [''] + sellers, format_func=lambda x: x if x else '--- selecione ---')


if st.sidebar.button('Executar procedure'):
    if selected_proc in {'filtroEstado', 'comprasPorVendedor'} and not param_value:
        st.warning('Informe um valor para o parâmetro antes de executar.')
    else:
        params = None
        if selected_proc == 'filtroEstado':
            params = {'loja': param_value}
        elif selected_proc == 'comprasPorVendedor':
            params = {'vendedor': param_value}

        execute_and_show(selected_proc, params)

if selected_proc in {'filtroEstado', 'comprasPorVendedor'} and param_value:
    params = None
    if selected_proc == 'filtroEstado':
        params = {'loja': param_value}
    elif selected_proc == 'comprasPorVendedor':
        params = {'vendedor': param_value}

    execute_and_show(selected_proc, params)

st.sidebar.markdown('---')
st.sidebar.markdown('Procedures disponíveis:')
st.sidebar.write(
    '- `filtroEstado(@loja)`\n'
    '- `comprasPorVendedor(@vendedor)`\n'
    '- `rankingVendedores()`\n'
    '- `rankingFormasPagamento()`\n'
    '- `rankingProdutos()`\n'
    '- `rankingGenero()`\n'
)
