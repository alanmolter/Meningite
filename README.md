# Meningite Dashboard (Streamlit)

Aplicação Streamlit para análise de dados de Meningite (Brasil). O app principal é dashboard_completo_v2.py.

## Requisitos
- Python 3.10+ (recomendado 3.13)
- Pip

## Instalação
`
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
`

## Execução
`
python -m streamlit run dashboard_completo_v2.py --server.port 8501 --server.headless false
`
Abra: http://localhost:8501

## Estrutura mínima de dados
- TABELAS/ (CSVs necessários)
- data/processed/analise_regional.csv
- data/processed/dados_imunizacao_processados.csv

## Troubleshooting
- Ative a venv antes de executar
- Verifique portas e colunas Ano válidas

