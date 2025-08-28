import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.integrate import odeint
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# Tentativa de importar bibliotecas epidemiológicas
try:
    from lmfit import Parameters, minimize as lm_minimize, report_fit
    LMFIT_AVAILABLE = True
except ImportError:
    LMFIT_AVAILABLE = False

try:
    import epimodels
    EPIMODELS_AVAILABLE = True
except ImportError:
    EPIMODELS_AVAILABLE = False

def sir_equations(y, t, beta, gamma):
    """
    Equações diferenciais do modelo SIR
    
    S' = -beta * S * I
    I' = beta * S * I - gamma * I  
    R' = gamma * I
    
    Parâmetros:
    - beta: taxa de transmissão
    - gamma: taxa de recuperação
    - y: [S, I, R] no tempo t
    """
    S, I, R = y
    N = S + I + R  # População total
    
    dSdt = -beta * S * I / N
    dIdt = beta * S * I / N - gamma * I
    dRdt = gamma * I
    
    return [dSdt, dIdt, dRdt]

def calculate_r0(beta, gamma):
    """Calcula o número básico de reprodução R₀"""
    return beta / gamma

def solve_sir_model(S0, I0, R0, beta, gamma, days):
    """
    Resolve o modelo SIR numericamente
    
    Parâmetros:
    - S0, I0, R0: condições iniciais
    - beta: taxa de transmissão
    - gamma: taxa de recuperação  
    - days: número de dias para simular
    """
    # Condições iniciais
    y0 = [S0, I0, R0]
    
    # Tempo
    t = np.linspace(0, days, days)
    
    # Resolver EDO
    solution = odeint(sir_equations, y0, t, args=(beta, gamma))
    
    return t, solution

def fit_sir_to_data(casos_data, population):
    """
    Ajusta modelo SIR aos dados reais de casos
    
    Parâmetros:
    - casos_data: DataFrame com colunas 'data' e 'casos'
    - population: população total
    """
    # Preparar dados
    casos_data = casos_data.copy()
    casos_data['data'] = pd.to_datetime(casos_data['data'])
    casos_data = casos_data.sort_values('data').reset_index(drop=True)
    
    # Calcular casos acumulados
    casos_data['casos_acumulados'] = casos_data['casos'].cumsum()
    
    # Dias desde o início
    start_date = casos_data['data'].min()
    casos_data['dias'] = (casos_data['data'] - start_date).dt.days
    
    # Dados observados
    days_obs = casos_data['dias'].values
    infected_obs = casos_data['casos_acumulados'].values
    
    # Condições iniciais
    I0 = infected_obs[0] if len(infected_obs) > 0 else 1
    R0 = 0
    S0 = population - I0 - R0
    
    def objective_function(params):
        """Função objetivo para minimizar"""
        beta, gamma = params
        
        if beta <= 0 or gamma <= 0:
            return 1e10
        
        try:
            # Resolver modelo
            t_model = np.arange(0, max(days_obs) + 1)
            _, solution = solve_sir_model(S0, I0, R0, beta, gamma, len(t_model))
            
            # Extrair infectados acumulados do modelo
            I_model = solution[:, 1]
            R_model = solution[:, 2]
            infected_cum_model = I_model + R_model
            
            # Interpolar para os dias observados
            infected_model_interp = np.interp(days_obs, t_model, infected_cum_model)
            
            # Calcular erro quadrático médio
            mse = np.mean((infected_obs - infected_model_interp) ** 2)
            return mse
            
        except Exception:
            return 1e10
    
    # Estimativas iniciais
    initial_guess = [0.3, 0.1]  # beta, gamma
    
    # Otimização
    result = minimize(objective_function, initial_guess, 
                     method='Nelder-Mead',
                     options={'maxiter': 1000})
    
    if result.success:
        beta_opt, gamma_opt = result.x
        r0_opt = calculate_r0(beta_opt, gamma_opt)
        
        return {
            'beta': beta_opt,
            'gamma': gamma_opt,
            'r0': r0_opt,
            'mse': result.fun,
            'success': True,
            'S0': S0,
            'I0': I0,
            'R0': R0,
            'days_obs': days_obs,
            'infected_obs': infected_obs
        }
    else:
        return {'success': False, 'message': 'Otimização falhou'}

