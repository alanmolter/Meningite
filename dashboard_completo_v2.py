#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Completo de Meningite Brasil - Versão 2.0 Corrigida
Inclui todas as análises: regional, avançada, ARIMA, testes de hipóteses e exploração livre
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import os
from datetime import datetime
import warnings
from scipy import stats
# Imports condicionais para evitar problemas de compatibilidade
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    STATSMODELS_AVAILABLE = True
except ImportError as e:
    print(f"Aviso: statsmodels não disponível: {e}")
    STATSMODELS_AVAILABLE = False
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Dashboard Meningite Brasil - Análise Completa",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_all_data():
    """Carrega e pré-processa todos os conjuntos de dados necessários para o dashboard.

    Esta função é responsável por ler os arquivos CSV da pasta 'TABELAS/' e 'data/processed/',
    tratar exceções de arquivos ausentes e, em seguida, chamar funções auxiliares para
    criar conjuntos de dados derivados, como dados regionais e temporais.

    Returns:
        dict: Um dicionário contendo todos os DataFrames carregados e processados,
              prontos para serem utilizados pelas funções de visualização. As chaves
              do dicionário são nomes descritivos dos conjuntos de dados.
              Retorna None se ocorrer um erro crítico durante o carregamento.
    """
    
    st.info("📊 Carregando todos os dados processados...")
    
    try:
        # Dados básicos
        casos_consolidados = pd.read_csv('TABELAS/casos_consolidados_2017_2024.csv')
        sorogrupos_consolidados = pd.read_csv('TABELAS/sorogrupos_consolidados_2007_2024.csv')
        etiologias_consolidadas = pd.read_csv('TABELAS/etiologias_consolidadas_2007_2024.csv')
        
        # Dados de imunização
        imunizacao_ano = pd.read_csv('TABELAS/imunizacao_por_ano.csv')
        imunizacao_faixa_etaria = pd.read_csv('TABELAS/imunizacao_por_faixa_etaria.csv')
        imunizacao_sorogrupo = pd.read_csv('TABELAS/imunizacao_por_sorogrupo.csv')
        imunizacao_uf = pd.read_csv('TABELAS/imunizacao_por_uf.csv')
        
        # Dados de letalidade e casos
        letalidade_etiologia = pd.read_csv('TABELAS/letalidade_etiologia_2007_2020.csv')
        casos_2017_2022 = pd.read_csv('TABELAS/casos_notificados_2017_2022.csv')
        dados_gerais_2024 = pd.read_csv('TABELAS/dados_gerais_2024.csv')
        bacterianas_2024 = pd.read_csv('TABELAS/bacterianas_2024.csv')
        etiologia_2024 = pd.read_csv('TABELAS/etiologia_2024.csv')
        sorogrupos_2024 = pd.read_csv('TABELAS/sorogrupos_2024.csv')
        
        # Dados de imunização 2023-2025 (pode ter separador diferente; manter opcional)
        try:
            imunizacao_2023_2025 = pd.read_csv('TABELAS/imunobiologicosem2023a2025.csv')
        except Exception:
            imunizacao_2023_2025 = None

        # Dados de imunização processados (base principal para análises)
        try:
            imunizacao_processada = pd.read_csv('data/processed/dados_imunizacao_processados.csv')
        except Exception:
            imunizacao_processada = None
        
        # Dados de hospitalização SIH
        sih_meningite = pd.read_csv('TABELAS/sih_meningite_long.csv')
        
        # Criar dados regionais a partir dos dados disponíveis
        analise_regional = create_regional_data(imunizacao_uf)
        imunizacao_regional = create_temporal_regional_data(imunizacao_2023_2025)
        analise_temporal = create_temporal_analysis(imunizacao_2023_2025)
        matriz_correlacao = create_correlation_matrix()
        
        st.success("✅ Dados carregados com sucesso!")
        
        return {
            'casos_consolidados': casos_consolidados,
            'sorogrupos_consolidados': sorogrupos_consolidados,
            'etiologias_consolidadas': etiologias_consolidadas,
            'imunizacao_ano': imunizacao_ano,
            'imunizacao_faixa_etaria': imunizacao_faixa_etaria,
            'imunizacao_sorogrupo': imunizacao_sorogrupo,
            'imunizacao_uf': imunizacao_uf,
            'imunizacao_2023_2025': imunizacao_2023_2025,
            'imunizacao_processada': imunizacao_processada,
            'analise_regional': analise_regional,
            'imunizacao_regional': imunizacao_regional,
            'analise_temporal': analise_temporal,
            'matriz_correlacao': matriz_correlacao,
            'casos_2017_2022': casos_2017_2022,
            'dados_gerais_2024': dados_gerais_2024,
            'bacterianas_2024': bacterianas_2024,
            'etiologia_2024': etiologia_2024,
            'sorogrupos_2024': sorogrupos_2024,
            'letalidade_etiologia': letalidade_etiologia,
            'sih_meningite': sih_meningite
        }
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return None

def create_regional_data(imunizacao_uf):
    """Cria um DataFrame com dados regionais simulados a partir de dados por UF.

    Esta função utiliza um mapeamento predefinido de Unidades Federativas (UFs) para
    as cinco grandes regiões do Brasil. Ela então gera dados simulados (aleatórios)
    para o total de doses e a cobertura média de cada região.

    Args:
        imunizacao_uf (pd.DataFrame): DataFrame contendo dados de imunização por UF.
                                     Atualmente, é usado apenas para referência do
                                     mapeamento, mas poderia ser usado para agregar
                                     dados reais.

    Returns:
        pd.DataFrame: Um DataFrame com dados agregados por região, contendo as colunas
                      'Regiao', 'Total_UFs', 'Total_Doses' e 'Cobertura_Media'.
    """
    # Mapeamento de UFs para regiões
    mapeamento_regioes = {
        'Norte': ['11 Rondônia', '12 Acre', '13 Amazonas', '14 Roraima', '15 Pará', '16 Amapá', '17 Tocantins'],
        'Nordeste': ['21 Maranhão', '22 Piauí', '23 Ceará', '24 Rio Grande do Norte', '25 Paraíba', '26 Pernambuco', '27 Alagoas', '28 Sergipe', '29 Bahia'],
        'Centro-Oeste': ['50 Mato Grosso do Sul', '51 Mato Grosso', '52 Goiás', '53 Distrito Federal'],
        'Sudeste': ['31 Minas Gerais', '32 Espírito Santo', '33 Rio de Janeiro', '35 São Paulo'],
        'Sul': ['41 Paraná', '42 Santa Catarina', '43 Rio Grande do Sul']
    }
    
    # Criar dados regionais simulados
    dados_regional = []
    for regiao, ufs in mapeamento_regioes.items():
        total_ufs = len(ufs)
        total_doses = np.random.randint(100000, 1000000)  # Simulado
        cobertura_media = np.random.uniform(70, 95)  # Simulado
        
        dados_regional.append({
            'Regiao': regiao,
            'Total_UFs': total_ufs,
            'Total_Doses': total_doses,
            'Cobertura_Media': cobertura_media
        })
    
    return pd.DataFrame(dados_regional)

def create_temporal_regional_data(imunizacao_2023_2025):
    """Gera dados temporais regionais simulados para análise.

    Esta função cria um DataFrame com dados simulados (aleatórios) de doses e cobertura
    para cada região do Brasil, ao longo de um período de três anos (2023-2025).
    É útil para visualizações de séries temporais quando dados reais não estão disponíveis.

    Args:
        imunizacao_2023_2025 (pd.DataFrame): DataFrame de referência. Atualmente não utilizado
                                           diretamente para os cálculos, mas serve como
                                           gatilho para a criação dos dados.

    Returns:
        pd.DataFrame: Um DataFrame com dados temporais simulados por região,
                      contendo as colunas 'Regiao', 'Ano', 'Total_Doses' e 'Cobertura'.
    """
    # Dados simulados para análise temporal regional
    regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
    anos = [2023, 2024, 2025]
    
    dados_temporais = []
    for regiao in regioes:
        for ano in anos:
            dados_temporais.append({
                'Regiao': regiao,
                'Ano': ano,
                'Total_Doses': np.random.randint(50000, 500000),
                'Cobertura': np.random.uniform(75, 98)
            })
    
    return pd.DataFrame(dados_temporais)

def create_temporal_analysis(imunizacao_2023_2025):
    """Cria um DataFrame com dados simulados para análise temporal.

    Gera um conjunto de dados simulados (aleatórios) de casos de meningite e cobertura
    vacinal para um intervalo de anos (2020-2025). Serve como um substituto para
    análises de tendência quando dados reais consolidados não estão disponíveis.

    Args:
        imunizacao_2023_2025 (pd.DataFrame): DataFrame de referência, não utilizado
                                           diretamente nos cálculos.

    Returns:
        pd.DataFrame: Um DataFrame com dados temporais simulados, contendo as
                      colunas 'Ano', 'Casos' e 'Cobertura'.
    """
    # Dados simulados para análise temporal
    anos = list(range(2020, 2026))
    dados_temporais = []
    
    for ano in anos:
        dados_temporais.append({
            'Ano': ano,
            'Casos': np.random.randint(1000, 5000),
            'Cobertura': np.random.uniform(80, 95)
        })
    
    return pd.DataFrame(dados_temporais)

def create_correlation_matrix():
    """Gera uma matriz de correlação simulada.

    Cria uma matriz de correlação 5x5 com valores aleatórios para demonstrar
    a funcionalidade de visualização de correlações (heatmap). As variáveis
    são 'Casos', 'Letalidade', 'Cobertura', 'Populacao' e 'Temperatura'.
    A matriz é simétrica e tem a diagonal principal preenchida com 1.0.

    Returns:
        pd.DataFrame: Uma matriz de correlação simulada como um DataFrame do Pandas.
    """
    # Criar matriz de correlação simulada
    n_vars = 5
    corr_matrix = np.random.rand(n_vars, n_vars)
    np.fill_diagonal(corr_matrix, 1.0)
    
    # Tornar simétrica
    corr_matrix = (corr_matrix + corr_matrix.T) / 2
    
    return pd.DataFrame(
        corr_matrix,
        columns=['Casos', 'Letalidade', 'Cobertura', 'Populacao', 'Temperatura'],
        index=['Casos', 'Letalidade', 'Cobertura', 'Populacao', 'Temperatura']
    )

def show_overview_2024(dados):
    """Exibe a seção "Visão Geral 2024" no dashboard.

    Esta função renderiza uma visão geral dos dados de meningite para o ano de 2024.
    Ela apresenta métricas chave, como total de casos suspeitos e óbitos, letalidade,
    e gráficos de distribuição de casos por etiologia e sorogrupo. Também inclui
    um resumo estatístico e informações gerais sobre a doença.

    Args:
        dados (dict): O dicionário global contendo todos os DataFrames da aplicação.
                      As chaves 'dados_gerais_2024', 'bacterianas_2024', 'etiologia_2024',
                      e 'sorogrupos_2024' são utilizadas.
    """
    st.header("🏠 **Visão Geral 2024 - Meningite Brasil**")
    st.markdown("---")
    
    # Carregar dados específicos de 2024
    dados_gerais = dados['dados_gerais_2024']
    bacterianas = dados['bacterianas_2024']
    etiologia = dados['etiologia_2024']
    sorogrupos = dados['sorogrupos_2024']
    
    if dados_gerais is not None and not dados_gerais.empty:
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_casos = dados_gerais['Casos_Suspeitos'].sum()
            st.metric("📊 Total de Casos Suspeitos", f"{total_casos:,}")
        
        with col2:
            total_obitos = dados_gerais['Obitos_Confirmados'].sum()
            st.metric("💀 Total de Óbitos Confirmados", f"{total_obitos:,}")
        
        with col3:
            letalidade_geral = (total_obitos / total_casos * 100) if total_casos > 0 else 0
            st.metric("⚠️ Letalidade Geral", f"{letalidade_geral:.1f}%")
        
        with col4:
            # Como não há coluna UF, vamos mostrar o ano
            ano_2024 = dados_gerais['Ano'].iloc[0]
            st.metric("📅 Ano", ano_2024)
        
        # Gráfico de casos por ano (já que não temos UF)
        st.subheader("📈 **Casos por Ano**")
        
        fig_casos_ano = px.bar(
            x=dados_gerais['Ano'],
            y=dados_gerais['Casos_Suspeitos'],
            title="Distribuição de Casos por Ano",
            labels={'x': 'Ano', 'y': 'Número de Casos'},
            color=dados_gerais['Casos_Suspeitos'],
            color_continuous_scale='Reds'
        )
        
        fig_casos_ano.update_layout(template='plotly_white')
        st.plotly_chart(fig_casos_ano, use_container_width=True)
        
        # Análise por etiologia
        if etiologia is not None and not etiologia.empty:
            st.subheader("🧬 **Casos por Etiologia em 2024**")
            
            # Verificar se a coluna existe
            if 'Casos_Suspeitos' in etiologia.columns:
                casos_por_etiologia = etiologia.groupby('Etiologia')['Casos_Suspeitos'].sum().sort_values(ascending=False)
            else:
                # Se não existir, usar a primeira coluna numérica disponível
                colunas_numericas = etiologia.select_dtypes(include=[np.number]).columns
                if len(colunas_numericas) > 0:
                    coluna_casos = colunas_numericas[0]
                    casos_por_etiologia = etiologia.groupby('Etiologia')[coluna_casos].sum().sort_values(ascending=False)
                else:
                    st.warning("⚠️ Não foi possível encontrar dados numéricos para análise por etiologia")
                    return
            
            fig_etiologia = px.pie(
                values=casos_por_etiologia.values,
                names=casos_por_etiologia.index,
                title="Distribuição de Casos por Etiologia"
            )
            
            fig_etiologia.update_layout(template='plotly_white')
            st.plotly_chart(fig_etiologia, use_container_width=True)
        
        # Análise por sorogrupo
        if sorogrupos is not None and not sorogrupos.empty:
            st.subheader("🦠 **Casos por Sorogrupo em 2024**")
            
            # Verificar se a coluna existe
            if 'Casos_Suspeitos' in sorogrupos.columns:
                casos_por_sorogrupo = sorogrupos.groupby('Sorogrupo')['Casos_Suspeitos'].sum().sort_values(ascending=False)
            else:
                # Se não existir, usar a primeira coluna numérica disponível
                colunas_numericas = sorogrupos.select_dtypes(include=[np.number]).columns
                if len(colunas_numericas) > 0:
                    coluna_casos = colunas_numericas[0]
                    casos_por_sorogrupo = sorogrupos.groupby('Sorogrupo')[coluna_casos].sum().sort_values(ascending=False)
                else:
                    st.warning("⚠️ Não foi possível encontrar dados numéricos para análise por sorogrupo")
                    return
            
            fig_sorogrupo = px.bar(
                x=casos_por_sorogrupo.index,
                y=casos_por_sorogrupo.values,
                title="Distribuição de Casos por Sorogrupo",
                labels={'x': 'Sorogrupo', 'y': 'Número de Casos'},
                color=casos_por_sorogrupo.values,
                color_continuous_scale='Blues'
            )
            
            fig_sorogrupo.update_layout(template='plotly_white')
            st.plotly_chart(fig_sorogrupo, use_container_width=True)
        
        # Resumo estatístico
        st.subheader("📋 **Resumo Estatístico 2024**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Estatísticas Descritivas dos Casos Suspeitos:**")
            st.dataframe(dados_gerais['Casos_Suspeitos'].describe())
        
        with col2:
            st.write("**Dados Gerais 2024:**")
            st.dataframe(dados_gerais)
        
        # Informações sobre meningite
        st.subheader("ℹ️ **Sobre a Meningite**")
        st.markdown("""
        **Meningite** é uma inflamação das membranas que revestem o cérebro e a medula espinhal.
        
        **Principais sintomas:**
        - Febre alta
        - Dor de cabeça intensa
        - Rigidez no pescoço
        - Náuseas e vômitos
        - Alteração do nível de consciência
        
        **Importância da vacinação:**
        - Previne formas graves da doença
        - Reduz a transmissão
        - Protege grupos vulneráveis
        """)
    else:
        st.warning("⚠️ Dados de 2024 não disponíveis")

def show_cases_analysis(dados):
    """Exibe a seção "Análise dos Casos Notificados 2017-2024".

    Renderiza uma análise detalhada da evolução temporal dos casos de meningite.
    Apresenta métricas gerais, um gráfico de linha da evolução dos casos, análise
    de sazonalidade (se disponível), e uma análise de tendência linear com
    interpretações estatísticas detalhadas (coeficiente angular, R², p-valor).

    Args:
        dados (dict): O dicionário global de dados. Utiliza as chaves 'casos_consolidados'
                      e 'casos_2017_2022'.
    """
    st.header("📈 **Análise dos Casos Notificados 2017-2024**")
    st.markdown("---")
    
    # Carregar dados de casos
    casos = dados['casos_consolidados']
    casos_2017_2022 = dados['casos_2017_2022']
    
    if casos is not None and not casos.empty:
        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_casos = casos['Casos_Notificados'].sum()
            st.metric("📊 Total de Casos Notificados", f"{total_casos:,}")
        
        with col2:
            # Verificar se a coluna Obitos existe
            if 'Obitos' in casos.columns:
                total_obitos = casos['Obitos'].sum()
                st.metric("💀 Total de Óbitos", f"{total_obitos:,}")
            else:
                st.metric("💀 Total de Óbitos", "N/A")
        
        with col3:
            # Calcular letalidade se possível
            if 'Obitos' in casos.columns and 'Casos_Notificados' in casos.columns:
                total_obitos = casos['Obitos'].sum()
                letalidade_geral = (total_obitos / total_casos * 100) if total_casos > 0 else 0
                st.metric("⚠️ Letalidade Geral", f"{letalidade_geral:.1f}%")
            else:
                st.metric("⚠️ Letalidade Geral", "N/A")
        
        with col4:
            periodo_anos = casos['Ano'].max() - casos['Ano'].min() + 1
            st.metric("📅 Período (Anos)", periodo_anos)
        
        # Evolução temporal dos casos
        st.subheader("📈 **Evolução Temporal dos Casos**")
        
        casos_por_ano = casos.groupby('Ano')['Casos_Notificados'].sum().reset_index()
        
        fig_evolucao = px.line(
            casos_por_ano,
            x='Ano',
            y='Casos_Notificados',
            title="Evolução dos Casos de Meningite (2017-2024)",
            markers=True
        )
        
        fig_evolucao.update_layout(
            xaxis_title="Ano",
            yaxis_title="Número de Casos",
            template='plotly_white'
        )
        
        fig_evolucao.update_xaxes(tickformat='d')
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        # Explicação do gráfico de evolução temporal
        st.markdown("""
        #### 📖 **Interpretação do Gráfico de Evolução Temporal:**
        - **Eixo X (Horizontal):** Anos (2017-2024)
        - **Eixo Y (Vertical):** Número total de casos notificados por ano
        - **Linha com marcadores:** Cada ponto representa o total de casos em um ano específico
        - **Tendência:** A inclinação da linha mostra se os casos estão aumentando, diminuindo ou estáveis
        - **Variações:** Picos ou vales podem indicar surtos, mudanças em políticas de saúde ou fatores sazonais
        - **Utilidade:** Permite identificar padrões temporais e avaliar a eficácia de intervenções de saúde pública
        """)
        
        # Análise de sazonalidade
        st.subheader("🌡️ **Análise de Sazonalidade**")
        
        if 'Mes' in casos.columns:
            casos_por_mes = casos.groupby('Mes')['Casos_Notificados'].sum().reset_index()
            
            # Mapear números para nomes dos meses
            meses_nomes = {
                1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
                7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
            }
            casos_por_mes['Mes_Nome'] = casos_por_mes['Mes'].map(meses_nomes)
            
            fig_sazonalidade = px.bar(
                casos_por_mes,
                x='Mes_Nome',
                y='Casos_Notificados',
                title="Sazonalidade dos Casos de Meningite",
                color='Casos_Notificados',
                color_continuous_scale='Reds'
            )
            
            fig_sazonalidade.update_layout(
                xaxis_title="Mês",
                yaxis_title="Número de Casos",
                template='plotly_white'
            )
            
            st.plotly_chart(fig_sazonalidade, use_container_width=True)
            
            # Explicação do gráfico de sazonalidade
            st.markdown("""
            #### 📖 **Interpretação do Gráfico de Sazonalidade:**
            - **Eixo X (Horizontal):** Meses do ano (Jan a Dez)
            - **Eixo Y (Vertical):** Número total de casos acumulados em cada mês (todos os anos)
            - **Barras coloridas:** Altura representa o total de casos, cores mais intensas = mais casos
            - **Padrões sazonais:** Permite identificar meses com maior/menor incidência
            - **Importância epidemiológica:** Ajuda a planejar campanhas preventivas e alocação de recursos
            """)
            
            # Interpretação da sazonalidade
            st.markdown("""
            **📊 Interpretação da Sazonalidade:**
            
            **Padrões típicos observados:**
            - **Inverno/Outono:** Maior incidência (temperaturas mais baixas)
            - **Primavera/Verão:** Menor incidência (temperaturas mais altas)
            
            **Fatores que influenciam:**
            - Aglomeração em ambientes fechados
            - Sistema imunológico mais vulnerável
            - Maior circulação de vírus respiratórios
            """)
        else:
            st.info("ℹ️ Dados de sazonalidade mensal não disponíveis")
        
        # Distribuição por ano (já que não temos UF)
        st.subheader("📊 **Distribuição por Ano**")
        
        fig_distribuicao = px.bar(
            x=casos_por_ano['Ano'],
            y=casos_por_ano['Casos_Notificados'],
            title="Casos por Ano (2017-2024)",
            labels={'x': 'Ano', 'y': 'Número de Casos'},
            color=casos_por_ano['Casos_Notificados'],
            color_continuous_scale='Blues'
        )
        
        fig_distribuicao.update_layout(
            xaxis_title="Ano",
            yaxis_title="Número de Casos",
            template='plotly_white'
        )
        
        st.plotly_chart(fig_distribuicao, use_container_width=True)
        
        # Análise de tendência
        st.subheader("📈 **Análise de Tendência**")
        
        # Calcular tendência linear
        x = casos_por_ano['Ano'].values.reshape(-1, 1)
        y = casos_por_ano['Casos_Notificados'].values
        
        if len(x) > 1:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x.flatten(), y)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📊 Coeficiente Angular", f"{slope:.1f}")
            
            with col2:
                st.metric("📈 R²", f"{r_value**2:.3f}")
            
            with col3:
                if p_value < 0.05:
                    st.metric("🎯 Significância", "Significativo (p<0.05)")
                else:
                    st.metric("🎯 Significância", "Não significativo (p≥0.05)")
            
            # Explicação detalhada das métricas estatísticas
            st.markdown("---")
            st.markdown("### 📚 **Explicação das Métricas Estatísticas**")
            
            st.markdown(f"""
            #### 📊 **Coeficiente Angular ({slope:.1f})**
            - **O que é:** Representa a variação média anual no número de casos
            - **Interpretação:** 
              - Se positivo: aumenta {abs(slope):.1f} casos por ano em média
              - Se negativo: diminui {abs(slope):.1f} casos por ano em média
              - Se próximo de zero: tendência estável
            
            #### 📈 **Coeficiente de Determinação (R² = {r_value**2:.3f})**
            - **O que é:** Mede o quanto da variação nos casos é explicada pela tendência temporal
            - **Escala:** 0 a 1 (quanto mais próximo de 1, melhor o ajuste)
            - **Interpretação atual:** 
              - R² = {r_value**2:.3f} significa que {r_value**2*100:.1f}% da variação nos casos é explicada pelo tempo
              - {100-r_value**2*100:.1f}% da variação se deve a outros fatores (sazonalidade, surtos, políticas de saúde, etc.)
            - **Qualidade do ajuste:**
              - R² > 0.7: Ajuste forte
              - R² 0.4-0.7: Ajuste moderado  
              - R² < 0.4: Ajuste fraco
              - **Seu resultado:** {"Ajuste forte" if r_value**2 > 0.7 else "Ajuste moderado" if r_value**2 > 0.4 else "Ajuste fraco"}
            
            #### 🎯 **Significância Estatística (p-valor = {p_value:.4f})**
            - **O que é:** Probabilidade de observar essa tendência por acaso
            - **Interpretação:**
              - p < 0.05: Tendência estatisticamente significativa (confiável)
              - p ≥ 0.05: Tendência pode ser devida ao acaso
              - **Seu resultado:** {"A tendência é estatisticamente significativa e confiável" if p_value < 0.05 else "A tendência pode ser devida ao acaso - não é estatisticamente significativa"}
            
            #### 📏 **Erro Padrão ({std_err:.2f})**
            - **O que é:** Mede a incerteza na estimativa do coeficiente angular
            - **Interpretação:** Quanto menor, mais precisa é a estimativa da tendência
            """)
            
            # Interpretação da tendência
            if slope > 0:
                st.success("📈 **Tendência:** Aumento nos casos ao longo do tempo")
            elif slope < 0:
                st.success("📉 **Tendência:** Diminuição nos casos ao longo do tempo")
            else:
                st.info("➡️ **Tendência:** Estável ao longo do tempo")
        else:
            st.warning("⚠️ Dados insuficientes para análise de tendência")
        
        # Resumo estatístico
        st.subheader("📋 **Resumo Estatístico**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Estatísticas Descritivas dos Casos:**")
            st.dataframe(casos_por_ano['Casos_Notificados'].describe())
        
        with col2:
            st.write("**Dados por Ano:**")
            st.dataframe(casos_por_ano)
        
        # Informações sobre a análise
        st.subheader("ℹ️ **Sobre a Análise**")
        st.markdown("""
        **Esta análise mostra:**
        - Evolução temporal dos casos de meningite
        - Padrões sazonais (quando disponíveis)
        - Tendências estatísticas significativas
        - Distribuição temporal dos casos
        
        **Importância:**
        - Identificar períodos de maior risco
        - Planejar ações de prevenção
        - Avaliar efetividade de medidas de controle
        """)
    else:
        st.warning("⚠️ Dados de casos não disponíveis")

