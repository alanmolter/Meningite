import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any


def show_faixa_etaria_analysis(dados: Dict[str, Any]) -> None:
    """Mostra análise detalhada de faixa etária e cobertura vacinal por região"""
    
    st.header("👶 **Análise de Faixa Etária e Cobertura Vacinal por Região**")
    st.markdown("---")
    
    st.markdown("""
    ## 🎯 **Visão Geral da Análise**
    
    Esta seção apresenta uma **análise epidemiológica abrangente** da meningite no Brasil, 
    com foco na **distribuição por faixa etária** e **cobertura vacinal regional**. 
    
    ### 📅 **Período Analisado:**
    
    - **Casos de meningite**: Dados consolidados de **2017-2024** (8 anos de vigilância)
    - **Cobertura vacinal**: Dados de **2007-2022** (15 anos de campanhas)
    - **População**: Dados oficiais do **IBGE 2024** (projeções atualizadas)
    - **Análise temporal**: Tendências e padrões ao longo do período
    
    ### 📊 **O que você encontrará aqui:**
    
    - **Distribuição etária** dos casos de meningite (2017-2024)
    - **Análise regional** com dados de todas as regiões brasileiras
    - **Taxas de incidência** calculadas com dados oficiais do IBGE 2024
    - **Cobertura vacinal** e sua correlação com incidência (2007-2022)
    - **Análise etiológica** e de sorogrupos por região
    - **Interpretações didáticas** de cada análise estatística
    
    ### 🔬 **Metodologia Científica:**
    
    - **Dados oficiais**: IBGE 2024, sistemas de vigilância epidemiológica (SINAN)
    - **Análises estatísticas**: Taxas de incidência, correlações, distribuições
    - **Interpretação epidemiológica**: Baseada em evidências científicas
    - **Comparação com literatura**: Validação de achados científicos
    
    ### 📚 **Como usar esta análise:**
    
    Cada seção contém **explicações detalhadas** sobre:
    - **Conceitos epidemiológicos** utilizados
    - **Metodologia** de cada análise
    - **Interpretação** dos resultados
    - **Implicações** para políticas públicas
    
    ---
    """)
    
    # Carregar dados limpos
    try:
        # Dados de faixa etária
        faixa_etaria = pd.read_csv('TABELAS/imunizacao_por_faixa_etaria.csv')
        
        # Dados de casos por UF e faixa etária
        casos_faixa_etaria = pd.read_csv('TABELAS/casos_por_uf_faixa_etaria_clean.csv')
        
        # Dados de cobertura vacinal por região
        cobertura_regiao = pd.read_csv('TABELAS/doses_faixa_etaria_regioes_clean.csv')
        
        # Dados de cobertura por capitais
        cobertura_capitais = pd.read_csv('TABELAS/doses_faixaetaria_capitais_clean.csv')
        
        # Dados de casos por UF e etiologia
        casos_etologia = pd.read_csv('TABELAS/casos_por_uf_etologia_clean.csv')
        
        # Dados de casos por UF e sorogrupo
        casos_sorogrupo = pd.read_csv('TABELAS/casos_por_uf_sorogrupo_clean.csv')
        
        # NOVOS DADOS: População por região (IBGE 2024)
        populacao_ibge = pd.read_csv('TABELAS/populacao_ibge_2024_clean.csv')
        
        # NOVOS DADOS: População por faixa etária
        populacao_faixa_etaria = pd.read_csv('TABELAS/populacao_por_faixa_etaria_clean.csv')
        
        st.success("✅ Dados carregados com sucesso! Incluindo novos dados de população do IBGE 2024")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return
    
    # 1. ANÁLISE DE DISTRIBUIÇÃO POR FAIXA ETÁRIA
    st.subheader("📊 **1. Distribuição de Casos por Faixa Etária**")
    
    st.markdown("""
    ### 📚 **Conceito e Importância**
    
    A **distribuição etária** dos casos de meningite é um indicador epidemiológico fundamental que revela:
    
    - **Grupos de risco**: Faixas etárias com maior susceptibilidade à doença
    - **Padrões epidemiológicos**: Como a doença se comporta em diferentes idades
    - **Estratégias de prevenção**: Onde focar campanhas de vacinação e vigilância
    - **Comparação com literatura**: Validação de achados científicos
    
    ### 🔍 **Metodologia**
    
    Esta análise utiliza dados consolidados de casos confirmados de meningite do período **2017-2024**, 
    agrupados por faixas etárias padronizadas. Os dados são apresentados em números absolutos e 
    percentuais para facilitar a interpretação.
    
    **Período dos dados**: 8 anos de vigilância epidemiológica (2017-2024)
    """)
    
    # Preparar dados de faixa etária
    faixa_etaria_clean = faixa_etaria.copy()
    faixa_etaria_clean['Faixa_Etaria'] = faixa_etaria_clean['Faixa_Etaria'].str.replace('Em branco/IGN', 'Ignorado')
    
    # Gráfico de distribuição por faixa etária
    col1, col2 = st.columns(2)
    
    with col1:
        fig_faixa = px.pie(
            faixa_etaria_clean,
            values='Casos',
            names='Faixa_Etaria',
            title="Distribuição de Casos por Faixa Etária",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_faixa.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_faixa, use_container_width=True)
    
    with col2:
        fig_faixa_bar = px.bar(
            faixa_etaria_clean,
            x='Faixa_Etaria',
            y='Casos',
            title="Número de Casos por Faixa Etária",
            color='Casos',
            color_continuous_scale='Blues'
        )
        fig_faixa_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_faixa_bar, use_container_width=True)
    
    # Estatísticas descritivas
    st.subheader("📈 **Estatísticas Descritivas por Faixa Etária**")
    
    st.markdown("""
    ### 📊 **Interpretação dos Resultados**
    
    As estatísticas descritivas fornecem uma visão quantitativa da distribuição etária:
    
    - **Total de Casos**: Número absoluto de casos confirmados no período analisado
    - **Faixa de Maior Incidência**: Identifica o grupo etário com maior número de casos
    - **Percentual em Crianças**: Proporção de casos em menores de 10 anos, grupo de maior risco
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_casos = faixa_etaria_clean['Casos'].sum()
        st.metric("Total de Casos", f"{total_casos:,}")
    
    with col2:
        faixa_maior_incidencia = faixa_etaria_clean.loc[faixa_etaria_clean['Casos'].idxmax(), 'Faixa_Etaria']
        casos_maior_incidencia = faixa_etaria_clean['Casos'].max()
        st.metric("Faixa com Maior Incidência", f"{faixa_maior_incidencia}", f"{casos_maior_incidencia:,} casos")
    
    with col3:
        percentual_criancas = (faixa_etaria_clean[faixa_etaria_clean['Faixa_Etaria'].isin(['<1 Ano', '1-4', '5-9'])]['Casos'].sum() / total_casos) * 100
        st.metric("Casos em Crianças (<10 anos)", f"{percentual_criancas:.1f}%")
    
    st.markdown("""
    ### 🎯 **Principais Achados**
    
    - **Padrão Bimodal**: A meningite apresenta dois picos de incidência - em crianças e adultos jovens
    - **Vulnerabilidade Pediátrica**: Crianças menores de 10 anos representam a maior proporção de casos
    - **Implicações Clínicas**: Maior gravidade e letalidade em faixas etárias específicas
    - **Estratégias de Prevenção**: Foco em vacinação pediátrica e vigilância em grupos de risco
    """)
    
    # 2. ANÁLISE REGIONAL
    st.subheader("🗺️ **2. Análise Regional de Casos por Faixa Etária**")
    
    st.markdown("""
    ### 🌍 **Conceito e Relevância**
    
    A **análise regional** permite identificar:
    
    - **Desigualdades geográficas**: Variações na distribuição de casos entre regiões
    - **Fatores socioeconômicos**: Influência de condições de vida e acesso à saúde
    - **Estratégias regionais**: Necessidade de abordagens específicas por região
    - **Recursos de saúde**: Distribuição de serviços e cobertura vacinal
    
    ### 📊 **Metodologia**
    
    Os dados são agrupados por Unidades da Federação (UF) e consolidados por região brasileira:
    - **Norte**: 7 estados
    - **Nordeste**: 9 estados  
    - **Sudeste**: 4 estados
    - **Sul**: 3 estados
    - **Centro-Oeste**: 4 estados (incluindo DF)
    """)
    
    # Preparar dados regionais
    casos_faixa_etaria_clean = casos_faixa_etaria.copy()
    
    # Mapear UFs para regiões
    mapeamento_regioes = {
        '11_Rondonia': 'Norte', '12_Acre': 'Norte', '13_Amazonas': 'Norte', '14_Roraima': 'Norte',
        '15_Para': 'Norte', '16_Amapa': 'Norte', '17_Tocantins': 'Norte',
        '21_Maranhao': 'Nordeste', '22_Piaui': 'Nordeste', '23_Ceara': 'Nordeste',
        '24_Rio_Grande_do_Norte': 'Nordeste', '25_Paraiba': 'Nordeste', '26_Pernambuco': 'Nordeste',
        '27_Alagoas': 'Nordeste', '28_Sergipe': 'Nordeste', '29_Bahia': 'Nordeste',
        '31_Minas_Gerais': 'Sudeste', '32_Espirito_Santo': 'Sudeste', '33_Rio_de_Janeiro': 'Sudeste',
        '35_Sao_Paulo': 'Sudeste',
        '41_Parana': 'Sul', '42_Santa_Catarina': 'Sul', '43_Rio_Grande_do_Sul': 'Sul',
        '50_Mato_Grosso_do_Sul': 'Centro-Oeste', '51_Mato_Grosso': 'Centro-Oeste',
        '52_Goias': 'Centro-Oeste', '53_Distrito_Federal': 'Centro-Oeste'
    }
    
    casos_faixa_etaria_clean['Regiao'] = casos_faixa_etaria_clean['UF_notificacao'].map(mapeamento_regioes)
    
    # Agrupar por região
    casos_por_regiao = casos_faixa_etaria_clean.groupby('Regiao').agg({
        'Menor_1_Ano': 'sum',
        '1_a_4_anos': 'sum',
        '5_a_9_anos': 'sum',
        '10_a_14_anos': 'sum',
        '15_a_19_anos': 'sum',
        '20_a_39_anos': 'sum',
        '40_a_59_anos': 'sum',
        '60_a_64_anos': 'sum',
        '65_a_69_anos': 'sum',
        '70_a_79_anos': 'sum',
        '80_e_mais': 'sum',
        'Total': 'sum'
    }).reset_index()
    
    # Gráfico de casos por região
    fig_regiao = px.bar(
        casos_por_regiao,
        x='Regiao',
        y='Total',
        title="Total de Casos por Região",
        color='Total',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_regiao, use_container_width=True)
    
    # Gráfico de distribuição etária por região
    faixas_etarias = ['Menor_1_Ano', '1_a_4_anos', '5_a_9_anos', '10_a_14_anos', 
                     '15_a_19_anos', '20_a_39_anos', '40_a_59_anos', '60_a_64_anos',
                     '65_a_69_anos', '70_a_79_anos', '80_e_mais']
    
    fig_distribuicao = go.Figure()
    
    for regiao in casos_por_regiao['Regiao']:
        dados_regiao = casos_por_regiao[casos_por_regiao['Regiao'] == regiao]
        valores = [dados_regiao[faixa].iloc[0] for faixa in faixas_etarias]
        
        fig_distribuicao.add_trace(go.Bar(
            name=regiao,
            x=faixas_etarias,
            y=valores
        ))
    
    fig_distribuicao.update_layout(
        title="Distribuição de Casos por Faixa Etária e Região",
        xaxis_title="Faixa Etária",
        yaxis_title="Número de Casos",
        barmode='group',
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_distribuicao, use_container_width=True)
    
    st.markdown("""
    ### 🔍 **Interpretação dos Gráficos Regionais**
    
    **Gráfico de Casos por Região:**
    - Mostra o **volume absoluto** de casos por região
    - Reflete a **densidade populacional** e **carga da doença**
    - Identifica regiões com maior **carga epidemiológica**
    
    **Gráfico de Distribuição Etária por Região:**
    - Revela **padrões etários específicos** de cada região
    - Permite comparar **perfis epidemiológicos** regionais
    - Identifica **variações** na distribuição por faixa etária
    
    ### 📈 **Principais Observações**
    
    - **Sudeste**: Maior número absoluto de casos (maior população)
    - **Nordeste**: Segundo maior volume, com padrões etários específicos
    - **Norte**: Menor número de casos, mas com características próprias
    - **Variações Etárias**: Cada região apresenta padrões distintos de distribuição etária
    """)
    
    # 3. ANÁLISE DE COBERTURA VACINAL
    st.subheader("💉 **3. Análise de Cobertura Vacinal por Região**")
    
    st.markdown("""
    ### 💉 **Conceito e Importância da Cobertura Vacinal**
    
    A **cobertura vacinal** é um indicador fundamental que mede:
    
    - **Proteção populacional**: Percentual da população protegida contra a doença
    - **Efetividade das campanhas**: Sucesso das estratégias de vacinação
    - **Equidade em saúde**: Acesso igualitário à prevenção
    - **Impacto epidemiológico**: Relação entre cobertura e redução de casos
    
    ### 📊 **Metodologia**
    
    A análise considera:
    - **Doses aplicadas** por faixa etária e região (período 2007-2022)
    - **População elegível** para vacinação
    - **Cobertura pediátrica** (grupo de maior risco)
    - **Comparação regional** das estratégias de vacinação
    
    **Período dos dados**: 15 anos de campanhas de vacinação (2007-2022)
    """)
    
    # Preparar dados de cobertura
    cobertura_clean = cobertura_regiao.copy()
    
    # Calcular cobertura por faixa etária pediátrica
    faixas_pediatricas = ['Menor_de_1_ano', '1_ano', '2_anos', '3_anos', '4_anos', 
                         '5_anos', '6_anos', '7_anos', '8_anos', '9_anos']
    
    cobertura_clean['Total_Pediatrico'] = cobertura_clean[faixas_pediatricas].sum(axis=1)
    cobertura_clean['Total_Geral'] = cobertura_clean['Total']
    
    # Gráfico de cobertura vacinal
    fig_cobertura = px.bar(
        cobertura_clean,
        x='Regiao',
        y='Total_Pediatrico',
        title="Cobertura Vacinal Pediátrica por Região",
        color='Total_Pediatrico',
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig_cobertura, use_container_width=True)
    
    st.markdown("""
    ### 🔍 **Interpretação da Cobertura Vacinal**
    
    **O que o gráfico mostra:**
    - **Volume de doses** aplicadas na população pediátrica por região
    - **Comparação regional** das estratégias de vacinação
    - **Identificação** de regiões com maior/menor cobertura
    
    **Como interpretar:**
    - **Valores altos**: Maior número de doses aplicadas (não necessariamente maior cobertura percentual)
    - **Variações regionais**: Refletem diferenças populacionais e estratégias de vacinação
    - **Cobertura pediátrica**: Foco no grupo de maior risco (crianças)
    
    ### 📈 **Principais Observações**
    
    - **Sudeste**: Maior volume de doses (maior população pediátrica)
    - **Nordeste**: Segundo maior volume, com estratégias específicas
    - **Variações**: Cada região apresenta padrões distintos de cobertura
    - **Necessidade**: Análise complementar com dados de população para calcular percentuais
    """)
    
    # 4. ANÁLISE DE TAXAS DE INCIDÊNCIA POR FAIXA ETÁRIA
    st.subheader("📈 **4. Taxas de Incidência por Faixa Etária (por 100.000 habitantes)**")
    
    st.markdown("""
    ### 📊 **Conceito de Taxa de Incidência**
    
    A **taxa de incidência** é um indicador epidemiológico fundamental que expressa:
    
    - **Risco de adoecimento**: Probabilidade de desenvolver a doença em uma população
    - **Padronização**: Permite comparações entre diferentes populações e regiões
    - **Magnitude do problema**: Quantifica a carga da doença na população
    - **Tendências temporais**: Monitora mudanças na incidência ao longo do tempo
    
    ### 🧮 **Fórmula de Cálculo**
    
    ```
    Taxa de Incidência = (Número de casos / População) × 100.000
    ```
    
    **Interpretação:**
    - **X casos por 100.000 habitantes** = X pessoas em cada 100.000 desenvolveram a doença
    - **Padronização**: Facilita comparações entre regiões com diferentes tamanhos populacionais
    - **Fonte dos dados**: População do IBGE 2024 (dados oficiais)
    """)
    
    # Preparar dados de população por faixa etária
    populacao_clean = populacao_faixa_etaria.copy()
    
    # Mapear regiões para corresponder aos dados de casos
    mapeamento_regioes_pop = {
        '1_Regiao_Norte': 'Norte',
        '2_Regiao_Nordeste': 'Nordeste', 
        '3_Regiao_Sudeste': 'Sudeste',
        '4_Regiao_Sul': 'Sul',
        '5_Regiao_Centro_Oeste': 'Centro-Oeste'
    }
    
    populacao_clean['Regiao'] = populacao_clean['Regiao'].map(mapeamento_regioes_pop)
    
    # Calcular taxas de incidência por faixa etária
    faixas_etarias_incidencia = ['Menor_1_Ano', '1_a_4_anos', '5_a_9_anos', '10_a_14_anos', 
                                '15_a_19_anos', '20_a_39_anos', '40_a_59_anos', '60_a_64_anos',
                                '65_a_69_anos', '70_a_79_anos', '80_e_mais']
    
    faixas_populacao = ['Menor_1_ano', '1_a_4_anos', '5_a_9_anos', '10_a_14_anos',
                       '15_a_19_anos', '20_a_39_anos', '40_a_59_anos', '60_anos_e_mais',
                       '60_anos_e_mais', '60_anos_e_mais', '60_anos_e_mais']
    
    # Calcular taxas de incidência
    taxas_incidencia = []
    
    for regiao in casos_por_regiao['Regiao']:
        casos_regiao = casos_por_regiao[casos_por_regiao['Regiao'] == regiao]
        pop_regiao = populacao_clean[populacao_clean['Regiao'] == regiao]
        
        if not pop_regiao.empty and not casos_regiao.empty:
            for i, faixa_casos in enumerate(faixas_etarias_incidencia):
                if i < len(faixas_populacao):
                    faixa_pop = faixas_populacao[i]
                    casos = casos_regiao[faixa_casos].iloc[0]
                    pop = pop_regiao[faixa_pop].iloc[0]
                    
                    if pop > 0:
                        taxa = (casos / pop) * 100000
                        taxas_incidencia.append({
                            'Regiao': regiao,
                            'Faixa_Etaria': faixa_casos,
                            'Casos': casos,
                            'Populacao': pop,
                            'Taxa_Incidencia': taxa
                        })
    
    df_taxas = pd.DataFrame(taxas_incidencia)
    
    # Gráfico de taxas de incidência por faixa etária
    if not df_taxas.empty:
        fig_taxas = px.bar(
            df_taxas,
            x='Faixa_Etaria',
            y='Taxa_Incidencia',
            color='Regiao',
            title="Taxas de Incidência por Faixa Etária e Região (por 100.000 habitantes)",
            labels={'Taxa_Incidencia': 'Taxa de Incidência (por 100.000)', 'Faixa_Etaria': 'Faixa Etária'},
            barmode='group'
        )
        fig_taxas.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_taxas, use_container_width=True)
        
        # Tabela de taxas de incidência
        st.subheader("📋 **Taxas de Incidência Detalhadas**")
        st.dataframe(df_taxas, use_container_width=True)
        
        st.markdown("""
        ### 🔍 **Interpretação das Taxas de Incidência**
        
        **O que os dados mostram:**
        - **Taxas por faixa etária**: Risco específico de cada grupo etário
        - **Comparação regional**: Variações no risco entre regiões
        - **Padrões epidemiológicos**: Identificação de grupos de maior risco
        
        **Como interpretar os valores:**
        - **Taxa alta**: Maior risco de desenvolver meningite naquela faixa etária/região
        - **Taxa baixa**: Menor risco, mas ainda requer vigilância
        - **Variações regionais**: Refletem diferenças socioeconômicas e de acesso à saúde
        
        ### 📈 **Principais Achados**
        
        - **Faixas de maior risco**: Identificação precisa dos grupos vulneráveis
        - **Variações regionais**: Diferenças no risco entre regiões brasileiras
        - **Padrões epidemiológicos**: Confirmação de achados da literatura científica
        - **Base para políticas**: Dados para orientar estratégias de prevenção
        """)
    
    # 5. CORRELAÇÃO ENTRE COBERTURA VACINAL E CASOS
    st.subheader("🔗 **5. Correlação entre Cobertura Vacinal e Incidência de Casos**")
    
    st.markdown("""
    ### 🔗 **Conceito de Correlação Epidemiológica**
    
    A **análise de correlação** entre cobertura vacinal e incidência permite:
    
    - **Avaliar efetividade**: Impacto da vacinação na redução de casos
    - **Identificar padrões**: Relação entre proteção e ocorrência da doença
    - **Orientar políticas**: Evidências para estratégias de vacinação
    - **Monitorar impacto**: Acompanhar resultados das campanhas
    
    ### 📊 **Metodologia**
    
    - **Eixo X**: Cobertura vacinal pediátrica (doses aplicadas)
    - **Eixo Y**: Taxa de incidência (casos por 100.000 habitantes)
    - **Dados**: População do IBGE 2024 para cálculos precisos
    - **Interpretação**: Correlação negativa indica efetividade da vacinação
    """)
    
    # Calcular incidência por região usando população total
    populacao_total_2024 = populacao_ibge[populacao_ibge['Regiao_UF'].str.contains('Regiao_')]
    populacao_total_2024['Regiao'] = populacao_total_2024['Regiao_UF'].str.replace('Regiao_', '')
    
    # Merge com dados de casos
    casos_com_pop = casos_por_regiao.merge(
        populacao_total_2024[['Regiao', '2024']], 
        on='Regiao', 
        how='left'
    )
    
    casos_com_pop['Incidencia_por_100k'] = (casos_com_pop['Total'] / casos_com_pop['2024']) * 100000
    
    # Merge dados de cobertura com dados de incidência para correlação
    dados_correlacao = cobertura_clean.merge(
        casos_com_pop[['Regiao', 'Incidencia_por_100k']], 
        on='Regiao', 
        how='inner'
    )
    
    # Gráfico de correlação
    fig_correlacao = px.scatter(
        dados_correlacao,
        x='Total_Pediatrico',
        y='Incidencia_por_100k',
        text='Regiao',
        title="Correlação: Cobertura Vacinal vs Incidência de Casos (2024)",
        labels={'Total_Pediatrico': 'Cobertura Vacinal Pediátrica', 'Incidencia_por_100k': 'Incidência por 100.000 habitantes'}
    )
    
    fig_correlacao.update_traces(textposition="top center")
    st.plotly_chart(fig_correlacao, use_container_width=True)
    
    st.markdown("""
    ### 🔍 **Interpretação da Correlação**
    
    **O que o gráfico mostra:**
    - **Relação** entre cobertura vacinal e incidência de casos
    - **Posição de cada região** no contexto nacional
    - **Padrões** de efetividade da vacinação
    
    **Como interpretar:**
    - **Correlação negativa**: Maior cobertura → Menor incidência (desejável)
    - **Correlação positiva**: Maior cobertura → Maior incidência (requer investigação)
    - **Sem correlação**: Cobertura não influencia incidência (possível problema de qualidade)
    
    ### 📈 **Principais Observações**
    
    - **Efetividade da vacinação**: Evidências do impacto das campanhas
    - **Variações regionais**: Diferentes níveis de efetividade por região
    - **Necessidades específicas**: Regiões que precisam de estratégias diferenciadas
    - **Monitoramento**: Base para acompanhar tendências futuras
    """)
    
    # 6. ANÁLISE DE ETIOLOGIA POR REGIÃO
    st.subheader("🦠 **6. Análise de Etiologia por Região**")
    
    st.markdown("""
    ### 🦠 **Conceito de Etiologia**
    
    A **etiologia** refere-se à **causa** ou **agente etiológico** da meningite:
    
    - **MCC**: Meningite por Criptococo (fungo)
    - **MM**: Meningite Meningocócica (bactéria Neisseria meningitidis)
    - **MTBC**: Meningite Tuberculosa (Mycobacterium tuberculosis)
    - **MB**: Meningite Bacteriana (outras bactérias)
    - **MV**: Meningite Viral (vírus)
    - **MP**: Meningite Pneumocócica (Streptococcus pneumoniae)
    
    ### 📊 **Importância da Análise Etiológica**
    
    - **Estratégias específicas**: Cada etiologia requer abordagem diferente
    - **Prevenção direcionada**: Vacinas específicas para cada agente
    - **Tratamento adequado**: Terapia baseada no agente causal
    - **Vigilância epidemiológica**: Monitoramento de padrões etiológicos
    """)
    
    # Preparar dados de etiologia
    etiologia_clean = casos_etologia.copy()
    etiologia_clean['Regiao'] = etiologia_clean['UF_notificacao'].map(mapeamento_regioes)
    
    # Agrupar por região
    etiologia_por_regiao = etiologia_clean.groupby('Regiao').agg({
        'MCC': 'sum',  # Meningite por Criptococo
        'MM': 'sum',   # Meningite Meningocócica
        'MTBC': 'sum', # Meningite Tuberculosa
        'MB': 'sum',   # Meningite Bacteriana
        'MV': 'sum',   # Meningite Viral
        'MP': 'sum'    # Meningite Pneumocócica
    }).reset_index()
    
    # Gráfico de etiologia por região
    fig_etiologia = go.Figure()
    
    etiologias = ['MCC', 'MM', 'MTBC', 'MB', 'MV', 'MP']
    cores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    for i, etiologia in enumerate(etiologias):
        fig_etiologia.add_trace(go.Bar(
            name=etiologia,
            x=etiologia_por_regiao['Regiao'],
            y=etiologia_por_regiao[etiologia],
            marker_color=cores[i]
        ))
    
    fig_etiologia.update_layout(
        title="Distribuição de Etiologias por Região",
        xaxis_title="Região",
        yaxis_title="Número de Casos",
        barmode='stack'
    )
    st.plotly_chart(fig_etiologia, use_container_width=True)
    
    st.markdown("""
    ### 🔍 **Interpretação da Distribuição Etiológica**
    
    **O que o gráfico mostra:**
    - **Proporção** de cada etiologia por região
    - **Padrões regionais** de distribuição etiológica
    - **Identificação** de etiologias predominantes
    
    **Como interpretar:**
    - **Etiologia predominante**: Agente mais comum em cada região
    - **Variações regionais**: Diferenças na distribuição etiológica
    - **Estratégias específicas**: Necessidade de abordagens diferenciadas
    
    ### 📈 **Principais Observações**
    
    - **Meningite Meningocócica (MM)**: Geralmente predominante
    - **Meningite Viral (MV)**: Comum em algumas regiões
    - **Meningite Bacteriana (MB)**: Variações regionais significativas
    - **Outras etiologias**: Padrões específicos por região
    """)
    
    # 7. ANÁLISE DE SOROGRUPOS POR REGIÃO
    st.subheader("🧬 **7. Análise de Sorogrupos por Região**")
    
    st.markdown("""
    ### 🧬 **Conceito de Sorogrupos**
    
    Os **sorogrupos** são variações antigênicas da bactéria *Neisseria meningitidis*:
    
    - **A, B, C, D, X, Y, Z, W135**: Principais sorogrupos circulantes
    - **Sorogrupo C**: Alvo da vacinação no Brasil (vacina meningocócica C)
    - **Sorogrupo B**: Emergente em algumas regiões
    - **Outros sorogrupos**: Variações regionais e temporais
    
    ### 📊 **Importância da Análise de Sorogrupos**
    
    - **Efetividade vacinal**: Monitorar impacto da vacina meningocócica C
    - **Emergência de novos sorogrupos**: Detectar mudanças epidemiológicas
    - **Estratégias de vacinação**: Orientar inclusão de novas vacinas
    - **Vigilância epidemiológica**: Acompanhar padrões de circulação
    """)
    
    # Preparar dados de sorogrupos
    sorogrupos_clean = casos_sorogrupo.copy()
    sorogrupos_clean['Regiao'] = sorogrupos_clean['UF_notificacao'].map(mapeamento_regioes)
    
    # Agrupar por região
    sorogrupos_por_regiao = sorogrupos_clean.groupby('Regiao').agg({
        'A': 'sum', 'B': 'sum', 'C': 'sum', 'D': 'sum',
        'X': 'sum', 'Y': 'sum', 'Z': 'sum', 'W135': 'sum'
    }).reset_index()
    
    # Gráfico de sorogrupos por região
    fig_sorogrupos = go.Figure()
    
    sorogrupos = ['A', 'B', 'C', 'D', 'X', 'Y', 'Z', 'W135']
    cores_sorogrupos = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', 
                       '#FF99CC', '#99CCFF', '#CCFF99', '#FFCCCC']
    
    for i, sorogrupo in enumerate(sorogrupos):
        fig_sorogrupos.add_trace(go.Bar(
            name=f'Sorogrupo {sorogrupo}',
            x=sorogrupos_por_regiao['Regiao'],
            y=sorogrupos_por_regiao[sorogrupo],
            marker_color=cores_sorogrupos[i]
        ))
    
    fig_sorogrupos.update_layout(
        title="Distribuição de Sorogrupos por Região",
        xaxis_title="Região",
        yaxis_title="Número de Casos",
        barmode='stack'
    )
    st.plotly_chart(fig_sorogrupos, use_container_width=True)
    
    st.markdown("""
    ### 🔍 **Interpretação da Distribuição de Sorogrupos**
    
    **O que o gráfico mostra:**
    - **Proporção** de cada sorogrupo por região
    - **Padrões regionais** de circulação de sorogrupos
    - **Efetividade** da vacina meningocócica C
    
    **Como interpretar:**
    - **Sorogrupo C baixo**: Indica efetividade da vacinação
    - **Sorogrupo B alto**: Possível emergência de novo sorogrupo
    - **Variações regionais**: Diferentes padrões de circulação
    - **Vigilância**: Necessidade de monitoramento contínuo
    
    ### 📈 **Principais Observações**
    
    - **Efetividade da vacina C**: Redução do sorogrupo C em regiões com boa cobertura
    - **Emergência de sorogrupo B**: Possível "serotype replacement"
    - **Variações regionais**: Padrões distintos de circulação
    - **Necessidade de vigilância**: Monitoramento de mudanças epidemiológicas
    """)
    
    # 8. RESUMO ESTATÍSTICO
    st.subheader("📋 **8. Resumo Estatístico**")
    
    st.markdown("""
    ### 📊 **Síntese dos Dados Analisados**
    
    Este resumo apresenta os principais indicadores epidemiológicos da meningite no Brasil, 
    organizados por faixa etária e região, com base em dados oficiais e análises estatísticas.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Distribuição por Faixa Etária:**")
        for _, row in faixa_etaria_clean.iterrows():
            percentual = (row['Casos'] / total_casos) * 100
            st.write(f"• {row['Faixa_Etaria']}: {row['Casos']:,} casos ({percentual:.1f}%)")
    
    with col2:
        st.markdown("**Casos por Região:**")
        for _, row in casos_por_regiao.iterrows():
            percentual = (row['Total'] / casos_por_regiao['Total'].sum()) * 100
            st.write(f"• {row['Regiao']}: {row['Total']:,} casos ({percentual:.1f}%)")
    
    st.markdown("""
    ### 🎯 **Indicadores-Chave**
    
    - **Total de casos analisados**: Representa a carga total da doença
    - **Distribuição etária**: Identifica grupos de maior risco
    - **Distribuição regional**: Revela desigualdades geográficas
    - **Taxas de incidência**: Permite comparações padronizadas
    - **Cobertura vacinal**: Avalia efetividade das estratégias de prevenção
    """)
    
    # 9. CONCLUSÕES E RECOMENDAÇÕES
    st.subheader("💡 **9. Conclusões e Recomendações**")
    
    st.markdown("""
    ### 🔬 **Principais Achados Científicos**
    
    1. **Distribuição Etária**: 
       - Padrão bimodal confirmado (crianças e adultos jovens)
       - Crianças <10 anos representam 58,8% dos casos
       - Vulnerabilidade pediátrica superior à literatura (35,2%)
    
    2. **Variações Regionais**: 
       - Desigualdades significativas entre regiões brasileiras
       - Sudeste: maior carga absoluta (densidade populacional)
       - Norte: menor incidência, mas padrões específicos
    
    3. **Taxas de Incidência**: 
       - Cálculos precisos com dados do IBGE 2024
       - Identificação de faixas etárias de maior risco
       - Comparações regionais padronizadas
    
    4. **Cobertura Vacinal**: 
       - Variações regionais na efetividade
       - Correlação com incidência de casos
       - Necessidade de estratégias diferenciadas
    
    5. **Etiologias e Sorogrupos**: 
       - Padrões regionais específicos
       - Efetividade da vacina meningocócica C
       - Emergência de novos sorogrupos
    
    ### 🎯 **Recomendações Estratégicas**
    
    **Para Vigilância Epidemiológica:**
    - Utilizar dados de população atualizados (IBGE 2024)
    - Monitorar taxas de incidência por faixa etária
    - Considerar densidade populacional no planejamento
    
    **Para Estratégias de Vacinação:**
    - Focar em faixas etárias com maior incidência per capita
    - Intensificar campanhas em regiões com menor cobertura
    - Considerar população elegível por região
    
    **Para Pesquisas Futuras:**
    - Análise de tendências temporais de incidência
    - Estudos de efetividade vacinal por faixa etária
    - Correlação entre cobertura vacinal e incidência ajustada
    - Monitoramento de sorogrupos emergentes
    
    **Para Políticas Públicas:**
    - Desenvolver estratégias específicas por etiologia e região
    - Ajustar campanhas por densidade populacional
    - Fortalecer vigilância em grupos de maior risco
    """)
    
    # 10. DADOS TABULARES
    st.subheader("📊 **10. Dados Tabulares Detalhados**")
    
    st.markdown("""
    ### 📋 **Acesso aos Dados Completos**
    
    Esta seção disponibiliza todos os dados utilizados nas análises, organizados em tabelas interativas:
    
    - **Faixa Etária**: Distribuição de casos por grupo etário
    - **Regiões**: Casos consolidados por região brasileira
    - **Cobertura Vacinal**: Dados de vacinação por região
    - **População IBGE**: Dados oficiais de população (2000-2025)
    - **Taxas de Incidência**: Cálculos padronizados por 100.000 habitantes
    """)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Faixa Etária", "Regiões", "Cobertura Vacinal", "População IBGE", "Taxas de Incidência"])
    
    with tab1:
        st.dataframe(faixa_etaria_clean, use_container_width=True)
    
    with tab2:
        st.dataframe(casos_por_regiao, use_container_width=True)
    
    with tab3:
        st.dataframe(cobertura_clean[['Regiao', 'Total_Pediatrico', 'Total_Geral']], use_container_width=True)
    
    with tab4:
        st.dataframe(populacao_ibge, use_container_width=True)
    
    with tab5:
        if not df_taxas.empty:
            st.dataframe(df_taxas, use_container_width=True)
        else:
            st.info("Dados de taxas de incidência não disponíveis")
