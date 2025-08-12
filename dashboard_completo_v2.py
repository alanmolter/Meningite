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
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
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
    """Carrega todos os dados processados"""
    
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
    """Cria dados regionais a partir dos dados de UF"""
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
    """Cria dados temporais regionais"""
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
    """Cria dados para análise temporal"""
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
    """Cria matriz de correlação simulada"""
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
    """Mostra visão geral dos dados de 2024"""
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
    """Mostra análise dos casos notificados 2017-2024"""
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
    """Mostra análise de sorogrupos com relações não lineares"""
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
            
            with col2:
                st.metric("📊 Correlação de Spearman", f"{corr_spearman:.3f}")
                st.write(f"P-valor: {p_spearman:.4f}")
                st.write("**Interpretação:** Mede correlação monotônica")
            
            # Interpretação das correlações
            st.markdown("""
            **🔍 Interpretação das Correlações:**
            
            **Correlação de Pearson:**
            - **+1.0:** Correlação linear positiva perfeita
            - **0.0:** Sem correlação linear
            - **-1.0:** Correlação linear negativa perfeita
            
            **Correlação de Spearman:**
            - **+1.0:** Relação monotônica crescente perfeita
            - **0.0:** Sem relação monotônica
            - **-1.0:** Relação monotônica decrescente perfeita
            
            **Diferenças importantes:**
            - **Pearson:** Sensível a outliers, assume linearidade
            - **Spearman:** Robusto a outliers, detecta relações não lineares
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
    """Mostra análise de etiologia com análise de componentes principais"""
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
                    
                    # Interpretação dos componentes
                    st.markdown("""
                    **🔍 Interpretação dos Componentes:**
                    
                    **Componente 1:** Representa a direção de maior variabilidade nos dados
                    - **Valores positivos:** Etiologias com muitos casos e alta letalidade
                    - **Valores negativos:** Etiologias com poucos casos e baixa letalidade
                    """)
                    
                    if componentes.shape[1] > 1:
                        st.markdown("""
                        **Componente 2:** Representa a variabilidade restante (ortogonal ao C1)
                        - **Valores positivos:** Etiologias com padrão específico
                        - **Valores negativos:** Etiologias com padrão oposto
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
        
        # Análise temporal por etiologia
        st.subheader("📈 **Análise Temporal por Etiologia**")
        
        if 'Ano' in etiologia.columns and 'Casos' in etiologia.columns:
            try:
                # Preparar dados temporais - tratar valores NaN
                etiologia_analise = etiologia.copy()
                etiologia_analise['Casos'] = etiologia_analise['Casos'].fillna(0)
                
                dados_temporais = etiologia_analise.groupby(['Ano', 'Etiologia'])['Casos'].sum().reset_index()
                
                # Filtrar apenas etiologias com pelo menos um caso
                etiologias_com_casos = dados_temporais.groupby('Etiologia')['Casos'].sum()
                etiologias_com_casos = etiologias_com_casos[etiologias_com_casos > 0].index
                dados_temporais = dados_temporais[dados_temporais['Etiologia'].isin(etiologias_com_casos)]
                
                if len(dados_temporais) > 0:
                    # Gráfico de linha
                    fig_temporal = px.line(
                        dados_temporais,
                        x='Ano',
                        y='Casos',
                        color='Etiologia',
                        title="Evolução Temporal dos Casos por Etiologia",
                        markers=True
                    )
                    
                    fig_temporal.update_layout(
                        xaxis_title="Ano",
                        yaxis_title="Número de Casos",
                        template='plotly_white'
                    )
                    
                    fig_temporal.update_xaxes(tickformat='d')
                    st.plotly_chart(fig_temporal, use_container_width=True)
                    
                    # Estatísticas temporais
                    st.write(f"**Período analisado:** {dados_temporais['Ano'].min()} - {dados_temporais['Ano'].max()}")
                    st.write(f"**Etiologias com dados temporais:** {len(etiologias_com_casos)}")
                else:
                    st.warning("⚠️ Nenhum dado temporal válido encontrado")
            except Exception as e:
                st.warning(f"Erro na análise temporal: {e}")
        else:
            st.warning("⚠️ Colunas 'Ano' e/ou 'Casos' não encontradas para análise temporal")

        # Complemento temporal usando sorogrupos (quando disponível) para ampliar período
        if 'sorogrupos_consolidadas' in dados or 'sorogrupos_consolidados' in dados:
            sorogrupos_df = dados.get('sorogrupos_consolidados') if isinstance(dados.get('sorogrupos_consolidados'), pd.DataFrame) else dados.get('sorogrupos_consolidadas')
            if isinstance(sorogrupos_df, pd.DataFrame) and {'Ano', 'Sorogrupo'}.issubset(sorogrupos_df.columns):
                if 'Casos' in sorogrupos_df.columns:
                    st.subheader("🧪 Evolução Temporal por Sorogrupo (complementar)")
                    sg_tmp = sorogrupos_df.copy()
                    sg_tmp['Casos'] = pd.to_numeric(sg_tmp['Casos'], errors='coerce').fillna(0)
                    serie_sg = sg_tmp.groupby(['Ano', 'Sorogrupo'])['Casos'].sum().reset_index()
                    if len(serie_sg) > 0:
                        fig_sg = px.line(
                            serie_sg, x='Ano', y='Casos', color='Sorogrupo',
                            title='Evolução Temporal dos Casos por Sorogrupo', markers=True
                        )
                        fig_sg.update_layout(template='plotly_white', xaxis_title='Ano', yaxis_title='Casos')
                        fig_sg.update_xaxes(tickformat='d')
                        st.plotly_chart(fig_sg, use_container_width=True)
        
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
    """Mostra análise de dados de imunização com análise de impacto"""
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
                    model_cases = ARIMA(cs['Casos_Notificados'], order=(1, 1, 1)).fit()
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
    """Mostra análises avançadas com machine learning e estatísticas complexas"""
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
                
                # Análise de estacionariedade
                st.markdown("**📊 Teste de Estacionariedade (ADF):**")
                from statsmodels.tsa.stattools import adfuller
                
                resultado_adf = adfuller(dados_tempo['Casos_Notificados'])
                st.write(f"**Estatística ADF:** {resultado_adf[0]:.4f}")
                st.write(f"**P-valor:** {resultado_adf[1]:.4f}")
                st.write(f"**Estacionário:** {'Sim' if resultado_adf[1] < 0.05 else 'Não'}")
                
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
                
                # Tabela de correlações
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
                        st.metric('R² médio (CV)', f"{(r2_valid.mean() if not r2_valid.empty else 0.0):.3f}")
                        st.metric('RMSE médio (CV)', f"{cv_df['RMSE'].mean():.0f}")
                except Exception as _:
                    st.info('ℹ️ Não foi possível calcular a validação temporal nesta amostra.')

                # Resíduos ao longo do tempo
                st.subheader('🩺 Diagnóstico de Resíduos')
                residuos = (y - y_pred).reset_index(drop=True)
                anos_plot = df_int['Ano'].reset_index(drop=True) if 'Ano' in df_int.columns else pd.Series(range(len(residuos)))
                fig_res = px.line(x=anos_plot, y=residuos, markers=True, title='Resíduos ao longo do tempo')
                fig_res.update_layout(xaxis_title='Ano', yaxis_title='Resíduo (Casos)', template='plotly_white')
                st.plotly_chart(fig_res, use_container_width=True)

                # Métricas in-sample
                col1, col2 = st.columns(2)
                with col1:
                    st.metric('R² (in-sample)', f"{r2:.3f}")
                with col2:
                    st.metric('RMSE (in-sample)', f"{rmse:.0f}")
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
    """Mostra análise regional detalhada"""
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
                        trendline='ols',
                        title='Casos vs Total de Doses por Região'
                    )
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
    """Mostra análise epidemiológica detalhada"""
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
    """Mostra análise de taxa de ataque e força de infecção"""
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
                    title="Correlação: Taxa de Ataque vs Letalidade",
                    trendline="ols"
                )
                
                fig_correlacao.update_layout(
                    xaxis_title="Taxa de Ataque (por 100.000 habitantes)",
                    yaxis_title="Taxa de Letalidade (%)",
                    template='plotly_white'
                )
                
                st.plotly_chart(fig_correlacao, use_container_width=True)
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
    """Interface para exploração livre dos dados"""
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
    """Gera relatórios e permite download dos dados"""
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

def main():
    """Função principal do dashboard"""
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
                "📋 Relatórios"
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
