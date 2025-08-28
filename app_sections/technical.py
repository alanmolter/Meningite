import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px

# Import graphviz com tratamento de erro
try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False


def create_advanced_flow_diagram():
    """Cria diagrama de fluxo avançado e complexo usando Plotly"""
    
    # Definir estrutura hierárquica complexa
    layers = {
        # Camada 1: Fontes de Dados (Topo)
        'sources': {
            'DataSUS': {'x': 1, 'y': 10, 'color': '#1565C0', 'icon': '🏥', 'size': 70},
            'SIPNI': {'x': 3, 'y': 10, 'color': '#2E7D32', 'icon': '💉', 'size': 70},
            'SIH': {'x': 5, 'y': 10, 'color': '#C62828', 'icon': '🏨', 'size': 70},
            'SINAN': {'x': 7, 'y': 10, 'color': '#F57C00', 'icon': '📊', 'size': 70},
        },
        # Camada 2: Automação (Nível 2)
        'automation': {
            'Web Scraping': {'x': 2, 'y': 8.5, 'color': '#4527A0', 'icon': '🕷️', 'size': 60},
            'API Requests': {'x': 4, 'y': 8.5, 'color': '#6A1B9A', 'icon': '🔗', 'size': 60},
            'Data Validation': {'x': 6, 'y': 8.5, 'color': '#AD1457', 'icon': '✅', 'size': 60},
        },
        # Camada 3: Processamento (Nível 3)
        'processing': {
            'Python Scripts': {'x': 1.5, 'y': 7, 'color': '#00695C', 'icon': '🐍', 'size': 55},
            'Pandas ETL': {'x': 3.5, 'y': 7, 'color': '#00838F', 'icon': '🔄', 'size': 55},
            'Data Cleaning': {'x': 5.5, 'y': 7, 'color': '#0277BD', 'icon': '🧹', 'size': 55},
            'Quality Check': {'x': 7.5, 'y': 7, 'color': '#0288D1', 'icon': '🔍', 'size': 55},
        },
        # Camada 4: Armazenamento (Nível 4)
        'storage': {
            'CSV Files': {'x': 2, 'y': 5.5, 'color': '#388E3C', 'icon': '📁', 'size': 70},
            'TABELAS/': {'x': 4, 'y': 5.5, 'color': '#43A047', 'icon': '🗂️', 'size': 50},
            'Backup System': {'x': 6, 'y': 5.5, 'color': '#4CAF50', 'icon': '💾', 'size': 60},
        },
        # Camada 5: Carregamento (Nível 5)
        'loading': {
            'load_all_data()': {'x': 4, 'y': 4, 'color': '#FF6F00', 'icon': '⚡', 'size': 75},
        },
        # Camada 6: Análise (Nível 6)
        'analysis': {
            'SciPy': {'x': 1, 'y': 2.5, 'color': '#D32F2F', 'icon': '📈', 'size': 50},
            'Scikit-learn': {'x': 2.5, 'y': 2.5, 'color': '#E64A19', 'icon': '🤖', 'size': 50},
            'Statsmodels': {'x': 4, 'y': 2.5, 'color': '#F57C00', 'icon': '📊', 'size': 50},
            'NumPy': {'x': 5.5, 'y': 2.5, 'color': '#FFA000', 'icon': '🔢', 'size': 50},
            'Pandas': {'x': 7, 'y': 2.5, 'color': '#FFB300', 'icon': '🐼', 'size': 50},
        },
        # Camada 7: Visualização (Nível 7)
        'visualization': {
            'Plotly': {'x': 2, 'y': 1, 'color': '#7B1FA2', 'icon': '📊', 'size': 60},
            'Streamlit': {'x': 4, 'y': 1, 'color': '#8E24AA', 'icon': '🎨', 'size': 60},
            'Interactive Charts': {'x': 6, 'y': 1, 'color': '#9C27B0', 'icon': '📈', 'size': 60},
        },
        # Camada 8: Dashboard Final (Base)
        'output': {
            'Dashboard\nEpidemiológico': {'x': 4, 'y': -0.5, 'color': '#1976D2', 'icon': '🚀', 'size': 90},
        }
    }
    
    # Definir conexões complexas entre camadas
    connections = [
        # Sources -> Automation
        ('DataSUS', 'Web Scraping'), ('DataSUS', 'API Requests'),
        ('SIPNI', 'API Requests'), ('SIPNI', 'Data Validation'),
        ('SIH', 'Web Scraping'), ('SIH', 'API Requests'),
        ('SINAN', 'API Requests'), ('SINAN', 'Data Validation'),
        
        # Automation -> Processing
        ('Web Scraping', 'Python Scripts'), ('Web Scraping', 'Pandas ETL'),
        ('API Requests', 'Python Scripts'), ('API Requests', 'Data Cleaning'),
        ('Data Validation', 'Data Cleaning'), ('Data Validation', 'Quality Check'),
        
        # Processing -> Storage
        ('Python Scripts', 'CSV Files'), ('Pandas ETL', 'TABELAS/'),
        ('Data Cleaning', 'TABELAS/'), ('Quality Check', 'Backup System'),
        
        # Storage -> Loading
        ('CSV Files', 'load_all_data()'), ('TABELAS/', 'load_all_data()'),
        ('Backup System', 'load_all_data()'),
        
        # Loading -> Analysis
        ('load_all_data()', 'SciPy'), ('load_all_data()', 'Scikit-learn'),
        ('load_all_data()', 'Statsmodels'), ('load_all_data()', 'NumPy'),
        ('load_all_data()', 'Pandas'),
        
        # Analysis -> Visualization
        ('SciPy', 'Plotly'), ('Scikit-learn', 'Interactive Charts'),
        ('Statsmodels', 'Plotly'), ('NumPy', 'Streamlit'),
        ('Pandas', 'Streamlit'),
        
        # Visualization -> Output
        ('Plotly', 'Dashboard\nEpidemiológico'), ('Streamlit', 'Dashboard\nEpidemiológico'),
        ('Interactive Charts', 'Dashboard\nEpidemiológico'),
    ]
    
    # Criar figura
    fig = go.Figure()
    
    # Adicionar gradiente de fundo
    fig.add_shape(
        type="rect",
        x0=0, y0=-1, x1=8, y1=11,
        fillcolor="rgba(240, 248, 255, 0.3)",
        line=dict(width=0)
    )
    
    # Adicionar camadas de fundo para organização visual
    layer_backgrounds = [
        {'y0': 9.5, 'y1': 10.5, 'color': 'rgba(33, 150, 243, 0.1)', 'label': 'FONTES DE DADOS'},
        {'y0': 8, 'y1': 9, 'color': 'rgba(156, 39, 176, 0.1)', 'label': 'AUTOMAÇÃO'},
        {'y0': 6.5, 'y1': 7.5, 'color': 'rgba(0, 150, 136, 0.1)', 'label': 'PROCESSAMENTO'},
        {'y0': 5, 'y1': 6, 'color': 'rgba(76, 175, 80, 0.1)', 'label': 'ARMAZENAMENTO'},
        {'y0': 3.5, 'y1': 4.5, 'color': 'rgba(255, 111, 0, 0.1)', 'label': 'CARREGAMENTO'},
        {'y0': 2, 'y1': 3, 'color': 'rgba(244, 67, 54, 0.1)', 'label': 'ANÁLISE ESTATÍSTICA'},
        {'y0': 0.5, 'y1': 1.5, 'color': 'rgba(156, 39, 176, 0.1)', 'label': 'VISUALIZAÇÃO'},
        {'y0': -1, 'y1': 0, 'color': 'rgba(25, 118, 210, 0.1)', 'label': 'DASHBOARD FINAL'},
    ]
    
    for bg in layer_backgrounds:
        fig.add_shape(
            type="rect",
            x0=0.5, y0=bg['y0'], x1=7.5, y1=bg['y1'],
            fillcolor=bg['color'],
            line=dict(color=bg['color'], width=1),
        )
        # Adicionar rótulo da camada
        fig.add_annotation(
            x=0.2, y=(bg['y0'] + bg['y1'])/2,
            text=bg['label'],
            showarrow=False,
            font=dict(size=10, color='#666'),
            textangle=90,
            xanchor='center',
            yanchor='middle'
        )
    
    # Criar dicionário unificado de todos os nós
    all_nodes = {}
    for layer_nodes in layers.values():
        all_nodes.update(layer_nodes)
    
    # Adicionar conexões com diferentes estilos
    for start_name, end_name in connections:
        if start_name in all_nodes and end_name in all_nodes:
            start = all_nodes[start_name]
            end = all_nodes[end_name]
            
            # Estilo da linha baseado na diferença de camada
            y_diff = abs(start['y'] - end['y'])
            if y_diff > 3:  # Conexões de longa distância
                line_style = dict(color='rgba(100, 100, 100, 0.6)', width=2, dash='dot')
            elif y_diff > 1.5:  # Conexões médias
                line_style = dict(color='rgba(50, 50, 50, 0.8)', width=3)
            else:  # Conexões próximas
                line_style = dict(color='rgba(0, 0, 0, 0.9)', width=4)
            
            fig.add_trace(go.Scatter(
                x=[start['x'], end['x']],
                y=[start['y'], end['y']],
                mode='lines',
                line=line_style,
                showlegend=False,
                hoverinfo='none'
            ))
            
            # Adicionar setas mais sofisticadas
            fig.add_annotation(
                x=end['x'],
                y=end['y'],
                ax=start['x'],
                ay=start['y'],
                xref='x', yref='y',
                axref='x', ayref='y',
                arrowhead=3,
                arrowsize=1.2,
                arrowwidth=2,
                arrowcolor='rgba(0, 0, 0, 0.7)',
                showarrow=True,
                text='',
            )
    
    # Adicionar nós com design sofisticado
    for name, props in all_nodes.items():
        # Nó principal
        fig.add_trace(go.Scatter(
            x=[props['x']],
            y=[props['y']],
            mode='markers+text',
            marker=dict(
                size=props['size'],
                color=props['color'],
                line=dict(color='rgba(255, 255, 255, 0.8)', width=3),
                opacity=0.9
            ),
            text=f"{props['icon']}<br>{name}",
            textposition='middle center',
            textfont=dict(size=9, color='white', family='Arial Black'),
            showlegend=False,
            hovertemplate=f'<b>{props["icon"]} {name}</b><br>Camada: {props["y"]}<extra></extra>'
        ))
        
        # Adicionar borda destacada para nós importantes
        if props['size'] > 120:
            fig.add_trace(go.Scatter(
                x=[props['x']],
                y=[props['y']],
                mode='markers',
                marker=dict(
                    size=props['size'] + 20,
                    color='rgba(255, 215, 0, 0.3)',
                    line=dict(color='gold', width=2),
                ),
                showlegend=False,
                hoverinfo='none'
            ))
    
    # Configurar layout sofisticado
    fig.update_layout(
        title={
            'text': '🏗️ Sistema Epidemiológico<br><sub>(Atualização Semanal)</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 12, 'color': '#1565C0', 'family': 'Arial Black'}
        },
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[0, 8]
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[-1.5, 11]
        ),
        plot_bgcolor='rgba(248, 250, 252, 0.8)',
        paper_bgcolor='white',
        height=320,  # Reduzido drasticamente para 320
        margin=dict(l=20, r=15, t=40, b=20),  # Margens mínimas
        annotations=[
            dict(
                x=4, y=-1.3,
                text='<i>Arquitetura modular com processamento distribuído e análises estatísticas avançadas</i>',
                showarrow=False,
                font=dict(size=10, color='#666'),  # Fonte menor
                xanchor='center'
            )
        ]
    )
    
    # Salvar diagrama Plotly como PNG na raiz do projeto
    try:
        import os
        import plotly.io as pio
        # Obter caminho da raiz do projeto
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        png_path = os.path.join(project_root, 'diagrama_plotly_sistema_epidemiologico.png')
        
        # Salvar como PNG
        pio.write_image(fig, png_path, width=1200, height=800, scale=2)
        st.success(f"✅ Diagrama Plotly PNG salvo em: {png_path}")
    except Exception as e:
        st.warning(f"⚠️ Não foi possível salvar PNG do Plotly: {e}")
    
    return fig