def create_sir_visualization(fit_result, prediction_days=365):
    """Cria visualizações do modelo SIR"""
    
    if not fit_result['success']:
        st.error("Não foi possível ajustar o modelo SIR aos dados")
        return None
    
    # Parâmetros ajustados
    beta = fit_result['beta']
    gamma = fit_result['gamma']
    S0 = fit_result['S0']
    I0 = fit_result['I0']
    R0_initial = fit_result['R0']
    
    # Simular modelo para previsão
    t_pred, solution_pred = solve_sir_model(S0, I0, R0_initial, beta, gamma, prediction_days)
    
    # Criar subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            'Comparação: Dados Reais vs Modelo SIR',
            'Evolução das Populações S-I-R',
            'Taxa de Infecção ao Longo do Tempo',
            'Fase Portrait (S vs I)'
        ],
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 1. Comparação dados reais vs modelo
    # Dados observados
    fig.add_trace(
        go.Scatter(
            x=fit_result['days_obs'],
            y=fit_result['infected_obs'],
            mode='markers',
            name='Dados Reais',
            marker=dict(size=8, color='red', symbol='circle'),
            hovertemplate='Dia: %{x}<br>Casos: %{y:.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Modelo ajustado
    I_model = solution_pred[:, 1]
    R_model = solution_pred[:, 2]
    infected_cum_model = I_model + R_model
    
    fig.add_trace(
        go.Scatter(
            x=t_pred,
            y=infected_cum_model,
            mode='lines',
            name='Modelo SIR',
            line=dict(color='blue', width=3),
            hovertemplate='Dia: %{x}<br>Casos Previstos: %{y:.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 2. Evolução S-I-R
    fig.add_trace(
        go.Scatter(x=t_pred, y=solution_pred[:, 0], mode='lines', 
                  name='Suscetíveis (S)', line=dict(color='green', width=2)),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=t_pred, y=solution_pred[:, 1], mode='lines', 
                  name='Infectados (I)', line=dict(color='red', width=2)),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=t_pred, y=solution_pred[:, 2], mode='lines', 
                  name='Recuperados (R)', line=dict(color='blue', width=2)),
        row=1, col=2
    )
    
    # 3. Taxa de infecção
    infection_rate = beta * solution_pred[:, 0] * solution_pred[:, 1] / (S0 + I0 + R0_initial)
    fig.add_trace(
        go.Scatter(x=t_pred, y=infection_rate, mode='lines', 
                  name='Taxa de Infecção', line=dict(color='orange', width=2)),
        row=2, col=1
    )
    
    # 4. Fase Portrait
    fig.add_trace(
        go.Scatter(x=solution_pred[:, 0], y=solution_pred[:, 1], mode='lines', 
                  name='Trajetória S-I', line=dict(color='purple', width=2)),
        row=2, col=2
    )
    
    # Atualizar layout
    fig.update_layout(
        height=800,
        title_text=f"<b>Modelo SIR para Meningite</b><br>" +
                  f"<sub>R₀ = {fit_result['r0']:.2f} | β = {beta:.4f} | γ = {gamma:.4f}</sub>",
        title_x=0.5,
        showlegend=True
    )
    
    # Títulos dos eixos
    fig.update_xaxes(title_text="Dias", row=1, col=1)
    fig.update_yaxes(title_text="Casos Acumulados", row=1, col=1)
    
    fig.update_xaxes(title_text="Dias", row=1, col=2)
    fig.update_yaxes(title_text="População", row=1, col=2)
    
    fig.update_xaxes(title_text="Dias", row=2, col=1)
    fig.update_yaxes(title_text="Taxa de Infecção", row=2, col=1)
    
    fig.update_xaxes(title_text="Suscetíveis (S)", row=2, col=2)
    fig.update_yaxes(title_text="Infectados (I)", row=2, col=2)
    
    return fig

def analyze_sir_parameters(fit_result):
    """Analisa e interpreta os parâmetros do modelo SIR"""
    
    if not fit_result['success']:
        return None
    
    beta = fit_result['beta']
    gamma = fit_result['gamma']
    r0 = fit_result['r0']
    
    # Calcular métricas derivadas
    infectious_period = 1 / gamma  # Período infeccioso médio
    transmission_rate = beta  # Taxa de transmissão
    
    # Interpretações
    analysis = {
        'r0': r0,
        'r0_interpretation': get_r0_interpretation(r0),
        'beta': beta,
        'gamma': gamma,
        'infectious_period': infectious_period,
        'infectious_period_interpretation': get_infectious_period_interpretation(infectious_period),
        'transmission_interpretation': get_transmission_interpretation(beta),
        'epidemic_control': get_epidemic_control_advice(r0)
    }
    
    return analysis

def get_r0_interpretation(r0):
    """Interpreta o valor de R₀"""
    if r0 < 1:
        return {
            'status': 'Epidemia em declínio',
            'color': 'green',
            'explanation': 'R₀ < 1 indica que cada pessoa infectada transmite para menos de 1 pessoa em média. A epidemia tende a se extinguir naturalmente.'
        }
    elif r0 == 1:
        return {
            'status': 'Epidemia estável',
            'color': 'orange',
            'explanation': 'R₀ = 1 indica equilíbrio. Cada pessoa infectada transmite para exatamente 1 pessoa em média.'
        }
    elif 1 < r0 < 2:
        return {
            'status': 'Epidemia em crescimento lento',
            'color': 'orange',
            'explanation': 'R₀ entre 1 e 2 indica crescimento epidêmico moderado. Medidas de controle são necessárias.'
        }
    elif 2 <= r0 < 3:
        return {
            'status': 'Epidemia em crescimento moderado',
            'color': 'red',
            'explanation': 'R₀ entre 2 e 3 indica crescimento epidêmico significativo. Medidas de controle urgentes são necessárias.'
        }
    else:
        return {
            'status': 'Epidemia em crescimento rápido',
            'color': 'darkred',
            'explanation': 'R₀ > 3 indica crescimento epidêmico muito rápido. Medidas de controle intensivas são críticas.'
        }

def get_infectious_period_interpretation(period):
    """Interpreta o período infeccioso"""
    if period < 7:
        return f"Período infeccioso curto ({period:.1f} dias) - típico de doenças agudas"
    elif period < 14:
        return f"Período infeccioso moderado ({period:.1f} dias) - padrão comum para meningite"
    else:
        return f"Período infeccioso longo ({period:.1f} dias) - pode indicar casos crônicos ou subnotificação"

def get_transmission_interpretation(beta):
    """Interpreta a taxa de transmissão"""
    if beta < 0.1:
        return "Taxa de transmissão baixa - doença pouco contagiosa"
    elif beta < 0.5:
        return "Taxa de transmissão moderada - contagiosidade média"
    else:
        return "Taxa de transmissão alta - doença altamente contagiosa"

def get_epidemic_control_advice(r0):
    """Fornece conselhos para controle epidêmico"""
    if r0 < 1:
        return [
            "✅ Manter vigilância epidemiológica",
            "✅ Continuar medidas preventivas atuais",
            "✅ Monitorar possíveis ressurgimentos"
        ]
    elif r0 < 1.5:
        return [
            "⚠️ Intensificar vigilância epidemiológica",
            "⚠️ Implementar medidas de controle moderadas",
            "⚠️ Melhorar detecção precoce de casos"
        ]
    elif r0 < 2.5:
        return [
            "🚨 Implementar medidas de controle intensivas",
            "🚨 Aumentar cobertura vacinal",
            "🚨 Melhorar isolamento e tratamento de casos"
        ]
    else:
        return [
            "🆘 Declarar emergência de saúde pública",
            "🆘 Implementar todas as medidas de controle disponíveis",
            "🆘 Considerar intervenções não farmacológicas adicionais"
        ]

def create_sir_sensitivity_analysis(fit_result):
    """Análise de sensibilidade dos parâmetros"""
    
    if not fit_result['success']:
        return None
    
    # Parâmetros base
    beta_base = fit_result['beta']
    gamma_base = fit_result['gamma']
    
    # Variações percentuais
    variations = [-30, -20, -10, 0, 10, 20, 30]
    
    # Criar figura
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['Sensibilidade ao β (Taxa de Transmissão)', 
                       'Sensibilidade ao γ (Taxa de Recuperação)']
    )
    
    colors = px.colors.qualitative.Set3
    
    # Análise de sensibilidade para beta
    for i, var in enumerate(variations):
        beta_var = beta_base * (1 + var/100)
        r0_var = calculate_r0(beta_var, gamma_base)
        
        t_var, sol_var = solve_sir_model(fit_result['S0'], fit_result['I0'], 
                                        fit_result['R0'], beta_var, gamma_base, 365)
        
        fig.add_trace(
            go.Scatter(
                x=t_var, 
                y=sol_var[:, 1],  # Infectados
                mode='lines',
                name=f'β {var:+d}% (R₀={r0_var:.2f})',
                line=dict(color=colors[i % len(colors)], width=2),
                opacity=0.8 if var == 0 else 0.6
            ),
            row=1, col=1
        )
    
    # Análise de sensibilidade para gamma
    for i, var in enumerate(variations):
        gamma_var = gamma_base * (1 + var/100)
        r0_var = calculate_r0(beta_base, gamma_var)
        
        t_var, sol_var = solve_sir_model(fit_result['S0'], fit_result['I0'], 
                                        fit_result['R0'], beta_base, gamma_var, 365)
        
        fig.add_trace(
            go.Scatter(
                x=t_var, 
                y=sol_var[:, 1],  # Infectados
                mode='lines',
                name=f'γ {var:+d}% (R₀={r0_var:.2f})',
                line=dict(color=colors[i % len(colors)], width=2),
                opacity=0.8 if var == 0 else 0.6,
                showlegend=False
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        height=500,
        title_text="<b>Análise de Sensibilidade do Modelo SIR</b>",
        title_x=0.5
    )
    
    fig.update_xaxes(title_text="Dias")
    fig.update_yaxes(title_text="Infectados")
    
    return fig

def debug_available_data(dados):
    """Função auxiliar para debug dos dados disponíveis"""
    st.subheader("🔍 **Debug: Dados Disponíveis**")
    
    for key, value in dados.items():
        if value is not None:
            if hasattr(value, 'columns'):
                st.write(f"**{key}**: {len(value)} linhas, colunas: {list(value.columns)}")
                if len(value) > 0:
                    st.write(f"  - Exemplo: {value.head(2).to_dict('records')}")
            else:
                st.write(f"**{key}**: {type(value)}")
        else:
            st.write(f"**{key}**: None")

def show_sir_modeling(dados):
    """Função principal para mostrar a modelagem SIR"""
    
    st.header("🧬 **Modelagem Epidemiológica SIR**")
    st.markdown("---")
    
    # Botão para mostrar debug (remover em produção)
    if st.checkbox("🔍 Mostrar dados disponíveis (debug)", value=False):
        debug_available_data(dados)
    
    # Introdução ao modelo SIR
    st.markdown("""
    ## 📚 **O que é o Modelo SIR? - Teoria Epidemiológica Fundamental**
    
    O **modelo SIR** é um dos modelos matemáticos mais fundamentais em epidemiologia, desenvolvido por 
    **Kermack e McKendrick em 1927**. Ele revolucionou nossa compreensão sobre a dinâmica de epidemias 
    e continua sendo amplamente usado até hoje para entender a propagação de doenças infecciosas.
    
    ### 🏢 **Compartimentos do Modelo - Divisão da População:**
    
    O modelo divide a população total em **três compartimentos mutuamente exclusivos**:
    
    - **🟢 S (Susceptible - Suscetíveis)**: 
      - Indivíduos que **podem contrair** a doença
      - Não têm imunidade natural ou adquirida
      - Representam o "combustível" da epidemia
      - **Diminuem** ao longo do tempo conforme se infectam
    
    - **🔴 I (Infected - Infectados)**: 
      - Indivíduos **atualmente infectados** e capazes de transmitir
      - São a fonte de **novas infecções**
      - Representam o "motor" da epidemia
      - **Primeiro aumentam**, depois diminuem conforme se recuperam
    
    - **🔵 R (Recovered/Removed - Recuperados/Removidos)**: 
      - Indivíduos que **se recuperaram** e adquiriram imunidade
      - Ou que **morreram** (foram "removidos" da população suscetível)
      - **Não podem mais** se infectar ou transmitir
      - **Sempre aumentam** monotonicamente
    
    ### ⚙️ **Equações Matemáticas - Como Funciona o Modelo:**
    
    O modelo é descrito por um sistema de **equações diferenciais ordinárias (EDOs)**:
    
    ```
    dS/dt = -β × S × I / N    [Taxa de novas infecções]
    dI/dt = β × S × I / N - γ × I    [Novos infectados - recuperados]
    dR/dt = γ × I    [Taxa de recuperação]
    ```
    
    **Interpretação física de cada termo:**
    
    1. **dS/dt = -β × S × I / N**:
       - **Negativo** porque suscetíveis diminuem
       - **β**: Eficiência de transmissão por contato
       - **S × I**: Número de contatos entre suscetíveis e infectados
       - **1/N**: Normalização pela população total (lei da ação das massas)
    
    2. **dI/dt = β × S × I / N - γ × I**:
       - **+β × S × I / N**: Novos infectados (ganho)
       - **-γ × I**: Infectados que se recuperam (perda)
       - Pode ser **positivo** (epidemia crescendo) ou **negativo** (declinando)
    
    3. **dR/dt = γ × I**:
       - **Sempre positivo** (recuperados só aumentam)
       - Proporcional ao número atual de infectados
    
    ### 📊 **Parâmetros do Modelo - Significado Epidemiológico:**
    
    **β (Beta) - Taxa de Transmissão:**
    - **Unidade**: 1/tempo (por exemplo: 1/dia)
    - **Significado**: Probabilidade de transmissão por contato entre S e I
    - **Fatores que influenciam**: Virulência, comportamento social, densidade populacional
    - **Valores típicos**: 0.1-1.0 por dia para doenças respiratórias
    
    **γ (Gamma) - Taxa de Recuperação:**
    - **Unidade**: 1/tempo (por exemplo: 1/dia)
    - **Significado**: Taxa na qual infectados se recuperam
    - **Relação**: γ = 1/(período infeccioso médio)
    - **Valores típicos**: 0.1-0.5 por dia (período de 2-10 dias)
    
    **R₀ = β/γ - Número Básico de Reprodução:**
    - **Unidade**: Adimensional (número puro)
    - **Significado físico**: Número médio de infecções secundárias causadas por 1 infectado
    - **Interpretação crítica**:
      - **R₀ < 1**: Cada infectado gera < 1 nova infecção → **Epidemia declina**
      - **R₀ = 1**: Cada infectado gera exatamente 1 nova infecção → **Epidemia estável**
      - **R₀ > 1**: Cada infectado gera > 1 nova infecção → **Epidemia cresce**
    
    ### 🎯 **Por que o R₀ é tão Importante?**
    
    O **R₀ determina completamente o destino da epidemia**:
    
    - **R₀ = 1.5**: Cada 100 infectados geram 150 novos casos → Crescimento de 50%
    - **R₀ = 2.0**: Cada 100 infectados geram 200 novos casos → Crescimento de 100%
    - **R₀ = 0.8**: Cada 100 infectados geram apenas 80 novos casos → Declínio de 20%
    
    ### 📈 **Limiar de Imunidade Coletiva:**
    
    **Fração crítica** que precisa ser imune: **Pc = 1 - 1/R₀**
    
    - Se R₀ = 2 → Pc = 50% da população precisa ser imune
    - Se R₀ = 3 → Pc = 67% da população precisa ser imune
    - Se R₀ = 4 → Pc = 75% da população precisa ser imune
    """)
    
    st.markdown("---")
    
    # Seção sobre o método de ajuste
    st.markdown("""
    ## 🔬 **Como Ajustamos o Modelo SIR aos Dados Reais?**
    
    ### 📊 **Metodologia de Ajuste Estatístico:**
    
    Para que o modelo SIR seja útil, precisamos **estimar os parâmetros β e γ** usando dados reais de casos.
    Este processo é chamado de **"inversão de parâmetros"** ou **"calibração do modelo"**.
    
    #### **1. 📈 Dados de Entrada:**
    - **Casos acumulados** por ano (ou período)
    - **População total** estimada
    - **Condições iniciais**: S₀, I₀, R₀ no tempo inicial
    
    #### **2. 🎯 Função Objetivo (Erro Quadrático Médio):**
    
    Queremos minimizar a diferença entre **dados observados** e **modelo predito**:
    
    ```
    MSE = (1/n) × Σ[Dados_Observados - Modelo_SIR]²
    ```
    
    **Por que MSE?**
    - **Penaliza erros grandes** mais que pequenos (quadrático)
    - **Diferenciável** (permite otimização)
    - **Estatisticamente robusto** para ruído gaussiano
    
    #### **3. ⚙️ Algoritmo de Otimização (Nelder-Mead):**
    
    **Nelder-Mead** é um algoritmo de otimização **livre de derivadas**:
    
    **Vantagens:**
    - ✅ **Não precisa** calcular gradientes (derivadas)
    - ✅ **Robusto** para funções não-suaves
    - ✅ **Eficiente** para problemas de baixa dimensionalidade (2 parâmetros)
    - ✅ **Converge bem** para a maioria dos problemas epidemiológicos
    
    **Como funciona:**
    1. **Simplex inicial**: Triângulo no espaço (β, γ)
    2. **Reflexão**: Espelha o pior ponto
    3. **Expansão/Contração**: Ajusta o tamanho do simplex
    4. **Convergência**: Para quando MSE não melhora mais
    
    #### **4. 🔄 Resolução Numérica das EDOs:**
    
    **Método usado**: `scipy.integrate.odeint` (LSODA algorithm)
    
    **LSODA** = **Livermore Solver for Ordinary Differential Equations**:
    - ✅ **Adaptativo**: Escolhe automaticamente método stiff/non-stiff
    - ✅ **Alta precisão**: Controle automático de erro
    - ✅ **Eficiente**: Otimizado para sistemas epidemiológicos
    - ✅ **Estável**: Não diverge numericamente
    
    #### **5. 🎯 Condições Iniciais:**
    
    **Como estimamos S₀, I₀, R₀?**
    
    - **I₀**: Primeiro valor observado de casos
    - **R₀**: Zero (no início da epidemia)
    - **S₀**: População total - I₀ - R₀ (quase toda população suscetível)
    
    **Justificativa epidemiológica:**
    - No início de uma epidemia, a **maioria é suscetível**
    - **Poucos estão infectados** (casos iniciais)
    - **Ninguém se recuperou** ainda (R₀ = 0)
    
    ### 🎲 **Validação do Ajuste:**
    
    **Como sabemos se o modelo está bom?**
    
    1. **MSE baixo**: Erro quadrático médio pequeno
    2. **R² alto**: Coeficiente de determinação próximo de 1
    3. **Parâmetros razoáveis**: β e γ dentro de faixas epidemiológicas esperadas
    4. **Visualização**: Curva do modelo "passa" pelos dados observados
    
    ### ⚠️ **Limitações do Método:**
    
    - **Dados limitados**: Poucos pontos temporais → incerteza alta
    - **Ruído nos dados**: Subnotificação, atrasos → viés nos parâmetros  
    - **Modelo simplificado**: SIR não captura todas as complexidades reais
    - **Parâmetros constantes**: β e γ assumidos fixos no tempo
    
    ### 💡 **Interpretação dos Resultados:**
    
    **Parâmetros estimados devem ser interpretados como:**
    - **β**: Taxa de transmissão **média** no período analisado
    - **γ**: Taxa de recuperação **média** no período analisado
    - **R₀**: Número básico de reprodução **efetivo** médio
    
    **⚡ O algoritmo roda automaticamente quando você configurar os parâmetros abaixo!**
    """)
    
    st.markdown("---")
    
    # Verificar disponibilidade de dados e preparar dataset adequado
    dataset_escolhido = None
    nome_dataset = ""
    
    # Tentar diferentes datasets em ordem de preferência (datasets com séries mais longas primeiro)
    
    # Prioridade 1: Sorogrupos consolidados 2007-2024 (agregado para SIR)
    try:
        df_sorogrupos = pd.read_csv('TABELAS/sorogrupos_consolidados_2007_2024.csv')
        if 'Ano' in df_sorogrupos.columns and 'Casos' in df_sorogrupos.columns:
            # Agregar casos por ano (somar todos os sorogrupos)
            df_temp = df_sorogrupos.groupby('Ano')['Casos'].sum().reset_index()
            df_temp = df_temp.rename(columns={'Ano': 'ano', 'Casos': 'casos'})
            df_temp['regiao'] = 'BRASIL'
            df_temp = df_temp.dropna(subset=['casos'])
            if len(df_temp) > 0:
                dataset_escolhido = df_temp
                nome_dataset = "Sorogrupos Consolidados 2007-2024 (Agregado)"
    except Exception:
        pass
    
    # Prioridade 2: Etiologias consolidadas 2007-2024 (se sorogrupos não funcionou)
    if dataset_escolhido is None:
        try:
            df_etiologias = pd.read_csv('TABELAS/etiologias_consolidadas_2007_2024.csv')
            if 'Ano' in df_etiologias.columns and 'Casos' in df_etiologias.columns:
                # Agregar casos por ano (somar todas as etiologias)
                df_temp = df_etiologias.groupby('Ano')['Casos'].sum().reset_index()
                df_temp = df_temp.rename(columns={'Ano': 'ano', 'Casos': 'casos'})
                df_temp['regiao'] = 'BRASIL'
                df_temp = df_temp.dropna(subset=['casos'])
                if len(df_temp) > 0:
                    dataset_escolhido = df_temp
                    nome_dataset = "Etiologias Consolidadas 2007-2024 (Agregado)"
        except Exception:
            pass
    
    # Prioridade 3: Tabela unificada 2007-2024 (casos por região)
    if dataset_escolhido is None:
        try:
            df_unificada = pd.read_csv('TABELAS/tabela_unificada.csv')
            if 'casos_confirmados' in df_unificada.columns and 'regiao_de_notificacao' in df_unificada.columns:
                # Filtrar apenas dados regionais (não UFs)
                df_temp = df_unificada[df_unificada['regiao_de_notificacao'].notna()].copy()
                df_temp = df_temp.rename(columns={
                    'casos_confirmados': 'casos',
                    'regiao_de_notificacao': 'regiao'
                })
                # Criar coluna ano estimada (baseada no período 2007-2024)
                anos_estimados = np.linspace(2007, 2024, len(df_temp))
                df_temp['ano'] = np.round(anos_estimados).astype(int)
                df_temp = df_temp.dropna(subset=['casos'])
                if len(df_temp) > 0:
                    dataset_escolhido = df_temp
                    nome_dataset = "Tabela Unificada 2007-2024 (Regional)"
        except Exception:
            pass
    
    # Prioridade 4: Casos consolidados 2017-2024
    if dataset_escolhido is None and 'casos_consolidados' in dados and dados['casos_consolidados'] is not None:
        df_temp = dados['casos_consolidados'].copy()
        if 'Ano' in df_temp.columns and 'Casos_Notificados' in df_temp.columns:
            df_temp = df_temp.rename(columns={
                'Ano': 'ano',
                'Casos_Notificados': 'casos'
            })
            df_temp['regiao'] = 'BRASIL'
            dataset_escolhido = df_temp
            nome_dataset = "Casos Consolidados 2017-2024"
    
    # Prioridade 5: Casos notificados 2017-2022
    if dataset_escolhido is None and 'casos_2017_2022' in dados and dados['casos_2017_2022'] is not None:
        df_temp = dados['casos_2017_2022'].copy()
        if 'Ano' in df_temp.columns and 'Casos_Notificados' in df_temp.columns:
            # Renomear colunas para padrão
            df_temp = df_temp.rename(columns={
                'Ano': 'ano',
                'Casos_Notificados': 'casos'
            })
            df_temp['regiao'] = 'BRASIL'  # Dataset nacional
            dataset_escolhido = df_temp
            nome_dataset = "Casos Notificados 2017-2022"
    
    # Prioridade 6: SIH Meningite (como último recurso)
    elif dataset_escolhido is None and 'sih_meningite' in dados and dados['sih_meningite'] is not None:
        df_temp = dados['sih_meningite'].copy()
        if 'Ano_Num' in df_temp.columns and 'Casos_Hospitalares' in df_temp.columns and 'Região' in df_temp.columns:
            # Agrupar por ano e região
            df_temp = df_temp.groupby(['Ano_Num', 'Região'])['Casos_Hospitalares'].sum().reset_index()
            df_temp = df_temp.rename(columns={
                'Ano_Num': 'ano',
                'Casos_Hospitalares': 'casos',
                'Região': 'regiao'
            })
            # Limpar dados - remover valores nulos
            df_temp = df_temp.dropna(subset=['casos'])
            df_temp['casos'] = df_temp['casos'].astype(int)
            dataset_escolhido = df_temp
            nome_dataset = "Casos Hospitalares SIH 2008-2023"
    
    if dataset_escolhido is None or dataset_escolhido.empty:
        st.error("❌ Nenhum dataset adequado encontrado para modelagem SIR")
        st.info("💡 **Datasets disponíveis:** " + ", ".join([k for k, v in dados.items() if v is not None]))
        return
    
    # Preparar dados
    df_casos = dataset_escolhido.copy()
    
    # Verificar se existem as colunas necessárias
    required_cols = ['ano', 'casos']
    missing_cols = [col for col in required_cols if col not in df_casos.columns]
    
    if missing_cols:
        st.error(f"❌ Colunas necessárias não encontradas: {missing_cols}")
        st.info("💡 **Colunas disponíveis:** " + ", ".join(df_casos.columns.tolist()))
        return
    
    # Informar sobre o dataset utilizado
    st.info(f"📊 **Dataset utilizado para modelagem:** {nome_dataset}")
    st.info(f"📈 **Período disponível:** {df_casos['ano'].min()} - {df_casos['ano'].max()}")
    st.info(f"🔢 **Total de registros:** {len(df_casos)}")
    
    # Interface para seleção de parâmetros
    st.header("🎛️ **Configuração da Modelagem**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Seleção de região baseada nos dados disponíveis
        if 'regiao' in df_casos.columns:
            regioes_unicas = df_casos['regiao'].unique()
            regioes_disponiveis = ['BRASIL'] + [r for r in sorted(regioes_unicas) if r != 'BRASIL']
            # Se só tem BRASIL, manter apenas BRASIL
            if len(regioes_unicas) == 1 and 'BRASIL' in regioes_unicas:
                regioes_disponiveis = ['BRASIL']
        else:
            regioes_disponiveis = ['BRASIL']
            
        regiao_selecionada = st.selectbox(
            "🌍 **Região para Análise:**",
            regioes_disponiveis,
            index=0
        )
    
    with col2:
        # Seleção de período
        anos_disponiveis = sorted(df_casos['ano'].unique())
        ano_inicio = st.selectbox(
            "📅 **Ano de Início:**",
            anos_disponiveis,
            index=0
        )
    
    with col3:
        # População estimada
        if regiao_selecionada == 'BRASIL':
            pop_default = 215000000  # População do Brasil
        else:
            pop_default = 15000000   # População regional estimada
            
        populacao = st.number_input(
            "👥 **População Total:**",
            min_value=100000,
            max_value=300000000,
            value=pop_default,
            step=1000000,
            format="%d"
        )
    
    # Filtrar dados
    if 'regiao' in df_casos.columns and regiao_selecionada != 'BRASIL':
        # Filtrar por região específica
        df_filtrado = df_casos[
            (df_casos['regiao'] == regiao_selecionada) & 
            (df_casos['ano'] >= ano_inicio)
        ].groupby('ano')['casos'].sum().reset_index()
    else:
        # Dados do Brasil ou dataset sem coluna região
        if 'regiao' in df_casos.columns:
            # Agregar todas as regiões
            df_filtrado = df_casos[df_casos['ano'] >= ano_inicio].groupby('ano')['casos'].sum().reset_index()
        else:
            # Dataset já é nacional
            df_filtrado = df_casos[df_casos['ano'] >= ano_inicio].copy()
    
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados")
        return
    
    # Criar coluna de data (assumindo meio do ano)
    df_filtrado['data'] = pd.to_datetime(df_filtrado['ano'].astype(str) + '-07-01')
    
    st.markdown("---")
    
    # Executar modelagem SIR
    st.header("🔬 **Resultados da Modelagem SIR**")
    
    with st.spinner("🧮 Ajustando modelo SIR aos dados..."):
        fit_result = fit_sir_to_data(df_filtrado[['data', 'casos']], populacao)
    
    if not fit_result['success']:
        st.error("❌ Não foi possível ajustar o modelo SIR aos dados disponíveis")
        st.info("💡 Isso pode ocorrer devido a dados insuficientes ou padrões não epidêmicos")
        return
    
    # Análise dos parâmetros
    analysis = analyze_sir_parameters(fit_result)
    
    # Mostrar métricas principais
    st.subheader("📊 **Parâmetros Estimados do Modelo**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        r0_interp = analysis['r0_interpretation']
        st.metric(
            label="**R₀ (Número Básico de Reprodução)**",
            value=f"{analysis['r0']:.2f}",
            help="Número médio de infecções secundárias causadas por um indivíduo infectado"
        )
        st.markdown(f"<p style='color: {r0_interp['color']}; font-size: 14px;'><b>{r0_interp['status']}</b></p>", 
                   unsafe_allow_html=True)
    
    with col2:
        st.metric(
            label="**β (Taxa de Transmissão)**",
            value=f"{analysis['beta']:.4f}",
            help="Probabilidade de transmissão por contato entre suscetível e infectado"
        )
        st.markdown(f"<p style='font-size: 14px;'>{analysis['transmission_interpretation']}</p>", 
                   unsafe_allow_html=True)
    
    with col3:
        st.metric(
            label="**γ (Taxa de Recuperação)**",
            value=f"{analysis['gamma']:.4f}",
            help="Taxa na qual infectados se recuperam (1/período_infeccioso)"
        )
        st.markdown(f"<p style='font-size: 14px;'>γ = 1/{analysis['infectious_period']:.1f} dias</p>", 
                   unsafe_allow_html=True)
    
    with col4:
        st.metric(
            label="**Período Infeccioso**",
            value=f"{analysis['infectious_period']:.1f} dias",
            help="Tempo médio que um indivíduo permanece infectado"
        )
        st.markdown(f"<p style='font-size: 14px;'>{analysis['infectious_period_interpretation']}</p>", 
                   unsafe_allow_html=True)
    
    # Interpretação detalhada do R₀
    st.subheader("🎯 **Interpretação do R₀**")
    r0_interp = analysis['r0_interpretation']
    
    st.markdown(f"""
    <div style='padding: 20px; border-left: 5px solid {r0_interp['color']}; background-color: rgba(128, 128, 128, 0.1); margin: 10px 0;'>
    <h4 style='color: {r0_interp['color']}; margin-top: 0;'>{r0_interp['status']}</h4>
    <p style='margin-bottom: 0;'>{r0_interp['explanation']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Recomendações para controle
    st.subheader("💡 **Recomendações para Controle Epidemiológico**")
    
    recommendations = analysis['epidemic_control']
    for rec in recommendations:
        st.markdown(f"- {rec}")
    
    st.markdown("---")
    
    # Visualizações
    st.subheader("📈 **Visualizações do Modelo SIR**")
    
    # Gráfico principal
    fig_main = create_sir_visualization(fit_result, prediction_days=365*2)
    if fig_main:
        st.plotly_chart(fig_main, use_container_width=True)
        
        # Explicações dos gráficos
        with st.expander("📖 **Entenda os Gráficos - Interpretação Detalhada**"):
            st.markdown("""
            ## 📊 **Gráfico 1: Comparação Dados Reais vs Modelo SIR**
            
            ### 🎯 **O que mostra:**
            - **Pontos vermelhos** 🔴: Casos reais observados (dados históricos do SINAN/DataSUS)
            - **Linha azul** 🔵: Previsão do modelo SIR com parâmetros ajustados
            - **Eixo X**: Tempo (dias desde o início do período analisado)
            - **Eixo Y**: Casos acumulados (I + R do modelo SIR)
            
            ### 🔍 **Como interpretar:**
            
            **✅ Bom ajuste (modelo confiável):**
            - Linha azul **passa próxima** aos pontos vermelhos
            - **Tendência geral** é capturada pelo modelo
            - **Não há padrões sistemáticos** nos resíduos
            
            **⚠️ Ajuste questionável:**
            - Linha azul **muito distante** dos pontos
            - **Tendências opostas** (modelo cresce, dados decrescem)
            - **Padrões sistemáticos** (modelo sempre acima ou abaixo)
            
            **🧮 Métricas de qualidade:**
            - **MSE baixo** (< 10% da variância dos dados)
            - **Curva suave** sem oscilações bruscas
            - **Biologicamente plausível** (sem crescimento exponencial infinito)
            
            ---
            
            ## 📈 **Gráfico 2: Evolução das Populações S-I-R**
            
            ### 🎯 **O que mostra:**
            - **Verde (S)** 🟢: População **Suscetível** ao longo do tempo
            - **Vermelho (I)** 🔴: População **Infectada** ao longo do tempo  
            - **Azul (R)** 🔵: População **Recuperada/Removida** ao longo do tempo
            
            ### 🔍 **Padrões típicos a observar:**
            
            **🟢 Curva S (Suscetíveis):**
            - **Sempre decresce** (nunca aumenta)
            - **Declínio acelerado** durante pico da epidemia
            - **Estabiliza** quando epidemia termina
            - **Formato**: Sigmoide invertida (S de cabeça para baixo)
            
            **🔴 Curva I (Infectados):**
            - **Cresce inicialmente** (fase exponencial)
            - **Atinge um pico** (momento crítico)
            - **Decresce** após o pico (controle da epidemia)
            - **Formato**: Sino (distribuição normal aproximada)
            
            **🔵 Curva R (Recuperados):**
            - **Sempre cresce** (monotônica crescente)
            - **Crescimento acelerado** durante pico
            - **Estabiliza** em valor final (ataque total)
            - **Formato**: Sigmoide (curva S normal)
            
            ### 💡 **Insights epidemiológicos:**
            
            - **Conservação**: S + I + R = N (sempre)
            - **Pico de I**: Momento de máxima pressão no sistema de saúde
            - **Valor final de R**: Total de pessoas que foram infectadas
            - **Valor final de S**: Pessoas que nunca se infectaram
            
            ---
            
            ## 🌡️ **Gráfico 3: Taxa de Infecção ao Longo do Tempo**
            
            ### 🎯 **O que mostra:**
            - **Taxa instantânea** de novas infecções (β × S × I / N)
            - **Velocidade** com que a epidemia se espalha
            - **Derivada** da curva de infectados (dI/dt)
            
            ### 🔍 **Como interpretar:**
            
            **📈 Fase crescente:**
            - **Taxa aumentando**: Epidemia acelerando
            - **Intervenções insuficientes** ou inexistentes
            - **R₀ > 1**: Cada infectado gera > 1 nova infecção
            
            **🏔️ Pico da taxa:**
            - **Momento de máxima transmissão**
            - **Ponto de inflexão** da curva epidêmica
            - **Pressão máxima** no sistema de saúde
            
            **📉 Fase decrescente:**
            - **Taxa diminuindo**: Epidemia desacelerando
            - **Intervenções efetivas** ou esgotamento de suscetíveis
            - **R₀ < 1**: Cada infectado gera < 1 nova infecção
            
            ### 💡 **Aplicações práticas:**
            - **Planejamento**: Estimar quando haverá pico de demanda
            - **Intervenções**: Identificar momentos críticos
            - **Avaliação**: Medir efetividade de medidas de controle
            
            ---
            
            ## 🔄 **Gráfico 4: Fase Portrait (S vs I)**
            
            ### 🎯 **O que mostra:**
            - **Trajetória dinâmica** no espaço de fases (S, I)
            - **Relação** entre suscetíveis e infectados
            - **Evolução temporal** como curva paramétrica
            
            ### 🔍 **Interpretação da trajetória:**
            
            **🚀 Início** (canto superior direito):
            - **Muitos suscetíveis** (S alto)
            - **Poucos infectados** (I baixo)
            - **Início da epidemia**
            
            **📈 Crescimento** (movimento para cima e esquerda):
            - **S diminui** (pessoas se infectando)
            - **I aumenta** (epidemia crescendo)
            - **Fase exponencial**
            
            **🏔️ Pico** (ponto mais alto da curva):
            - **Máximo de infectados**
            - **S ainda significativo**
            - **Ponto de inflexão**
            
            **📉 Declínio** (movimento para baixo e esquerda):
            - **I diminui** (pessoas se recuperando)
            - **S continua diminuindo** (mas mais lentamente)
            - **Epidemia em controle**
            
            **🏁 Final** (canto inferior esquerdo):
            - **Poucos suscetíveis** restantes
            - **Poucos infectados** restantes
            - **Epidemia extinta**
            
            ### 💡 **Formato característico:**
            - **"Joelho invertido"**: Típico do modelo SIR
            - **Movimento unidirecional**: Tempo sempre avança
            - **Área sob a curva**: Relacionada ao R₀
            
            ### 🔬 **Usos científicos:**
            - **Comparar epidemias**: Diferentes trajetórias
            - **Identificar padrões**: Formato da curva
            - **Validar modelos**: Consistência física
            """)
            
            st.markdown("---")
            st.markdown("""
            ## 🎯 **Como Usar Essas Informações na Prática:**
            
            ### 👩‍⚕️ **Para Profissionais de Saúde:**
            - **Gráfico 1**: Valide se o modelo é confiável para sua região
            - **Gráfico 2**: Identifique quando haverá pico de casos
            - **Gráfico 3**: Planeje recursos para momentos de alta transmissão
            - **Gráfico 4**: Compare diferentes cenários epidemiológicos
            
            ### 👨‍💼 **Para Gestores Públicos:**
            - **Timing de intervenções**: Use o pico previsto para planejar
            - **Dimensionamento**: Estime quantos serão infectados (R final)
            - **Monitoramento**: Compare realidade com previsões
            - **Comunicação**: Explique à população o que esperar
            
            ### 👩‍🎓 **Para Pesquisadores:**
            - **Validação**: Verifique se R₀ é biologicamente plausível
            - **Comparação**: Analise diferenças entre regiões/períodos
            - **Incerteza**: Considere limitações dos dados
            - **Refinamento**: Use para orientar modelos mais complexos
            """)
    
    # Análise de sensibilidade
    st.subheader("🎚️ **Análise de Sensibilidade**")
    
    fig_sensitivity = create_sir_sensitivity_analysis(fit_result)
    if fig_sensitivity:
        st.plotly_chart(fig_sensitivity, use_container_width=True)
        
        with st.expander("🔍 **Entenda a Análise de Sensibilidade - Guia Completo**"):
            st.markdown("""
            ## 🎚️ **O que é Análise de Sensibilidade?**
            
            A **análise de sensibilidade** é uma técnica estatística que **quantifica como incertezas nos parâmetros 
            de entrada se propagam para as previsões do modelo**. É essencial para entender a **robustez** e 
            **confiabilidade** dos resultados.
            
            ### 🔬 **Por que é Importante?**
            
            1. **📊 Quantificar incerteza**: Dados reais têm ruído e limitações
            2. **🎯 Identificar parâmetros críticos**: Quais têm maior impacto?
            3. **🛡️ Avaliar robustez**: Previsões são estáveis ou frágeis?
            4. **📋 Orientar coleta de dados**: Onde melhorar a qualidade dos dados?
            5. **⚠️ Comunicar limitações**: Ser transparente sobre incertezas
            
            ### 📈 **Metodologia Utilizada:**
            
            **Variação percentual sistemática:**
            - **Valores testados**: -30%, -20%, -10%, 0%, +10%, +20%, +30%
            - **Parâmetro base**: Valor estimado pelo ajuste
            - **Cenários**: 7 variações para cada parâmetro (β e γ)
            - **Análise**: Como cada variação afeta o pico de infectados
            
            ---
            
            ## 📊 **Gráfico 1: Sensibilidade ao β (Taxa de Transmissão)**
            
            ### 🎯 **O que o β representa:**
            - **Definição**: Probabilidade de transmissão por contato
            - **Fatores**: Virulência, comportamento social, densidade populacional
            - **Intervenções que afetam β**: Distanciamento, máscaras, higiene
            
            ### 🔍 **Padrões esperados:**
            
            **📈 Aumento do β (+10%, +20%, +30%):**
            - **Pico maior**: Mais pessoas infectadas simultaneamente
            - **Pico mais precoce**: Epidemia acelera
            - **R₀ maior**: Transmissão mais eficiente
            - **Curva mais acentuada**: Crescimento/declínio mais rápido
            
            **📉 Diminuição do β (-10%, -20%, -30%):**
            - **Pico menor**: Menos pessoas infectadas simultaneamente  
            - **Pico mais tardio**: Epidemia desacelera
            - **R₀ menor**: Transmissão menos eficiente
            - **Curva mais suave**: Crescimento/declínio mais lento
            
            ### 💡 **Interpretações práticas:**
            
            **🚨 Alta sensibilidade ao β (curvas muito diferentes):**
            - **Significa**: Pequenas mudanças em comportamento → grandes impactos
            - **Implicação**: Intervenções de distanciamento são muito efetivas
            - **Ação**: Focar em medidas que reduzam transmissão
            
            **🛡️ Baixa sensibilidade ao β (curvas similares):**
            - **Significa**: Mudanças em comportamento → impactos moderados
            - **Implicação**: Outros fatores dominam a dinâmica
            - **Ação**: Considerar intervenções complementares
            
            ---
            
            ## 📊 **Gráfico 2: Sensibilidade ao γ (Taxa de Recuperação)**
            
            ### 🎯 **O que o γ representa:**
            - **Definição**: Taxa de recuperação/remoção
            - **Fatores**: Eficácia do tratamento, qualidade do sistema de saúde
            - **Intervenções que afetam γ**: Novos tratamentos, protocolos clínicos
            
            ### 🔍 **Padrões esperados:**
            
            **📈 Aumento do γ (+10%, +20%, +30%):**
            - **Pico menor**: Recuperação mais rápida → menos acúmulo
            - **Pico mais precoce**: Dinâmica acelerada
            - **R₀ menor**: R₀ = β/γ, então γ maior → R₀ menor
            - **Epidemia mais curta**: Resolução mais rápida
            
            **📉 Diminuição do γ (-10%, -20%, -30%):**
            - **Pico maior**: Recuperação mais lenta → mais acúmulo
            - **Pico mais tardio**: Dinâmica desacelerada  
            - **R₀ maior**: γ menor → R₀ maior
            - **Epidemia mais longa**: Resolução mais demorada
            
            ### 💡 **Interpretações práticas:**
            
            **🚨 Alta sensibilidade ao γ (curvas muito diferentes):**
            - **Significa**: Qualidade do tratamento é crítica
            - **Implicação**: Investir em sistema de saúde é prioritário
            - **Ação**: Melhorar protocolos clínicos e capacidade hospitalar
            
            **🛡️ Baixa sensibilidade ao γ (curvas similares):**
            - **Significa**: Tratamento tem impacto limitado na dinâmica geral
            - **Implicação**: Foco deve ser na prevenção (reduzir β)
            - **Ação**: Priorizar medidas preventivas
            
            ---
            
            ## 🔄 **Como Usar a Análise de Sensibilidade:**
            
            ### 📊 **1. Avaliação da Qualidade do Modelo:**
            
            **✅ Modelo robusto:**
            - **Variações pequenas** nos parâmetros → **mudanças proporcionais** nas previsões
            - **Tendências consistentes** (sempre na mesma direção)
            - **Curvas suaves** sem comportamentos erráticos
            
            **⚠️ Modelo instável:**
            - **Variações pequenas** → **mudanças dramáticas** nas previsões
            - **Comportamentos contraditórios** (parâmetro aumenta, efeito diminui)
            - **Curvas com oscilações** ou descontinuidades
            
            ### 📋 **2. Planejamento de Cenários:**
            
            **🎯 Cenário otimista** (β baixo, γ alto):
            - **Use** para **limite inferior** de recursos necessários
            - **Representa** intervenções efetivas + tratamento melhorado
            
            **⚠️ Cenário pessimista** (β alto, γ baixo):
            - **Use** para **limite superior** de recursos necessários  
            - **Representa** sem intervenções + sistema de saúde sobrecarregado
            
            **📊 Cenário central** (valores ajustados):
            - **Use** para **planejamento base**
            - **Representa** condições atuais continuando
            
            ### 🎛️ **3. Identificação de Prioridades:**
            
            **Se β tem maior impacto:**
            - **Priorize**: Medidas de prevenção e controle de transmissão
            - **Exemplos**: Distanciamento, máscaras, higiene, vacinação
            
            **Se γ tem maior impacto:**
            - **Priorize**: Melhoria do sistema de saúde e tratamentos
            - **Exemplos**: Mais leitos, protocolos clínicos, medicamentos
            
            ### 📈 **4. Comunicação de Incertezas:**
            
            **Para gestores:**
            - **"O pico pode variar entre X e Y casos, dependendo das medidas adotadas"**
            - **Mostrar faixa de valores** ao invés de número único
            
            **Para o público:**
            - **"Se mantivermos as medidas atuais, esperamos..."**
            - **"Se relaxarmos muito cedo, poderemos ter..."**
            
            ### ⚡ **Limitações da Análise:**
            
            - **Variações independentes**: Na realidade, β e γ podem estar correlacionados
            - **Linearidade assumida**: Efeitos podem não ser lineares  
            - **Parâmetros constantes**: Na realidade, podem variar no tempo
            - **Modelo simplificado**: SIR ignora muitas complexidades reais
            """)
            
            st.markdown("---")
            st.markdown("""
            ## 🎯 **Conclusão Prática:**
            
            A análise de sensibilidade **não é apenas um exercício acadêmico** - é uma ferramenta essencial para:
            
            1. **🎯 Tomar decisões informadas** com base em intervalos de confiança
            2. **📊 Comunicar incertezas** de forma transparente
            3. **🛡️ Preparar-se para múltiplos cenários** 
            4. **🔍 Identificar onde melhorar** a qualidade dos dados
            5. **⚙️ Orientar o desenvolvimento** de modelos mais sofisticados
            
            **💡 Lembre-se**: "Todos os modelos estão errados, mas alguns são úteis" - George Box
            """)
    
    # Limitações e considerações
    st.markdown("---")
    st.subheader("⚠️ **Limitações e Considerações Importantes**")
    
    st.markdown("""
    ### 🚫 **Limitações do Modelo SIR:**
    
    1. **📊 Simplicidade**: Assume população homogênea e mistura aleatória
    2. **⏱️ Parâmetros constantes**: β e γ assumidos constantes no tempo
    3. **🚫 Sem reinfecção**: Assume imunidade permanente após recuperação
    4. **👥 População fechada**: Não considera nascimentos, mortes ou migração
    5. **📈 Dados limitados**: Qualidade dos ajustes depende da qualidade dos dados
    
    ### ✅ **Pontos Fortes:**
    
    1. **🎯 Simplicidade**: Fácil de entender e implementar
    2. **📚 Base teórica**: Fundamentação matemática sólida
    3. **🔍 Insights qualitativos**: Revela dinâmicas epidemiológicas fundamentais
    4. **⚡ Rapidez**: Permite análises rápidas para tomada de decisão
    
    ### 💡 **Recomendações para Uso:**
    
    - Use para **análises exploratórias** e **compreensão de tendências**
    - **Combine com outros modelos** mais complexos quando disponível
    - **Valide constantemente** com dados novos
    - **Considere fatores externos** (sazonalidade, intervenções, etc.)
    """)
    
    # Dados utilizados
    st.markdown("---")
    st.subheader("📋 **Dados Utilizados na Modelagem**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Resumo dos Dados:**")
        st.write(f"- **Região:** {regiao_selecionada}")
        st.write(f"- **Período:** {ano_inicio} - {df_filtrado['ano'].max()}")
        st.write(f"- **Total de casos:** {df_filtrado['casos'].sum():,}")
        st.write(f"- **População estimada:** {populacao:,}")
        st.write(f"- **Anos analisados:** {len(df_filtrado)}")
    
    with col2:
        st.markdown("**📈 Dados por Ano:**")
        st.dataframe(
            df_filtrado[['ano', 'casos']].rename(columns={'ano': 'Ano', 'casos': 'Casos'}),
            hide_index=True
        )

if __name__ == "__main__":
    # Para teste independente
    st.set_page_config(page_title="Modelagem SIR", layout="wide")
    show_sir_modeling({})
