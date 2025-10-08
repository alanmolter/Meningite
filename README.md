# Meningite Dashboard (Streamlit) - Análise de Dados de Meningite no Brasil

![Banner](https://raw.githubusercontent.com/code-review-doctor/Meningtitis-in-Brazil-2024/main/diagrama_plotly_sistema_epidemiologico.png)

## 🇧🇷 Sobre o Projeto

Este repositório contém o código-fonte de um dashboard interativo desenvolvido em **Streamlit** para a análise de dados epidemiológicos de **Meningite no Brasil**. A aplicação permite a visualização de séries temporais, distribuições geográficas, análises por etiologia, sorogrupo, e o impacto da imunização.

O objetivo principal é fornecer uma ferramenta robusta para que analistas de dados, profissionais de saúde e pesquisadores possam explorar os dados de forma intuitiva, identificar tendências, padrões sazonais e correlações importantes para a saúde pública.

## ✨ Funcionalidades Principais

- **Visão Geral 2024**: Métricas e gráficos atualizados para o ano corrente.
- **Análise de Casos**: Evolução temporal, sazonalidade e tendências de longo prazo.
- **Análise de Sorogrupos e Etiologia**: Detalhamento dos casos por agente causador e sorogrupo, incluindo taxas de letalidade.
- **Impacto da Imunização**: Correlação entre cobertura vacinal e incidência da doença.
- **Análise Regional**: Comparativos entre as cinco grandes regiões do Brasil.
- **Análises Avançadas**: Modelagem estatística, machine learning (clustering) e análise de componentes principais.
- **Exploração Livre**: Interface para que o usuário possa filtrar e analisar os dados brutos de forma personalizada.
- **Relatórios e Downloads**: Geração de relatórios e exportação de dados em formato CSV.

## 📁 Estrutura do Repositório

```
/
├── app/                  # Contém a versão modularizada da aplicação
│   ├── __init__.py
│   └── main.py
├── app_sections/         # Módulos de cada seção do dashboard
│   ├── cases.py
│   ├── etiology.py
│   └── ...
├── data/                 # Dados processados e prontos para análise
│   └── processed/
├── TABELAS/              # Dados brutos em formato CSV
├── .venv/                # Ambiente virtual (ignorado pelo Git)
├── Dockerfile            # Configuração para criar a imagem Docker
├── docker-compose.yml    # Orquestração do container Docker
├── dashboard_completo_v2.py # Script principal (monolítico) da aplicação
├── requirements.txt      # Dependências Python do projeto
└── README.md             # Este arquivo
```

## 📊 Fontes de Dados

Os dados utilizados neste projeto são provenientes de fontes públicas do sistema de saúde brasileiro, incluindo:

- **DATASUS**: Departamento de Informática do SUS.
- **SINAN**: Sistema de Informação de Agravos de Notificação.
- **SI-PNI**: Sistema de Informação do Programa Nacional de Imunizações.
- **SIH**: Sistema de Informações Hospitalares.

Os dados brutos são armazenados na pasta `TABELAS/` e, após o processamento, as tabelas consolidadas são salvas em `data/processed/`.

## 🚀 Como Executar o Projeto

Existem duas maneiras principais de executar o dashboard: localmente com um ambiente virtual Python ou via Docker.

### 1. Configuração Local (Ambiente Virtual)

Este método é recomendado para desenvolvimento e análise local.

**Pré-requisitos:**
- [Python 3.10+](https://www.python.org/downloads/)
- `pip` (gerenciador de pacotes do Python)

**Passos:**

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/code-review-doctor/Meningtitis-in-Brazil-2024.git
    cd Meningtitis-in-Brazil-2024
    ```

2.  **Crie e ative um ambiente virtual:**
    - **Windows:**
      ```bash
      python -m venv .venv
      .venv\Scripts\activate
      ```
    - **macOS/Linux:**
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação Streamlit:**
    ```bash
    streamlit run dashboard_completo_v2.py
    ```

5.  **Acesse o dashboard** no seu navegador através do endereço: `http://localhost:8501`.

### 2. Configuração com Docker

Este método é ideal para garantir um ambiente consistente e facilitar o deploy.

**Pré-requisitos:**
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/) (geralmente incluído no Docker Desktop)

**Passos:**

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/code-review-doctor/Meningtitis-in-Brazil-2024.git
    cd Meningtitis-in-Brazil-2024
    ```

2.  **Construa a imagem e inicie o container:**
    ```bash
    docker-compose up --build
    ```
    O comando `--build` é necessário apenas na primeira vez ou quando o `Dockerfile` ou as dependências mudarem.

3.  **Acesse o dashboard** no seu navegador através do endereço: `http://localhost:8501`.

Para parar o container, pressione `CTRL + C` no terminal onde o docker-compose está rodando ou execute `docker-compose down` em outro terminal.

---

Desenvolvido com ❤️ e Python. Sinta-se à vontade para contribuir, reportar issues ou sugerir novas funcionalidades.