def create_graphviz_flow_diagram():
    """Cria diagrama usando Graphviz nativo para máxima complexidade"""
    
    if not GRAPHVIZ_AVAILABLE:
        return None
    
    try:
        # Criar diagrama Graphviz
        dot = graphviz.Digraph(
            name='sistema_epidemiologico',
            comment='Sistema de Análise Epidemiológica de Meningite - Atualização Semanal',
            format='png'
        )
        
        # Configurações globais do diagrama
        dot.attr(
            rankdir='TB',  # Top to Bottom
            size='6,7',    # Reduzido drasticamente para 6x7
            dpi='120',     # Reduzido para 120
            bgcolor='white',
            fontname='Arial',
            fontsize='9',  # Reduzido para 9
            labelloc='t',
            label='Sistema Epidemiológico\\n(Atualização Semanal)'  # Título com informação de atualização
        )
        
        # Configurações de nós padrão
        dot.attr('node', 
                 shape='box',
                 style='filled,rounded',
                 fontname='Arial Bold',
                 fontsize='7',     # Reduzido drasticamente para 7
                 margin='0.1,0.02', # Margens mínimas
                 width='0.8',      # Largura mínima
                 height='0.5')     # Altura mínima
        
        # Configurações de edges padrão
        dot.attr('edge',
                 fontname='Arial',
                 fontsize='5',     # Reduzido drasticamente para 5
                 color='#333333')
        
        # Definir subgrafos por camadas
        
        # Camada 1: Fontes de Dados
        with dot.subgraph(name='cluster_sources') as sources:
            sources.attr(label='🌐 FONTES DE DADOS OFICIAIS',
                        style='filled',
                        color='lightblue',
                        fontsize='8',  # Reduzido de 14 para 12
                        fontname='Arial Bold')
            
            sources.node('datasus', '🏥\\nDataSUS', 
                        fillcolor='#1565C0', fontcolor='white')
            sources.node('sipni', '💉\\nSIPNI', 
                        fillcolor='#2E7D32', fontcolor='white')
            sources.node('sih', '🏨\\nSIH', 
                        fillcolor='#C62828', fontcolor='white')
            sources.node('sinan', '📊\\nSINAN', 
                        fillcolor='#F57C00', fontcolor='white')
        
        # Camada 2: Automação
        with dot.subgraph(name='cluster_automation') as automation:
            automation.attr(label='🤖 CAMADA DE AUTOMAÇÃO',
                           style='filled',
                           color='#F3E5F5',
                           fontsize='8',
                           fontname='Arial Bold')
            
            automation.node('webscraping', '🕷️\\nWeb Scraping', 
                           fillcolor='#4527A0', fontcolor='white')
            automation.node('apis', '🔗\\nAPI Requests', 
                           fillcolor='#6A1B9A', fontcolor='white')
            automation.node('validation', '✅\\nData Validation', 
                           fillcolor='#AD1457', fontcolor='white')
        
        # Camada 3: Processamento
        with dot.subgraph(name='cluster_processing') as processing:
            processing.attr(label='🔧 CAMADA DE PROCESSAMENTO',
                           style='filled',
                           color='#E8F5E8',
                           fontsize='8',
                           fontname='Arial Bold')
            
            processing.node('python', '🐍\\nPython Scripts\\n(Customizados)', 
                           fillcolor='#00695C', fontcolor='white')
            processing.node('pandas_etl', '🔄\\nPandas ETL\\n(Extract, Transform, Load)', 
                           fillcolor='#00838F', fontcolor='white')
            processing.node('cleaning', '🧹\\nData Cleaning\\n(Normalização)', 
                           fillcolor='#0277BD', fontcolor='white')
            processing.node('quality', '🔍\\nQuality Check\\n(Consistência)', 
                           fillcolor='#0288D1', fontcolor='white')
        
        # Camada 4: Armazenamento
        with dot.subgraph(name='cluster_storage') as storage:
            storage.attr(label='💾 CAMADA DE ARMAZENAMENTO',
                        style='filled',
                        color='#E8F5E8',
                        fontsize='14',
                        fontname='Arial Bold')
            
            storage.node('csv', '📁\\nCSV Files\\n(Estruturados)', 
                        fillcolor='#388E3C', fontcolor='white')
            storage.node('tabelas', '🗂️\\nTABELAS/\\n(Diretório Central)', 
                        fillcolor='#43A047', fontcolor='white')
            storage.node('backup', '💾\\nBackup System\\n(Versionamento)', 
                        fillcolor='#4CAF50', fontcolor='white')
        
        # Camada 5: Carregamento
        with dot.subgraph(name='cluster_loading') as loading:
            loading.attr(label='⚡ CAMADA DE CARREGAMENTO',
                        style='filled',
                        color='#FFF3E0',
                        fontsize='14',
                        fontname='Arial Bold')
            
            loading.node('loader', '⚡\\nload_all_data()\\n(Função Principal)', 
                        fillcolor='#FF6F00', fontcolor='white',
                        shape='ellipse',
                        style='filled,bold')
        
        # Camada 6: Análise Estatística
        with dot.subgraph(name='cluster_analysis') as analysis:
            analysis.attr(label='📈 CAMADA DE ANÁLISE ESTATÍSTICA',
                         style='filled',
                         color='#FFEBEE',
                         fontsize='14',
                         fontname='Arial Bold')
            
            analysis.node('scipy', '📈\\nSciPy\\n(Estatísticas)', 
                         fillcolor='#D32F2F', fontcolor='white')
            analysis.node('sklearn', '🤖\\nScikit-learn\\n(Machine Learning)', 
                         fillcolor='#E64A19', fontcolor='white')
            analysis.node('statsmodels', '📊\\nStatsmodels\\n(Modelos Avançados)', 
                         fillcolor='#F57C00', fontcolor='white')
            analysis.node('numpy', '🔢\\nNumPy\\n(Computação)', 
                         fillcolor='#FFA000', fontcolor='white')
            analysis.node('pandas_analysis', '🐼\\nPandas\\n(Análise)', 
                         fillcolor='#FFB300', fontcolor='white')
        
        # Camada 7: Visualização
        with dot.subgraph(name='cluster_visualization') as viz:
            viz.attr(label='🎨 CAMADA DE VISUALIZAÇÃO',
                     style='filled',
                     color='#F3E5F5',
                     fontsize='14',
                     fontname='Arial Bold')
            
            viz.node('plotly', '📊\\nPlotly\\n(Gráficos Interativos)', 
                    fillcolor='#7B1FA2', fontcolor='white')
            viz.node('streamlit', '🎨\\nStreamlit\\n(Interface Web)', 
                    fillcolor='#8E24AA', fontcolor='white')
            viz.node('charts', '📈\\nInteractive Charts\\n(Dashboards)', 
                    fillcolor='#9C27B0', fontcolor='white')
        
        # Camada 8: Dashboard Final
        with dot.subgraph(name='cluster_output') as output:
            output.attr(label='🚀 DASHBOARD FINAL',
                       style='filled',
                       color='#E3F2FD',
                       fontsize='14',
                       fontname='Arial Bold')
            
            output.node('dashboard', '🚀\\nDashboard\\nEpidemiológico\\n(Completo)', 
                       fillcolor='#1976D2', fontcolor='white',
                       shape='doubleoctagon',
                       style='filled,bold',
                       fontsize='12')
        
        # Definir conexões entre as camadas
        
        # Sources -> Automation
        dot.edge('datasus', 'webscraping', label='scraping')
        dot.edge('datasus', 'apis', label='APIs')
        dot.edge('sipni', 'apis', label='REST API')
        dot.edge('sipni', 'validation', label='validar')
        dot.edge('sih', 'webscraping', label='extração')
        dot.edge('sih', 'apis', label='consultas')
        dot.edge('sinan', 'apis', label='dados')
        dot.edge('sinan', 'validation', label='verificar')
        
        # Automation -> Processing
        dot.edge('webscraping', 'python', label='scripts')
        dot.edge('webscraping', 'pandas_etl', label='ETL')
        dot.edge('apis', 'python', label='processar')
        dot.edge('apis', 'cleaning', label='limpar')
        dot.edge('validation', 'cleaning', label='normalizar')
        dot.edge('validation', 'quality', label='verificar')
        
        # Processing -> Storage
        dot.edge('python', 'csv', label='salvar')
        dot.edge('pandas_etl', 'tabelas', label='armazenar')
        dot.edge('cleaning', 'tabelas', label='persistir')
        dot.edge('quality', 'backup', label='backup')
        
        # Storage -> Loading
        dot.edge('csv', 'loader', label='carregar')
        dot.edge('tabelas', 'loader', label='importar')
        dot.edge('backup', 'loader', label='recuperar')
        
        # Loading -> Analysis
        dot.edge('loader', 'scipy', label='estatísticas')
        dot.edge('loader', 'sklearn', label='ML')
        dot.edge('loader', 'statsmodels', label='modelos')
        dot.edge('loader', 'numpy', label='cálculos')
        dot.edge('loader', 'pandas_analysis', label='análise')
        
        # Analysis -> Visualization
        dot.edge('scipy', 'plotly', label='gráficos')
        dot.edge('sklearn', 'charts', label='viz ML')
        dot.edge('statsmodels', 'plotly', label='plots')
        dot.edge('numpy', 'streamlit', label='interface')
        dot.edge('pandas_analysis', 'streamlit', label='dados')
        
        # Visualization -> Output
        dot.edge('plotly', 'dashboard', label='integrar')
        dot.edge('streamlit', 'dashboard', label='renderizar')
        dot.edge('charts', 'dashboard', label='exibir')
        
        # Salvar diagrama como PNG na raiz do projeto
        try:
            import os
            # Obter caminho da raiz do projeto (3 níveis acima de app_sections)
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(current_dir)
            png_path = os.path.join(project_root, 'diagrama_sistema_epidemiologico')
            
            # Renderizar e salvar
            dot.render(png_path, cleanup=True)
            st.success(f"✅ Diagrama PNG salvo em: {png_path}.png")
        except Exception as e:
            st.warning(f"⚠️ Não foi possível salvar PNG: {e}")
        
        return dot
        
    except Exception as e:
        st.error(f"Erro ao criar diagrama Graphviz: {e}")
        return None


