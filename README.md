# Projeto de Dados

Este projeto demonstra um fluxo simples de dados:

- `createData/gerarDados.py`: gera dados fictícios para lojas, produtos e compras.
- `loadData/loadSQL.py`: lê os CSVs gerados e insere os dados em um banco SQL Server.
- `configDB/dbconfig.sql`: define o banco de dados e tabelas.
- `configDB/procedures.sql`: contém procedures para consultas e rankings.
- `transformData/app.py`: dashboard Streamlit que consome as procedures.

## Estrutura do projeto

- `createData/`: scripts e dados de geração.
- `loadData/`: script de carga para o banco.
- `configDB/`: configuração de banco de dados e procedures.
- `transformData/`: aplicação de visualização.

## Requisitos

- Python 3.10+
- SQL Server com ODBC Driver 17
- `pip install -r requirements.txt`

## Configuração

1. Copie o arquivo `.env` e ajuste os valores se necessário.
2. Deixe `DB_SERVER`, `DB_NAME` e `DATA_DIR` apontando para seu ambiente.

Exemplo de `.env`:

```ini
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=
DB_NAME=
DB_TRUSTED_CONNECTION=yes
DATA_DIR=createData/dados
```

## Como usar

1. Gere os dados:

```bash
python createData/gerarDados.py
```

2. Carregue os dados no SQL Server:

```bash
python loadData/loadSQL.py
```

3. Execute a aplicação Streamlit:

```bash
streamlit run transformData/app.py
```

## Observações

- O projeto utiliza caminhos relativos e lê variáveis de conexão do arquivo `.env`.
- Não versionar o `.env` em repositórios públicos.
