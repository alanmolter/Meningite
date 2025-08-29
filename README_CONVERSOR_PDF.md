# 📄 Conversor Markdown para PDF

Este diretório contém scripts para converter o `GUIA_DEPLOYMENT.md` em um arquivo PDF profissional.

## 🚀 **Como Usar (Opções Funcionais)**

### **Opção 1: Conversão Automática (Recomendado)**

1. **Clique duas vezes** no arquivo `abrir_html.bat`
2. **Aguarde** o navegador abrir com o HTML formatado
3. **Pressione Ctrl+P** no navegador
4. **Selecione "Salvar como PDF"**
5. **Escolha o local** e salve o arquivo

### **Opção 2: PowerShell**

1. **Clique com botão direito** no arquivo `abrir_html.ps1`
2. **Selecione** "Executar com PowerShell"
3. **Siga os passos** da Opção 1

### **Opção 3: Conversão Direta (Avançado)**

```bash
# 1. Instalar dependências
pip install markdown2

# 2. Executar conversão para HTML
python convert_to_pdf_alternative.py

# 3. Abrir HTML e converter para PDF manualmente
```

## 📦 **Dependências Necessárias**

- **Python 3.7+** (já instalado)
- **markdown2** (biblioteca para processar Markdown)

## 🔧 **Solução de Problemas**

### **Erro: "pip não é reconhecido"**
- Instale o Python do site oficial: https://python.org
- Marque a opção "Add Python to PATH" durante a instalação

### **Erro: "Arquivo não encontrado"**
- Certifique-se de estar no diretório correto
- Verifique se `GUIA_DEPLOYMENT.md` existe

### **Problemas com WeasyPrint (Windows)**
- **Solução**: Use a abordagem HTML → Navegador → PDF
- Mais confiável no Windows
- Melhor formatação

## 📋 **Arquivos Criados**

- `convert_to_pdf_alternative.py` - Script principal Python
- `abrir_html.bat` - **Script automático Windows (RECOMENDADO)**
- `abrir_html.ps1` - Script PowerShell
- `converter_pdf.bat` - Script antigo (pode não funcionar)
- `converter_pdf.ps1` - Script antigo (pode não funcionar)
- `requirements_pdf.txt` - Dependências Python
- `GUIA_DEPLOYMENT.html` - **Arquivo HTML formatado**
- `GUIA_DEPLOYMENT.pdf` - **Arquivo PDF (criado manualmente)**

## 🎨 **Características do PDF**

- **Formato A4** com margens adequadas
- **Tabelas formatadas** com cores alternadas
- **Código destacado** com fundo cinza
- **Títulos hierárquicos** com cores diferentes
- **Quebras de página** inteligentes
- **Design responsivo** e profissional

## 🌐 **Alternativas Online (Se necessário)**

Se os scripts não funcionarem, você pode usar:

1. **Markdown to PDF**: https://www.markdowntopdf.com/
2. **Pandoc Online**: https://pandoc.org/try/
3. **GitHub**: Visualizar o .md e imprimir como PDF

## 📞 **Suporte**

Para problemas técnicos:
1. Verifique se o Python está instalado: `python --version`
2. Verifique se o pip está funcionando: `pip --version`
3. Tente instalar manualmente: `pip install markdown2`

## 🎯 **Fluxo Recomendado**

1. **Execute** `abrir_html.bat`
2. **Navegador abre** com HTML formatado
3. **Pressione Ctrl+P**
4. **Selecione "Salvar como PDF"**
5. **Escolha local** e salve
6. **Pronto!** PDF profissional criado

---

**🎯 Resultado**: Um PDF profissional do seu guia de deployment, pronto para impressão e compartilhamento!

**💡 Dica**: A abordagem HTML → Navegador → PDF é mais confiável no Windows e produz PDFs com melhor formatação!