def create_data_architecture_diagram():
    """Cria diagrama da arquitetura de dados usando Plotly"""
    
    # Definir categorias e suas tabelas
    categories = {
        'Epidemiológicos': {
            'x': 2, 'y': 6, 'color': '#E3F2FD',
            'tables': ['casos_consolidados', 'casos_notificados', 'dados_gerais', 'tabela_unificada']
        },
        'Sorogrupos': {
            'x': 6, 'y': 6, 'color': '#F3E5F5', 
            'tables': ['sorogrupos_2024', 'sorogrupos_consolidados', 'df_sorogrupos_completo']
        },
        'Etiologia': {
            'x': 10, 'y': 6, 'color': '#E8F5E8',
            'tables': ['etiologia_2024', 'etiologias_consolidadas', 'bacterianas_2024']
        },
        'Imunização': {
            'x': 2, 'y': 3, 'color': '#FFF3E0',
            'tables': ['imunizacoesmenin', 'dados_imunizacao_processados', 'imunobiologicos']
        },
        'Hospitalares': {
            'x': 6, 'y': 3, 'color': '#FFEBEE',
            'tables': ['sih_meningite_hospitalar', 'sih_meningite_long', 'sih_meningite_wide']
        },
        'Letalidade': {
            'x': 10, 'y': 3, 'color': '#F1F8E9',
            'tables': ['df_letalidade', 'letalidade_etiologia']
        },
        'Dashboard': {'x': 6, 'y': 0, 'color': '#FFECB3', 'tables': ['Análises Integradas']}
    }
    
    fig = go.Figure()
    
    # Adicionar conexões para o dashboard central
    for cat_name, cat_data in categories.items():
        if cat_name != 'Dashboard':
            fig.add_trace(go.Scatter(
                x=[cat_data['x'], 6],
                y=[cat_data['y'], 0],
                mode='lines',
                line=dict(color='#999999', width=1, dash='dot'),
                showlegend=False,
                hoverinfo='none'
            ))
    
    # Adicionar nós das categorias
    for cat_name, cat_data in categories.items():
        # Tamanho baseado no número de tabelas
        size = 100 + len(cat_data['tables']) * 10
        
        fig.add_trace(go.Scatter(
            x=[cat_data['x']],
            y=[cat_data['y']],
            mode='markers+text',
            marker=dict(
                size=size,
                color=cat_data['color'],
                line=dict(color='#333333', width=2)
            ),
            text=cat_name,
            textposition='middle center',
            textfont=dict(size=11, color='#000000'),
            showlegend=False,
            hovertemplate=f'<b>{cat_name}</b><br>' + 
                         '<br>'.join([f'• {table}' for table in cat_data['tables']]) + 
                         '<extra></extra>'
        ))
    
    # Configurar layout
    fig.update_layout(
        title={
            'text': '🏗️ Arquitetura de Dados - Categorias das Tabelas',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#1f77b4'}
        },
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[0, 12]
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[-1, 7]
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=250,  # Reduzido drasticamente para 250
        margin=dict(l=20, r=20, t=30, b=20)  # Margens mínimas
    )
    
    return fig


