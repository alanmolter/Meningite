# 📊 PASTA TABELAS - Central de Dados

Esta pasta centraliza **TODOS** os arquivos CSV de dados utilizados para análise de meningite no Brasil.

## 🎯 Propósito

A pasta `TABELAS` é o **único local** onde devem estar todos os arquivos CSV com dados para análise. Quando você quiser adicionar novos dados, simplesmente cole os arquivos CSV nesta pasta.

## 📁 Arquivos Atuais

### 📊 Dados de Casos
- `df_casos_notificados_2017_2022.csv` - Casos notificados por ano (2017-2022)
- `df_geral_2024.csv` - Dados gerais de 2024 (casos, óbitos, incidência, etc.)
- `casos_consolidados_2017_2024.csv` - Casos consolidados (2017-2024)

### 🦠 Dados de Sorogrupos
- `df_sorogrupos_2007_2020.csv` - Dados históricos de sorogrupos (2007-2020)
- `df_sorogrupos_2024.csv` - Dados de sorogrupos de 2024
- `df_sorogrupos_completo.csv` - Dados completos de sorogrupos
- `sorogrupos_consolidados_2007_2024.csv` - Sorogrupos consolidados (2007-2024)

### 🧬 Dados de Etiologia
- `df_etiologia_2024.csv` - Etiologia de 2024
- `df_bacterianas_2024.csv` - Dados bacterianos de 2024
- `df_letalidade_2007_2020.csv` - Letalidade por etiologia (2007-2020)
- `etiologias_consolidadas_2007_2024.csv` - Etiologias consolidadas (2007-2024)

### 💉 Dados de Imunização
- `data_meninatu.csv` - Dados de imunização por ano, faixa etária, sorogrupo e UF
- `imunizacao_por_ano.csv` - Imunização processada por ano
- `imunizacao_por_faixa_etaria.csv` - Imunização processada por faixa etária
- `imunizacao_por_sorogrupo.csv` - Imunização processada por sorogrupo
- `imunizacao_por_uf.csv` - Imunização processada por UF
- `doses_todosimunosate2022.csv` - Doses de todos os imunobiológicos até 2022
- `imunobiologicosem2023a2025.csv` - Imunobiológicos de 2023 a 2025

### 🏥 Dados de Hospitalização
- `sih_meningite_hospitalar.csv` - Dados de hospitalização por meningite
- `sih_meningite_long.csv` - Dados de hospitalização em formato longo
- `sih_meningite_wide.csv` - Dados de hospitalização em formato largo

### 📋 Outros Dados
- `tabela_unificada.csv` - Tabela unificada com diversos dados
- `dados_imunizacao_processados.csv` - Dados de imunização processados

## ➕ Como Adicionar Novos Dados

### Método 1: Copiar e Colar
1. Cole o arquivo CSV diretamente na pasta `TABELAS`
2. Execute o script `manage_tabelas.py` para validar o arquivo

### Método 2: Usar o Script de Gerenciamento
```bash
python manage_tabelas.py
```
- Escolha a opção 2 "Adicionar novo arquivo CSV"
- Forneça o caminho do arquivo
- O script validará e copiará automaticamente

## 🔍 Validação de Dados

Para validar todos os arquivos na pasta:
```bash
python manage_tabelas.py
```
- Escolha a opção 3 "Validar dados"

## 📊 Visualização dos Dados

Para ver um resumo de todos os arquivos:
```bash
python manage_tabelas.py
```
- Escolha a opção 4 "Criar resumo"

## ⚠️ Importante

- **NUNCA** delete arquivos desta pasta sem verificar se são utilizados
- **SEMPRE** valide novos arquivos antes de usar
- **MANTENHA** a estrutura de colunas consistente
- **USE** nomes descritivos para os arquivos

## 🔄 Processamento

Após adicionar novos dados:
1. Execute `python process_new_data.py` para processar os novos dados
2. Execute `python update_dashboard_with_new_data.py` para atualizar o dashboard
3. Execute `python run_dashboard.py` para visualizar os resultados

## 📞 Suporte

Se encontrar problemas:
1. Verifique se o arquivo CSV está no formato correto
2. Execute a validação com `manage_tabelas.py`
3. Consulte os logs de processamento
4. Verifique se as colunas estão nomeadas corretamente

---

**Última atualização**: $(Get-Date -Format "dd/MM/yyyy HH:mm")
**Total de arquivos**: $(Get-ChildItem -Filter "*.csv" | Measure-Object | Select-Object -ExpandProperty Count)
