# Guia Completo de Deployment - Dashboard IMUNOPREVINIVEIS Brasil

## 📋 Índice
1. [Como a Aplicação Funciona Localmente](#como-a-aplicação-funciona-localmente)
2. [Arquitetura do Projeto](#arquitetura-do-projeto)
3. [Deployment em Servidor Institucional](#deployment-em-servidor-institucional)
4. [Requisitos de Sistema](#requisitos-de-sistema)
5. [Configuração de Segurança](#configuração-de-segurança)
6. [Manutenção e Atualizações](#manutenção-e-atualizações)

---Todas as tecnologias e implementações nescessarias para o deploy da aplicação no SERVIDOR se encontram na seção REQUISITOS DO SISTEMA.

## 🏠 Como a Aplicação Funciona Localmente

### O que é o Streamlit?
O **Streamlit** é uma biblioteca Python que permite criar aplicações web interativas diretamente a partir de código Python. Ele é especialmente útil para dashboards de dados, visualizações científicas e aplicações de análise.

### Como Funciona o Desenvolvimento Local?

#### 1. **Ambiente Virtual Python**
- Um **ambiente virtual** é como uma "caixa isolada" onde instalamos apenas as bibliotecas necessárias para este projeto
- Evita conflitos com outras versões de Python ou bibliotecas do sistema
- No projeto: pasta `.venv/` contém este ambiente isolado

#### 2. **Execução da Aplicação**
```bash
# Ativar o ambiente virtual
.venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
source .venv/bin/activate    # Linux/Mac

# Verificar versão do Python
python --version  # Deve mostrar Python 3.13.7 ou superior

# Executar a aplicação
streamlit run app/main.py
```

#### 3. **O que Acontece Quando Executamos?**
1. **Streamlit inicia um servidor web local** na sua máquina
2. **Compila o código Python** em uma interface web
3. **Abre automaticamente o navegador** no endereço `http://localhost:8501`
4. **Mantém o servidor rodando** enquanto você desenvolve

#### 4. **O que é Localhost e Por que Não é Acessível pela Internet?**

##### **O que é Localhost?**
- **Localhost** = "esta máquina" (127.0.0.1)
- **Porta 8501** = "canal de comunicação" específico
- **http://localhost:8501** = endereço para acessar a aplicação rodando na SUA máquina

##### **Por que Localhost Não é Acessível pela Internet?**
```
Internet → Roteador → Sua Máquina (localhost:8501)
    ❌     ❌         ✅ (apenas você)
```

**1. Endereço IP Privado:**
- **127.0.0.1** é um endereço IP **reservado** e **privado**
- Significa literalmente "esta máquina aqui"
- Não é roteável pela internet

**2. Roteamento de Rede:**
- **Internet pública** não sabe onde está o endereço 127.0.0.1
- Cada pessoa tem seu próprio 127.0.0.1 (sua própria máquina)
- É como um "endereço interno" que só funciona na sua casa

**3. Firewall e Segurança:**
- **Roteadores domésticos** bloqueiam conexões externas por padrão
- **ISP (provedor de internet)** não encaminha tráfego para 127.0.0.1
- **Sua máquina** não está configurada para aceitar conexões externas

**4. Analogia Simples:**
- **Localhost** = endereço da sua casa (só você sabe onde fica)
- **Internet** = cidade grande (não sabe onde fica sua casa)
- **Servidor** = endereço público com placa na rua (todos podem encontrar)

#### 5. **Fluxo de Funcionamento Local**
```
Seu Código Python → Streamlit → Servidor Local → Navegador
     ↓
app/main.py → Interface Web → http://localhost:8501 → Dashboard
```

---

## 🏗️ Arquitetura do Projeto

### Estrutura de Pastas
```
imunopreviniveis/
├── app/                          # Aplicação principal
│   ├── __init__.py              # Torna a pasta um pacote Python
│   └── main.py                  # Arquivo principal da aplicação
├── app_sections/                 # Módulos organizados por funcionalidade
│   ├── __init__.py              # Pacote de seções
│   ├── overview.py              # Visão geral dos dados
│   ├── cases.py                 # Análise de casos
│   ├── sorogrupos.py            # Análise de sorogrupos
│   ├── etiologia.py             # Análise de etiologia
│   ├── imunizacao.py            # Análise de imunização
│   ├── regional.py              # Análise regional
│   ├── advanced.py              # Análises avançadas
│   ├── epidemiologica.py        # Análise epidemiológica
│   ├── attack_rate.py           # Taxa de ataque
│   ├── sir_modeling.py          # Modelagem SIR
│   ├── explore.py               # Exploração livre dos dados
│   ├── reports.py               # Geração de relatórios
│   └── technical.py             # Documentação técnica
├── data/                        # Dados processados
│   └── processed/               # Arquivos CSV processados
├── TABELAS/                     # Dados brutos e consolidados
├── dashboard_completo_v2.py     # Lógica principal e funções
├── requirements.txt             # Dependências Python
└── .venv/                       # Ambiente virtual
```

### Como a Arquitetura Funciona

#### 1. **Padrão Modular**
- **`main.py`**: Orquestrador principal - define a interface e navegação
- **`app_sections/`**: Cada arquivo representa uma funcionalidade específica
- **`dashboard_completo_v2.py`**: Motor de dados - carrega e processa informações

#### 2. **Fluxo de Dados**
```
Dados CSV → dashboard_completo_v2.py → app_sections/ → main.py → Interface Web
```

#### 3. **Separação de Responsabilidades**
- **Dados**: Pastas `data/` e `TABELAS/`
- **Lógica**: `dashboard_completo_v2.py`
- **Interface**: `app_sections/` + `main.py`
- **Configuração**: `requirements.txt` + `.venv/`

#### 4. **Sistema de Navegação**
- **Sidebar**: Menu lateral com todas as seções disponíveis
- **Tabs**: Cada seção é carregada dinamicamente
- **Estado**: Streamlit mantém o estado entre navegações

---

## 🌐 Deployment em Servidor Institucional

### O que é Deployment?
**Deployment** é o processo de colocar uma aplicação rodando localmente em um servidor para que outras pessoas possam acessá-la pela internet.

### Por que Precisamos de um Servidor?

#### **Problemas do Desenvolvimento Local:**
- ❌ **Apenas você pode acessar** (localhost)
- ❌ **Aplicação para quando você desliga o computador**
- ❌ **Recursos limitados** da sua máquina
- ❌ **Sem controle de acesso** ou segurança

#### **Soluções do Servidor:**
- ✅ **Acesso público**: Qualquer pessoa pode acessar via internet
- ✅ **Disponibilidade 24/7**: Aplicação sempre disponível
- ✅ **Recursos compartilhados**: Múltiplos usuários simultâneos
- ✅ **Segurança institucional**: Controle de acesso e backup

#### **Como o Servidor Resolve o Problema do Localhost:**

**1. Endereço IP Público:**
```
Internet → Servidor (IP Público: 200.150.100.50) → Aplicação (Porta 8501)
    ✅         ✅                                    ✅
```

- **Servidor** tem um **IP público** visível na internet
- **DNS** converte `imunopreviniveis.fiocruz.br` → `200.150.100.50`
- **Qualquer pessoa** pode encontrar o endereço

**2. Roteamento de Rede:**
- **Internet pública** sabe onde está o servidor
- **Roteadores** encaminham tráfego para o IP correto
- **Firewall** permite conexões na porta 80/443 (HTTP/HTTPS)

**3. Configuração de Rede:**
- **Servidor** está configurado para aceitar conexões externas
- **Nginx** recebe requisições e encaminha para Streamlit
- **Port forwarding** direciona tráfego para a aplicação

**4. Analogia com Servidor:**
- **Servidor** = loja na rua principal com placa visível
- **IP público** = endereço da loja (Rua das Flores, 123)
- **DNS** = placa da loja ("IMUNOPREVINIVEIS")
- **Internet** = todos os clientes podem encontrar a loja

### Cenário: Fiocruz Rio de Janeiro

#### 1. **Infraestrutura Necessária**
```
Internet → Firewall → Load Balancer → Servidor Web → Aplicação Streamlit
```

#### 2. **Componentes do Sistema**
- **Servidor Web**: Máquina física ou virtual rodando Linux
- **Proxy Reverso**: Nginx ou Apache (gerencia requisições)
- **Process Manager**: Supervisor ou systemd (mantém aplicação rodando)
- **Banco de Dados**: PostgreSQL ou MySQL (se necessário)
- **Monitoramento**: Logs, métricas de performance

---

## 💻 Requisitos de Sistema

### Versões do Python e Compatibilidade

#### **Python 3.12+ (Recomendado)**
- **Versão atual do projeto**: Python 3.13.7
- **Versão mínima suportada**: Python 3.10
- **Versão recomendada para produção**: Python 3.12 LTS
- **Por que Python 3.12+?**
  - Suporte estendido até 2028
  - Melhor performance e otimizações
  - Compatibilidade com bibliotecas modernas
  - Correções de segurança

#### **Compatibilidade de Bibliotecas**
- **Streamlit**: 1.28.0+ (requer Python 3.8+)
- **Pandas**: 2.0.0+ (requer Python 3.9+)
- **NumPy**: 1.24.0+ (requer Python 3.9+)
- **Plotly**: 5.15.0+ (requer Python 3.8+)

### Servidor de Produção

#### **Especificações Mínimas**
- **CPU**: 4 cores (Intel i5 ou AMD Ryzen 5)
- **RAM**: 8GB DDR4
- **Armazenamento**: 100GB SSD
- **Sistema Operacional**: Ubuntu 22.04 LTS ou Rocky Linux 9

#### **Especificações Recomendadas**
- **CPU**: 8 cores (Intel i7 ou AMD Ryzen 7)
- **RAM**: 16GB DDR5
- **Armazenamento**: 500GB SSD NVMe
- **Sistema Operacional**: Ubuntu 24.04 LTS ou Rocky Linux 9

#### **Software Necessário**
```bash
# Sistema base
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
sudo apt install nginx supervisor

# Python e dependências
python3.12 -m venv /opt/meningite/venv
source /opt/meningite/venv/bin/activate
pip install -r requirements.txt
```

### Rede e Conectividade

#### **Configuração de Rede**
- **IP Público**: Endereço visível na internet
- **Porta 80/443**: HTTP/HTTPS padrão
- **Firewall**: Regras para permitir tráfego web
- **DNS**: Nome de domínio (ex: meningite.fiocruz.br)

#### **Segurança de Rede**
- **SSL/TLS**: Certificado para HTTPS
- **Rate Limiting**: Proteção contra ataques
- **IP Whitelist**: Restrição de acesso se necessário

---

## 🔒 Configuração de Segurança

### 1. **Usuários e Permissões**
```bash
# Criar usuário específico para a aplicação
sudo useradd -m -s /bin/bash imunopreviniveis
sudo usermod -aG www-data imunopreviniveis

# Definir permissões
sudo chown -R imunopreviniveis:www-data /opt/imunopreviniveis/
sudo chmod -R 755 /opt/imunopreviniveis/
```

### 2. **Configuração do Nginx**
```nginx
# /etc/nginx/sites-available/imunopreviniveis
server {
    listen 80;
    server_name imunopreviniveis.fiocruz.br;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 3. **Configuração do Supervisor**
```ini
# /etc/supervisor/conf.d/imunopreviniveis.conf
[program:imunopreviniveis]
command=/opt/imunopreviniveis/venv/bin/streamlit run /opt/imunopreviniveis/app/main.py --server.port 8501 --server.address 127.0.0.1
directory=/opt/imunopreviniveis
user=imunopreviniveis
autostart=true
autorestart=true
stderr_logfile=/var/log/imunopreviniveis/err.log
stdout_logfile=/var/log/imunopreviniveis/out.log
```

### 4. **Firewall e Segurança**
```bash
# Configurar UFW (Uncomplicated Firewall)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

---

## 🚀 Processo de Deployment

### Passo a Passo Completo

#### **1. Preparação do Servidor**
```bash
# Conectar via SSH
ssh usuario@servidor.fiocruz.br

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install python3.9 python3.9-venv python3-pip nginx supervisor
```

#### **2. Configuração do Ambiente Python**
```bash
# Criar diretório da aplicação
sudo mkdir -p /opt/imunopreviniveis
sudo chown $USER:$USER /opt/imunopreviniveis

# Copiar código do projeto
scp -r ./* usuario@servidor:/opt/imunopreviniveis/

# Criar ambiente virtual
cd /opt/imunopreviniveis
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### **3. Configuração dos Serviços**
```bash
# Configurar Nginx
sudo ln -s /etc/nginx/sites-available/imunopreviniveis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Configurar Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start imunopreviniveis
```

#### **4. Teste e Validação**
```bash
# Verificar status dos serviços
sudo systemctl status nginx
sudo supervisorctl status imunopreviniveis

# Verificar logs
sudo tail -f /var/log/imunopreviniveis/out.log
sudo tail -f /var/log/nginx/error.log

# Verificar versão do Python
python3 --version
pip list | grep -E "(streamlit|pandas|numpy|plotly)"
```

---

## 🛠️ Manutenção e Atualizações

### 🔑 Acesso Remoto ao Servidor (De Casa)

#### **1. Configuração Inicial de Acesso SSH**

##### **Passo 1: Gerar Chave SSH na Sua Máquina**
```bash
# No seu computador de casa (Windows PowerShell ou Linux/Mac)
ssh-keygen -t rsa -b 4096 -C "seu.email@fiocruz.br"

# A chave será salva em:
# Windows: C:\Users\seu_usuario\.ssh\id_rsa
# Linux/Mac: ~/.ssh/id_rsa
```

##### **Passo 2: Adicionar Chave ao Servidor**
```bash
# Copiar sua chave pública para o servidor
ssh-copy-id seu_usuario@servidor.fiocruz.br

# Ou manualmente:
# 1. Copiar conteúdo de ~/.ssh/id_rsa.pub
# 2. Adicionar ao arquivo ~/.ssh/authorized_keys no servidor
```

##### **Passo 3: Testar Conexão**
```bash
# Conectar ao servidor
ssh seu_usuario@servidor.fiocruz.br

# Se funcionar, você verá o prompt do servidor:
# seu_usuario@servidor:~$
```

#### **2. Acesso Diário ao Projeto**

##### **Conectar ao Servidor**
```bash
# De casa, conecte via SSH
ssh seu_usuario@servidor.fiocruz.br

# Navegar para o projeto
cd /opt/imunopreviniveis

# Ver estrutura do projeto
ls -la
```

##### **Verificar Status da Aplicação**
```bash
# Ver se está rodando
sudo supervisorctl status imunopreviniveis

# Ver logs em tempo real
sudo tail -f /var/log/imunopreviniveis/out.log

# Ver uso de recursos
htop
```

#### **3. Trabalhando com o Código**

##### **Editar Arquivos Diretamente no Servidor**
```bash
# Usar editor de texto (nano, vim, ou instalar code)
sudo apt install nano vim

# Editar arquivo principal
nano app/main.py

# Ou instalar Visual Studio Code no servidor
sudo snap install code --classic
code app/main.py
```

##### **Sincronizar Código com Seu Computador**
```bash
# Opção 1: Usar rsync para sincronizar
rsync -avz --delete seu_usuario@servidor.fiocruz.br:/opt/imunopreviniveis/ ./imunopreviniveis_local/

# Opção 2: Usar Git (recomendado)
# No servidor:
cd /opt/imunopreviniveis
git init
git add .
git commit -m "Versão inicial"

# No seu computador:
git clone ssh://seu_usuario@servidor.fiocruz.br/opt/imunopreviniveis
```

#### **4. Fluxo de Desenvolvimento Remoto**

##### **Ciclo de Desenvolvimento**
```bash
# 1. Conectar ao servidor
ssh seu_usuario@servidor.fiocruz.br

# 2. Fazer alterações no código
cd /opt/imunopreviniveis
nano app/main.py

# 3. Testar alterações
sudo supervisorctl restart imunopreviniveis

# 4. Verificar se funcionou
sudo supervisorctl status imunopreviniveis

# 5. Ver logs para debug
sudo tail -f /var/log/imunopreviniveis/out.log
```

##### **Sincronização Bidirecional**
```bash
# Do servidor para seu computador
scp -r seu_usuario@servidor.fiocruz.br:/opt/imunopreviniveis/app/ ./app_servidor/

# Do seu computador para o servidor
scp -r ./app/ seu_usuario@servidor.fiocruz.br:/opt/imunopreviniveis/
```

#### **2. Scripts de Deploy Automatizado**
```bash
#!/bin/bash
# deploy.sh
cd /opt/imunopreviniveis
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart imunopreviniveis
```

#### **3. Adicionando Novas Funcionalidades**

##### **Passo 1: Criar Nova Seção**
```bash
# No servidor, criar novo arquivo
cd /opt/imunopreviniveis/app_sections
nano nova_analise.py

# Estrutura básica para nova seção:
import streamlit as st
from typing import Dict, Any

def show_nova_analise(dados: Dict[str, Any]) -> None:
    st.title("🔬 Nova Análise")
    st.write("Descrição da nova funcionalidade")
    
    # Sua lógica aqui
    st.write("Implementar análise específica...")
```

##### **Passo 2: Integrar ao Menu Principal**
```bash
# Editar main.py para incluir nova seção
nano app/main.py

# Adicionar import:
from app_sections.nova_analise import show_nova_analise

# Adicionar ao menu:
opcao = st.sidebar.selectbox(
    "Selecione a seção:",
    [
        "🏠 Visão Geral 2024",
        "📊 Análise de Casos",
        # ... outras opções ...
        "🔬 Nova Análise",  # NOVA OPÇÃO
    ],
)

# Adicionar lógica de execução:
elif opcao == "🔬 Nova Análise":
    show_nova_analise(dados)
```

##### **Passo 3: Testar e Deploy**
```bash
# Reiniciar aplicação para testar
sudo supervisorctl restart imunopreviniveis

# Verificar se funcionou
sudo supervisorctl status imunopreviniveis

# Ver logs para debug
sudo tail -f /var/log/imunopreviniveis/out.log
```

#### **4. Atualizando Dados**

##### **Adicionar Novos Arquivos CSV**
```bash
# Copiar novos dados para o servidor
scp novo_arquivo.csv seu_usuario@servidor.fiocruz.br:/opt/imunopreviniveis/TABELAS/

# Ou usar rsync para sincronizar pasta inteira
rsync -avz --delete ./TABELAS/ seu_usuario@servidor.fiocruz.br:/opt/imunopreviniveis/TABELAS/
```

##### **Atualizar Código de Processamento**
```bash
# Editar dashboard_completo_v2.py para incluir novos dados
nano dashboard_completo_v2.py

# Adicionar função para carregar novos dados
def load_novos_dados():
    # Sua lógica aqui
    pass

# Integrar na função load_all_data()
```

### Monitoramento

#### **1. Logs e Métricas**
- **Logs da aplicação**: `/var/log/meningite/`
- **Logs do Nginx**: `/var/log/nginx/`
- **Métricas do sistema**: `htop`, `iotop`, `nethogs`

#### **2. Backup e Recuperação**
```bash
# Backup automático diário
0 2 * * * tar -czf /backup/imunopreviniveis-$(date +\%Y\%m\%d).tar.gz /opt/imunopreviniveis/
```

#### **3. Atualizações de Segurança**
```bash
# Atualizações automáticas de segurança
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

#### **4. Atualizações do Python**
```bash
# Verificar versões disponíveis
sudo apt list --upgradable | grep python3

# Atualizar Python (se necessário)
sudo apt update
sudo apt install python3.12 python3.12-venv

# Recriar ambiente virtual com nova versão
cd /opt/imunopreviniveis
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 🛠️ Ferramentas de Desenvolvimento Remoto

#### **1. Editores de Código no Servidor**

##### **Visual Studio Code (Recomendado)**
```bash
# Instalar VS Code no servidor
sudo snap install code --classic

# Abrir projeto
cd /opt/imunopreviniveis
code .

# Configurar extensões Python
# - Python (Microsoft)
# - Pylance
# - Python Indent
# - Streamlit
```

##### **Editores de Terminal**
```bash
# Nano (simples)
nano app/main.py

# Vim (avançado)
vim app/main.py

# Micro (moderno)
sudo apt install micro
micro app/main.py
```

#### **2. Desenvolvimento Local + Sincronização**

##### **Configuração de Ambiente Local**
```bash
# No seu computador de casa
git clone ssh://seu_usuario@servidor.fiocruz.br/opt/imunopreviniveis
cd imunopreviniveis

# Criar ambiente virtual local
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\Activate.ps1  # Windows

# Instalar dependências
pip install -r requirements.txt
```

##### **Sincronização Automática**
```bash
# Script para sincronizar automaticamente
# sync_to_server.sh
#!/bin/bash
rsync -avz --delete \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    ./ seu_usuario@servidor.fiocruz.br:/opt/imunopreviniveis/

# Executar sempre que fizer alterações
./sync_to_server.sh
```

#### **3. Debug e Testes Remotos**

##### **Logs em Tempo Real**
```bash
# Conectar ao servidor e monitorar logs
ssh seu_usuario@servidor.fiocruz.br
cd /opt/imunopreviniveis

# Ver logs da aplicação
sudo tail -f /var/log/imunopreviniveis/out.log

# Ver logs de erro
sudo tail -f /var/log/imunopreviniveis/err.log

# Ver logs do sistema
sudo journalctl -u supervisor -f
```

##### **Testes Rápidos**
```bash
# Testar alterações sem reiniciar tudo
cd /opt/imunopreviniveis
source venv/bin/activate

# Testar módulo específico
python -c "from app_sections.nova_analise import show_nova_analise; print('OK')"

# Testar import principal
python -c "from app.main import main; print('Main OK')"
```

---

## 📊 Diferenças: Local vs. Produção

### **Comparação Técnica Detalhada**

| Aspecto | Desenvolvimento Local | Servidor de Produção |
|---------|----------------------|---------------------|
| **Acesso** | Apenas você (localhost) | Qualquer pessoa (internet) |
| **Disponibilidade** | Quando você executa | 24/7 |
| **Recursos** | Sua máquina | Servidor dedicado |
| **Segurança** | Básica | Firewall, SSL, usuários |
| **Backup** | Manual | Automatizado |
| **Monitoramento** | Console | Logs, métricas, alertas |
| **Atualizações** | Manual | Scripts automatizados |

### **Por que Localhost Não Funciona na Internet?**

#### **1. Endereçamento de Rede**
```
Desenvolvimento Local:
Sua Máquina: 127.0.0.1 (localhost) → Porta 8501
    ❌ IP privado, não roteável
    ❌ Apenas acessível localmente
    ❌ Internet não sabe onde está

Servidor de Produção:
Internet → 200.150.100.50 (IP público) → Porta 80/443 → Porta 8501
    ✅ IP público, roteável
    ✅ Acessível globalmente
    ✅ Internet sabe exatamente onde está
```

#### **2. Roteamento e DNS**
```
Localhost:
Internet → ❌ Não sabe onde está 127.0.0.1
Roteador → ❌ Não encaminha para sua máquina
Sua Máquina → ✅ Apenas você pode acessar

Servidor:
Internet → ✅ Sabe onde está o IP público
Roteador → ✅ Encaminha para o servidor
Servidor → ✅ Qualquer pessoa pode acessar
```

#### **3. Configuração de Rede**
```
Localhost:
- ❌ Sem configuração de firewall para conexões externas
- ❌ Sem port forwarding
- ❌ Sem proxy reverso
- ❌ Sem configuração de rede pública

Servidor:
- ✅ Firewall configurado para permitir tráfego web
- ✅ Port forwarding configurado
- ✅ Nginx como proxy reverso
- ✅ Configuração de rede pública
```

#### **4. Segurança e Acesso**
```
Localhost:
- ❌ Sem controle de acesso
- ❌ Sem autenticação
- ❌ Sem logs de acesso
- ❌ Sem proteção contra ataques

Servidor:
- ✅ Controle de acesso configurado
- ✅ Autenticação se necessário
- ✅ Logs detalhados de acesso
- ✅ Firewall e proteções ativas
```

---

## 🔍 Troubleshooting Comum

### Problemas Frequentes

#### **1. Aplicação não inicia**
```bash
# Verificar logs
sudo supervisorctl tail imunopreviniveis

# Verificar dependências
source venv/bin/activate
pip list | grep streamlit
```

#### **2. Erro 502 Bad Gateway**
```bash
# Verificar se Streamlit está rodando
sudo supervisorctl status imunopreviniveis

# Verificar porta
netstat -tlnp | grep 8501
```

#### **3. Problemas de Performance**
```bash
# Verificar uso de recursos
htop
df -h
free -h
```

---

## 📚 Recursos Adicionais

### Documentação Oficial
- [Streamlit Deployment](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [Supervisor Documentation](http://supervisord.org/)

### Ferramentas Úteis
- **Monitoramento**: Prometheus + Grafana
- **Logs**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **CI/CD**: GitHub Actions, GitLab CI
- **Containerização**: Docker + Docker Compose

---

## ✨ Conclusão

Este guia fornece uma visão completa de como:
1. **Desenvolver localmente** com Streamlit
2. **Entender a arquitetura** modular do projeto
3. **Configurar um servidor de produção** institucional
4. **Manter e atualizar** a aplicação de forma segura
5. **Acessar remotamente** o servidor de casa
6. **Desenvolver e modificar** o código remotamente

A aplicação está estruturada de forma profissional e modular, facilitando tanto o desenvolvimento local quanto o deployment em produção. O Streamlit oferece uma experiência de desenvolvimento ágil, enquanto a arquitetura permite escalabilidade e manutenibilidade.

Para a Fiocruz ou qualquer instituição de ensino, este projeto representa uma solução robusta para disponibilizar dados de meningite de forma acessível e interativa para pesquisadores, profissionais de saúde e o público em geral.

---

## 🚀 **Resumo do Fluxo de Trabalho Diário**

### **De Casa para o Servidor:**
1. **Conectar**: `ssh seu_usuario@servidor.fiocruz.br`
2. **Navegar**: `cd /opt/meningite`
3. **Editar**: `code .` ou `nano app/main.py`
4. **Testar**: `sudo supervisorctl restart meningite`
5. **Verificar**: `sudo tail -f /var/log/meningite/out.log`

### **Sincronização com Seu Computador:**
1. **Desenvolver localmente** com VS Code
2. **Sincronizar para servidor**: `./sync_to_server.sh`
3. **Testar no servidor**: reiniciar aplicação
4. **Ver resultado**: acessar via navegador

### **Adicionar Novas Funcionalidades:**
1. **Criar arquivo**: `app_sections/nova_funcionalidade.py`
2. **Integrar menu**: editar `app/main.py`
3. **Testar**: reiniciar aplicação
4. **Deploy**: sincronizar com servidor

### **Atualizar Dados:**
1. **Copiar novos CSV**: `scp dados.csv servidor:/opt/meningite/TABELAS/`
2. **Atualizar código**: modificar `dashboard_completo_v2.py`
3. **Testar**: reiniciar aplicação
4. **Verificar**: acessar dashboard

**🎯 Resultado**: Você pode trabalhar de casa como se estivesse no servidor, com acesso completo ao código, dados e aplicação em produção!

---

## 📝 **Nota sobre o Nome do Projeto**

Este guia foi adaptado para o projeto **IMUNOPREVINIVEIS**, que é um dashboard abrangente para análise de dados de doenças imunopreveníveis no Brasil. O projeto inclui análises de:

- **Casos de doenças** imunopreveníveis
- **Dados de imunização** e cobertura vacinal
- **Análises epidemiológicas** regionais
- **Modelagem matemática** de surtos
- **Relatórios técnicos** para profissionais de saúde

O nome **IMUNOPREVINIVEIS** reflete o foco do projeto em doenças que podem ser prevenidas através de vacinação, incluindo mas não se limitando a meningite, sarampo, caxumba, rubéola, poliomielite e outras doenças imunopreveníveis importantes para a saúde pública brasileira.