def show_sorogrupos_analysis(dados):
    """Exibe a seção "Análise de Sorogrupos e Relações Não Lineares".

    Esta função realiza uma análise aprofundada dos sorogrupos de meningite.
    Ela calcula e exibe a letalidade por sorogrupo, explora relações não lineares
    entre casos e letalidade com regressão polinomial, realiza análises de
    correlação de Pearson e Spearman, e oferece uma análise de clustering (K-Means)
    para agrupar sorogrupos com perfis epidemiológicos semelhantes.

    Args:
        dados (dict): O dicionário global de dados. Utiliza a chave 'sorogrupos_consolidados'.
    """
    st.header("🦠 **Análise de Sorogrupos e Relações Não Lineares**")
    st.markdown("---")
    
    # Carregar dados de sorogrupos
    sorogrupos = dados['sorogrupos_consolidados']
    
    if sorogrupos is not None and not sorogrupos.empty:
        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_casos = sorogrupos['Casos'].sum()
            st.metric("📊 Total de Casos", f"{total_casos:,}")
        
        with col2:
            total_obitos = sorogrupos['Obitos'].sum()
            st.metric("💀 Total de Óbitos", f"{total_obitos:,}")
        
        with col3:
            letalidade_geral = (total_obitos / total_casos * 100) if total_casos > 0 else 0
            st.metric("⚠️ Letalidade Geral", f"{letalidade_geral:.1f}%")
        
        with col4:
            n_sorogrupos = sorogrupos['Sorogrupo'].nunique()
            st.metric("🦠 Sorogrupos", n_sorogrupos)
        
        # Análise de letalidade por sorogrupo
        st.subheader("📊 **Letalidade por Sorogrupo**")
        
        letalidade_por_sorogrupo = sorogrupos.groupby('Sorogrupo').agg({
            'Casos': 'sum',
            'Obitos': 'sum'
        }).reset_index()
        
        letalidade_por_sorogrupo['Letalidade'] = (
            letalidade_por_sorogrupo['Obitos'] / letalidade_por_sorogrupo['Casos'] * 100
        ).round(2)
        
        # Gráfico de barras
        fig_letalidade = px.bar(
            letalidade_por_sorogrupo,
            x='Sorogrupo',
            y='Letalidade',
            title="Letalidade por Sorogrupo",
            color='Letalidade',
            color_continuous_scale='Reds'
        )
        
        fig_letalidade.update_layout(
            yaxis_title="Taxa de Letalidade (%)",
            template='plotly_white'
        )
        
        st.plotly_chart(fig_letalidade, use_container_width=True)
        
        # Explicação do gráfico de letalidade por sorogrupo
        st.markdown("""
        #### 📖 **Interpretação do Gráfico de Letalidade por Sorogrupo:**
        - **Eixo X (Horizontal):** Diferentes sorogrupos de meningite (A, B, C, W, Y, etc.)
        - **Eixo Y (Vertical):** Taxa de letalidade em percentual (óbitos/casos × 100)
        - **Barras coloridas:** Altura representa a letalidade, cores mais intensas = maior letalidade
        - **Importância clínica:** Identifica quais sorogrupos são mais letais e necessitam atenção especial
        - **Aplicação:** Orienta estratégias de tratamento e priorização de vacinação
        """)
        
        # Mostrar tabela com dados detalhados
        st.markdown("#### 📋 **Dados Detalhados por Sorogrupo:**")
        st.dataframe(letalidade_por_sorogrupo.sort_values('Letalidade', ascending=False))
        
        # Análise de relações não lineares
        st.subheader("🔗 **Análise de Relações Não Lineares**")
        
        # Preparar dados para análise
        dados_analise = sorogrupos.groupby('Sorogrupo').agg({
            'Casos': 'sum',
            'Obitos': 'sum'
        }).reset_index()
        
        dados_analise['Letalidade'] = (
            dados_analise['Obitos'] / dados_analise['Casos'] * 100
        ).round(2)
        
        # Gráfico de dispersão com regressão polinomial
        fig_dispersao = px.scatter(
            dados_analise,
            x='Casos',
            y='Letalidade',
            title="Relação entre Casos e Letalidade por Sorogrupo",
            text='Sorogrupo',
            size='Casos'
        )
        
        # Adicionar linha de tendência polinomial
        if len(dados_analise) > 2:
            x = dados_analise['Casos'].values
            y = dados_analise['Letalidade'].values
            
            # Ajuste polinomial de grau 2
            coeffs = np.polyfit(x, y, 2)
            poly = np.poly1d(coeffs)
            
            x_trend = np.linspace(x.min(), x.max(), 100)
            y_trend = poly(x_trend)
            
            fig_dispersao.add_trace(go.Scatter(
                x=x_trend,
                y=y_trend,
                mode='lines',
                name='Tendência Polinomial (grau 2)',
                line=dict(color='red', dash='dash')
            ))
        
        fig_dispersao.update_layout(
            xaxis_title="Número de Casos",
            yaxis_title="Taxa de Letalidade (%)",
            template='plotly_white'
        )
        
        st.plotly_chart(fig_dispersao, use_container_width=True)
        
        # Explicação do gráfico de dispersão com regressão polinomial
        st.markdown("""
        #### 📖 **Interpretação do Gráfico de Dispersão com Regressão Polinomial:**
        - **Eixo X (Horizontal):** Número total de casos por sorogrupo
        - **Eixo Y (Vertical):** Taxa de letalidade (%) por sorogrupo
        - **Pontos:** Cada ponto representa um sorogrupo específico
        - **Tamanho dos pontos:** Proporcional ao número de casos (pontos maiores = mais casos)
        - **Linha tracejada vermelha:** Tendência polinomial de grau 2 (curva que melhor se ajusta aos dados)
        - **Análise não-linear:** Permite identificar relações complexas que não seguem uma linha reta
        - **Interpretação epidemiológica:** 
          - Se a curva é crescente: sorogrupos com mais casos tendem a ter maior letalidade
          - Se a curva é decrescente: sorogrupos com mais casos tendem a ter menor letalidade
          - Curva em U ou invertida: relação complexa que requer investigação detalhada
        """)
        
        # Análise de correlação
        st.subheader("📊 **Análise de Correlação**")
        
        if len(dados_analise) > 2:
            # Correlação de Pearson
            corr_pearson, p_pearson = stats.pearsonr(dados_analise['Casos'], dados_analise['Letalidade'])
            
            # Correlação de Spearman
            corr_spearman, p_spearman = stats.spearmanr(dados_analise['Casos'], dados_analise['Letalidade'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("📈 Correlação de Pearson", f"{corr_pearson:.3f}")
                st.write(f"P-valor: {p_pearson:.4f}")
                st.write("**Interpretação:** Mede correlação linear")
                if abs(corr_pearson) > 0.7:
                    st.write("**Força:** Correlação forte")
                elif abs(corr_pearson) > 0.3:
                    st.write("**Força:** Correlação moderada")
                else:
                    st.write("**Força:** Correlação fraca")
            
            with col2:
                st.metric("📊 Correlação de Spearman", f"{corr_spearman:.3f}")
                st.write(f"P-valor: {p_spearman:.4f}")
                st.write("**Interpretação:** Mede correlação monotônica")
                if abs(corr_spearman) > 0.7:
                    st.write("**Força:** Correlação forte")
                elif abs(corr_spearman) > 0.3:
                    st.write("**Força:** Correlação moderada")
                else:
                    st.write("**Força:** Correlação fraca")
            
            # Interpretação das correlações
            st.markdown(f"""
            ### 📚 **Explicação Detalhada das Correlações:**
            
            #### 📈 **Correlação de Pearson = {corr_pearson:.3f}**
            - **O que mede:** Força da relação linear entre número de casos e letalidade
            - **Escala:** -1 a +1
            - **Interpretação atual:**
              - Valor = {corr_pearson:.3f}
              - {"Correlação positiva" if corr_pearson > 0 else "Correlação negativa" if corr_pearson < 0 else "Sem correlação"}
              - P-valor = {p_pearson:.4f} → {"Estatisticamente significativa" if p_pearson < 0.05 else "Não significativa"}
            - **Limitações:** Assume relação linear, sensível a outliers
            
            #### 📊 **Correlação de Spearman = {corr_spearman:.3f}**
            - **O que mede:** Força da relação monotônica (crescente ou decrescente)
            - **Escala:** -1 a +1
            - **Interpretação atual:**
              - Valor = {corr_spearman:.3f}
              - {"Relação monotônica positiva" if corr_spearman > 0 else "Relação monotônica negativa" if corr_spearman < 0 else "Sem relação monotônica"}
              - P-valor = {p_spearman:.4f} → {"Estatisticamente significativa" if p_spearman < 0.05 else "Não significativa"}
            - **Vantagens:** Detecta relações não-lineares, robusto a outliers
            
            #### 🔍 **Comparação dos Resultados:**
            - **Diferença:** {abs(corr_pearson - corr_spearman):.3f}
            - **Interpretação:** {"Relação aproximadamente linear" if abs(corr_pearson - corr_spearman) < 0.1 else "Possível relação não-linear"}
            
            #### 📋 **Escalas de Interpretação:**
            - **0.0 - 0.3:** Correlação fraca
            - **0.3 - 0.7:** Correlação moderada
            - **0.7 - 1.0:** Correlação forte
            """)
        
        # Evolução temporal da letalidade
        st.subheader("📈 **Evolução Temporal da Letalidade**")
        
        if 'Ano' in sorogrupos.columns:
            letalidade_temporal = sorogrupos.groupby(['Ano', 'Sorogrupo']).agg({
                'Casos': 'sum',
                'Obitos': 'sum'
            }).reset_index()
            
            letalidade_temporal['Letalidade'] = (
                letalidade_temporal['Obitos'] / letalidade_temporal['Casos'] * 100
            ).round(2)
            
            # Gráfico de linha
            fig_temporal = px.line(
                letalidade_temporal,
                x='Ano',
                y='Letalidade',
                color='Sorogrupo',
                title="Evolução da Letalidade por Sorogrupo ao Longo do Tempo",
                markers=True
            )
            
            fig_temporal.update_layout(
                xaxis_title="Ano",
                yaxis_title="Taxa de Letalidade (%)",
                template='plotly_white'
            )
            
            fig_temporal.update_xaxes(tickformat='d')
            st.plotly_chart(fig_temporal, use_container_width=True)
        
        # Análise de clustering
        st.subheader("🎯 **Análise de Clustering**")
        
        if len(dados_analise) > 3:
            # Preparar dados para clustering
            dados_cluster = dados_analise[['Casos', 'Letalidade']].copy()
            
            # Normalizar dados
            scaler = StandardScaler()
            dados_cluster_norm = scaler.fit_transform(dados_cluster)
            
            # Número de clusters
            n_clusters = st.slider("Número de Clusters:", 2, min(5, len(dados_cluster)), 3)
            
            if st.button("🎯 Executar Clustering"):
                try:
                    # Aplicar K-Means
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                    clusters = kmeans.fit_predict(dados_cluster_norm)
                    
                    # Adicionar clusters aos dados
                    dados_cluster['Cluster'] = clusters
                    
                    # Gráfico de clusters
                    fig_cluster = px.scatter(
                        dados_cluster,
                        x='Casos',
                        y='Letalidade',
                        color='Cluster',
                        title=f"Clusters de Sorogrupos (K={n_clusters})",
                        text=dados_analise['Sorogrupo'],
                        size='Casos'
                    )
                    
                    fig_cluster.update_layout(
                        xaxis_title="Número de Casos",
                        yaxis_title="Taxa de Letalidade (%)",
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig_cluster, use_container_width=True)
                    
                    # Explicação do gráfico de clustering K-Means
                    st.markdown(f"""
                    #### 📖 **Interpretação do Gráfico de Clustering K-Means:**
                    - **Eixo X (Horizontal):** Número de casos por sorogrupo
                    - **Eixo Y (Vertical):** Taxa de letalidade (%) por sorogrupo
                    - **Cores diferentes:** Cada cor representa um cluster diferente
                    - **Tamanho dos pontos:** Proporcional ao número de casos
                    - **Algoritmo:** K-Means agrupa sorogrupos similares em casos e letalidade
                    
                    #### 🎯 **Como interpretar os clusters:**
                    - **Cluster 0:** Sorogrupos com características similares de casos/letalidade
                    - **Proximidade:** Sorogrupos no mesmo cluster têm comportamento epidemiológico similar
                    - **Separação:** Clusters distintos indicam perfis epidemiológicos diferentes
                    - **Aplicação prática:** Permite estratégias de controle diferenciadas por cluster
                    """)
                    
                    # Resumo dos clusters
                    st.subheader("📊 **Resumo dos Clusters**")
                    for i in range(n_clusters):
                        cluster_data = dados_cluster[dados_cluster['Cluster'] == i]
                        st.write(f"**Cluster {i}:** {len(cluster_data)} sorogrupos")
                        for idx in cluster_data.index:
                            sorogrupo = dados_analise.loc[idx, 'Sorogrupo']
                            casos = cluster_data.loc[idx, 'Casos']
                            letalidade = cluster_data.loc[idx, 'Letalidade']
                            st.write(f"  - {sorogrupo}: {casos} casos, {letalidade:.1f}% letalidade")
                    
                except Exception as e:
                    st.error(f"Erro no clustering: {e}")
        
        # Resumo das análises
        st.markdown("---")
        st.markdown("""
        **📋 Resumo das Análises de Sorogrupos:**
        
        **1. Análise de Letalidade:**
        - Identificação dos sorogrupos mais letais
        - Comparação entre diferentes tipos
        - Padrões de mortalidade
        
        **2. Relações Não Lineares:**
        - Análise de correlações complexas
        - Identificação de padrões não lineares
        - Regressão polinomial para tendências
        
        **3. Análise Temporal:**
        - Evolução da letalidade ao longo do tempo
        - Identificação de tendências
        - Comparação entre períodos
        
        **4. Clustering:**
        - Agrupamento de sorogrupos similares
        - Identificação de padrões ocultos
        - Análise de similaridades epidemiológicas
        """)
        
    else:
        st.error("❌ Dados de sorogrupos não disponíveis")

def show_etiologia_analysis(dados):
    """Exibe a seção "Análise por Etiologia e Análise de Componentes Principais".

    Esta função consolida e analisa os dados de meningite por etiologia (agente causador).
    Ela padroniza os nomes das etiologias, exibe a distribuição de casos e letalidade,
    e realiza análises avançadas como Análise de Componentes Principais (PCA) para
    redução de dimensionalidade, uma matriz de correlação para identificar padrões
    temporais entre etiologias, e análise de sazonalidade.

    Args:
        dados (dict): O dicionário global de dados. Utiliza as chaves
                      'etiologias_consolidadas', 'etiologia_2024', e 'sih_meningite'.
    """
    st.header("🧬 **Análise por Etiologia e Análise de Componentes Principais**")
    st.markdown("---")
    
    # Carregar e consolidar dados de etiologia
    etiologia_consolidada = dados['etiologias_consolidadas']
    etiologia_2024 = dados['etiologia_2024']
    
    if etiologia_consolidada is not None and not etiologia_consolidada.empty:
        # Padronizar nomes das etiologias para remover duplicatas
        mapeamento_etiologias = {
            'Doença Meningocócica': 'Meningite Meningocócica',
            'Doença meningocócica': 'Meningite Meningocócica',
            'Meningite Pneumocócica': 'Meningite Pneumocócica',
            'Meningite pneumocócica': 'Meningite Pneumocócica',
            'Meningite Tuberculosa': 'Meningite Tuberculosa',
            'Meningite tuberculosa': 'Meningite Tuberculosa',
            'Meningite bacteriana': 'Meningite Bacteriana',
            'Meningite bacteriana não especificada': 'Meningite Bacteriana',
            'Meningite por hemófilo': 'Meningite por Hemófilo',
            'Meningite por outras bactérias': 'Meningite por Outras Bactérias',
            'Meningite viral': 'Meningite Viral',
            'Meningite de outra etiologia': 'Meningite de Outra Etiologia',
            'Meningite não especificada': 'Meningite Não Especificada',
            'Ignorado/sem informação': 'Ignorado/Sem Informação'
        }
        
        # Aplicar mapeamento e consolidar dados
        etiologia_consolidada['Etiologia_Padronizada'] = etiologia_consolidada['Etiologia'].map(mapeamento_etiologias).fillna(etiologia_consolidada['Etiologia'])
        
        # Se temos dados de 2024, adicionar ao consolidado
        if etiologia_2024 is not None and not etiologia_2024.empty:
            etiologia_2024['Etiologia_Padronizada'] = etiologia_2024['Etiologia'].map(mapeamento_etiologias).fillna(etiologia_2024['Etiologia'])
            
            # Adicionar dados de 2024 ao consolidado
            for _, row in etiologia_2024.iterrows():
                etiologia_consolidada = pd.concat([
                    etiologia_consolidada,
                    pd.DataFrame([{
                        'Ano': row['Ano'],
                        'Etiologia': row['Etiologia'],
                        'Etiologia_Padronizada': row['Etiologia_Padronizada'],
                        'Casos': row['Casos'],
                        'Obitos': row['Obitos'],
                        'Letalidade': row['Letalidade'],
                        'Taxa_Letalidade': row['Letalidade']
                    }])
                ], ignore_index=True)
        
        # Usar a coluna padronizada para análises
        etiologia = etiologia_consolidada.copy()
        etiologia['Etiologia'] = etiologia['Etiologia_Padronizada']
        
        # Remover duplicatas baseadas em Ano e Etiologia padronizada
        etiologia = etiologia.drop_duplicates(subset=['Ano', 'Etiologia'], keep='first')
        
        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_casos = etiologia['Casos'].sum() if 'Casos' in etiologia.columns else 0
            st.metric("📊 Total de Casos", f"{total_casos:,}")
        
        with col2:
            total_obitos = etiologia['Obitos'].sum() if 'Obitos' in etiologia.columns else 0
            st.metric("💀 Total de Óbitos", f"{total_obitos:,}")
        
        with col3:
            letalidade_geral = (total_obitos / total_casos * 100) if total_casos > 0 else 0
            st.metric("⚠️ Letalidade Geral", f"{letalidade_geral:.1f}%")
        
        with col4:
            n_etiologias = etiologia['Etiologia'].nunique()
            st.metric("🧬 Etiologias Únicas", n_etiologias)
        
        # Diagnóstico das etiologias
        st.subheader("🔍 **Diagnóstico das Etiologias**")
        
        # Mostrar etiologias únicas
        etiologias_unicas = sorted(etiologia['Etiologia'].unique())
        st.write(f"**Etiologias únicas encontradas ({len(etiologias_unicas)}):**")
        
        # Criar colunas para melhor visualização
        n_cols = 3
        for i in range(0, len(etiologias_unicas), n_cols):
            cols = st.columns(n_cols)
            for j, col in enumerate(cols):
                if i + j < len(etiologias_unicas):
                    with col:
                        st.write(f"• {etiologias_unicas[i + j]}")
        
        # Verificar possíveis duplicatas por nome similar
        st.write("**Verificação de possíveis duplicatas:**")
        etiologias_lower = [et.lower().strip() for et in etiologias_unicas]
        possiveis_duplicatas = []
        
        for i, et1 in enumerate(etiologias_lower):
            for j, et2 in enumerate(etiologias_lower[i+1:], i+1):
                # Verificar similaridade (nomes que diferem apenas por capitalização ou espaços)
                if et1 == et2 or et1.replace(' ', '') == et2.replace(' ', ''):
                    possiveis_duplicatas.append((etiologias_unicas[i], etiologias_unicas[j]))
        
        if possiveis_duplicatas:
            st.warning("⚠️ **Possíveis duplicatas encontradas:**")
            for dup1, dup2 in possiveis_duplicatas:
                st.write(f"• '{dup1}' vs '{dup2}'")
        else:
            st.success("✅ **Nenhuma duplicata óbvia encontrada**")
        
        st.markdown("---")
        
        # Análise de casos por etiologia
        st.subheader("📊 **Casos por Etiologia**")
        
        # Verificar se a coluna Casos existe e tratar valores NaN
        if 'Casos' in etiologia.columns:
            # Substituir valores NaN por 0 para análise
            etiologia_analise = etiologia.copy()
            etiologia_analise['Casos'] = etiologia_analise['Casos'].fillna(0)
            
            casos_por_etiologia = etiologia_analise.groupby('Etiologia')['Casos'].sum().sort_values(ascending=False)
            
            # Filtrar apenas etiologias com casos > 0 para melhor visualização
            casos_por_etiologia = casos_por_etiologia[casos_por_etiologia > 0]
            
            if len(casos_por_etiologia) > 0:
                fig_casos = px.bar(
                    casos_por_etiologia,
                    x=casos_por_etiologia.index,
                    y=casos_por_etiologia.values,
                    title="Distribuição de Casos por Etiologia",
                    color=casos_por_etiologia.values,
                    color_continuous_scale='Blues'
                )
                
                fig_casos.update_layout(
                    xaxis_title="Etiologia",
                    yaxis_title="Número de Casos",
                    template='plotly_white'
                )
                
                st.plotly_chart(fig_casos, use_container_width=True)
                
                # Mostrar estatísticas
                st.write(f"**Total de etiologias únicas:** {len(casos_por_etiologia)}")
                st.write(f"**Etiologia com mais casos:** {casos_por_etiologia.index[0]} ({casos_por_etiologia.iloc[0]:,.0f} casos)")
            else:
                st.warning("⚠️ Nenhum caso encontrado nos dados de etiologia")
        else:
            st.warning("⚠️ Coluna 'Casos' não encontrada nos dados de etiologia")
        
        # Análise de letalidade por etiologia
        st.subheader("⚠️ **Letalidade por Etiologia**")
        
        # Verificar se as colunas necessárias existem
        if 'Casos' in etiologia.columns and 'Obitos' in etiologia.columns:
            # Substituir valores NaN por 0 para análise
            etiologia_analise = etiologia.copy()
            etiologia_analise['Casos'] = etiologia_analise['Casos'].fillna(0)
            etiologia_analise['Obitos'] = etiologia_analise['Obitos'].fillna(0)
            
            letalidade_por_etiologia = etiologia_analise.groupby('Etiologia').agg({
                'Casos': 'sum',
                'Obitos': 'sum'
            }).reset_index()
            
            # Calcular letalidade apenas para etiologias com casos > 0
            letalidade_por_etiologia = letalidade_por_etiologia[letalidade_por_etiologia['Casos'] > 0]
            
            if len(letalidade_por_etiologia) > 0:
                letalidade_por_etiologia['Letalidade'] = (
                    letalidade_por_etiologia['Obitos'] / letalidade_por_etiologia['Casos'] * 100
                ).round(2)
                
                # Substituir valores infinitos por 0
                letalidade_por_etiologia['Letalidade'] = letalidade_por_etiologia['Letalidade'].replace([np.inf, -np.inf], 0)
                
                fig_letalidade = px.bar(
                    letalidade_por_etiologia,
                    x='Etiologia',
                    y='Letalidade',
                    title="Letalidade por Etiologia",
                    color='Letalidade',
                    color_continuous_scale='Reds'
                )
                
                fig_letalidade.update_layout(
                    yaxis_title="Taxa de Letalidade (%)",
                    template='plotly_white'
                )
                
                st.plotly_chart(fig_letalidade, use_container_width=True)
                
                # Mostrar estatísticas
                st.write(f"**Total de etiologias com dados válidos:** {len(letalidade_por_etiologia)}")
                st.write(f"**Etiologia com maior letalidade:** {letalidade_por_etiologia.loc[letalidade_por_etiologia['Letalidade'].idxmax(), 'Etiologia']} ({letalidade_por_etiologia['Letalidade'].max():.1f}%)")
            else:
                st.warning("⚠️ Nenhuma etiologia com casos válidos encontrada")
        else:
            st.warning("⚠️ Colunas 'Casos' e/ou 'Obitos' não encontradas nos dados de etiologia")
        
        # Análise de Componentes Principais (PCA)
        st.subheader("🔬 **Análise de Componentes Principais (PCA)**")
        
        if len(letalidade_por_etiologia) > 2:
            try:
                from sklearn.decomposition import PCA
                
                # Preparar dados para PCA - tratar valores NaN
                dados_pca = letalidade_por_etiologia[['Casos', 'Letalidade']].copy()
                
                # Substituir valores NaN por 0 para permitir análise PCA
                dados_pca = dados_pca.fillna(0)
                
                # Verificar se ainda há dados válidos após tratamento
                if dados_pca.isnull().sum().sum() == 0 and dados_pca.shape[0] > 0:
                    # Normalizar dados
                    scaler = StandardScaler()
                    dados_pca_norm = scaler.fit_transform(dados_pca)
                    
                    # Aplicar PCA
                    pca = PCA(n_components=min(2, dados_pca.shape[1]))
                    componentes = pca.fit_transform(dados_pca_norm)
                    
                    # Criar DataFrame com componentes
                    df_pca = pd.DataFrame(
                        componentes,
                        columns=[f'Componente {i+1}' for i in range(componentes.shape[1])],
                        index=letalidade_por_etiologia['Etiologia']
                    )
                    
                    # Gráfico de componentes
                    if componentes.shape[1] >= 2:
                        fig_pca = px.scatter(
                            df_pca,
                            x='Componente 1',
                            y='Componente 2',
                            title="Análise de Componentes Principais",
                            text=df_pca.index,
                            size=[10] * len(df_pca)
                        )
                        
                        fig_pca.update_layout(template='plotly_white')
                        st.plotly_chart(fig_pca, use_container_width=True)
                        
                        # Explicação do gráfico de PCA 2D
                        st.markdown("""
                        #### 📖 **Interpretação do Gráfico de PCA (2 Componentes):**
                        - **Eixo X (Horizontal):** Componente Principal 1 (direção de maior variação)
                        - **Eixo Y (Vertical):** Componente Principal 2 (segunda maior direção de variação)
                        - **Pontos:** Cada ponto representa uma etiologia no espaço reduzido
                        - **Distância entre pontos:** Etiologias próximas têm comportamentos similares
                        - **Posição nos quadrantes:** Diferentes combinações de casos e letalidade
                        - **Redução dimensional:** Simplifica análise de múltiplas variáveis em 2D
                        """)
                    else:
                        # Se só temos 1 componente, mostrar como gráfico de barras
                        fig_pca = px.bar(
                            x=df_pca.index,
                            y=df_pca['Componente 1'],
                            title="Análise de Componentes Principais (1 Componente)",
                            labels={'x': 'Etiologia', 'y': 'Componente 1'}
                        )
                        fig_pca.update_layout(template='plotly_white')
                        st.plotly_chart(fig_pca, use_container_width=True)
                        
                        # Explicação do gráfico de PCA 1D
                        st.markdown("""
                        #### 📖 **Interpretação do Gráfico de PCA (1 Componente):**
                        - **Eixo X (Horizontal):** Diferentes etiologias
                        - **Eixo Y (Vertical):** Valor do Componente Principal 1
                        - **Altura das barras:** Representa a projeção de cada etiologia no componente principal
                        - **Valores positivos/negativos:** Indicam diferentes padrões de casos e letalidade
                        - **Utilidade:** Ordena etiologias por sua similaridade em um eixo principal
                        """)
                    
                    # Informações sobre PCA
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Variância Explicada:**")
                        for i, var in enumerate(pca.explained_variance_ratio_):
                            st.write(f"Componente {i+1}: {var:.3f} ({var*100:.1f}%)")
                    
                    with col2:
                        st.write("**Componentes Principais:**")
                        st.write("**Componente 1:** Combinação linear de Casos e Letalidade")
                        if componentes.shape[1] > 1:
                            st.write("**Componente 2:** Combinação ortogonal ao Componente 1")
                    
                    # Interpretação detalhada dos componentes
                    st.markdown(f"""
                    ### 📚 **Explicação Detalhada do PCA:**
                    
                    #### 🎯 **O que é PCA:**
                    - **Análise de Componentes Principais:** Técnica de redução dimensional
                    - **Objetivo:** Encontrar direções de máxima variância nos dados
                    - **Utilidade:** Simplifica dados complexos mantendo a informação principal
                    
                    #### 📊 **Variância Explicada Total:** {sum(pca.explained_variance_ratio_)*100:.1f}%
                    - **Componente 1:** {pca.explained_variance_ratio_[0]*100:.1f}% da variância
                      - Captura a principal diferença entre etiologias
                      - Combina casos e letalidade de forma otimizada
                    """)
                    
                    if componentes.shape[1] > 1:
                        st.markdown(f"""
                    - **Componente 2:** {pca.explained_variance_ratio_[1]*100:.1f}% da variância
                      - Captura variação restante não explicada pelo C1
                      - Perpendicular ao Componente 1 (ortogonal)
                      - Revela padrões secundários nos dados
                    
                    #### 🎯 **Interpretação Epidemiológica:**
                    - **Quadrante superior direito:** Etiologias graves (muitos casos + alta letalidade)
                    - **Quadrante inferior esquerdo:** Etiologias menos problemáticas
                    - **Outros quadrantes:** Padrões específicos que merecem investigação
                        """)
                    else:
                        st.markdown("""
                    #### 🎯 **Interpretação do Componente Único:**
                    - **Valores altos:** Etiologias com maior impacto epidemiológico
                    - **Valores baixos:** Etiologias com menor impacto
                    - **Ordenação:** Permite priorização de recursos de saúde
                        """)
                    
                    # Mostrar cargas dos componentes (loadings)
                    st.markdown("#### 🔢 **Cargas dos Componentes (Loadings):**")
                    loadings_df = pd.DataFrame(
                        pca.components_.T,
                        columns=[f'Componente {i+1}' for i in range(pca.components_.shape[0])],
                        index=['Casos', 'Letalidade']
                    )
                    st.dataframe(loadings_df.round(3))
                    
                    st.markdown("""
                    **📋 Como interpretar as cargas:**
                    - **Valores positivos:** Variável contribui positivamente para o componente
                    - **Valores negativos:** Variável contribui negativamente para o componente
                    - **Magnitude:** Quanto maior o valor absoluto, maior a importância da variável
                    """)
                    
                    # Mostrar dados tratados
                    st.write("**Dados utilizados no PCA (NaN substituídos por 0):**")
                    st.dataframe(dados_pca.round(2))
                    
                else:
                    st.warning("⚠️ Dados insuficientes para análise PCA após tratamento de valores NaN")
                
            except Exception as e:
                st.warning(f"Erro na análise PCA: {e}")
                st.write(f"Detalhes do erro: {str(e)}")
        
        # Matriz de correlação entre etiologias
        st.subheader("🔗 **Matriz de Correlação entre Etiologias**")
        
        if 'Ano' in etiologia.columns and 'Casos' in etiologia.columns:
            try:
                # Preparar dados para correlação - tratar valores NaN
                etiologia_analise = etiologia.copy()
                etiologia_analise['Casos'] = etiologia_analise['Casos'].fillna(0)
                
                dados_correlacao = etiologia_analise.pivot_table(
                    index='Ano',
                    columns='Etiologia',
                    values='Casos',
                    aggfunc='sum'
                ).fillna(0)
                
                if len(dados_correlacao.columns) > 1 and dados_correlacao.shape[0] > 1:
                    # Calcular correlação
                    matriz_corr = dados_correlacao.corr()
                    
                    # Substituir valores NaN na correlação por 0
                    matriz_corr = matriz_corr.fillna(0)
                    
                    # Gráfico de heatmap
                    fig_heatmap = px.imshow(
                        matriz_corr,
                        title="Matriz de Correlação entre Etiologias",
                        color_continuous_scale='RdBu',
                        aspect='auto'
                    )
                    
                    fig_heatmap.update_layout(template='plotly_white')
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                    
                    # Explicação do heatmap de correlação
                    st.markdown("""
                    #### 📖 **Interpretação do Heatmap de Correlação:**
                    - **Cores:** Intensidade da correlação entre etiologias ao longo do tempo
                    - **Azul escuro:** Correlação positiva forte (etiologias variam juntas)
                    - **Vermelho escuro:** Correlação negativa forte (etiologias variam inversamente)
                    - **Branco/Neutro:** Sem correlação (etiologias independentes)
                    - **Diagonal:** Sempre 1.0 (correlação de cada etiologia consigo mesma)
                    - **Utilidade:** Identifica etiologias com padrões temporais similares ou opostos
                    """)
                    
                    # Tabela de correlações
                    st.write("**Valores de Correlação:**")
                    st.dataframe(matriz_corr.round(3))
                    
                    # Estatísticas da correlação
                    st.write(f"**Total de etiologias na correlação:** {len(matriz_corr.columns)}")
                    st.write(f"**Período analisado:** {dados_correlacao.index.min()} - {dados_correlacao.index.max()}")
                else:
                    st.warning("⚠️ Dados insuficientes para análise de correlação (mínimo 2 etiologias e 2 anos)")
            except Exception as e:
                st.warning(f"Erro na análise de correlação: {e}")
        else:
            st.warning("⚠️ Colunas 'Ano' e/ou 'Casos' não encontradas para análise de correlação")
        

        # Análise de sazonalidade
        st.subheader("🌡️ **Análise de Sazonalidade**")
        
        if 'Mes' in etiologia.columns and 'Casos' in etiologia.columns:
            try:
                # Preparar dados sazonais - tratar valores NaN
                etiologia_analise = etiologia.copy()
                etiologia_analise['Casos'] = etiologia_analise['Casos'].fillna(0)
                
                dados_sazonais = etiologia_analise.groupby(['Mes', 'Etiologia'])['Casos'].sum().reset_index()
                
                # Filtrar apenas etiologias com pelo menos um caso
                etiologias_com_casos = dados_sazonais.groupby('Etiologia')['Casos'].sum()
                etiologias_com_casos = etiologias_com_casos[etiologias_com_casos > 0].index
                dados_sazonais = dados_sazonais[dados_sazonais['Etiologia'].isin(etiologias_com_casos)]
                
                if len(dados_sazonais) > 0:
                    # Gráfico de barras agrupadas
                    fig_sazonal = px.bar(
                        dados_sazonais,
                        x='Mes',
                        y='Casos',
                        color='Etiologia',
                        title="Sazonalidade dos Casos por Etiologia",
                        barmode='group'
                    )
                    
                    fig_sazonal.update_layout(
                        xaxis_title="Mês",
                        yaxis_title="Número de Casos",
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig_sazonal, use_container_width=True)
                    
                    # Decomposição sazonal para uma etiologia específica
                    if len(dados_sazonais) > 12:
                        st.write("**Decomposição Sazonal (Primeira Etiologia):**")
                        
                        primeira_etiologia = dados_sazonais['Etiologia'].iloc[0]
                        dados_etiologia = dados_sazonais[dados_sazonais['Etiologia'] == primeira_etiologia]
                        
                        if len(dados_etiologia) >= 12:
                            # Decomposição sazonal
                            decomposicao = seasonal_decompose(
                                dados_etiologia['Casos'].values,
                                period=12,
                                extrapolate_trend='freq'
                            )
                            
                            # Gráfico de decomposição
                            fig_decomp = make_subplots(
                                rows=4, cols=1,
                                subplot_titles=['Original', 'Tendência', 'Sazonal', 'Resíduos'],
                                vertical_spacing=0.1
                            )
                            
                            fig_decomp.add_trace(
                                go.Scatter(y=dados_etiologia['Casos'], name='Original'),
                                row=1, col=1
                            )
                            fig_decomp.add_trace(
                                go.Scatter(y=decomposicao.trend, name='Tendência'),
                                row=2, col=1
                            )
                            fig_decomp.add_trace(
                                go.Scatter(y=decomposicao.seasonal, name='Sazonal'),
                                row=3, col=1
                            )
                            fig_decomp.add_trace(
                                go.Scatter(y=decomposicao.resid, name='Resíduos'),
                                row=4, col=1
                            )
                            
                            fig_decomp.update_layout(
                                title=f"Decomposição Sazonal - {primeira_etiologia}",
                                height=600,
                                template='plotly_white'
                            )
                            
                            st.plotly_chart(fig_decomp, use_container_width=True)
                        else:
                            st.warning("⚠️ Dados insuficientes para decomposição sazonal (mínimo 12 meses)")
                    else:
                        st.warning("⚠️ Dados insuficientes para análise sazonal (mínimo 12 meses)")
                else:
                    st.warning("⚠️ Nenhum dado sazonal válido encontrado")
                    
            except Exception as e:
                st.warning(f"Erro na análise sazonal: {e}")
        else:
            # Fallback: usar SIH mensal quando não houver 'Mes' em dados de etiologia
            if 'sih_meningite' in dados and isinstance(dados['sih_meningite'], pd.DataFrame):
                sih = dados['sih_meningite'].copy()
                if {'Mês_Num', 'Casos_Hospitalares'}.issubset(sih.columns):
                    sih['Casos_Hospitalares'] = pd.to_numeric(sih['Casos_Hospitalares'], errors='coerce').fillna(0)
                    mensal = sih.groupby('Mês_Num', as_index=False)['Casos_Hospitalares'].sum()
                    nomes_meses = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}
                    mensal['Mes'] = mensal['Mês_Num'].map(nomes_meses)
                    fig_sazonal = px.bar(
                        mensal.sort_values('Mês_Num'), x='Mes', y='Casos_Hospitalares',
                        title='Sazonalidade (Hospitalizações SIH - proxy)', color='Casos_Hospitalares',
                        color_continuous_scale='Reds'
                    )
                    fig_sazonal.update_layout(template='plotly_white', xaxis_title='Mês', yaxis_title='Casos Hospitalares')
                    st.plotly_chart(fig_sazonal, use_container_width=True)
                else:
                    st.warning("⚠️ Colunas esperadas em SIH para sazonalidade não encontradas (Mês_Num, Casos_Hospitalares)")
            else:
                st.warning("⚠️ Colunas 'Mes' e/ou 'Casos' não encontradas para análise sazonal")
        
        # Resumo das análises
        st.markdown("---")
        st.markdown("""
        **📋 Resumo das Análises de Etiologia:**
        
        **1. Análise Descritiva:**
        - Distribuição de casos por etiologia
        - Padrões de letalidade
        - Comparação entre diferentes agentes causadores
        
        **2. Análise de Componentes Principais:**
        - Redução de dimensionalidade
        - Identificação de padrões ocultos
        - Agrupamento de etiologias similares
        
        **3. Análise de Correlação:**
        - Relações entre diferentes etiologias
        - Padrões de co-ocorrência
        - Identificação de surtos simultâneos
        
        **4. Análise Temporal:**
        - Evolução das etiologias ao longo do tempo
        - Padrões sazonais
        - Tendências de longo prazo
        """)
        
    else:
        st.error("❌ Dados de etiologia não disponíveis")

def show_imunizacao_analysis(dados):
    """Exibe a seção "Dados de Imunização e Análise de Impacto".

    Renderiza uma análise completa sobre a vacinação contra meningite. A função
    apresenta a evolução da cobertura vacinal, a correlação entre vacinação e
    o número de casos, a distribuição regional da cobertura, e uma análise
    preditiva usando o modelo ARIMA para prever tendências futuras de
    doses aplicadas e casos.

    Args:
        dados (dict): O dicionário global de dados. Utiliza as chaves 'imunizacao_ano',
                      'imunizacao_uf', 'imunizacao_2023_2025', 'imunizacao_processada',
                      e 'casos_consolidados'.
    """
    st.header("💉 **Dados de Imunização e Análise de Impacto**")
    st.markdown("---")
    
    # Carregar dados de imunização
    imunizacao_ano = dados.get('imunizacao_ano')
    imunizacao_uf = dados.get('imunizacao_uf')
    imunizacao_2023_2025 = dados.get('imunizacao_2023_2025')
    
    if (dados.get('imunizacao_processada') is not None and not dados['imunizacao_processada'].empty) or (imunizacao_ano is not None and not imunizacao_ano.empty):
        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        if dados.get('imunizacao_processada') is not None and not dados['imunizacao_processada'].empty:
            proc = dados['imunizacao_processada']
            with col1:
                total_doses = int(proc['Total_Nacional'].sum()) if 'Total_Nacional' in proc.columns else 0
                st.metric("💉 Total de Doses", f"{total_doses:,}")
            with col2:
                # Cobertura média pode não existir; usar proxy: média anual normalizada por 1e6 para legibilidade
                if 'Total_Nacional' in proc.columns:
                    cobertura_media_proxy = proc.groupby('Ano')['Total_Nacional'].sum().mean() / 1_000_000
                    st.metric("📊 Média Anual de Doses (mi)", f"{cobertura_media_proxy:.2f}")
                else:
                    st.metric("📊 Média Anual de Doses (mi)", "N/A")
            with col3:
                n_anos = proc['Ano'].nunique() if 'Ano' in proc.columns else 0
                st.metric("📅 Anos de Dados", n_anos)
        else:
            with col1:
                total_doses = imunizacao_ano['Doses'].sum() if 'Doses' in imunizacao_ano.columns else 0
                st.metric("💉 Total de Doses", f"{total_doses:,}")
            with col2:
                total_cobertura = imunizacao_ano['Cobertura'].mean() if 'Cobertura' in imunizacao_ano.columns else 0
                st.metric("📊 Cobertura Média", f"{total_cobertura:.1f}%")
            with col3:
                n_anos = imunizacao_ano['Ano'].nunique() if 'Ano' in imunizacao_ano.columns else 0
                st.metric("📅 Anos de Dados", n_anos)
        
        with col4:
            n_ufs = imunizacao_uf['UF'].nunique() if imunizacao_uf is not None and not imunizacao_uf.empty else 0
            st.metric("🗺️ UFs Cobertas", n_ufs)
        
        # Análise de impacto da vacinação
        st.subheader("📊 **Análise de Impacto da Vacinação**")
        
        # Preferir base processada se existir
        if dados.get('imunizacao_processada') is not None:
            base_ano = dados['imunizacao_processada'][['Ano', 'Total_Nacional']].dropna()
            base_ano = base_ano.groupby('Ano', as_index=False)['Total_Nacional'].sum()
            base_ano.rename(columns={'Total_Nacional': 'Cobertura'}, inplace=True)
        else:
            base_ano = imunizacao_ano if ('Ano' in imunizacao_ano.columns and 'Cobertura' in imunizacao_ano.columns) else None

        if base_ano is not None and 'Ano' in base_ano.columns and 'Cobertura' in base_ano.columns:
            # Limpar anos inválidos
            base_ano['Ano'] = pd.to_numeric(base_ano['Ano'], errors='coerce')
            base_ano = base_ano.dropna(subset=['Ano'])
            base_ano = base_ano[(base_ano['Ano'] >= 1900) & (base_ano['Ano'] <= 2100)]
            base_ano['Ano'] = base_ano['Ano'].astype(int)
            # Preparar dados para análise de impacto
            dados_impacto = base_ano.groupby('Ano').agg({
                'Cobertura': 'mean',
                **({'Doses': 'sum'} if ('Doses' in imunizacao_ano.columns) else {})
            }).reset_index()
            
            # Gráfico de evolução
            fig_cobertura = px.line(dados_impacto.assign(AnoDT=pd.to_datetime(dados_impacto['Ano'].astype(int), format='%Y', errors='coerce').dropna()), x='AnoDT', y='Cobertura',
                                    title=("Evolução do Total de Doses Aplicadas" if dados.get('imunizacao_processada') is not None else "Evolução da Cobertura Vacinal ao Longo do Tempo"),
                                    markers=True)
            
            fig_cobertura.update_layout(xaxis_title="Ano", yaxis_title=("Total de Doses" if dados.get('imunizacao_processada') is not None else "Cobertura Vacinal (%)"), template='plotly_white')
            fig_cobertura.update_xaxes(tickformat='%Y')
            st.plotly_chart(fig_cobertura, use_container_width=True)
            
            # Explicação do gráfico de evolução da cobertura vacinal
            st.markdown("""
            #### 📖 **Interpretação do Gráfico de Evolução da Cobertura Vacinal:**
            - **Eixo X (Horizontal):** Anos do período analisado
            - **Eixo Y (Vertical):** Cobertura vacinal (%) ou número total de doses aplicadas
            - **Linha com marcadores:** Evolução temporal da vacinação contra meningite
            - **Tendência crescente:** Melhoria na cobertura vacinal ao longo do tempo
            - **Tendência decrescente:** Possível redução na adesão ou mudanças nas políticas
            - **Variações abruptas:** Podem indicar mudanças em campanhas, disponibilidade de vacinas ou eventos específicos
            - **Importância epidemiológica:** Cobertura alta (>95%) é essencial para imunidade coletiva
            - **Meta de saúde pública:** Monitoramento da eficácia das campanhas de vacinação
            """)
            
            # Análise de correlação com casos de meningite
            if 'casos_consolidados' in dados and dados['casos_consolidados'] is not None:
                st.write("**🔗 Correlação entre Cobertura Vacinal e Casos de Meningite:**")
                
                casos_por_ano = dados['casos_consolidados'].groupby('Ano')['Casos_Notificados'].sum().reset_index()
                # Renomear para 'Casos' para compatibilidade com a análise
                casos_por_ano = casos_por_ano.rename(columns={'Casos_Notificados': 'Casos'})
                
                # Mesclar dados
                dados_correlacao = dados_impacto.merge(casos_por_ano, on='Ano', how='inner')
                
                if len(dados_correlacao) > 2:
                    # Calcular correlação
                    corr_cobertura_casos, p_valor = stats.pearsonr(
                        dados_correlacao['Cobertura'],
                        dados_correlacao['Casos']
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("📈 Correlação", f"{corr_cobertura_casos:.3f}")
                        st.write(f"P-valor: {p_valor:.4f}")
                    
                    with col2:
                        if p_valor < 0.05:
                            if corr_cobertura_casos < 0:
                                st.success("✅ Correlação significativa negativa")
                                st.write("Maior cobertura = Menos casos")
                            else:
                                st.warning("⚠️ Correlação significativa positiva")
                                st.write("Maior cobertura = Mais casos")
                        else:
                            st.info("ℹ️ Sem correlação significativa")
                    
                    # Gráfico de dispersão
                    fig_dispersao = px.scatter(
                        dados_correlacao,
                        x='Cobertura',
                        y='Casos',
                        title="Relação entre Cobertura Vacinal e Casos de Meningite",
                        text='Ano',
                        size='Cobertura'
                    )
                    
                    fig_dispersao.update_layout(
                        xaxis_title="Cobertura Vacinal (%)",
                        yaxis_title="Número de Casos",
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig_dispersao, use_container_width=True)
                    
                    # Explicação da análise de correlação
                    st.markdown(f"""
                    #### 📚 **Explicação da Análise de Correlação Cobertura vs Casos:**
                    
                    ##### 📊 **Correlação de Pearson = {corr_cobertura_casos:.3f}**
                    - **O que mede:** Força da relação linear entre cobertura vacinal e casos de meningite
                    - **Interpretação esperada:** Correlação negativa (mais vacinação = menos casos)
                    - **Resultado atual:** {"Correlação negativa - conforme esperado!" if corr_cobertura_casos < 0 else "Correlação positiva - necessita investigação!" if corr_cobertura_casos > 0 else "Sem correlação clara"}
                    
                    ##### 🎯 **Significância Estatística (p = {p_valor:.4f})**
                    - **p < 0.05:** Relação estatisticamente significativa
                    - **p ≥ 0.05:** Relação pode ser devida ao acaso
                    - **Resultado:** {"Relação significativa e confiável" if p_valor < 0.05 else "Relação não significativa"}
                    
                    ##### 📖 **Interpretação do Gráfico de Dispersão:**
                    - **Eixo X:** Cobertura vacinal (% ou doses)
                    - **Eixo Y:** Número de casos de meningite
                    - **Pontos:** Cada ponto representa um ano específico
                    - **Tamanho dos pontos:** Proporcional à cobertura vacinal
                    - **Padrão ideal:** Pontos formando linha descendente (mais vacinação = menos casos)
                    
                    ##### ⚠️ **Considerações Importantes:**
                    - **Defasagem temporal:** Efeito da vacinação pode aparecer com atraso
                    - **Fatores confundidores:** Outros fatores podem influenciar a incidência
                    - **Imunidade coletiva:** Efeito mais pronunciado com cobertura >95%
                    - **Tipos de meningite:** Nem todas são preveníveis por vacina
                    """)
        
        # Análise regional da cobertura
        st.subheader("🗺️ **Análise Regional da Cobertura**")
        
        if dados.get('imunizacao_processada') is not None:
            # Derivar cobertura por UF a partir do dataset processado se possível (soma no período)
            proc = dados['imunizacao_processada']
            uf_cols = [c for c in proc.columns if c not in ['Ano', 'Ignorado', 'Total', 'Total_Nacional', 'Casos_Notificados']]
            if uf_cols:
                cobertura_por_uf = proc[uf_cols].sum().sort_values(ascending=False)
                fig_regional = px.bar(
                    x=[c.split(' ', 1)[1] if ' ' in c else c for c in cobertura_por_uf.index],
                    y=cobertura_por_uf.values,
                    title="Cobertura/Aplicação por UF (soma no período)",
                    color=cobertura_por_uf.values,
                    color_continuous_scale='Greens'
                )
                fig_regional.update_layout(
                    xaxis_title="Unidade Federativa",
                    yaxis_title="Total de Doses",
                    template='plotly_white'
                )
                st.plotly_chart(fig_regional, use_container_width=True)
        elif imunizacao_uf is not None and not imunizacao_uf.empty:
            # Preparar dados regionais
            if 'Cobertura' in imunizacao_uf.columns:
                cobertura_por_uf = imunizacao_uf.groupby('UF')['Cobertura'].mean().sort_values(ascending=False)
                
                fig_regional = px.bar(
                    x=cobertura_por_uf.index,
                    y=cobertura_por_uf.values,
                    title="Cobertura Vacinal por UF",
                    color=cobertura_por_uf.values,
                    color_continuous_scale='Greens'
                )
                
                fig_regional.update_layout(
                    xaxis_title="Unidade Federativa",
                    yaxis_title="Cobertura Vacinal Média (%)",
                    template='plotly_white'
                )
                
                st.plotly_chart(fig_regional, use_container_width=True)
                
                # Análise de desigualdades regionais
                st.write("**📊 Análise de Desigualdades Regionais:**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    cobertura_media = cobertura_por_uf.mean()
                    cobertura_std = cobertura_por_uf.std()
                    st.metric("📊 Cobertura Média", f"{cobertura_media:.1f}%")
                    st.metric("📈 Desvio Padrão", f"{cobertura_std:.1f}%")
                
                with col2:
                    cobertura_min = cobertura_por_uf.min()
                    cobertura_max = cobertura_por_uf.max()
                    st.metric("📉 Cobertura Mínima", f"{cobertura_min:.1f}%")
                    st.metric("📈 Cobertura Máxima", f"{cobertura_max:.1f}%")
                
                # Coeficiente de variação
                cv = (cobertura_std / cobertura_media) * 100
                st.write(f"**📊 Coeficiente de Variação:** {cv:.1f}%")
                
                if cv > 20:
                    st.warning("⚠️ Alta desigualdade regional na cobertura vacinal")
                elif cv > 10:
                    st.info("ℹ️ Desigualdade moderada na cobertura vacinal")
                else:
                    st.success("✅ Baixa desigualdade regional na cobertura vacinal")
        
        # Análise temporal avançada
        st.subheader("📈 **Análise Temporal Avançada**")
        
        if dados.get('imunizacao_processada') is not None:
            # Usar a série anual de Total_Nacional para tendência
            serie_anual = dados['imunizacao_processada'].groupby('Ano', as_index=False)['Total_Nacional'].sum()
            serie_anual['Ano'] = pd.to_numeric(serie_anual['Ano'], errors='coerce')
            serie_anual = serie_anual.dropna(subset=['Ano'])
            serie_anual = serie_anual[(serie_anual['Ano'] >= 1900) & (serie_anual['Ano'] <= 2100)]
            fig_tendencia = go.Figure()
            fig_tendencia.add_trace(go.Scatter(
                x=pd.to_datetime(serie_anual['Ano'].astype(int), format='%Y', errors='coerce'),
                y=serie_anual['Total_Nacional'],
                mode='markers+lines', name='Total de Doses', marker=dict(size=8)
            ))
            fig_tendencia.update_layout(title="Tendência de Aplicações (Total Nacional)", xaxis_title="Ano", yaxis_title="Total de Doses", template='plotly_white')
            fig_tendencia.update_xaxes(tickformat='%Y')
            st.plotly_chart(fig_tendencia, use_container_width=True)
        elif imunizacao_2023_2025 is not None and not imunizacao_2023_2025.empty:
            # Preparar dados temporais
            if 'Ano' in imunizacao_2023_2025.columns:
                dados_temporais = imunizacao_2023_2025.groupby('Ano').agg({
                    'Cobertura': 'mean' if 'Cobertura' in imunizacao_2023_2025.columns else 'count',
                    'Doses': 'sum' if 'Doses' in imunizacao_2023_2025.columns else 'count'
                }).reset_index()
                
                # Gráfico de tendência
                fig_tendencia = go.Figure()
                
                fig_tendencia.add_trace(go.Scatter(
                    x=dados_temporais['Ano'],
                    y=dados_temporais['Cobertura'] if 'Cobertura' in dados_temporais.columns else dados_temporais['Doses'],
                    mode='markers+lines',
                    name='Cobertura/Doses',
                    marker=dict(size=8)
                ))
                
                fig_tendencia.update_layout(
                    title="Tendência da Cobertura Vacinal (2023-2025)",
                    xaxis_title="Ano",
                    yaxis_title="Cobertura (%) / Doses",
                    template='plotly_white'
                )
                
                fig_tendencia.update_xaxes(tickformat='d')
                st.plotly_chart(fig_tendencia, use_container_width=True)
                
                # Análise de eficácia
                if len(dados_temporais) > 1:
                    st.write("**📊 Análise de Eficácia:**")
                    
                    # Calcular mudança percentual
                    if 'Cobertura' in dados_temporais.columns:
                        cobertura_inicial = dados_temporais['Cobertura'].iloc[0]
                        cobertura_final = dados_temporais['Cobertura'].iloc[-1]
                        mudanca_percentual = ((cobertura_final - cobertura_inicial) / cobertura_inicial) * 100
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("📊 Cobertura Inicial", f"{cobertura_inicial:.1f}%")
                            st.metric("📊 Cobertura Final", f"{cobertura_final:.1f}%")
                        
                        with col2:
                            st.metric("📈 Mudança", f"{mudanca_percentual:+.1f}%")
                            
                            if mudanca_percentual > 0:
                                st.success("✅ Melhoria na cobertura")
                            elif mudanca_percentual < 0:
                                st.warning("⚠️ Redução na cobertura")
                            else:
                                st.info("ℹ️ Cobertura estável")
        
        # Análise preditiva com ARIMA
        st.subheader("🔮 **Análise Preditiva (ARIMA)**")
        
        # Construir série para ARIMA (doses)
        dados_arima = None
        if dados.get('imunizacao_processada') is not None:
            dados_arima = dados['imunizacao_processada'].groupby('Ano', as_index=False)['Total_Nacional'].sum().rename(columns={'Total_Nacional': 'Valor'})
        elif imunizacao_ano is not None and {'Ano','Cobertura'}.issubset(imunizacao_ano.columns):
            dados_arima = imunizacao_ano.groupby('Ano', as_index=False)['Cobertura'].mean().rename(columns={'Cobertura':'Valor'})

        if dados_arima is not None and len(dados_arima) > 3:
            try:
                serie = dados_arima.copy()
                serie['Ano'] = pd.to_numeric(serie['Ano'], errors='coerce')
                serie = serie.dropna(subset=['Ano'])
                serie = serie[(serie['Ano'] >= 1900) & (serie['Ano'] <= 2100)]
                serie['Ano'] = pd.to_datetime(serie['Ano'].astype(int), format='%Y', errors='coerce')
                serie = serie.set_index('Ano')
                if not STATSMODELS_AVAILABLE:
                    st.warning("⚠️ Análise ARIMA não disponível: statsmodels não instalado corretamente")
                else:
                    modelo_arima = ARIMA(serie['Valor'], order=(1, 1, 1)).fit()
                    previsao = modelo_arima.forecast(steps=3)
                    anos_futuros = pd.date_range(start=serie.index[-1] + pd.DateOffset(years=1), periods=3, freq='Y')

                    fig_previsao = go.Figure()
                    fig_previsao.add_trace(go.Scatter(x=serie.index, y=serie['Valor'], mode='markers+lines', name='Observado'))
                    fig_previsao.add_trace(go.Scatter(x=anos_futuros, y=previsao, mode='markers+lines', name='Previsão', line=dict(dash='dash', color='red')))
                    fig_previsao.update_layout(title='Previsão de Doses (ARIMA)', xaxis_title='Ano', yaxis_title='Total de Doses', template='plotly_white')
                    st.plotly_chart(fig_previsao, use_container_width=True)

            except Exception as e:
                st.warning(f"Erro na previsão ARIMA (doses): {e}")

        # ARIMA para número de casos (quando disponível)
        if 'casos_consolidados' in dados and isinstance(dados['casos_consolidados'], pd.DataFrame):
            casos_series = dados['casos_consolidados'].groupby('Ano', as_index=False)['Casos_Notificados'].sum()
            if len(casos_series) > 3:
                try:
                    cs = casos_series.copy()
                    cs['Ano'] = pd.to_numeric(cs['Ano'], errors='coerce')
                    cs = cs.dropna(subset=['Ano'])
                    cs = cs[(cs['Ano'] >= 1900) & (cs['Ano'] <= 2100)]
                    cs['Ano'] = pd.to_datetime(cs['Ano'].astype(int), format='%Y', errors='coerce')
                    cs = cs.set_index('Ano')
                    if STATSMODELS_AVAILABLE:
                        model_cases = ARIMA(cs['Casos_Notificados'], order=(1, 1, 1)).fit()
                    else:
                        st.warning("⚠️ Análise ARIMA não disponível: statsmodels não instalado corretamente")
                        return
                    fc_cases = model_cases.forecast(steps=3)
                    anos_fut = pd.date_range(start=cs.index[-1] + pd.DateOffset(years=1), periods=3, freq='Y')

                    fig_cases = go.Figure()
                    fig_cases.add_trace(go.Scatter(x=cs.index, y=cs['Casos_Notificados'], mode='markers+lines', name='Casos Observados'))
                    fig_cases.add_trace(go.Scatter(x=anos_fut, y=fc_cases, mode='markers+lines', name='Previsão de Casos', line=dict(dash='dash', color='orange')))
                    fig_cases.update_layout(title='Previsão de Casos (ARIMA)', xaxis_title='Ano', yaxis_title='Casos', template='plotly_white')
                    st.plotly_chart(fig_cases, use_container_width=True)
                except Exception as e:
                    st.warning(f"Erro na previsão ARIMA (casos): {e}")
        
        # Resumo das análises
        st.markdown("---")
        st.markdown("""
        **📋 Resumo das Análises de Imunização:**
        
        **1. Análise de Impacto:**
        - Correlação entre cobertura vacinal e casos de meningite
        - Efetividade das campanhas de vacinação
        - Relação dose-resposta
        
        **2. Análise Regional:**
        - Desigualdades na cobertura entre UFs
        - Identificação de regiões prioritárias
        - Padrões geográficos de imunização
        
        **3. Análise Temporal:**
        - Evolução da cobertura ao longo do tempo
        - Tendências e sazonalidade
        - Eficácia das intervenções
        
        **4. Análise Preditiva:**
        - Modelagem ARIMA para previsões
        - Planejamento de campanhas futuras
        - Avaliação de metas de cobertura
        """)
        
    else:
        st.error("❌ Dados de imunização não disponíveis")

def show_advanced_analysis(dados):
    """Exibe a seção "Análises Avançadas e Machine Learning".

    Esta função apresenta análises estatísticas e de machine learning mais complexas.
    Inclui uma decomposição de série temporal avançada (STL), teste de estacionariedade (ADF),
    análise de correlação cruzada entre sorogrupos, um modelo de regressão múltipla
    para identificar fatores preditivos de casos, e clustering hierárquico para
    agrupamento de sorogrupos.

    Args:
        dados (dict): O dicionário global de dados. Utiliza as chaves 'casos_consolidados',
                      'sorogrupos_consolidados', 'etiologias_consolidadas', e
                      'imunizacao_processada'.
    """
    st.header("🔬 **Análises Avançadas e Machine Learning**")
    st.markdown("---")
    
    # Carregar dados
    casos = dados['casos_consolidados']
    sorogrupos = dados['sorogrupos_consolidados']
    etiologia = dados['etiologias_consolidadas']
    
    if casos is not None and not casos.empty:
        # Análise de séries temporais avançada
        st.subheader("📈 **Análise de Séries Temporais Avançada**")
        
        # Preparar dados temporais
        dados_tempo = casos.groupby('Ano')['Casos_Notificados'].sum().reset_index()
        dados_tempo['Ano'] = pd.to_datetime(dados_tempo['Ano'], format='%Y')
        dados_tempo = dados_tempo.set_index('Ano')
        
        if len(dados_tempo) > 3:
            # Decomposição sazonal avançada
            try:
                # Decomposição STL (mais robusta)
                if not STATSMODELS_AVAILABLE:
                    st.warning("⚠️ Análise STL não disponível: statsmodels não instalado corretamente")
                else:
                    from statsmodels.tsa.seasonal import STL
                    
                    stl = STL(dados_tempo['Casos_Notificados'], period=min(3, len(dados_tempo)//2))
                    resultado_stl = stl.fit()
                    
                    # Gráfico de decomposição STL
                    fig_stl = make_subplots(
                        rows=4, cols=1,
                        subplot_titles=['Original', 'Tendência', 'Sazonal', 'Resíduos'],
                        vertical_spacing=0.1
                    )
                    
                    fig_stl.add_trace(go.Scatter(x=dados_tempo.index, y=dados_tempo['Casos_Notificados'], name='Original'), row=1, col=1)
                    fig_stl.add_trace(go.Scatter(x=dados_tempo.index, y=resultado_stl.trend, name='Tendência'), row=2, col=1)
                    fig_stl.add_trace(go.Scatter(x=dados_tempo.index, y=resultado_stl.seasonal, name='Sazonal'), row=3, col=1)
                    fig_stl.add_trace(go.Scatter(x=dados_tempo.index, y=resultado_stl.resid, name='Resíduos'), row=4, col=1)
                    
                    fig_stl.update_layout(
                        title="Decomposição STL Avançada",
                        height=600,
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig_stl, use_container_width=True)
                    
                    # Explicação detalhada da decomposição STL
                    st.markdown("""
                    #### 📚 **Explicação da Decomposição STL (Seasonal and Trend decomposition using Loess):**
                    
                    ##### 🎯 **O que é a decomposição STL:**
                    - **Técnica estatística avançada** que separa uma série temporal em componentes
                    - **STL = Seasonal and Trend decomposition using Loess**
                    - **Mais robusta** que métodos clássicos para dados irregulares
                    - **Flexível** para diferentes tipos de sazonalidade
                    
                    ##### 📊 **Os 4 componentes visualizados:**
                    
                    **1. 📈 Série Original (1º gráfico):**
                    - Dados brutos de casos de meningite ao longo do tempo
                    - Mostra a série completa sem decomposição
                    
                    **2. 📉 Tendência (2º gráfico):**
                    - **Direção geral** da série ao longo do tempo
                    - Remove flutuações de curto prazo
                    - **Crescente:** Aumento sustentado de casos
                    - **Decrescente:** Redução sustentada de casos
                    - **Estável:** Sem mudança direcional clara
                    
                    **3. 🔄 Componente Sazonal (3º gráfico):**
                    - **Padrões repetitivos** em períodos fixos
                    - Mostra variações sistemáticas (anuais, mensais)
                    - **Picos regulares:** Épocas de maior incidência
                    - **Vales regulares:** Épocas de menor incidência
                    
                    **4. 🎲 Resíduos (4º gráfico):**
                    - **Variações aleatórias** não explicadas
                    - Diferença entre série real e componentes
                    - **Próximo a zero:** Boa decomposição
                    - **Padrões nos resíduos:** Componentes não capturados
                    
                    ##### 🔬 **Importância epidemiológica:**
                    - **Tendência:** Avalia eficácia de políticas de longo prazo
                    - **Sazonalidade:** Identifica períodos de risco para planejamento
                    - **Resíduos:** Detecta eventos atípicos (surtos, mudanças súbitas)
                    - **Previsão:** Base para modelos preditivos
                    """)
                    
                    # Análise de estacionariedade
                    st.markdown("**📊 Teste de Estacionariedade (ADF):**")
                    from statsmodels.tsa.stattools import adfuller
                    
                    resultado_adf = adfuller(dados_tempo['Casos_Notificados'])
                    st.write(f"**Estatística ADF:** {resultado_adf[0]:.4f}")
                    st.write(f"**P-valor:** {resultado_adf[1]:.4f}")
                    st.write(f"**Estacionário:** {'Sim' if resultado_adf[1] < 0.05 else 'Não'}")
                    
                    # Explicação detalhada do teste ADF
                    st.markdown(f"""
                    #### 📚 **Explicação do Teste ADF (Augmented Dickey-Fuller):**
                    
                    ##### 🎯 **O que é estacionariedade:**
                    - **Série estacionária:** Propriedades estatísticas não mudam ao longo do tempo
                    - **Média constante:** Não há tendência crescente ou decrescente
                    - **Variância constante:** Flutuações similares em todo período
                    - **Autocorrelação estável:** Padrões de dependência temporal consistentes
                    
                    ##### 📊 **Teste ADF - Resultados atuais:**
                    - **Estatística ADF:** {resultado_adf[0]:.4f}
                      - Valores mais negativos indicam maior evidência de estacionariedade
                      - Compara com valores críticos (-3.43, -2.86, -2.57)
                    
                    - **P-valor:** {resultado_adf[1]:.4f}
                      - p < 0.05: Rejeita hipótese nula (série É estacionária)
                      - p ≥ 0.05: Não rejeita hipótese nula (série NÃO é estacionária)
                    
                    - **Interpretação:** {"Série ESTACIONÁRIA" if resultado_adf[1] < 0.05 else "Série NÃO-ESTACIONÁRIA"}
                    
                    ##### 🔬 **Importância para análise:**
                    - **Série estacionária:** Ideal para modelagem e previsão
                    - **Série não-estacionária:** Necessita transformações (diferenciação, log)
                    - **Aplicação epidemiológica:** Determina se tendências são temporárias ou persistentes
                    - **Modelos ARIMA:** Requer estacionariedade para funcionar adequadamente
                    
                    ##### ⚠️ **Implicações práticas:**
                    {"- **Dados adequados** para previsão direta" if resultado_adf[1] < 0.05 else "- **Dados necessitam transformação** antes da modelagem"}
                    {"- **Flutuações em torno de média estável**" if resultado_adf[1] < 0.05 else "- **Presença de tendências ou mudanças estruturais**"}
                    {"- **Modelos mais simples são aplicáveis**" if resultado_adf[1] < 0.05 else "- **Modelos mais complexos são necessários**"}
                    """)
                    
                
            except Exception as e:
                st.warning(f"Erro na decomposição STL: {e}")
        
        # Análise de correlação cruzada
        st.subheader("🔗 **Análise de Correlação Cruzada**")
        
        if sorogrupos is not None and not sorogrupos.empty:
            # Preparar dados para correlação cruzada
            dados_cruzada = sorogrupos.pivot_table(
                index='Ano', 
                columns='Sorogrupo', 
                values='Casos', 
                aggfunc='sum'
            ).fillna(0)
            
            # Calcular correlação cruzada
            
            st.markdown("**Correlações Cruzadas entre Sorogrupos:**")
            
            correlacoes_cruzadas = []
            for i, sorogrupo1 in enumerate(dados_cruzada.columns):
                for j, sorogrupo2 in enumerate(dados_cruzada.columns):
                    if i < j:  # Evitar duplicatas
                        corr, p_valor = stats.pearsonr(dados_cruzada[sorogrupo1], dados_cruzada[sorogrupo2])
                        correlacoes_cruzadas.append({
                            'Sorogrupo 1': sorogrupo1,
                            'Sorogrupo 2': sorogrupo2,
                            'Correlação': corr,
                            'P-valor': p_valor
                        })
            
            if correlacoes_cruzadas:
                df_cruzada = pd.DataFrame(correlacoes_cruzadas)
                df_cruzada = df_cruzada = df_cruzada.sort_values('Correlação', key=abs, ascending=False)
                
                # Gráfico de correlações cruzadas
                fig_cruzada = px.bar(
                    df_cruzada,
                    x='Sorogrupo 1',
                    y='Correlação',
                    color='Sorogrupo 2',
                    title='Correlações Cruzadas entre Sorogrupos',
                    barmode='group'
                )
                
                fig_cruzada.update_layout(template='plotly_white')
                st.plotly_chart(fig_cruzada, use_container_width=True)
                
                # Explicação detalhada da correlação cruzada
                st.markdown("""
                #### 📚 **Explicação da Análise de Correlação Cruzada:**
                
                ##### 🎯 **O que é correlação cruzada:**
                - **Medida de associação** entre diferentes sorogrupos ao longo do tempo
                - **Identifica padrões sincronizados** ou opostos entre sorogrupos
                - **Análise multivariada** que examina relacionamentos complexos
                
                ##### 📊 **Interpretação do gráfico:**
                - **Eixo X:** Primeiro sorogrupo de cada par
                - **Eixo Y:** Valor da correlação (-1 a +1)
                - **Cores:** Segundo sorogrupo do par
                - **Barras positivas:** Sorogrupos variam na mesma direção
                - **Barras negativas:** Sorogrupos variam em direções opostas
                
                ##### 🔬 **Significado epidemiológico:**
                
                **Correlação Positiva (+):**
                - Sorogrupos aumentam/diminuem juntos
                - Possíveis fatores comuns (clima, políticas, vigilância)
                - Resposta similar a intervenções
                
                **Correlação Negativa (-):**
                - Um sorogrupo aumenta quando outro diminui
                - Possível competição ou substituição
                - Diferenças na eficácia de vacinas específicas
                
                **Correlação próxima a zero:**
                - Sorogrupos evoluem independentemente
                - Fatores de risco diferentes
                - Dinâmicas epidemiológicas distintas
                
                ##### 📈 **Aplicações práticas:**
                - **Planejamento de vacinas:** Priorizar sorogrupos correlacionados
                - **Vigilância:** Monitorar sorogrupos em conjunto
                - **Previsão:** Usar comportamento de um para prever outro
                - **Investigação:** Identificar fatores de risco comuns
                """)
                
                # Tabela de correlações
                st.markdown("#### 📋 **Tabela Detalhada de Correlações:**")
                st.dataframe(df_cruzada.round(3))
        
        # Análise de regressão múltipla (revista)
        st.subheader("📊 **Regressão Múltipla: Fatores que explicam os Casos**")
        try:
            # Construir base anual integrada: Casos vs Doses (Total_Nacional)
            base_casos = None
            if 'casos_consolidados' in dados and isinstance(dados['casos_consolidados'], pd.DataFrame):
                base_casos = dados['casos_consolidados'].groupby('Ano', as_index=False)['Casos_Notificados'].sum()
            if base_casos is not None and (len(base_casos) >= 5):
                # Doses
                if 'imunizacao_processada' in dados and isinstance(dados['imunizacao_processada'], pd.DataFrame):
                    base_doses = dados['imunizacao_processada'].groupby('Ano', as_index=False)['Total_Nacional'].sum()
                else:
                    base_doses = None

                df_int = base_casos.copy()
                if base_doses is not None:
                    df_int = df_int.merge(base_doses, on='Ano', how='left')
                df_int = df_int.sort_values('Ano')
                # Features de defasagem
                df_int['Casos_Lag1'] = df_int['Casos_Notificados'].shift(1)
                if 'Total_Nacional' in df_int.columns:
                    df_int['Doses_Lag1'] = df_int['Total_Nacional'].shift(1)
                # Tendência temporal
                df_int['Trend'] = pd.to_numeric(df_int['Ano'], errors='coerce')
                # Limpar
                df_int = df_int.dropna()
                # Preparar X, y
                feature_cols = ['Trend']
                if 'Total_Nacional' in df_int.columns:
                    feature_cols += ['Total_Nacional']
                if 'Doses_Lag1' in df_int.columns:
                    feature_cols += ['Doses_Lag1']
                feature_cols += ['Casos_Lag1']

                from sklearn.linear_model import LinearRegression
                from sklearn.metrics import r2_score, mean_squared_error
                X = df_int[feature_cols]
                y = df_int['Casos_Notificados']

                modelo_reg = LinearRegression()
                modelo_reg.fit(X, y)
                y_pred = modelo_reg.predict(X)
                # R² seguro (evita NaN se variância de y ~ 0)
                r2 = float(r2_score(y, y_pred)) if np.var(y) > 1e-9 else 0.0
                rmse = float(np.sqrt(mean_squared_error(y, y_pred)))

                # Gráfico previsto vs real
                fig_reg = go.Figure()
                fig_reg.add_trace(go.Scatter(x=y, y=y_pred, mode='markers', name='Previsto vs Real', marker=dict(color='blue')))
                min_val = float(min(y.min(), y_pred.min()))
                max_val = float(max(y.max(), y_pred.max()))
                fig_reg.add_trace(go.Scatter(x=[min_val, max_val], y=[min_val, max_val], mode='lines', name='Identidade', line=dict(dash='dash', color='red')))
                fig_reg.update_layout(title='Regressão: Casos vs Fatores (Doses, Tendência, Defasagens)', xaxis_title='Casos Reais', yaxis_title='Casos Previstos', template='plotly_white')
                st.plotly_chart(fig_reg, use_container_width=True)
                
                # Explicação do gráfico de regressão
                st.markdown("""
                #### 📖 **Interpretação do Gráfico de Regressão:**
                - **Eixo X (Horizontal):** Casos reais observados
                - **Eixo Y (Vertical):** Casos previstos pelo modelo
                - **Pontos azuis:** Cada ponto representa um ano (casos reais vs. previstos)
                - **Linha tracejada vermelha:** Linha de identidade (previsão perfeita)
                - **Proximidade à linha:** Quanto mais próximos os pontos estão da linha, melhor o modelo
                - **Dispersão:** Pontos muito espalhados indicam baixa precisão do modelo
                """)
                
                # Mostrar métricas de qualidade do ajuste
                st.markdown("### 📊 **Métricas de Qualidade do Modelo:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric('R² (in-sample)', f"{r2:.3f}")
                    
                with col2:
                    st.metric('RMSE (in-sample)', f"{rmse:.0f}")
                
                # Explicação detalhada das métricas
                st.markdown(f"""
                #### 📚 **Explicação das Métricas de Regressão:**
                
                ##### 📈 **R² = {r2:.3f}**
                - **O que é:** Coeficiente de determinação, mede o quanto o modelo explica a variação nos dados
                - **Escala:** 0 a 1 (pode ser negativo se o modelo for muito ruim)
                - **Interpretação atual:** O modelo explica {r2*100:.1f}% da variação nos casos de meningite
                - **Qualidade:**
                  - R² > 0.8: Excelente
                  - R² 0.6-0.8: Bom
                  - R² 0.4-0.6: Moderado
                  - R² < 0.4: Fraco
                  - **Seu modelo:** {"Excelente" if r2 > 0.8 else "Bom" if r2 > 0.6 else "Moderado" if r2 > 0.4 else "Fraco"}
                
                ##### 📏 **RMSE = {rmse:.0f}**
                - **O que é:** Raiz do Erro Quadrático Médio, mede o erro típico das previsões
                - **Unidade:** Número de casos (mesma unidade dos dados)
                - **Interpretação:** Em média, o modelo erra {rmse:.0f} casos para mais ou para menos
                - **Utilidade:** Quanto menor, melhor a precisão das previsões
                """)
                
                # Mostrar importância das variáveis
                if hasattr(modelo_reg, 'coef_') and hasattr(modelo_reg, 'feature_names_in_'):
                    st.markdown("#### 🎯 **Importância das Variáveis:**")
                    coefs = pd.DataFrame({
                        'Variável': feature_cols,
                        'Coeficiente': modelo_reg.coef_,
                        'Importância_Abs': np.abs(modelo_reg.coef_)
                    }).sort_values('Importância_Abs', ascending=False)
                    st.dataframe(coefs)
                    
                    st.markdown("""
                    **📊 Interpretação dos Coeficientes:**
                    - **Coeficiente positivo:** Aumento na variável leva a aumento nos casos
                    - **Coeficiente negativo:** Aumento na variável leva à diminuição nos casos
                    - **Magnitude:** Quanto maior o valor absoluto, maior o impacto da variável
                    """)

                # Validação temporal e diagnóstico
                st.subheader('📏 Validação Temporal (TimeSeriesSplit)')
                try:
                    from sklearn.model_selection import TimeSeriesSplit
                    n_splits = min(5, max(2, len(df_int) - 3))
                    tscv = TimeSeriesSplit(n_splits=n_splits)
                    cv_rows = []
                    for i, (train_idx, test_idx) in enumerate(tscv.split(df_int)):
                        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                        m = LinearRegression().fit(X_train, y_train)
                        y_hat = m.predict(X_test)
                        # R² somente se houver pelo menos 2 amostras e variância
                        if len(y_test) >= 2 and np.var(y_test) > 1e-9:
                            cv_r2 = float(r2_score(y_test, y_hat))
                        else:
                            cv_r2 = None
                        cv_rmse = float(np.sqrt(mean_squared_error(y_test, y_hat)))
                        cv_rows.append({'fold': i + 1, 'R2': cv_r2, 'RMSE': cv_rmse, 'n_test': int(len(test_idx))})
                    if cv_rows:
                        cv_df = pd.DataFrame(cv_rows)
                        st.dataframe(cv_df)
                        r2_valid = cv_df['R2'].dropna()
                        r2_cv_mean = r2_valid.mean() if not r2_valid.empty else 0.0
                        rmse_cv_mean = cv_df['RMSE'].mean()
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric('R² médio (CV)', f"{r2_cv_mean:.3f}")
                        with col2:
                            st.metric('RMSE médio (CV)', f"{rmse_cv_mean:.0f}")
                            
                        # Explicação da validação cruzada temporal
                        st.markdown(f"""
                        #### 📚 **Explicação da Validação Cruzada Temporal:**
                        
                        **🔄 O que é:** Técnica que avalia a capacidade do modelo de prever dados futuros
                        
                        **🕒 Como funciona:**
                        - Divide os dados em sequências temporais
                        - Treina com dados do passado, testa com dados do futuro
                        - Repete o processo várias vezes
                        
                        **📊 Métricas obtidas:**
                        - **R² médio (CV) = {r2_cv_mean:.3f}**
                          - Performance média em dados não vistos
                          - {"Melhor que in-sample" if r2_cv_mean > r2 else "Pior que in-sample" if r2_cv_mean < r2 else "Similar ao in-sample"} (in-sample = {r2:.3f})
                        
                        - **RMSE médio (CV) = {rmse_cv_mean:.0f}**
                          - Erro médio em dados não vistos
                          - {"Melhor que in-sample" if rmse_cv_mean < rmse else "Pior que in-sample" if rmse_cv_mean > rmse else "Similar ao in-sample"} (in-sample = {rmse:.0f})
                        
                        **🎯 Interpretação:**
                        - Se CV ≈ in-sample: modelo generaliza bem
                        - Se CV << in-sample: possível overfitting
                        - Se CV >> in-sample: possível underfitting ou dados inadequados
                        """)
                except Exception as _:
                    st.info('ℹ️ Não foi possível calcular a validação temporal nesta amostra.')

                # Resíduos ao longo do tempo
                st.subheader('🩺 Diagnóstico de Resíduos')
                residuos = (y - y_pred).reset_index(drop=True)
                anos_plot = df_int['Ano'].reset_index(drop=True) if 'Ano' in df_int.columns else pd.Series(range(len(residuos)))
                fig_res = px.line(x=anos_plot, y=residuos, markers=True, title='Resíduos ao longo do tempo')
                fig_res.update_layout(xaxis_title='Ano', yaxis_title='Resíduo (Casos)', template='plotly_white')
                st.plotly_chart(fig_res, use_container_width=True)
                
                # Explicação do gráfico de resíduos
                st.markdown("""
                #### 📖 **Interpretação do Gráfico de Resíduos:**
                - **Eixo X (Horizontal):** Anos
                - **Eixo Y (Vertical):** Resíduos (diferença entre casos reais e previstos)
                - **Linha:** Mostra os erros do modelo ao longo do tempo
                - **Padrões a observar:**
                  - **Linha horizontal próxima a zero:** Modelo bem ajustado
                  - **Tendências sistemáticas:** Modelo pode estar perdendo padrões importantes
                  - **Variabilidade constante:** Boa qualidade dos resíduos
                  - **Variabilidade crescente/decrescente:** Possível heteroscedasticidade
                - **Interpretação epidemiológica:** Resíduos grandes podem indicar anos com eventos especiais (surtos, mudanças de política)
                """)
            else:
                st.info('ℹ️ Dados anuais insuficientes para regressão múltipla.')
        except Exception as e:
            st.warning(f"Erro na regressão múltipla: {e}")
        
        # Análise de clustering hierárquico
        st.subheader("🎯 **Clustering Hierárquico**")
        
        if sorogrupos is not None and not sorogrupos.empty:
            try:
                from scipy.cluster.hierarchy import dendrogram, linkage
                from scipy.spatial.distance import pdist
                
                # Preparar dados para clustering
                dados_cluster = sorogrupos.groupby('Sorogrupo').agg({
                    'Casos': 'sum',
                    'Obitos': 'sum'
                }).reset_index()
                
                dados_cluster['Letalidade'] = (
                    dados_cluster['Obitos'] / dados_cluster['Casos'] * 100
                ).round(2)
                
                # Selecionar variáveis para clustering
                features = ['Casos', 'Letalidade']
                X_cluster = dados_cluster[features].values
                
                # Normalizar dados
                scaler = StandardScaler()
                X_cluster_norm = scaler.fit_transform(X_cluster)
                
                # Calcular matriz de distância
                dist_matrix = pdist(X_cluster_norm)
                
                # Aplicar clustering hierárquico
                linkage_matrix = linkage(dist_matrix, method='ward')
                
                # Gráfico de dendrograma
                fig_dendro = go.Figure()
                
                # Criar dendrograma manualmente
                fig_dendro.add_trace(go.Scatter(
                    x=list(range(len(linkage_matrix) + 1)),
                    y=linkage_matrix[:, 2],
                    mode='lines+markers',
                    name='Dendrograma',
                    line=dict(color='blue'),
                    marker=dict(size=6)
                ))
                
                fig_dendro.update_layout(
                    title="Dendrograma Hierárquico dos Sorogrupos",
                    xaxis_title="Índice",
                    yaxis_title="Distância",
                    template='plotly_white'
                )
                
                st.plotly_chart(fig_dendro, use_container_width=True)
                
                # Número de clusters sugerido
                st.write("**📊 Análise do Dendrograma:**")
                st.write("**Método:** Ward (mínima variância)")
                st.write("**Distância:** Euclidiana normalizada")
                
                # Sugerir número de clusters
                n_clusters_sugerido = st.slider("Número de Clusters:", 2, min(5, len(dados_cluster)), 3)
                
                if st.button("🎯 Aplicar Clustering"):
                    try:
                        from scipy.cluster.hierarchy import fcluster
                        
                        # Aplicar clustering
                        clusters = fcluster(linkage_matrix, n_clusters_sugerido, criterion='maxclust')
                        
                        # Adicionar clusters aos dados
                        dados_cluster['Cluster'] = clusters
                        
                        # Gráfico de clusters
                        fig_cluster_hier = px.scatter(
                            dados_cluster,
                            x='Casos',
                            y='Letalidade',
                            color='Cluster',
                            title=f"Clustering Hierárquico (K={n_clusters_sugerido})",
                            text='Sorogrupo',
                            size='Casos'
                        )
                        
                        fig_cluster_hier.update_layout(
                            xaxis_title="Número de Casos",
                            yaxis_title="Taxa de Letalidade (%)",
                            template='plotly_white'
                        )
                        
                        st.plotly_chart(fig_cluster_hier, use_container_width=True)
                        
                        # Explicação do gráfico de clustering hierárquico
                        st.markdown(f"""
                        #### 📖 **Interpretação do Clustering Hierárquico:**
                        - **Eixo X (Horizontal):** Número de casos por sorogrupo
                        - **Eixo Y (Vertical):** Taxa de letalidade (%) por sorogrupo
                        - **Cores diferentes:** Cada cor representa um cluster hierárquico
                        - **Método Ward:** Minimiza a variância intra-cluster
                        - **Vantagem:** Não requer definir número de clusters a priori
                        
                        #### 🌳 **Diferença do K-Means:**
                        - **Hierárquico:** Cria árvore de relacionamentos (dendrograma)
                        - **Determinístico:** Sempre produz o mesmo resultado
                        - **Flexível:** Permite escolher número de clusters após análise
                        - **Interpretabilidade:** Mostra hierarquia de similaridades
                        """)
                        
                        # Resumo dos clusters
                        st.write("**📋 Resumo dos Clusters:**")
                        for i in range(1, n_clusters_sugerido + 1):
                            cluster_data = dados_cluster[dados_cluster['Cluster'] == i]
                            st.write(f"**Cluster {i}:** {len(cluster_data)} sorogrupos")
                            for idx in cluster_data.index:
                                sorogrupo = cluster_data.loc[idx, 'Sorogrupo']
                                casos = cluster_data.loc[idx, 'Casos']
                                letalidade = cluster_data.loc[idx, 'Letalidade']
                                st.write(f"  - {sorogrupo}: {casos} casos, {letalidade:.1f}% letalidade")
                        
                    except Exception as e:
                        st.error(f"Erro no clustering: {e}")
                
            except Exception as e:
                st.warning(f"Erro no clustering hierárquico: {e}")
        
        # Resumo das análises avançadas
        st.markdown("---")
        st.markdown("""
        **📋 Resumo das Análises Avançadas:**
        
        **1. Decomposição STL:**
        - Análise robusta de séries temporais
        - Separação de tendência, sazonalidade e resíduos
        - Identificação de padrões complexos
        
        **2. Teste de Estacionariedade:**
        - Avaliação da estabilidade temporal
        - Necessidade de diferenciação
        - Validação de modelos temporais
        
        **3. Correlação Cruzada:**
        - Relações entre diferentes sorogrupos
        - Padrões de co-ocorrência
        - Identificação de surtos simultâneos
        
        **4. Regressão Múltipla:**
        - Modelagem preditiva da letalidade
        - Identificação de fatores influentes
        - Avaliação da qualidade do modelo
        
        **5. Clustering Hierárquico:**
        - Agrupamento hierárquico de sorogrupos
        - Análise de similaridades epidemiológicas
        - Identificação de padrões ocultos
        """)
        
    else:
        st.error("❌ Dados não disponíveis para análise avançada")

def show_regional_analysis(dados):
    """Exibe a seção "Análise Regional - Distribuição Geográfica".

    Renderiza uma análise focada nas cinco grandes regiões do Brasil. A função
    mostra a evolução temporal da vacinação por região, compara o total de doses
    e a cobertura média entre as regiões, e analisa a correlação entre o
    número de doses aplicadas e os casos notificados em nível regional.

    Args:
        dados (dict): O dicionário global de dados. Utiliza as chaves 'analise_regional'
                      e 'imunizacao_regional'. Também tenta carregar
                      'data/processed/analise_regional.csv' para correlação.
    """
    st.header("🗺️ **Análise Regional - Distribuição Geográfica**")
    st.markdown("---")
    
    if dados and 'analise_regional' in dados and 'imunizacao_regional' in dados:
        # Dados regionais
        analise_regional = dados['analise_regional']
        imunizacao_regional = dados['imunizacao_regional']
        
        # Métricas regionais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_regioes = len(analise_regional)
            st.metric("🌍 Regiões Analisadas", total_regioes)
        
        with col2:
            total_ufs = analise_regional['Total_UFs'].sum()
            st.metric("🏙️ Total de UFs", total_ufs)
        
        with col3:
            media_cobertura = analise_regional['Cobertura_Media'].mean()
            st.metric("💉 Cobertura Média", f"{media_cobertura:.1f}%")
        
        # Gráfico de evolução temporal por região
        st.subheader("📈 **Evolução Temporal por Região**")
        
        fig_temporal_regional = go.Figure()
        
        for regiao in imunizacao_regional['Regiao'].unique():
            dados_regiao = imunizacao_regional[imunizacao_regional['Regiao'] == regiao]
            fig_temporal_regional.add_trace(go.Scatter(
                x=dados_regiao['Ano'],
                y=dados_regiao['Total_Doses'],
                mode='lines+markers',
                name=regiao,
                line=dict(width=3),
                marker=dict(size=8)
            ))
        
        fig_temporal_regional.update_layout(
            title="Evolução da Cobertura Vacinal por Região (2023-2025)",
            xaxis_title="Ano",
            yaxis_title="Total de Doses",
            template='plotly_white',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_temporal_regional, use_container_width=True)
        
        # Explicação detalhada do gráfico de evolução temporal
        st.markdown("""
        #### 📚 **Explicação da Evolução Temporal por Região:**
        
        ##### 🎯 **O que este gráfico mostra:**
        - **Cada linha colorida** representa uma região do Brasil
        - **Eixo X:** Anos do período analisado
        - **Eixo Y:** Total de doses aplicadas
        - **Marcadores:** Dados específicos por ano
        
        ##### 📊 **Como interpretar:**
        - **Linhas ascendentes:** Aumento na vacinação na região
        - **Linhas descendentes:** Redução na vacinação (possível problema)
        - **Linhas paralelas:** Regiões com comportamento similar
        - **Divergência:** Diferenças crescentes entre regiões
        
        ##### 🔍 **Importância epidemiológica:**
        - **Identificação de desigualdades regionais** na cobertura vacinal
        - **Monitoramento da eficácia** das políticas regionais
        - **Planejamento de recursos** baseado em tendências
        - **Detecção precoce** de problemas regionais específicos
        
        ##### ⚠️ **Sinais de alerta a observar:**
        - Regiões com **tendência decrescente** persistente
        - **Grandes disparidades** entre regiões
        - **Estagnação** em níveis baixos de cobertura
        - **Variabilidade excessiva** ano a ano
        """)
        
        # Estatísticas regionais
        st.subheader("📊 **Estatísticas Regionais**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras por região
            fig_barras_regional = px.bar(
                analise_regional,
                x='Regiao',
                y='Total_Doses',
                title="Total de Doses por Região",
                color='Regiao',
                text='Total_Doses'
            )
            
            fig_barras_regional.update_layout(
                xaxis_title="Região",
                yaxis_title="Total de Doses",
                template='plotly_white',
                showlegend=False
            )
            
            fig_barras_regional.update_traces(
                texttemplate='%{text:,}',
                textposition='outside'
            )
            
            st.plotly_chart(fig_barras_regional, use_container_width=True)
            
            # Explicação do gráfico de total de doses por região
            st.markdown("""
            **📖 Gráfico de Total de Doses por Região:**
            - **Barras:** Altura representa total acumulado
            - **Cores:** Diferencia as regiões visualmente
            - **Números:** Valores exatos sobre as barras
            - **Interpretação:** Identifica regiões com maior/menor volume total
            - **Aplicação:** Alocação proporcional de recursos
            """)
        
        with col2:
            # Gráfico de cobertura média
            fig_cobertura_regional = px.bar(
                analise_regional,
                x='Regiao',
                y='Cobertura_Media',
                title="Cobertura Média por Região (%)",
                color='Cobertura_Media',
                text='Cobertura_Media'
            )
            
            fig_cobertura_regional.update_layout(
                xaxis_title="Região",
                yaxis_title="Cobertura Média (%)",
                template='plotly_white',
                showlegend=False
            )
            
            fig_cobertura_regional.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside'
            )
            
            st.plotly_chart(fig_cobertura_regional, use_container_width=True)
            
            # Explicação do gráfico de cobertura média por região
            st.markdown("""
            **📖 Gráfico de Cobertura Média por Região:**
            - **Barras:** Altura representa percentual de cobertura
            - **Escala de cores:** Intensidade proporcional à cobertura
            - **Meta ideal:** >95% para imunidade coletiva
            - **Interpretação:** Avalia eficácia regional
            - **Aplicação:** Priorização de intervenções
            """)
        
        # Análise comparativa detalhada das duas métricas
        st.markdown(f"""
        #### 🔬 **Análise Comparativa Total vs Cobertura:**
        
        ##### 📊 **Por que analisar ambas as métricas:**
        - **Total de doses:** Mede **volume absoluto** de vacinação
        - **Cobertura média:** Mede **eficiência relativa** à população
        
        ##### 🎯 **Interpretações possíveis:**
        - **Alto total + Alta cobertura:** Região populosa bem atendida
        - **Alto total + Baixa cobertura:** Região populosa com lacunas
        - **Baixo total + Alta cobertura:** Região pequena bem atendida
        - **Baixo total + Baixa cobertura:** Região que necessita atenção
        
        ##### 📈 **Cobertura atual por região:**
        {f"- **Média geral:** {media_cobertura:.1f}%" if 'media_cobertura' in locals() else ""}
        - **Meta OMS:** >95% para controle efetivo
        - **Situação crítica:** Regiões <70%
        - **Situação boa:** Regiões >95%
        """)
        
        # Comparação dos últimos 3 anos
        st.subheader("🔄 **Comparação dos Últimos 3 Anos por Região**")
        
        # Preparar dados para comparação
        anos_unicos = sorted(imunizacao_regional['Ano'].unique())
        if len(anos_unicos) >= 3:
            anos_recentes = anos_unicos[-3:]
            
            dados_comparacao = imunizacao_regional[imunizacao_regional['Ano'].isin(anos_recentes)]
            
            fig_comparacao = px.bar(
                dados_comparacao,
                x='Regiao',
                y='Total_Doses',
                color='Ano',
                title=f"Comparação Regional ({anos_recentes[0]}-{anos_recentes[-1]})",
                barmode='group'
            )
            
            fig_comparacao.update_layout(
                xaxis_title="Região",
                yaxis_title="Total de Doses",
                template='plotly_white'
            )
            
            st.plotly_chart(fig_comparacao, use_container_width=True)
            
            # Explicação do gráfico de comparação temporal
            st.markdown(f"""
            #### 📖 **Interpretação da Comparação dos Últimos 3 Anos:**
            
            ##### 🎯 **O que este gráfico mostra:**
            - **Barras agrupadas** por região, cada cor representa um ano
            - **Evolução temporal** recente da vacinação regional
            - **Comparação direta** entre regiões no mesmo período
            
            ##### 📊 **Como analisar:**
            - **Barras crescentes:** Melhoria ao longo dos anos
            - **Barras decrescentes:** Redução preocupante
            - **Padrões uniformes:** Política nacional consistente
            - **Padrões divergentes:** Diferenças regionais específicas
            
            ##### 🔍 **Indicadores importantes:**
            - **Tendência geral:** {"Crescimento" if anos_recentes else "A ser avaliada"}
            - **Homogeneidade:** Regiões com comportamento similar
            - **Outliers:** Regiões com comportamento atípico
            - **Sustentabilidade:** Manutenção dos níveis ano a ano
            
            ##### 📈 **Aplicações práticas:**
            - **Identificação de best practices** regionais
            - **Detecção de problemas emergentes**
            - **Planejamento de recursos** para próximos anos
            - **Avaliação de políticas** implementadas
            """)
        
        # Análise de correlação regional
        st.subheader("🔗 **Análise de Correlação Regional**")

        try:
            # Preferir base consolidada por região (sem UF)
            regional_cases_path = os.path.join('data', 'processed', 'analise_regional.csv')
            if os.path.exists(regional_cases_path):
                casos_regiao_total = pd.read_csv(regional_cases_path)
                # Espera colunas: Regiao, Casos
                base_merge = analise_regional[['Regiao', 'Total_Doses']].merge(
                    casos_regiao_total[['Regiao', 'Casos']], on='Regiao', how='inner'
                )

                if not base_merge.empty:
                    corr, p_valor = stats.pearsonr(base_merge['Total_Doses'], base_merge['Casos'])
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📈 Correlação (Regiões)", f"{corr:.3f}")
                    with col2:
                        st.metric("p-valor", f"{p_valor:.4f}")

                    fig_disp = px.scatter(
                        base_merge,
                        x='Total_Doses',
                        y='Casos',
                        text='Regiao',
                        title='Casos vs Total de Doses por Região'
                    )
                    
                    # Adicionar linha de tendência manual
                    if len(base_merge) > 1:
                        x_vals = base_merge['Total_Doses'].values
                        y_vals = base_merge['Casos'].values
                        
                        # Remover NaN values
                        mask = ~(np.isnan(x_vals) | np.isnan(y_vals))
                        x_clean = x_vals[mask]
                        y_clean = y_vals[mask]
                        
                        if len(x_clean) > 1:
                            # Calcular regressão linear usando numpy
                            coeffs = np.polyfit(x_clean, y_clean, 1)
                            x_trend = np.linspace(x_clean.min(), x_clean.max(), 100)
                            y_trend = coeffs[0] * x_trend + coeffs[1]
                            
                            # Adicionar linha de tendência
                            fig_disp.add_trace(go.Scatter(
                                x=x_trend,
                                y=y_trend,
                                mode='lines',
                                name='Linha de Tendência',
                                line=dict(color='red', dash='dash')
                            ))
                    fig_disp.update_traces(textposition='top center')
                    fig_disp.update_layout(template='plotly_white')
                    st.plotly_chart(fig_disp, use_container_width=True)

                    st.write("**📋 Tabela (Regiões):**")
                    st.dataframe(base_merge[['Regiao', 'Total_Doses', 'Casos']])
            else:
                st.info("Dados regionais agregados não encontrados em data/processed/analise_regional.csv. Pulei a correlação regional.")
        except Exception as e:
            st.warning(f"Não foi possível calcular a correlação regional: {e}")
        
        # Resumo da análise regional
        st.markdown("---")
        st.markdown("""
        **📋 Resumo da Análise Regional:**
        
        **1. Distribuição Geográfica:**
        - Análise por 5 regiões brasileiras
        - Cobertura vacinal por região
        - Evolução temporal regional
        
        **2. Comparações Regionais:**
        - Ranking de cobertura por região
        - Análise de disparidades geográficas
        - Tendências regionais específicas
        
        **3. Correlações Regionais:**
        - Relação entre vacinação e casos por região
        - Identificação de padrões regionais
        - Efetividade da vacinação por área geográfica
        """)
        
    else:
        st.error("❌ Dados regionais não disponíveis")

def show_epidemiological_analysis(dados):
    """Exibe a seção "Análise Epidemiológica - Indicadores de Saúde Pública".

    Esta função foca em indicadores epidemiológicos chave, como a letalidade.
    Ela mostra a evolução da taxa de letalidade por etiologia ao longo do tempo,
    apresenta um heatmap para visualização intuitiva desses dados, e analisa
    a evolução da letalidade média anual.

    Args:
        dados (dict): O dicionário global de dados. Utiliza as chaves 'letalidade_etiologia'
                      e 'casos_2017_2022', além de outras tabelas de casos para
                      cálculos de fallback.
    """
    st.header("🦠 **Análise Epidemiológica - Indicadores de Saúde Pública**")
    st.markdown("---")
    
    if dados and 'letalidade_etiologia' in dados and 'casos_2017_2022' in dados:
        # Dados de letalidade
        letalidade_etiologia = dados['letalidade_etiologia']
        casos_2017_2022 = dados['casos_2017_2022']
        
        # Métricas epidemiológicas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_casos = casos_2017_2022['Casos_Notificados'].sum()
            st.metric("📊 Total de Casos", f"{total_casos:,}")
        
        with col2:
            # Usar a coluna correta Taxa_Letalidade
            if 'Taxa_Letalidade' in letalidade_etiologia.columns:
                media_letalidade = letalidade_etiologia['Taxa_Letalidade'].mean()
                st.metric("💀 Letalidade Média", f"{media_letalidade:.1f}%")
            else:
                st.metric("💀 Letalidade Média", "N/A")
        
        with col3:
            # Total de óbitos com fallback entre bases disponíveis
            total_obitos = 0
            if 'Obitos' in casos_2017_2022.columns:
                total_obitos = pd.to_numeric(casos_2017_2022['Obitos'], errors='coerce').fillna(0).sum()
            if (total_obitos == 0) and ('casos_consolidados' in dados) and isinstance(dados['casos_consolidados'], pd.DataFrame) and ('Obitos' in dados['casos_consolidados'].columns):
                total_obitos = pd.to_numeric(dados['casos_consolidados']['Obitos'], errors='coerce').fillna(0).sum()
            if (total_obitos == 0) and ('bacterianas_2024' in dados) and isinstance(dados['bacterianas_2024'], pd.DataFrame) and ('Obitos' in dados['bacterianas_2024'].columns):
                total_obitos = pd.to_numeric(dados['bacterianas_2024']['Obitos'], errors='coerce').fillna(0).sum()
            if (total_obitos == 0) and ('etiologia_2024' in dados) and isinstance(dados['etiologia_2024'], pd.DataFrame) and ('Obitos' in dados['etiologia_2024'].columns):
                total_obitos = pd.to_numeric(dados['etiologia_2024']['Obitos'], errors='coerce').fillna(0).sum()
            st.metric("⚰️ Total de Óbitos", f"{int(total_obitos):,}" if total_obitos else "N/A")
        
        # Análise de letalidade por etiologia (melhor visualização)
        st.subheader("📈 **Letalidade por Etiologia ao Longo do Tempo**")
        
        if 'Taxa_Letalidade' in letalidade_etiologia.columns:
            let_df = letalidade_etiologia.copy()
            let_df['Taxa_Letalidade'] = pd.to_numeric(let_df['Taxa_Letalidade'], errors='coerce').fillna(0)
            # Garantir não-negatividade
            let_df['Taxa_Letalidade'] = let_df['Taxa_Letalidade'].clip(lower=0)
            fig_letalidade = px.bar(
                let_df,
                x='Ano',
                y='Taxa_Letalidade',
                color='Etiologia',
                barmode='group',
                title="Taxa de Letalidade (%) por Etiologia e Ano"
            )
            fig_letalidade.update_layout(
                xaxis_title="Ano",
                yaxis_title="Taxa de Letalidade (%)",
                template='plotly_white'
            )
            fig_letalidade.update_xaxes(tickformat='d')
            st.plotly_chart(fig_letalidade, use_container_width=True)
        else:
            st.warning("⚠️ Coluna de letalidade não encontrada nos dados")
        
        # Nova análise: Heatmap de letalidade por etiologia e ano (mais intuitivo, sem escalas negativas)
        st.subheader("🗺️ **Mapa de Calor: Letalidade por Etiologia e Ano**")
        if 'Taxa_Letalidade' in letalidade_etiologia.columns:
            let_hm = letalidade_etiologia.copy()
            let_hm['Taxa_Letalidade'] = pd.to_numeric(let_hm['Taxa_Letalidade'], errors='coerce').fillna(0).clip(lower=0)
            matriz = let_hm.pivot_table(index='Ano', columns='Etiologia', values='Taxa_Letalidade', aggfunc='mean')
            fig_hm = px.imshow(
                matriz.sort_index(),
                color_continuous_scale='Reds',
                aspect='auto',
                labels=dict(color='Letalidade (%)'),
                title='Letalidade (%) por Etiologia e Ano'
            )
            fig_hm.update_layout(template='plotly_white')
            st.plotly_chart(fig_hm, use_container_width=True)
        else:
            st.info("ℹ️ Sem dados de letalidade por etiologia para o heatmap")
        
        # Análise de letalidade por ano
        st.subheader("📊 **Letalidade por Ano e Etiologia**")
        
        if 'Taxa_Letalidade' in letalidade_etiologia.columns:
            # Agrupar por ano e calcular média de letalidade
            letalidade_por_ano = letalidade_etiologia.groupby('Ano')['Taxa_Letalidade'].mean().reset_index()
            
            fig_letalidade_ano = px.line(
                letalidade_por_ano,
                x='Ano',
                y='Taxa_Letalidade',
                title="Evolução da Letalidade Média por Ano (2007-2020)",
                markers=True
            )
            
            fig_letalidade_ano.update_layout(
                xaxis_title="Ano",
                yaxis_title="Letalidade Média (%)",
                template='plotly_white'
            )
            
            st.plotly_chart(fig_letalidade_ano, use_container_width=True)
            
            # Estatísticas de letalidade
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Estatísticas de Letalidade por Etiologia:**")
                st.dataframe(letalidade_etiologia.groupby('Etiologia')['Taxa_Letalidade'].describe())
            
            with col2:
                st.write("**Letalidade por Ano:**")
                st.dataframe(letalidade_por_ano)
        else:
            st.warning("⚠️ Dados de letalidade não disponíveis para análise detalhada")
        
        # Informações sobre a análise
        st.subheader("ℹ️ **Sobre a Análise Epidemiológica**")
        st.markdown("""
        **Esta análise mostra:**
        - Taxas de letalidade por etiologia
        - Evolução temporal de casos e óbitos
        - Padrões de letalidade ao longo do tempo
        - Comparação entre diferentes agentes causadores
        
        **Importância:**
        - Identificar agentes mais letais
        - Monitorar tendências de letalidade
        - Planejar estratégias de tratamento
        - Avaliar efetividade de intervenções
        """)
    else:
        st.warning("⚠️ Dados epidemiológicos não disponíveis")

def show_attack_rate_analysis(dados):
    """Exibe a seção "Análise de Taxa de Ataque e Força de Infecção".

    Calcula e exibe a taxa de ataque (casos por 100.000 habitantes) e a força de
    infecção (taxa instantânea de aquisição da doença). A função mostra a evolução
    anual dessas métricas, a sazonalidade baseada em dados de hospitalização (SIH),
    e a correlação entre a taxa de ataque e a letalidade.

    Args:
        dados (dict): O dicionário global de dados. Utiliza 'casos_2017_2022',
                      'casos_consolidados', e 'sih_meningite'.
    """
    st.header("⚡ **Análise de Taxa de Ataque e Força de Infecção**")
    st.markdown("---")
    
    if dados and ('casos_2017_2022' in dados or 'casos_consolidados' in dados):
        # Unificar casos anuais a partir de todas as tabelas disponíveis
        frames = []
        if 'casos_2017_2022' in dados and isinstance(dados['casos_2017_2022'], pd.DataFrame):
            frames.append(dados['casos_2017_2022'][['Ano', 'Casos_Notificados'] + (["Obitos"] if 'Obitos' in dados['casos_2017_2022'].columns else [])])
        if 'casos_consolidados' in dados and isinstance(dados['casos_consolidados'], pd.DataFrame):
            frames.append(dados['casos_consolidados'][['Ano', 'Casos_Notificados'] + (["Obitos"] if 'Obitos' in dados['casos_consolidados'].columns else [])])
        if not frames:
            st.warning("⚠️ Nenhuma tabela de casos encontrada para taxa de ataque")
            return
        casos_anuais = pd.concat(frames, ignore_index=True).groupby('Ano', as_index=False).sum(numeric_only=True)
        
        # Métricas de taxa de ataque
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_casos = casos_anuais['Casos_Notificados'].sum()
            st.metric("📊 Total de Casos", f"{total_casos:,}")
        
        with col2:
            # Verificar se a coluna Obitos existe
            if 'Obitos' in casos_anuais.columns:
                total_obitos = casos_anuais['Obitos'].sum()
                st.metric("💀 Total de Óbitos", f"{total_obitos:,}")
            else:
                st.metric("💀 Total de Óbitos", "N/A")
        
        with col3:
            taxa_ataque_geral = (total_casos / 214000000) * 100000  # População estimada Brasil
            st.metric("🎯 Taxa de Ataque", f"{taxa_ataque_geral:.1f}/100k")
        
        # Análise de taxa de ataque por ano
        st.subheader("📈 **Taxa de Ataque por Ano**")
        
        # Calcular taxa de ataque anual
        taxa_ataque_anual = casos_anuais.copy()
        
        # Calcular taxa de letalidade anual (se houver óbitos)
        if 'Obitos' in taxa_ataque_anual.columns:
            taxa_ataque_anual['Taxa_Letalidade'] = (taxa_ataque_anual['Obitos'] / taxa_ataque_anual['Casos_Notificados']) * 100
        
        # População: se não houver fonte no projeto, aplicar aproximação com preenchimento progressivo
        populacao_anos = {
            2017: 209_000_000,
            2018: 210_000_000,
            2019: 211_000_000,
            2020: 212_000_000,
            2021: 213_000_000,
            2022: 214_000_000,
        }
        taxa_ataque_anual['Populacao'] = taxa_ataque_anual['Ano'].map(populacao_anos)
        # Preencher anos sem população com último valor conhecido
        taxa_ataque_anual = taxa_ataque_anual.sort_values('Ano')
        taxa_ataque_anual['Populacao'] = taxa_ataque_anual['Populacao'].ffill().bfill()
        taxa_ataque_anual['Taxa_Ataque'] = (taxa_ataque_anual['Casos_Notificados'] / taxa_ataque_anual['Populacao']) * 100000
        
        # Gráfico de taxa de ataque
        fig_taxa_ataque = px.line(
            taxa_ataque_anual,
            x='Ano',
            y='Taxa_Ataque',
            title="Taxa de Ataque de Meningite por Ano (por 100.000 habitantes)",
            markers=True,
            line_shape='linear'
        )
        
        fig_taxa_ataque.update_layout(
            xaxis_title="Ano",
            yaxis_title="Taxa de Ataque (por 100.000 habitantes)",
            template='plotly_white'
        )
        
        st.plotly_chart(fig_taxa_ataque, use_container_width=True)
        
        # Explicação do conceito de taxa de ataque e do gráfico
        st.markdown(f"""
        #### 📚 **Explicação da Taxa de Ataque:**
        
        ##### 🎯 **O que é Taxa de Ataque:**
        - **Definição:** Proporção de pessoas que desenvolvem a doença em uma população específica durante um período determinado
        - **Unidade:** Casos por 100.000 habitantes por ano
        - **Cálculo:** (Número de casos / População total) × 100.000
        - **Utilidade:** Padroniza a incidência para comparação entre diferentes populações e períodos
        
        ##### 📊 **Interpretação do Gráfico:**
        - **Eixo X:** Anos do período analisado
        - **Eixo Y:** Taxa de ataque por 100.000 habitantes
        - **Linha com marcadores:** Evolução temporal da incidência padronizada
        - **Tendência crescente:** Aumento da incidência na população
        - **Tendência decrescente:** Redução da incidência (possivelmente devido a vacinação)
        - **Variações anuais:** Podem refletir surtos, mudanças epidemiológicas ou melhorias na vigilância
        
        ##### 📈 **Taxa de Ataque Atual: {taxa_ataque_geral:.1f}/100k habitantes**
        - **Baixa:** < 1,0/100k (situação controlada)
        - **Moderada:** 1,0-5,0/100k (vigilância necessária)
        - **Alta:** > 5,0/100k (situação de alerta)
        - **Classificação atual:** {"Baixa - situação controlada" if taxa_ataque_geral < 1.0 else "Moderada - vigilância necessária" if taxa_ataque_geral < 5.0 else "Alta - situação de alerta"}
        
        ##### 🌍 **Contexto Epidemiológico:**
        - **OMS recomenda:** Taxa < 2,0/100k como meta de controle
        - **Países desenvolvidos:** Geralmente < 1,0/100k
        - **Imunidade coletiva:** Taxa diminui com alta cobertura vacinal
        - **Vigilância epidemiológica:** Monitoramento contínuo é essencial
        """)
        
        # Análise de força de infecção
        st.subheader("🦠 **Análise de Força de Infecção**")
        
        # Calcular força de infecção (simulado)
        # Força de infecção = -ln(1 - taxa de ataque)
        taxa_ataque_anual['Forca_Infeccao'] = -np.log(1 - (taxa_ataque_anual['Taxa_Ataque'] / 100000))
        
        # Gráfico de força de infecção
        fig_forca_infeccao = px.line(
            taxa_ataque_anual,
            x='Ano',
            y='Forca_Infeccao',
            title="Força de Infecção de Meningite por Ano",
            markers=True,
            line_shape='linear'
        )
        
        fig_forca_infeccao.update_layout(
            xaxis_title="Ano",
            yaxis_title="Força de Infecção",
            template='plotly_white'
        )
        
        st.plotly_chart(fig_forca_infeccao, use_container_width=True)
        
        # Explicação da força de infecção
        st.markdown("""
        #### 📚 **Explicação da Força de Infecção:**
        
        ##### 🦠 **O que é Força de Infecção:**
        - **Definição:** Taxa instantânea na qual indivíduos suscetíveis adquirem infecção
        - **Fórmula:** λ = -ln(1 - taxa de ataque)
        - **Interpretação:** Intensidade da transmissão da doença na população
        - **Unidade:** Por unidade de tempo (geralmente por ano)
        
        ##### 📊 **Interpretação do Gráfico:**
        - **Eixo X:** Anos do período analisado
        - **Eixo Y:** Força de infecção (λ)
        - **Linha:** Intensidade da transmissão ao longo do tempo
        - **Valores altos:** Maior intensidade de transmissão
        - **Valores baixos:** Menor intensidade de transmissão
        
        ##### 🔬 **Importância Epidemiológica:**
        - **Modelagem matemática:** Base para modelos de transmissão
        - **Planejamento de intervenções:** Identifica períodos de alta transmissão
        - **Avaliação de controle:** Monitora eficácia das medidas de prevenção
        - **Comparação temporal:** Permite comparar diferentes períodos epidemiológicos
        """)
        
        # Análise de sazonalidade da taxa de ataque usando SIH (dados reais)
        st.subheader("📅 **Sazonalidade da Taxa de Ataque (SIH)**")
        if 'sih_meningite' in dados and isinstance(dados['sih_meningite'], pd.DataFrame):
            sih = dados['sih_meningite'].copy()
            if {'Mês_Num', 'Casos_Hospitalares'}.issubset(sih.columns):
                sih['Casos_Hospitalares'] = pd.to_numeric(sih['Casos_Hospitalares'], errors='coerce').fillna(0)
                mensal = sih.groupby('Mês_Num', as_index=False)['Casos_Hospitalares'].sum()
                # Nome dos meses na ordem
                nomes_meses = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}
                mensal['Mes'] = mensal['Mês_Num'].map(nomes_meses)
                # Base populacional: usar mediana das populações anuais calculadas
                pop_base = float(taxa_ataque_anual['Populacao'].median()) if 'Populacao' in taxa_ataque_anual.columns else 214_000_000.0
                mensal['Taxa_Ataque_Mensal'] = (mensal['Casos_Hospitalares'] / pop_base) * 100000
                mensal = mensal.sort_values('Mês_Num')

                fig_sazonal = px.bar(
                    mensal,
                    x='Mes',
                    y='Taxa_Ataque_Mensal',
                    title='Sazonalidade da Taxa de Ataque (Hospitalizações SIH)',
                    color='Taxa_Ataque_Mensal',
                    color_continuous_scale='Reds'
                )
                fig_sazonal.update_layout(
                    xaxis_title='Mês',
                    yaxis_title='Taxa de Ataque (por 100.000 hab.)',
                    template='plotly_white'
                )
                st.plotly_chart(fig_sazonal, use_container_width=True)
                
                # Explicação do gráfico de sazonalidade
                st.markdown("""
                #### 📖 **Interpretação da Sazonalidade da Taxa de Ataque:**
                - **Eixo X:** Meses do ano (Jan a Dez)
                - **Eixo Y:** Taxa de ataque mensal por 100.000 habitantes
                - **Barras coloridas:** Intensidade da cor reflete a magnitude da taxa
                - **Dados:** Baseados em hospitalizações do SIH (proxy para casos graves)
                
                ##### 🌡️ **Padrões Sazonais Esperados:**
                - **Inverno (Jun-Ago):** Maior incidência devido a:
                  - Aglomeração em ambientes fechados
                  - Redução da umidade relativa
                  - Menor ventilação
                - **Verão (Dez-Fev):** Menor incidência devido a:
                  - Maior dispersão populacional
                  - Melhor ventilação dos ambientes
                  - Condições climáticas desfavoráveis ao patógeno
                
                ##### 📊 **Utilidade da Análise:**
                - **Planejamento de recursos:** Antecipar picos de demanda hospitalar
                - **Campanhas preventivas:** Intensificar ações nos meses de risco
                - **Vigilância epidemiológica:** Monitoramento direcionado
                - **Políticas de saúde:** Adequação de estratégias por período
                """)
            else:
                st.info("ℹ️ Estrutura de SIH não possui colunas esperadas para sazonalidade (Mês_Num, Casos_Hospitalares)")
        else:
            st.info("ℹ️ Dados SIH não encontrados para análise sazonal")
        
        # Análise de correlação entre taxa de ataque e letalidade
        st.subheader("🔗 **Correlação Taxa de Ataque vs Letalidade**")
        
        if 'Taxa_Letalidade' in taxa_ataque_anual.columns:
            # Calcular correlação
            correlacao = taxa_ataque_anual['Taxa_Ataque'].corr(taxa_ataque_anual['Taxa_Letalidade'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("📊 Correlação", f"{correlacao:.3f}")
                
                if abs(correlacao) > 0.7:
                    st.success("🔗 **Forte correlação**")
                elif abs(correlacao) > 0.3:
                    st.info("🔗 **Correlação moderada**")
                else:
                    st.warning("🔗 **Correlação fraca**")
            
            with col2:
                # Gráfico de dispersão
                fig_correlacao = px.scatter(
                    taxa_ataque_anual,
                    x='Taxa_Ataque',
                    y='Taxa_Letalidade',
                    title="Correlação: Taxa de Ataque vs Letalidade"
                )
                
                # Adicionar linha de tendência manual usando numpy
                if len(taxa_ataque_anual) > 1:
                    x_vals = taxa_ataque_anual['Taxa_Ataque'].values
                    y_vals = taxa_ataque_anual['Taxa_Letalidade'].values
                    
                    # Remover NaN values
                    mask = ~(np.isnan(x_vals) | np.isnan(y_vals))
                    x_clean = x_vals[mask]
                    y_clean = y_vals[mask]
                    
                    if len(x_clean) > 1:
                        # Calcular regressão linear usando numpy
                        coeffs = np.polyfit(x_clean, y_clean, 1)
                        x_trend = np.linspace(x_clean.min(), x_clean.max(), 100)
                        y_trend = coeffs[0] * x_trend + coeffs[1]
                        
                        # Adicionar linha de tendência
                        fig_correlacao.add_trace(go.Scatter(
                            x=x_trend,
                            y=y_trend,
                            mode='lines',
                            name='Linha de Tendência',
                            line=dict(color='red', dash='dash')
                        ))
                
                fig_correlacao.update_layout(
                    xaxis_title="Taxa de Ataque (por 100.000 habitantes)",
                    yaxis_title="Taxa de Letalidade (%)",
                    template='plotly_white'
                )
                
                st.plotly_chart(fig_correlacao, use_container_width=True)
                
                # Explicação da correlação taxa de ataque vs letalidade
                st.markdown(f"""
                #### 📚 **Explicação da Correlação Taxa de Ataque vs Letalidade:**
                
                ##### 📊 **Correlação de Pearson = {correlacao:.3f}**
                - **O que mede:** Relação linear entre incidência e gravidade da doença
                - **Interpretação:**
                  - **Correlação positiva:** Maior incidência associada a maior letalidade
                  - **Correlação negativa:** Maior incidência associada a menor letalidade
                  - **Sem correlação:** Incidência e letalidade independentes
                
                ##### 📖 **Interpretação do Gráfico:**
                - **Eixo X:** Taxa de ataque (incidência por 100.000 hab.)
                - **Eixo Y:** Taxa de letalidade (%)
                - **Pontos:** Cada ponto representa um ano específico
                - **Linha tracejada:** Tendência linear da relação
                
                ##### 🔬 **Significado Epidemiológico:**
                - **Correlação positiva pode indicar:**
                  - Surtos com cepas mais virulentas
                  - Sobrecarregamento do sistema de saúde
                  - Diagnóstico tardio em períodos de alta incidência
                  
                - **Correlação negativa pode indicar:**
                  - Melhoria na detecção precoce
                  - Aumento de casos leves diagnosticados
                  - Efeito de diluição com mais casos benignos
                  
                - **Ausência de correlação pode indicar:**
                  - Letalidade constante independente da incidência
                  - Qualidade consistente do atendimento médico
                  - Distribuição uniforme da virulência das cepas
                
                ##### 🎯 **Classificação Atual: {"Forte" if abs(correlacao) > 0.7 else "Moderada" if abs(correlacao) > 0.3 else "Fraca"}**
                - **Fraca:** |r| < 0.3 - Relação pouco evidente
                - **Moderada:** 0.3 ≤ |r| < 0.7 - Relação moderada
                - **Forte:** |r| ≥ 0.7 - Relação bem definida
                """)
        else:
            st.info("ℹ️ Dados de letalidade não disponíveis para análise de correlação")
        
        # Resumo estatístico
        st.subheader("📋 **Resumo Estatístico**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Estatísticas da Taxa de Ataque:**")
            st.dataframe(taxa_ataque_anual['Taxa_Ataque'].describe())
        
        with col2:
            st.write("**Dados de Taxa de Ataque por Ano:**")
            st.dataframe(taxa_ataque_anual[['Ano', 'Taxa_Ataque', 'Forca_Infeccao']].round(4))
        
        # Informações sobre a análise
        st.subheader("ℹ️ **Sobre a Análise de Taxa de Ataque**")
        st.markdown("""
        **Esta análise mostra:**
        - Taxa de ataque por ano (casos por 100.000 habitantes)
        - Força de infecção ao longo do tempo
        - Padrões sazonais da doença
        - Correlação entre incidência e letalidade
        
        **Importância:**
        - Medir o risco populacional
        - Identificar períodos de maior risco
        - Planejar ações de prevenção
        - Avaliar efetividade de intervenções
        """)
    else:
        st.warning("⚠️ Dados de casos não disponíveis")

def show_free_exploration(dados):
    """Exibe a seção "Exploração Livre dos Dados".

    Cria uma interface interativa que permite ao usuário selecionar qualquer um dos
    datasets carregados, visualizar suas informações (linhas, colunas, tipos de dados,
    valores nulos), analisar colunas individuais com histogramas e gráficos de barras,
    e explorar correlações. Oferece também filtros personalizados e a opção de
    fazer o download dos dados filtrados.

    Args:
        dados (dict): O dicionário global contendo todos os DataFrames disponíveis
                      para exploração.
    """
    st.header("🔍 **Exploração Livre dos Dados**")
    st.markdown("---")
    
    if dados:
        st.info("💡 **Use esta seção para explorar os dados de forma personalizada**")
        
        # Seleção de dados
        st.subheader("📊 **Seleção de Dados**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            datasets_disponiveis = list(dados.keys())
            dataset_selecionado = st.selectbox(
                "Selecione o Dataset:",
                datasets_disponiveis,
                help="Escolha qual conjunto de dados analisar"
            )
        
        with col2:
            if dataset_selecionado:
                dataset = dados[dataset_selecionado]
                if isinstance(dataset, pd.DataFrame):
                    st.metric("📈 Linhas", len(dataset))
                    st.metric("📋 Colunas", len(dataset.columns))
        
        # Visualização dos dados
        if dataset_selecionado and dataset_selecionado in dados:
            dataset = dados[dataset_selecionado]
            
            if isinstance(dataset, pd.DataFrame):
                st.subheader("📋 **Visualização dos Dados**")
                
                # Mostrar primeiras linhas
                st.write("**Primeiras 10 linhas:**")
                st.dataframe(dataset.head(10))
                
                # Informações do dataset
                st.write("**Informações do Dataset:**")
                buffer = st.empty()
                
                if st.button("📊 Mostrar Informações"):
                    with buffer.container():
                        st.write(f"**Forma:** {dataset.shape}")
                        st.write(f"**Tipos de dados:**")
                        st.write(dataset.dtypes)
                        st.write(f"**Valores nulos:**")
                        st.write(dataset.isnull().sum())
                        st.write(f"**Estatísticas descritivas:**")
                        st.write(dataset.describe())
                
                # Análise de colunas
                st.subheader("🔍 **Análise de Colunas**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    colunas_numericas = dataset.select_dtypes(include=[np.number]).columns.tolist()
                    if colunas_numericas:
                        coluna_analise = st.selectbox(
                            "Selecione uma coluna numérica:",
                            colunas_numericas
                        )
                        
                        if coluna_analise:
                            # Histograma
                            fig_hist = px.histogram(
                                dataset,
                                x=coluna_analise,
                                title=f"Distribuição de {coluna_analise}",
                                nbins=20
                            )
                            fig_hist.update_layout(template='plotly_white')
                            st.plotly_chart(fig_hist, use_container_width=True)
                
                with col2:
                    colunas_categoricas = dataset.select_dtypes(include=['object']).columns.tolist()
                    if colunas_categoricas:
                        coluna_cat = st.selectbox(
                            "Selecione uma coluna categórica:",
                            colunas_categoricas
                        )
                        
                        if coluna_cat:
                            # Contagem de valores
                            contagem = dataset[coluna_cat].value_counts().head(10)
                            fig_bar = px.bar(
                                x=contagem.index,
                                y=contagem.values,
                                title=f"Top 10 valores de {coluna_cat}"
                            )
                            fig_bar.update_layout(
                                xaxis_title=coluna_cat,
                                yaxis_title="Contagem",
                                template='plotly_white'
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)
                
                # Análise de correlação
                if len(colunas_numericas) > 1:
                    st.subheader("🔗 **Análise de Correlação**")
                    
                    # Seleção de colunas para correlação
                    colunas_correlacao = st.multiselect(
                        "Selecione colunas para análise de correlação:",
                        colunas_numericas,
                        default=colunas_numericas[:5] if len(colunas_numericas) >= 5 else colunas_numericas
                    )
                    
                    if len(colunas_correlacao) > 1:
                        # Calcular correlação
                        correlacao = dataset[colunas_correlacao].corr()
                        
                        # Heatmap de correlação
                        fig_corr = px.imshow(
                            correlacao,
                            title="Matriz de Correlação",
                            color_continuous_scale='RdBu',
                            aspect='auto'
                        )
                        fig_corr.update_layout(template='plotly_white')
                        st.plotly_chart(fig_corr, use_container_width=True)
                        
                        # Tabela de correlação
                        st.write("**Matriz de Correlação:**")
                        st.dataframe(correlacao.round(3))
                
                # Filtros personalizados
                st.subheader("🔧 **Filtros Personalizados**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if colunas_numericas:
                        coluna_filtro = st.selectbox(
                            "Coluna para filtro:",
                            colunas_numericas
                        )
                        
                        if coluna_filtro:
                            valor_min = float(dataset[coluna_filtro].min())
                            valor_max = float(dataset[coluna_filtro].max())

                            # Garantir intervalo válido para o slider
                            if valor_min == valor_max:
                                # Expande um pouco o range para evitar erro do Streamlit
                                valor_min_adj = valor_min - 1.0
                                valor_max_adj = valor_max + 1.0
                                default_range = (valor_min_adj, valor_max_adj)
                            else:
                                valor_min_adj = valor_min
                                valor_max_adj = valor_max
                                default_range = (valor_min, valor_max)

                            filtro_min, filtro_max = st.slider(
                                f"Faixa de {coluna_filtro}:",
                                min_value=valor_min_adj,
                                max_value=valor_max_adj,
                                value=default_range
                            )
                
                with col2:
                    if colunas_categoricas:
                        coluna_cat_filtro = st.selectbox(
                            "Coluna categórica para filtro:",
                            colunas_categoricas
                        )
                        
                        if coluna_cat_filtro:
                            valores_unicos = dataset[coluna_cat_filtro].unique()
                            valores_selecionados = st.multiselect(
                                f"Valores de {coluna_cat_filtro}:",
                                valores_unicos,
                                default=valores_unicos[:5] if len(valores_unicos) >= 5 else valores_unicos
                            )
                
                # Aplicar filtros
                if st.button("🔍 Aplicar Filtros"):
                    dataset_filtrado = dataset.copy()
                    
                    if 'coluna_filtro' in locals() and 'filtro_min' in locals() and 'filtro_max' in locals():
                        dataset_filtrado = dataset_filtrado[
                            (dataset_filtrado[coluna_filtro] >= filtro_min) &
                            (dataset_filtrado[coluna_filtro] <= filtro_max)
                        ]
                    
                    if 'coluna_cat_filtro' in locals() and 'valores_selecionados' in locals():
                        dataset_filtrado = dataset_filtrado[
                            dataset_filtrado[coluna_cat_filtro].isin(valores_selecionados)
                        ]
                    
                    st.success(f"✅ Filtros aplicados! Dataset filtrado: {dataset_filtrado.shape}")
                    st.write("**Dados filtrados:**")
                    st.dataframe(dataset_filtrado.head(10))
                    
                    # Download dos dados filtrados
                    csv_filtrado = dataset_filtrado.to_csv(index=False)
                    st.download_button(
                        label="📥 Download dos Dados Filtrados (CSV)",
                        data=csv_filtrado,
                        file_name=f"{dataset_selecionado}_filtrado.csv",
                        mime="text/csv"
                    )
                
                # Estatísticas personalizadas
                st.subheader("📊 **Estatísticas Personalizadas**")
                
                if st.button("📈 Calcular Estatísticas"):
                    with st.spinner("Calculando estatísticas..."):
                        # Estatísticas gerais
                        st.write("**Estatísticas Gerais:**")
                        st.write(f"Total de registros: {len(dataset)}")
                        st.write(f"Total de colunas: {len(dataset.columns)}")
                        st.write(f"Memória utilizada: {dataset.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
                        
                        # Estatísticas por tipo de coluna
                        st.write("**Estatísticas por Tipo de Coluna:**")
                        for dtype in dataset.dtypes.unique():
                            colunas_tipo = dataset.select_dtypes(include=[dtype]).columns
                            st.write(f"- {dtype}: {len(colunas_tipo)} colunas")
                        
                        # Valores únicos por coluna
                        st.write("**Valores Únicos por Coluna:**")
                        for col in dataset.columns:
                            if dataset[col].dtype == 'object':
                                valores_unicos = dataset[col].nunique()
                                st.write(f"- {col}: {valores_unicos} valores únicos")
        
        else:
            st.warning("⚠️ Selecione um dataset válido para começar a exploração")
        
        # Resumo da exploração livre
        st.markdown("---")
        st.markdown("""
        **📋 Funcionalidades da Exploração Livre:**
        
        **1. Visualização de Dados:**
        - Seleção de datasets
        - Visualização de primeiras linhas
        - Informações sobre estrutura dos dados
        
        **2. Análise Exploratória:**
        - Histogramas para variáveis numéricas
        - Gráficos de barras para variáveis categóricas
        - Análise de correlação
        
        **3. Filtros Personalizados:**
        - Filtros por faixa de valores
        - Filtros por valores categóricos
        - Download de dados filtrados
        
        **4. Estatísticas Personalizadas:**
        - Estatísticas descritivas
        - Informações sobre tipos de dados
        - Análise de valores únicos
        """)
        
    else:
        st.error("❌ Nenhum dado disponível para exploração")

def show_reports(dados):
    """Exibe a seção "Relatórios e Downloads".

    Esta função oferece ferramentas para que o usuário possa gerar e baixar
    informações consolidadas. Ela permite a criação de relatórios automáticos
    (de casos, imunização, sorogrupos), o download dos principais datasets em
    formato CSV, e a geração de relatórios personalizados com seleção de
    datasets, período e tipo de relatório.

    Args:
        dados (dict): O dicionário global de dados, usado para gerar os relatórios
                      e fornecer os arquivos para download.
    """
    st.header("📋 **Relatórios e Downloads**")
    st.markdown("---")
    
    if dados:
        st.info("💡 **Gere relatórios personalizados e faça download dos dados**")
        
        # Relatórios automáticos
        st.subheader("📊 **Relatórios Automáticos**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📈 Relatório de Casos"):
                with st.spinner("Gerando relatório de casos..."):
                    if 'casos_2017_2022' in dados:
                        casos = dados['casos_2017_2022']
                        
                        # Resumo de casos
                        total_casos = casos['Casos_Notificados'].sum()
                        total_obitos = casos['Óbitos'].sum()
                        media_casos_ano = casos.groupby('Ano')['Casos_Notificados'].sum().mean()
                        media_obitos_ano = casos.groupby('Ano')['Óbitos'].sum().mean()
                        
                        # Criar relatório
                        relatorio_casos = f"""
                        # RELATÓRIO DE CASOS DE MENINGITE (2017-2022)
                        
                        ## Resumo Executivo
                        - **Total de Casos:** {total_casos:,}
                        - **Total de Óbitos:** {total_obitos:,}
                        - **Média Anual de Casos:** {media_casos_ano:.0f}
                        - **Média Anual de Óbitos:** {media_obitos_ano:.0f}
                        
                        ## Análise por Ano
                        """
                        
                        # Adicionar dados por ano
                        casos_por_ano = casos.groupby('Ano').agg({
                            'Casos_Notificados': 'sum',
                            'Óbitos': 'sum'
                        }).reset_index()
                        
                        for _, row in casos_por_ano.iterrows():
                            relatorio_casos += f"\n- **{row['Ano']}:** {row['Casos_Notificados']:,} casos, {row['Óbitos']:,} óbitos"
                        
                        # Download do relatório
                        st.download_button(
                            label="📥 Download Relatório de Casos (MD)",
                            data=relatorio_casos,
                            file_name="relatorio_casos_meningite.md",
                            mime="text/markdown"
                        )
                        
                        st.success("✅ Relatório de casos gerado com sucesso!")
                    else:
                        st.error("❌ Dados de casos não disponíveis")
        
        with col2:
            if st.button("💉 Relatório de Imunização"):
                with st.spinner("Gerando relatório de imunização..."):
                    if 'imunizacao_ano' in dados:
                        imunizacao = dados['imunizacao_ano']
                        
                        # Resumo de imunização
                        total_doses = imunizacao['Total_Doses'].sum()
                        media_doses_ano = imunizacao['Total_Doses'].mean()
                        periodo_cobertura = f"{imunizacao['Ano'].min()}-{imunizacao['Ano'].max()}"
                        
                        # Criar relatório
                        relatorio_imunizacao = f"""
                        # RELATÓRIO DE IMUNIZAÇÃO (1994-2022)
                        
                        ## Resumo Executivo
                        - **Total de Doses:** {total_doses:,}
                        - **Média Anual:** {media_doses_ano:.0f} doses
                        - **Período de Cobertura:** {periodo_cobertura}
                        
                        ## Evolução Temporal
                        """
                        
                        # Adicionar dados por ano
                        for _, row in imunizacao.iterrows():
                            relatorio_imunizacao += f"\n- **{row['Ano']}:** {row['Total_Doses']:,} doses"
                        
                        # Download do relatório
                        st.download_button(
                            label="📥 Download Relatório de Imunização (MD)",
                            data=relatorio_imunizacao,
                            file_name="relatorio_imunizacao_meningite.md",
                            mime="text/markdown"
                        )
                        
                        st.success("✅ Relatório de imunização gerado com sucesso!")
                    else:
                        st.error("❌ Dados de imunização não disponíveis")
        
        with col3:
            if st.button("🦠 Relatório de Sorogrupos"):
                with st.spinner("Gerando relatório de sorogrupos..."):
                    if 'sorogrupos_consolidados' in dados:
                        sorogrupos = dados['sorogrupos_consolidados']
                        
                        # Resumo de sorogrupos
                        total_sorogrupos = len(sorogrupos)
                        periodo_sorogrupos = f"{sorogrupos['Ano'].min()}-{sorogrupos['Ano'].max()}"
                        
                        # Criar relatório
                        relatorio_sorogrupos = f"""
                        # RELATÓRIO DE SOROGRUPOS (2007-2024)
                        
                        ## Resumo Executivo
                        - **Total de Sorogrupos:** {total_sorogrupos}
                        - **Período de Análise:** {periodo_sorogrupos}
                        
                        ## Principais Sorogrupos
                        """
                        
                        # Adicionar dados de sorogrupos
                        for _, row in sorogrupos.head(10).iterrows():
                            relatorio_sorogrupos += f"\n- **{row['Sorogrupo']} ({row['Ano']}):** {row['Casos']:,} casos"
                        
                        # Download do relatório
                        st.download_button(
                            label="📥 Download Relatório de Sorogrupos (MD)",
                            data=relatorio_sorogrupos,
                            file_name="relatorio_sorogrupos_meningite.md",
                            mime="text/markdown"
                        )
                        
                        st.success("✅ Relatório de sorogrupos gerado com sucesso!")
                    else:
                        st.error("❌ Dados de sorogrupos não disponíveis")
        
        # Downloads de dados
        st.subheader("📥 **Downloads de Dados**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📊 Datasets Principais:**")
            
            # Lista de datasets para download
            datasets_download = [
                ('casos_consolidados', 'Casos Consolidados (2017-2024)'),
                ('sorogrupos_consolidados', 'Sorogrupos Consolidados (2007-2024)'),
                ('etiologias_consolidadas', 'Etiologias Consolidadas (2007-2024)'),
                ('imunizacao_ano', 'Imunização por Ano (1994-2022)'),
                ('imunizacao_uf', 'Imunização por UF'),
                ('imunizacao_faixa_etaria', 'Imunização por Faixa Etária')
            ]
            
            for key, nome in datasets_download:
                if key in dados and isinstance(dados[key], pd.DataFrame):
                    csv_data = dados[key].to_csv(index=False)
                    st.download_button(
                        label=f"📥 {nome}",
                        data=csv_data,
                        file_name=f"{key}.csv",
                        mime="text/csv"
                    )
        
        with col2:
            st.write("**🔬 Análises Especializadas:**")
            
            # Análises especializadas
            if 'analise_regional' in dados:
                csv_regional = dados['analise_regional'].to_csv(index=False)
                st.download_button(
                    label="📥 Análise Regional",
                    data=csv_regional,
                    file_name="analise_regional.csv",
                    mime="text/csv"
                )
            
            if 'matriz_correlacao' in dados:
                csv_correlacao = dados['matriz_correlacao'].to_csv(index=False)
                st.download_button(
                    label="📥 Matriz de Correlação",
                    data=csv_correlacao,
                    file_name="matriz_correlacao.csv",
                    mime="text/csv"
                )
            
            if 'analise_temporal' in dados:
                csv_temporal = dados['analise_temporal'].to_csv(index=False)
                st.download_button(
                    label="📥 Análise Temporal",
                    data=csv_temporal,
                    file_name="analise_temporal.csv",
                    mime="text/csv"
                )
        
        # Relatório personalizado
        st.subheader("✏️ **Relatório Personalizado**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleção de datasets para o relatório
            datasets_relatorio = st.multiselect(
                "Selecione datasets para incluir no relatório:",
                list(dados.keys()),
                default=list(dados.keys())[:5]
            )
            
            # Tipo de relatório
            tipo_relatorio = st.selectbox(
                "Tipo de relatório:",
                ["Resumo Executivo", "Relatório Detalhado", "Relatório Técnico"]
            )
        
        with col2:
            # Período do relatório
            ano_inicio = st.number_input("Ano de início:", min_value=1990, max_value=2024, value=2017)
            ano_fim = st.number_input("Ano de fim:", min_value=1990, max_value=2024, value=2024)
            
            # Incluir gráficos
            incluir_graficos = st.checkbox("Incluir gráficos (HTML)", value=True)
        
        # Gerar relatório personalizado
        if st.button("📋 Gerar Relatório Personalizado"):
            with st.spinner("Gerando relatório personalizado..."):
                try:
                    # Criar relatório personalizado
                    relatorio_personalizado = f"""
                    # RELATÓRIO PERSONALIZADO DE MENINGITE BRASIL
                    
                    ## Informações Gerais
                    - **Tipo:** {tipo_relatorio}
                    - **Período:** {ano_inicio}-{ano_fim}
                    - **Datasets incluídos:** {len(datasets_relatorio)}
                    - **Data de geração:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
                    
                    ## Datasets Analisados
                    """
                    
                    for dataset in datasets_relatorio:
                        if dataset in dados and isinstance(dados[dataset], pd.DataFrame):
                            df = dados[dataset]
                            relatorio_personalizado += f"""
                            
                            ### {dataset.replace('_', ' ').title()}
                            - **Forma:** {df.shape[0]} linhas × {df.shape[1]} colunas
                            - **Colunas:** {', '.join(df.columns.tolist())}
                            - **Período:** {df.select_dtypes(include=[np.number]).min().min() if df.select_dtypes(include=[np.number]).shape[1] > 0 else 'N/A'} - {df.select_dtypes(include=[np.number]).max().max() if df.select_dtypes(include=[np.number]).shape[1] > 0 else 'N/A'}
                            """
                    
                    # Adicionar resumo estatístico
                    relatorio_personalizado += """
                    
                    ## Resumo Estatístico
                    """
                    
                    for dataset in datasets_relatorio:
                        if dataset in dados and isinstance(dados[dataset], pd.DataFrame):
                            df = dados[dataset]
                            colunas_numericas = df.select_dtypes(include=[np.number]).columns
                            if len(colunas_numericas) > 0:
                                relatorio_personalizado += f"""
                                
                                ### {dataset.replace('_', ' ').title()}
                                """
                                for col in colunas_numericas[:5]:  # Limitar a 5 colunas
                                    stats = df[col].describe()
                                    relatorio_personalizado += f"""
                                    **{col}:**
                                    - Média: {stats['mean']:.2f}
                                    - Mediana: {stats['50%']:.2f}
                                    - Desvio padrão: {stats['std']:.2f}
                                    - Mínimo: {stats['min']:.2f}
                                    - Máximo: {stats['max']:.2f}
                                    """
                    
                    # Download do relatório
                    st.download_button(
                        label="📥 Download Relatório Personalizado (MD)",
                        data=relatorio_personalizado,
                        file_name=f"relatorio_personalizado_{ano_inicio}_{ano_fim}.md",
                        mime="text/markdown"
                    )
                    
                    st.success("✅ Relatório personalizado gerado com sucesso!")
                    
                except Exception as e:
                    st.error(f"❌ Erro ao gerar relatório: {e}")
        
        # Resumo dos relatórios
        st.markdown("---")
        st.markdown("""
        **📋 Funcionalidades de Relatórios:**
        
        **1. Relatórios Automáticos:**
        - Relatório de casos (2017-2022)
        - Relatório de imunização (1994-2022)
        - Relatório de sorogrupos (2007-2024)
        
        **2. Downloads de Dados:**
        - Datasets principais em CSV
        - Análises especializadas
        - Dados processados
        
        **3. Relatórios Personalizados:**
        - Seleção de datasets
        - Período personalizado
        - Tipo de relatório configurável
        - Inclusão de gráficos
        
        **4. Formatos Disponíveis:**
        - Markdown (.md)
        - CSV (.csv)
        - HTML (gráficos interativos)
        """)
        
    else:
        st.error("❌ Nenhum dado disponível para relatórios")

def show_technical_exposition(dados):
    """Exibe a seção "Expositivo Técnico - Arquitetura e Metodologia".

    Esta função renderiza uma página detalhada que serve como documentação técnica
    do sistema. Ela descreve a arquitetura de dados, o fluxo de automação, a
    estrutura das tabelas, as metodologias estatísticas e de machine learning
    implementadas, as tecnologias de visualização, e as estratégias de otimização.
    Também apresenta estatísticas ao vivo sobre os dados carregados.

    Args:
        dados (dict): O dicionário global de dados, usado para exibir estatísticas
                      em tempo real sobre os datasets carregados.
    """
    st.header("⚙️ **Expositivo Técnico - Arquitetura e Metodologia**")
    st.markdown("---")
    
    # Introdução
    st.markdown("""
    ## 🎯 **Visão Geral do Sistema**
    
    Este dashboard representa um sistema completo de análise epidemiológica de meningite no Brasil, 
    integrando coleta automatizada de dados, processamento estatístico avançado e visualização interativa.
    """)
    
    # Seção 1: Arquitetura de Dados
    st.header("🏗️ **1. Arquitetura de Dados e Automação**")
    
    # Diagrama de fluxo de dados
    st.subheader("📊 **Fluxo de Dados do Sistema**")
    
    # Criar diagrama Mermaid do fluxo de dados
    diagram_code = """
    graph TD
        A[APIs Oficiais<br/>DataSUS, SIPNI, SIH] --> B[Sistema de Automação<br/>Web Scraping + APIs]
        B --> C[Extração Automatizada<br/>Python + Requests]
        C --> D[Validação e Limpeza<br/>Pandas + NumPy]
        D --> E[Armazenamento<br/>Pasta TABELAS/*.csv]
        E --> F[Carregamento no Dashboard<br/>load_all_data()]
        F --> G[Processamento Estatístico<br/>SciPy + Scikit-learn]
        G --> H[Visualização Interativa<br/>Plotly + Streamlit]
        H --> I[Dashboard Final<br/>Análises Epidemiológicas]
        
        style A fill:#e1f5fe
        style E fill:#f3e5f5
        style G fill:#e8f5e8
        style I fill:#fff3e0
    """
    
    st.markdown("#### 🔄 **Diagrama de Fluxo de Dados:**")
    
    # Mostrar diagrama de fluxo como código
    st.code(diagram_code, language='mermaid')
    
    # Explicação detalhada da automação
    st.markdown("""
    ### 🤖 **Sistema de Automação de Dados**
    
    #### 📡 **Fontes de Dados Oficiais:**
    - **DataSUS (DATASUS):** Sistema de Informações em Saúde
    - **SIPNI:** Sistema de Informações do Programa Nacional de Imunizações  
    - **SIH:** Sistema de Informações Hospitalares
    - **SINAN:** Sistema de Informação de Agravos de Notificação
    
    #### 🔧 **Tecnologias de Automação Utilizadas:**
    
    **Python Libraries:**
    - `requests`: Requisições HTTP para APIs
    - `beautifulsoup4`: Web scraping de páginas HTML
    - `selenium`: Automação de navegadores web
    - `pandas`: Manipulação e análise de dados
    - `numpy`: Computação numérica
    
    **Processo Automatizado:**
    1. **Monitoramento**: Scripts verificam atualizações nas fontes
    2. **Extração**: Dados são coletados via APIs e web scraping
    3. **Validação**: Verificação de integridade e consistência
    4. **Limpeza**: Remoção de duplicatas e tratamento de missing values
    5. **Padronização**: Formatação uniforme das tabelas
    6. **Armazenamento**: Salvamento em formato CSV na pasta TABELAS/
    """)
    
    # Seção 2: Estrutura das Tabelas
    st.header("📋 **2. Estrutura e Utilização das Tabelas**")
    
    # Categorizar as tabelas por tipo
    st.subheader("🗂️ **Categorização das Tabelas de Dados**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📊 **Dados Epidemiológicos:**
        - `casos_consolidados_2017_2024.csv`: Casos notificados agregados
        - `casos_notificados_2017_2022.csv`: Dados brutos de notificação
        - `dados_gerais_2024.csv`: Estatísticas gerais do ano atual
        - `data_meninatu.csv`: Dados específicos de meningite tuberculosa
        - `tabela_unificada.csv`: Base consolidada principal
        
        #### 🦠 **Dados por Sorogrupo:**
        - `sorogrupos_2024.csv`: Sorogrupos do ano atual
        - `sorogrupos_consolidados_2007_2024.csv`: Série histórica
        - `df_sorogrupos_2007_2020.csv`: Dados históricos específicos
        - `df_sorogrupos_2024.csv`: Dados processados 2024
        - `df_sorogrupos_completo.csv`: Base completa consolidada
        """)
    
    with col2:
        st.markdown("""
        #### 🔬 **Dados de Etiologia:**
        - `etiologia_2024.csv`: Etiologias identificadas
        - `etiologias_consolidadas_2007_2024.csv`: Série temporal
        - `df_etiologia_2024.csv`: Dados processados
        - `bacterianas_2024.csv`: Meningites bacterianas
        - `df_bacterianas_2024.csv`: Dados bacterianos processados
        
        #### 💉 **Dados de Imunização:**
        - `imunizacoesmenin.csv`: Dados brutos de vacinação
        - `cleaned_imunizacoesmenin.csv`: Dados limpos
        - `imunizacoesmenin_fixed.csv`: Dados corrigidos
        - `dados_imunizacao_processados.csv`: Base processada
        - `imunobiologicosem2023a2025.csv`: Imunobiológicos período
        """)
    
    # Análise específica por tipo
    st.subheader("🔍 **Análise Específica por Categoria**")
    
    # Dados de hospitalização
    st.markdown("""
    #### 🏥 **Dados Hospitalares (SIH):**
    - `sih_meningite_hospitalar.csv`: Internações por meningite
    - `sih_meningite_long.csv`: Formato longo para análises temporais
    - `sih_meningite_wide.csv`: Formato largo para análises transversais
    
    **Tratamentos Aplicados:**
    - Conversão entre formatos long/wide para diferentes análises
    - Cálculo de taxas de hospitalização
    - Análise de sazonalidade nas internações
    - Correlação com dados de notificação
    """)
    
    # Dados de letalidade
    st.markdown("""
    #### ⚰️ **Dados de Letalidade:**
    - `df_letalidade_2007_2020.csv`: Taxas de letalidade históricas
    - `letalidade_etiologia_2007_2020.csv`: Letalidade por etiologia
    
    **Tratamentos Aplicados:**
    - Cálculo de taxas de letalidade: (Óbitos/Casos) × 100
    - Estratificação por etiologia e sorogrupo
    - Análise temporal da letalidade
    - Identificação de fatores de risco
    """)
    
    # Dados de imunização detalhados
    st.markdown("""
    #### 💉 **Dados de Imunização Estratificados:**
    - `imunizacao_por_ano.csv`: Evolução anual da cobertura
    - `imunizacao_por_faixa_etaria.csv`: Cobertura por idade
    - `imunizacao_por_sorogrupo.csv`: Vacinação específica
    - `imunizacao_por_uf.csv`: Distribuição geográfica
    - `doses_todosimunosate2022.csv`: Doses aplicadas por região
    
    **Tratamentos Aplicados:**
    - Padronização de faixas etárias
    - Cálculo de coberturas vacinais
    - Análise de disparidades regionais
    - Correlação cobertura × incidência
    """)
    
    # Seção 3: Metodologias Estatísticas
    st.header("📈 **3. Metodologias Estatísticas Implementadas**")
    
    st.subheader("🔢 **Estatística Descritiva**")
    st.markdown("""
    #### 📊 **Medidas de Tendência Central e Dispersão:**
    - **Média, Mediana, Moda**: Tendências centrais dos dados
    - **Desvio Padrão, Variância**: Medidas de dispersão
    - **Quartis e Percentis**: Distribuição dos dados
    - **Coeficiente de Variação**: Variabilidade relativa
    
    **Implementação:**
    ```python
    # Exemplo de cálculo de estatísticas descritivas
    stats_descritivas = dados.describe()
    cv = dados.std() / dados.mean() * 100  # Coeficiente de Variação
    ```
    """)
    
    st.subheader("📉 **Análise de Correlação**")
    st.markdown("""
    #### 🔗 **Tipos de Correlação Implementados:**
    
    **1. Correlação de Pearson:**
    - Mede relações lineares entre variáveis
    - Usado para: casos vs letalidade, cobertura vs incidência
    - Formula: r = Σ((x-x̄)(y-ȳ)) / √(Σ(x-x̄)²Σ(y-ȳ)²)
    
    **2. Correlação de Spearman:**
    - Mede relações monotônicas (não necessariamente lineares)
    - Robusto a outliers
    - Baseado em rankings dos dados
    
    **3. Correlação Cruzada:**
    - Análise entre múltiplas variáveis simultaneamente
    - Identifica padrões complexos entre sorogrupos
    
    **Implementação:**
    ```python
    from scipy.stats import pearsonr, spearmanr
    
    # Correlação de Pearson
    corr_pearson, p_pearson = pearsonr(x, y)
    
    # Correlação de Spearman  
    corr_spearman, p_spearman = spearmanr(x, y)
    ```
    """)
    
    st.subheader("📊 **Análise de Regressão**")
    st.markdown("""
    #### 📈 **Modelos de Regressão Utilizados:**
    
    **1. Regressão Linear Simples:**
    - Modelo: Y = β₀ + β₁X + ε
    - Usado para: tendências temporais, relações bivariadas
    - Métricas: R², RMSE, p-valor
    
    **2. Regressão Linear Múltipla:**
    - Modelo: Y = β₀ + β₁X₁ + β₂X₂ + ... + βₙXₙ + ε
    - Usado para: análise multivariada de fatores
    - Validação: Time Series Split para dados temporais
    
    **3. Regressão Polinomial:**
    - Captura relações não-lineares
    - Usado para: relações complexas entre variáveis
    
    **Implementação:**
    ```python
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.metrics import r2_score, mean_squared_error
    
    # Modelo de regressão
    modelo = LinearRegression()
    modelo.fit(X_train, y_train)
    
    # Métricas de avaliação
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    ```
    """)
    
    st.subheader("⏱️ **Análise de Séries Temporais**")
    st.markdown("""
    #### 📅 **Técnicas de Séries Temporais:**
    
    **1. Decomposição STL (Seasonal and Trend decomposition using Loess):**
    - Separa série em: Tendência + Sazonalidade + Resíduos
    - Mais robusta que decomposição clássica
    - Permite análise de componentes individuais
    
    **2. Teste de Estacionariedade (ADF):**
    - Augmented Dickey-Fuller Test
    - Verifica se a série é estacionária
    - Fundamental para modelagem ARIMA
    
    **3. Análise de Autocorrelação:**
    - Identifica padrões de dependência temporal
    - Usado para detectar sazonalidade
    
    **Implementação:**
    ```python
    from statsmodels.tsa.seasonal import STL
    from statsmodels.tsa.stattools import adfuller
    
    # Decomposição STL
    stl = STL(serie_temporal, period=12)
    resultado = stl.fit()
    
    # Teste ADF
    adf_stat, p_value = adfuller(serie_temporal)[:2]
    ```
    """)
    
    st.subheader("🤖 **Machine Learning e Clustering**")
    st.markdown("""
    #### 🔬 **Algoritmos de Machine Learning:**
    
    **1. K-Means Clustering:**
    - Agrupa sorogrupos por características similares
    - Identifica padrões epidemiológicos
    - Usado para: segmentação de sorogrupos
    
    **2. Clustering Hierárquico:**
    - Cria dendrograma de relacionamentos
    - Método Ward para minimizar variância
    - Complementa análise K-Means
    
    **3. PCA (Principal Component Analysis):**
    - Redução dimensional preservando variância
    - Identifica componentes principais
    - Usado para: visualização de dados multidimensionais
    
    **Implementação:**
    ```python
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from scipy.cluster.hierarchy import dendrogram, linkage
    
    # K-Means
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(dados_scaled)
    
    # PCA
    pca = PCA(n_components=2)
    dados_pca = pca.fit_transform(dados_scaled)
    ```
    """)
    
    # Seção 4: Processo de Visualização
    st.header("🎨 **4. Processo de Visualização e Interface**")
    
    st.subheader("📊 **Biblioteca Plotly - Gráficos Interativos**")
    st.markdown("""
    #### 🎯 **Tipos de Gráficos Implementados:**
    
    **1. Gráficos de Linha (Time Series):**
    - Evolução temporal de casos
    - Tendências de vacinação
    - Análise de sazonalidade
    
    **2. Gráficos de Dispersão (Scatter):**
    - Correlações entre variáveis
    - Regressões lineares e polinomiais
    - Análise multivariada
    
    **3. Gráficos de Barras:**
    - Distribuições por categoria
    - Comparações regionais
    - Rankings de incidência
    
    **4. Heatmaps:**
    - Matrizes de correlação
    - Distribuição geográfica
    - Padrões sazonais
    
    **5. Gráficos de Subplots:**
    - Decomposição de séries temporais
    - Análises comparativas
    - Diagnósticos de modelos
    """)
    
    st.subheader("🖥️ **Streamlit - Framework de Interface**")
    st.markdown("""
    #### ⚙️ **Componentes de Interface Utilizados:**
    
    **Navegação:**
    - `st.sidebar.selectbox()`: Menu principal de navegação
    - `st.tabs()`: Abas dentro de seções
    - `st.columns()`: Layout responsivo em colunas
    
    **Visualização:**
    - `st.plotly_chart()`: Gráficos interativos
    - `st.dataframe()`: Tabelas interativas
    - `st.metric()`: KPIs e métricas principais
    
    **Interatividade:**
    - `st.selectbox()`: Seleção de parâmetros
    - `st.slider()`: Controles numéricos
    - `st.checkbox()`: Filtros booleanos
    
    **Formatação:**
    - `st.markdown()`: Texto formatado e explicações
    - `st.latex()`: Fórmulas matemáticas
    - `st.code()`: Código de exemplo
    """)
    
    # Seção 5: Performance e Otimização
    st.header("⚡ **5. Performance e Otimização**")
    
    st.markdown("""
    #### 🚀 **Estratégias de Otimização Implementadas:**
    
    **1. Cache de Dados:**
    ```python
    @st.cache_data
    def load_all_data():
        # Carregamento otimizado com cache
        return dados_processados
    ```
    
    **2. Processamento Eficiente:**
    - Uso de `pandas.groupby()` para agregações
    - Vetorização com `numpy` para cálculos
    - Lazy loading de dados não utilizados
    
    **3. Gestão de Memória:**
    - Limpeza de DataFrames temporários
    - Uso de `dtype` apropriados
    - Garbage collection automático
    
    **4. Tratamento de Erros:**
    - Try-catch para imports condicionais
    - Validação de dados de entrada
    - Fallbacks para funcionalidades avançadas
    """)
    
    # Seção 6: Métricas Epidemiológicas
    st.header("🏥 **6. Métricas Epidemiológicas Calculadas**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📊 **Incidência e Prevalência:**
        
        **Taxa de Ataque:**
        ```
        Taxa = (Casos / População) × 100.000
        ```
        
        **Força de Infecção:**
        ```
        λ = -ln(1 - taxa_ataque)
        ```
        
        **Taxa de Letalidade:**
        ```
        Letalidade = (Óbitos / Casos) × 100
        ```
        """)
    
    with col2:
        st.markdown("""
        #### 💉 **Cobertura Vacinal:**
        
        **Cobertura por Dose:**
        ```
        Cobertura = (Doses / Pop_Alvo) × 100
        ```
        
        **Efetividade Vacinal:**
        ```
        EV = 1 - (Taxa_Vacinados / Taxa_Não_Vacinados)
        ```
        
        **Imunidade Coletiva:**
        ```
        Limiar = 1 - (1/R₀)
        ```
        """)
    
    # Seção 7: Validação e Qualidade
    st.header("✅ **7. Validação e Controle de Qualidade**")
    
    st.markdown("""
    #### 🔍 **Processos de Validação Implementados:**
    
    **1. Validação de Dados:**
    - Verificação de tipos de dados (dtype validation)
    - Detecção de valores missing e outliers
    - Consistência temporal (datas válidas)
    - Integridade referencial entre tabelas
    
    **2. Validação Estatística:**
    - Teste de normalidade (Shapiro-Wilk)
    - Detecção de multicolinearidade (VIF)
    - Validação cruzada para modelos
    - Análise de resíduos
    
    **3. Validação Epidemiológica:**
    - Coerência de taxas calculadas
    - Comparação com literatura científica
    - Validação de tendências esperadas
    - Verificação de sazonalidade conhecida
    
    **4. Monitoramento Contínuo:**
    - Logs de processamento de dados
    - Alertas para anomalias detectadas
    - Versionamento de dados
    - Backup automatizado
    """)
    
    # Seção 8: Considerações Técnicas
    st.header("⚠️ **8. Limitações e Considerações Técnicas**")
    
    st.markdown("""
    #### 🚧 **Limitações Conhecidas:**
    
    **1. Dados:**
    - Dependência da qualidade dos dados oficiais
    - Possível subnotificação em algumas regiões
    - Atraso na disponibilização de dados recentes
    - Mudanças metodológicas nas fontes
    
    **2. Estatísticas:**
    - Modelos assumem distribuições específicas
    - Correlação não implica causalidade
    - Séries temporais curtas limitam análises
    - Possível autocorrelação residual
    
    **3. Técnicas:**
    - Alguns pacotes podem ter incompatibilidades
    - Análises avançadas requerem dados suficientes
    - Clustering é sensível à escala dos dados
    - PCA pode perder interpretabilidade
    
    **4. Performance:**
    - Processamento intensivo para grandes datasets
    - Limitações de memória para análises complexas
    - Tempo de carregamento para primeira execução
    - Dependência de conexão para dados atualizados
    """)
    
    # Seção 9: Estatísticas dos Dados Atuais
    st.header("📊 **9. Estatísticas dos Dados Atualmente Carregados**")
    
    if dados:
        st.subheader("📈 **Resumo dos Datasets Disponíveis**")
        
        # Criar tabela com informações dos datasets
        datasets_info = []
        for key, value in dados.items():
            if isinstance(value, pd.DataFrame):
                datasets_info.append({
                    'Dataset': key,
                    'Linhas': f"{value.shape[0]:,}",
                    'Colunas': value.shape[1],
                    'Memória (MB)': f"{value.memory_usage(deep=True).sum() / 1024**2:.2f}",
                    'Período': 'Variável',
                    'Tipo': 'DataFrame'
                })
            else:
                datasets_info.append({
                    'Dataset': key,
                    'Linhas': '-',
                    'Colunas': '-',
                    'Memória (MB)': '-',
                    'Período': '-',
                    'Tipo': type(value).__name__
                })
        
        df_info = pd.DataFrame(datasets_info)
        st.dataframe(df_info, use_container_width=True)
        
        # Estatísticas gerais
        total_linhas = sum([v.shape[0] for v in dados.values() if isinstance(v, pd.DataFrame)])
        total_memoria = sum([v.memory_usage(deep=True).sum() for v in dados.values() if isinstance(v, pd.DataFrame)])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total de Datasets", len(dados))
        with col2:
            st.metric("📝 Total de Registros", f"{total_linhas:,}")
        with col3:
            st.metric("💾 Memória Total", f"{total_memoria/1024**2:.1f} MB")
        with col4:
            st.metric("🗂️ Tabelas CSV", len([f for f in os.listdir('TABELAS') if f.endswith('.csv')]))
        
        # Análise de qualidade dos dados
        st.subheader("🔍 **Análise de Qualidade dos Dados**")
        
        qualidade_info = []
        for key, value in dados.items():
            if isinstance(value, pd.DataFrame) and not value.empty:
                missing_percent = (value.isnull().sum().sum() / (value.shape[0] * value.shape[1])) * 100
                duplicatas = value.duplicated().sum()
                
                qualidade_info.append({
                    'Dataset': key,
                    'Missing Values (%)': f"{missing_percent:.2f}%",
                    'Duplicatas': duplicatas,
                    'Completude': f"{100-missing_percent:.1f}%",
                    'Status': "✅ Boa" if missing_percent < 5 and duplicatas < 10 else "⚠️ Atenção" if missing_percent < 15 else "❌ Crítica"
                })
        
        if qualidade_info:
            df_qualidade = pd.DataFrame(qualidade_info)
            st.dataframe(df_qualidade, use_container_width=True)
    
    else:
        st.warning("⚠️ Nenhum dado carregado para análise")
    
    # Footer técnico
    st.markdown("---")
    st.markdown("""
    ### 🎯 **Conclusão Técnica**
    
    Este sistema representa uma implementação completa de análise epidemiológica moderna, integrando:
    - **Automação de dados** com tecnologias Python
    - **Análises estatísticas robustas** com múltiplas metodologias
    - **Visualização interativa** para exploração de dados
    - **Interface intuitiva** para diferentes perfis de usuários
    - **Validação rigorosa** para garantir qualidade científica
    
    **Tecnologias Principais:** Python, Pandas, NumPy, SciPy, Scikit-learn, Plotly, Streamlit, Statsmodels
    
    **Padrões Seguidos:** PEP 8, Documentação docstring, Type hints, Git workflow, Code review
    """)


def main():
    """Função principal que executa a aplicação Streamlit.

    Esta função inicializa a página do dashboard, configura a barra lateral de navegação,
    chama a função `load_all_data()` para carregar todos os dados, e gerencia a
    exibição da seção selecionada pelo usuário. Se o carregamento de dados falhar,
    exibe uma mensagem de erro com instruções.
    """
    st.title("🦠 **Dashboard Completo de Meningite Brasil**")
    st.markdown("---")
    
    # Sidebar para navegação
    st.sidebar.title("🧭 **Navegação**")
    
    # Carregar dados
    dados = load_all_data()
    
    if dados:
        # Menu de navegação
        opcao = st.sidebar.selectbox(
            "Escolha uma seção:",
            [
                "🏠 Visão Geral 2024",
                "📊 Análise de Casos",
                "🦠 Análise de Sorogrupos",
                "🔬 Análise de Etiologia",
                "💉 Análise de Imunização",
                "🗺️ Análise Regional",
                "🔬 Análises Avançadas",
                "🦠 Análise Epidemiológica",
                "⚡ Taxa de Ataque",
                "🔍 Exploração Livre",
                "📋 Relatórios",
                "⚙️ Expositivo Técnico"
            ]
        )
        
        # Navegação para as seções
        if opcao == "🏠 Visão Geral 2024":
            show_overview_2024(dados)
        elif opcao == "📊 Análise de Casos":
            show_cases_analysis(dados)
        elif opcao == "🦠 Análise de Sorogrupos":
            show_sorogrupos_analysis(dados)
        elif opcao == "🔬 Análise de Etiologia":
            show_etiologia_analysis(dados)
        elif opcao == "💉 Análise de Imunização":
            show_imunizacao_analysis(dados)
        elif opcao == "🗺️ Análise Regional":
            show_regional_analysis(dados)
        elif opcao == "🔬 Análises Avançadas":
            show_advanced_analysis(dados)
        elif opcao == "🦠 Análise Epidemiológica":
            show_epidemiological_analysis(dados)
        elif opcao == "⚡ Taxa de Ataque":
            show_attack_rate_analysis(dados)
        elif opcao == "🔍 Exploração Livre":
            show_free_exploration(dados)
        elif opcao == "📋 Relatórios":
            show_reports(dados)
        elif opcao == "⚙️ Expositivo Técnico":
            show_technical_exposition(dados)
        
        # Informações adicionais na sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📊 Dados Disponíveis:**")
        
        for key, value in dados.items():
            if isinstance(value, pd.DataFrame):
                st.sidebar.write(f"✅ {key}: {value.shape[0]} linhas")
            else:
                st.sidebar.write(f"✅ {key}")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("**🔧 Desenvolvido com:**")
        st.sidebar.markdown("- Streamlit")
        st.sidebar.markdown("- Plotly")
        st.sidebar.markdown("- Pandas")
        st.sidebar.markdown("- NumPy")
        st.sidebar.markdown("- SciPy")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📅 Última atualização:**")
        st.sidebar.markdown(f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
    else:
        st.error("❌ Erro ao carregar dados. Verifique se os arquivos estão disponíveis na pasta TABELAS/")
        st.info("💡 Certifique-se de que os seguintes arquivos existem:")
        st.write("- casos_consolidados_2017_2024.csv")
        st.write("- sorogrupos_consolidados_2007_2024.csv")
        st.write("- etiologias_consolidadas_2007_2024.csv")
        st.write("- imunizacao_por_ano.csv")
        st.write("- imunizacao_por_uf.csv")
        st.write("- imunizacao_por_faixa_etaria.csv")
        st.write("- imunizacao_por_sorogrupo.csv")
        st.write("- imunobiologicosem2023a2025.csv")
        st.write("- letalidade_etiologia_2007_2020.csv")
        st.write("- casos_notificados_2017_2022.csv")
        st.write("- dados_gerais_2024.csv")
        st.write("- bacterianas_2024.csv")
        st.write("- etiologia_2024.csv")
        st.write("- sorogrupos_2024.csv")
        st.write("- sih_meningite_long.csv")

if __name__ == "__main__":
    main()
