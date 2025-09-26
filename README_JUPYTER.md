# 🦠 Dashboard IMUNOPREVINIVEIS - Versão Jupyter Notebook

Esta é uma versão adaptada do dashboard Streamlit para funcionar em Jupyter Notebook, oferecendo uma experiência interativa e flexível para análise de dados de meningite no Brasil.

## 🚀 Características

- **📊 Análises Interativas** - Execute células individualmente
- **🎯 Widgets Interativos** - Navegação por dropdown
- **📈 Visualizações Plotly** - Gráficos interativos inline
- **🔧 Flexível** - Modifique análises facilmente
- **📝 Reproduzível** - Salve e compartilhe o notebook

## 📋 Funcionalidades Disponíveis

- 🏠 **Visão Geral 2024** - Dados gerais, sorogrupos e etiologia
- 📊 **Análise de Casos** - Evolução temporal e distribuição geográfica
- 🦠 **Análise de Sorogrupos** - Distribuição e tendências
- 🔬 **Análise de Etiologia** - Causas e padrões
- 💉 **Análise de Imunização** - Cobertura vacinal e efetividade
- 🗺️ **Análise Regional** - Comparações entre regiões
- 👶 **Faixa Etária** - Análises por idade
- 🔬 **Análises Avançadas** - Estatísticas e modelagem
- 🦠 **Análise Epidemiológica** - Indicadores epidemiológicos
- ⚡ **Taxa de Ataque** - Cálculos epidemiológicos
- 🧮 **Modelagem SIR** - Modelos epidemiológicos
- 🔍 **Exploração Livre** - Análises customizadas
- 📋 **Relatórios** - Geração de relatórios
- ⚙️ **Expositivo Técnico** - Documentação técnica

## 🛠️ Instalação

### 1. Instalar Dependências

```bash
# Instalar dependências específicas para Jupyter
pip install -r requirements_jupyter.txt

# Ou instalar manualmente
pip install pandas numpy matplotlib seaborn plotly scikit-learn scipy jupyter ipywidgets
```

### 2. Executar o Notebook

```bash
# Iniciar Jupyter Notebook
jupyter notebook

# Ou usar JupyterLab
jupyter lab
```

### 3. Abrir o Dashboard

1. Abra o arquivo `dashboard_jupyter.ipynb`
2. Execute as células em ordem sequencial
3. Use o widget de navegação para explorar as seções

## 📖 Como Usar

### Execução Sequencial

1. **Primeira célula** - Importações e configurações
2. **Segunda célula** - Carregamento de dados
3. **Terceira célula** - Widget de navegação
4. **Demais células** - Funções de análise

### Navegação

- Use o **dropdown** para selecionar a seção desejada
- Os gráficos são **interativos** (zoom, pan, hover)
- Execute células **individualmente** conforme necessário

### Personalização

Para adicionar novas seções:

1. **Importe funções** dos módulos `app_sections/`
2. **Adapte código Streamlit** para Jupyter:
   - `st.write()` → `print()`
   - `st.plotly_chart()` → `fig.show()`
   - `st.selectbox()` → `widgets.Dropdown()`
3. **Adicione ao widget** de navegação

## 🔄 Diferenças da Versão Streamlit

| Aspecto | Streamlit | Jupyter |
|---------|-----------|---------|
| **Interface** | Web app | Notebook |
| **Navegação** | Sidebar | Dropdown widget |
| **Execução** | Servidor | Células |
| **Interatividade** | Automática | Manual |
| **Compartilhamento** | URL | Arquivo .ipynb |
| **Desenvolvimento** | Deploy | Local |

## 📊 Dados Utilizados

O notebook utiliza os mesmos dados da versão Streamlit:

- **TABELAS/** - Arquivos CSV principais
- **data/processed/** - Dados processados
- **22 arquivos CSV** essenciais

## 🎯 Vantagens do Jupyter

### Para Pesquisa
- ✅ **Análise exploratória** detalhada
- ✅ **Experimentos** com diferentes parâmetros
- ✅ **Documentação** integrada com código
- ✅ **Reproduzibilidade** científica

### Para Desenvolvimento
- ✅ **Prototipagem** rápida
- ✅ **Debugging** facilitado
- ✅ **Versionamento** com Git
- ✅ **Colaboração** em equipe

### Para Apresentação
- ✅ **Relatórios** interativos
- ✅ **Visualizações** inline
- ✅ **Exportação** para PDF/HTML
- ✅ **Compartilhamento** fácil

## 🔧 Troubleshooting

### Problemas Comuns

1. **Widgets não aparecem**
   ```bash
   jupyter nbextension enable --py widgetsnbextension
   ```

2. **Plotly não renderiza**
   ```python
   import plotly.io as pio
   pio.renderers.default = "notebook"
   ```

3. **Dados não carregam**
   - Verifique se os arquivos CSV estão na pasta `TABELAS/`
   - Execute as células em ordem

4. **Dependências faltando**
   ```bash
   pip install -r requirements_jupyter.txt
   ```

## 📝 Exemplo de Uso

```python
# Executar análise específica
show_overview_2024(dados)

# Explorar dados diretamente
dados['casos_consolidados'].head()

# Criar visualização customizada
import plotly.express as px
fig = px.bar(dados['sorogrupos_2024'], x='Sorogrupo', y='Casos')
fig.show()
```

## 🤝 Contribuição

Para contribuir com novas funcionalidades:

1. **Fork** o repositório
2. **Crie** nova seção no notebook
3. **Teste** a funcionalidade
4. **Documente** o código
5. **Submeta** pull request

## 📄 Licença

Este projeto segue a mesma licença do projeto principal IMUNOPREVINIVEIS.

---

**🎯 Dashboard IMUNOPREVINIVEIS - Versão Jupyter Notebook**  
*Análise interativa de dados de meningite no Brasil*