def create_data_statistics_charts(dados):
    """Cria gráficos de estatísticas dos dados carregados"""
    
    if not dados:
        return None, None
    
    # Preparar dados para visualização
    datasets_info = []
    for key, value in dados.items():
        if isinstance(value, pd.DataFrame):
            datasets_info.append({
                'Dataset': key.replace('_', ' ').title(),
                'Linhas': value.shape[0],
                'Colunas': value.shape[1],
                'Memória_MB': value.memory_usage(deep=True).sum() / 1024**2,
                'Missing_Percent': (value.isnull().sum().sum() / (value.shape[0] * value.shape[1])) * 100 if value.shape[0] > 0 and value.shape[1] > 0 else 0
            })
    
    if not datasets_info:
        return None, None
    
    df_stats = pd.DataFrame(datasets_info)
    
    # Gráfico 1: Tamanho dos datasets (linhas)
    fig1 = px.bar(
        df_stats, 
        x='Dataset', 
        y='Linhas',
        title='📊 Número de Registros por Dataset',
        color='Linhas',
        color_continuous_scale='Blues',
        text='Linhas'
    )
    fig1.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig1.update_layout(
        xaxis_tickangle=-45,
        height=220,  # Reduzido drasticamente para 220
        showlegend=False
    )
    
    # Gráfico 2: Uso de memória
    fig2 = px.pie(
        df_stats, 
        values='Memória_MB', 
        names='Dataset',
        title='💾 Distribuição de Uso de Memória',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    fig2.update_layout(height=220)  # Reduzido drasticamente para 220
    
    return fig1, fig2


def show_technical_exposition(dados):
    """Mostra exposição técnica completa do sistema"""
    st.header("⚙️ **Expositivo Técnico - Arquitetura e Metodologia**")
    st.markdown("---")
    
    # Introdução
    st.markdown("""
    ## 🎯 **Visão Geral do Sistema**
    
    Este dashboard representa um sistema completo de análise epidemiológica de meningite no Brasil, 
    integrando coleta automatizada de dados, processamento estatístico avançado e visualização interativa.
    
    ### 📅 **Atualização Semanal Automática**
    
    ⏰ **O sistema atualiza automaticamente todos os dados SEMANALMENTE (1x por semana):**
    - 🔄 **Consulta automática** aos sites oficiais (DataSUS, SIPNI, SIH, SINAN)
    - 🆕 **Criação de novas tabelas** com dados atualizados
    - 📊 **Substituição completa** dos arquivos na pasta `TABELAS/`
    - ✅ **Garantia de dados sempre atuais** para análises precisas
    
    Isso garante que todas as análises e visualizações reflitam sempre os dados mais recentes disponíveis.
    """)
    
    # Seção 1: Arquitetura de Dados
    st.header("🏗️ **1. Arquitetura de Dados e Automação**")
    
    # Diagrama de fluxo de dados visual
    st.subheader("📊 **Fluxo de Dados do Sistema**")
    
    # Oferecer opção entre diagramas
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Escolha o tipo de diagrama:**")
    with col2:
        diagram_type = st.selectbox(
            "Tipo:",
            ["Plotly (Interativo)", "Graphviz (Profissional)"],
            index=0
        )
    
    if diagram_type == "Graphviz (Profissional)" and GRAPHVIZ_AVAILABLE:
        # Criar diagrama Graphviz
        try:
            graphviz_diagram = create_graphviz_flow_diagram()
            if graphviz_diagram:
                st.markdown("#### 🏗️ **Diagrama Graphviz - Máxima Qualidade Profissional**")
                st.graphviz_chart(graphviz_diagram.source)
                st.success("✅ Diagrama Graphviz renderizado com sucesso!")
            else:
                st.warning("⚠️ Não foi possível gerar o diagrama Graphviz. Mostrando versão Plotly.")
                flow_diagram = create_advanced_flow_diagram()
                st.plotly_chart(flow_diagram, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Erro no Graphviz: {e}")
            st.info("🔄 Alternando para diagrama Plotly...")
            flow_diagram = create_advanced_flow_diagram()
            st.plotly_chart(flow_diagram, use_container_width=True)
    else:
        if diagram_type == "Graphviz (Profissional)" and not GRAPHVIZ_AVAILABLE:
            st.warning("⚠️ Graphviz não está disponível. Mostrando versão Plotly interativa.")
        
        # Criar diagrama Plotly
        flow_diagram = create_advanced_flow_diagram()
        st.plotly_chart(flow_diagram, use_container_width=True)
    
    # Explicação detalhada das camadas do fluxo
    st.markdown("""
    #### 🔍 **Explicação Detalhada das 8 Camadas do Sistema:**
    
    ##### 🌐 **Camada 1: FONTES DE DADOS**
    - 🏥 **DataSUS:** Sistema de Informações em Saúde do Ministério
    - 💉 **SIPNI:** Sistema de Informações do Programa Nacional de Imunizações
    - 🏨 **SIH:** Sistema de Informações Hospitalares
    - 📊 **SINAN:** Sistema de Informação de Agravos de Notificação
    
    ##### 🤖 **Camada 2: AUTOMAÇÃO**
    - 🕷️ **Web Scraping:** Extração automatizada de páginas web
    - 🔗 **API Requests:** Requisições diretas a APIs oficiais
    - ✅ **Data Validation:** Validação automática de integridade
    
    ##### 🔧 **Camada 3: PROCESSAMENTO**
    - 🐍 **Python Scripts:** Scripts customizados de processamento
    - 🔄 **Pandas ETL:** Extract, Transform, Load com Pandas
    - 🧹 **Data Cleaning:** Limpeza e normalização de dados
    - 🔍 **Quality Check:** Verificação de qualidade e consistência
    
    ##### 💾 **Camada 4: ARMAZENAMENTO**
    - 📁 **CSV Files:** Arquivos estruturados em formato CSV
    - 🗂️ **TABELAS/:** Diretório central de armazenamento
    - 💾 **Backup System:** Sistema de backup e versionamento
    
    ##### ⚡ **Camada 5: CARREGAMENTO**
    - ⚡ **load_all_data():** Função principal de carregamento otimizado
    
    ##### 📈 **Camada 6: ANÁLISE ESTATÍSTICA**
    - 📈 **SciPy:** Estatísticas científicas e testes
    - 🤖 **Scikit-learn:** Machine learning e modelagem
    - 📊 **Statsmodels:** Modelos estatísticos avançados
    - 🔢 **NumPy:** Computação numérica de alta performance
    - 🐼 **Pandas:** Manipulação e análise de dados
    
    ##### 🎨 **Camada 7: VISUALIZAÇÃO**
    - 📊 **Plotly:** Gráficos interativos e dashboards
    - 🎨 **Streamlit:** Framework de interface web
    - 📈 **Interactive Charts:** Visualizações dinâmicas
    
    ##### 🚀 **Camada 8: DASHBOARD FINAL**
    - 🚀 **Dashboard Epidemiológico:** Interface completa integrada
    
    **💡 Dica:** Passe o mouse sobre cada elemento do diagrama para ver detalhes específicos!
    """)
    
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
    
    **Processo Automatizado (SEMANAL):**
    
    📅 **Cronograma: Toda SEGUNDA-FEIRA às 06:00h**
    
    1. **🔍 Monitoramento**: Scripts verificam atualizações nas fontes oficiais
    2. **📥 Extração**: Dados são coletados via APIs e web scraping automatizado
    3. **✅ Validação**: Verificação de integridade e consistência dos dados
    4. **🧹 Limpeza**: Remoção de duplicatas e tratamento de missing values
    5. **📊 Padronização**: Formatação uniforme das tabelas (padrão CSV)
    6. **💾 Armazenamento**: Substituição completa dos arquivos na pasta `TABELAS/`
    7. **🔄 Backup**: Versionamento automático dos dados anteriores
    8. **📋 Log**: Registro detalhado de todas as operações realizadas
    
    ⚡ **Resultado:** Dados sempre atualizados com no máximo 7 dias de defasagem!
    """)
    
    # Seção 2: Estrutura das Tabelas
    st.header("📋 **2. Estrutura e Utilização das Tabelas**")
    
    # Diagrama de arquitetura de dados
    st.subheader("🏗️ **Arquitetura Visual das Categorias de Dados**")
    
    # Criar e exibir diagrama de arquitetura
    architecture_diagram = create_data_architecture_diagram()
    st.plotly_chart(architecture_diagram, use_container_width=True)
    
    st.markdown("""
    **💡 Dica:** Passe o mouse sobre cada categoria para ver as tabelas específicas que ela contém!
    """)
    
    # Categorizar as tabelas por tipo
    st.subheader("🗂️ **Detalhamento das Categorias de Dados**")
    
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
    
    # Seção 7: Modelagem Epidemiológica
    st.header("🧮 **7. Modelagem Epidemiológica Avançada**")
    
    st.markdown("""
    ### 🦠 **Modelo SIR Implementado**
    
    O sistema inclui uma implementação completa do **modelo SIR** (Susceptible-Infected-Recovered), 
    um dos modelos matemáticos mais fundamentais em epidemiologia.
    
    #### 🔬 **Características da Implementação:**
    
    **📊 Funcionalidades Principais:**
    - ✅ **Ajuste automático** de parâmetros aos dados reais
    - ✅ **Estimação de R₀** (número básico de reprodução)
    - ✅ **Visualizações interativas** com múltiplas perspectivas
    - ✅ **Análise de sensibilidade** dos parâmetros
    - ✅ **Interpretação didática** dos resultados
    
    **⚙️ Métodos Matemáticos:**
    - **Resolução numérica**: Método odeint (scipy.integrate)
    - **Otimização**: Minimização de erro quadrático médio
    - **Algoritmo**: Nelder-Mead para ajuste de parâmetros
    - **Validação**: Comparação com dados históricos
    
    **📈 Equações Diferenciais:**
    ```
    dS/dt = -β × S × I / N
    dI/dt = β × S × I / N - γ × I  
    dR/dt = γ × I
    ```
    
    **🎯 Parâmetros Estimados:**
    - **β (beta)**: Taxa de transmissão
    - **γ (gamma)**: Taxa de recuperação
    - **R₀ = β/γ**: Número básico de reprodução
    
    #### 📊 **Visualizações Geradas:**
    
    1. **Comparação Dados Reais vs Modelo**: Validação do ajuste
    2. **Evolução S-I-R**: Dinâmica dos compartimentos
    3. **Taxa de Infecção**: Velocidade de propagação
    4. **Fase Portrait**: Relação dinâmica S vs I
    5. **Análise de Sensibilidade**: Impacto de variações nos parâmetros
    
    #### 🎓 **Interpretação Epidemiológica:**
    
    **R₀ (Número Básico de Reprodução):**
    - **R₀ < 1**: Epidemia em declínio
    - **R₀ = 1**: Epidemia estável  
    - **R₀ > 1**: Epidemia em crescimento
    
    **Período Infeccioso**: 1/γ (tempo médio de infecção)
    
    **Taxa de Transmissão**: β (probabilidade de transmissão por contato)
    
    #### 🔍 **Limitações Reconhecidas:**
    
    - **População homogênea**: Assume mistura aleatória
    - **Parâmetros constantes**: β e γ fixos no tempo
    - **Sem reinfecção**: Imunidade permanente assumida
    - **Dados agregados**: Resolução temporal limitada
    
    #### 💡 **Aplicações Práticas:**
    
    - **Previsão de surtos**: Estimativa de picos epidêmicos
    - **Avaliação de intervenções**: Impacto de medidas de controle
    - **Planejamento de recursos**: Dimensionamento de leitos/vacinas
    - **Comunicação de risco**: Visualização didática para gestores
    
    #### 📚 **Bibliotecas Utilizadas:**
    
    **Modelagem Epidemiológica:**
    - `epimodels`: Modelos epidemiológicos clássicos
    - `epydemiology`: Análises epidemiológicas avançadas
    - `lmfit`: Ajuste de modelos não-lineares
    - `pymc`: Modelagem probabilística bayesiana
    - `arviz`: Análise e visualização de modelos bayesianos
    
    **Computação Científica:**
    - `scipy.integrate.odeint`: Resolução de EDOs
    - `scipy.optimize.minimize`: Otimização de parâmetros
    - `numpy`: Operações numéricas eficientes
    - `pandas`: Manipulação de dados temporais
    """)
    
    # Seção 8: Validação e Qualidade
    st.header("✅ **8. Validação e Controle de Qualidade**")
    
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
    
    # Seção 9: Considerações Técnicas
    st.header("⚠️ **9. Limitações e Considerações Técnicas**")
    
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
        # Gráficos visuais das estatísticas
        st.subheader("📈 **Visualização das Estatísticas dos Dados**")
        
        chart1, chart2 = create_data_statistics_charts(dados)
        
        if chart1 and chart2:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(chart1, use_container_width=True)
            with col2:
                st.plotly_chart(chart2, use_container_width=True)
        
        st.subheader("📋 **Tabela Detalhada dos Datasets**")
        
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
