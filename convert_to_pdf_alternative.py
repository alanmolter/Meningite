#!/usr/bin/env python3
"""
Script alternativo para converter Markdown para PDF no Windows
Usa markdown2 e uma abordagem mais compatível
"""

import markdown2
from pathlib import Path
import subprocess
import sys
import os

def convert_md_to_html(md_file_path):
    """Converte Markdown para HTML"""
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Converter Markdown para HTML
        html_content = markdown2.markdown(
            md_content,
            extras=['tables', 'fenced-code-blocks', 'code-friendly', 'toc']
        )
        
        return html_content
        
    except Exception as e:
        print(f"❌ Erro ao ler/converter Markdown: {str(e)}")
        return None

def create_html_file(html_content, output_html_path):
    """Cria arquivo HTML completo"""
    full_html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Guia de Deployment - IMUNOPREVINIVEIS</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                margin: 2cm;
                color: #333;
                max-width: 1200px;
                margin-left: auto;
                margin-right: auto;
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                color: #2c3e50;
                margin-top: 1.5em;
                margin-bottom: 0.5em;
            }}
            
            h1 {{
                font-size: 2.5em;
                border-bottom: 3px solid #3498db;
                padding-bottom: 0.3em;
                text-align: center;
            }}
            
            h2 {{
                font-size: 2em;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 0.2em;
                color: #34495e;
            }}
            
            h3 {{
                font-size: 1.5em;
                color: #34495e;
            }}
            
            code {{
                background-color: #f8f9fa;
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                border: 1px solid #e9ecef;
            }}
            
            pre {{
                background-color: #f8f9fa;
                padding: 1em;
                border-radius: 5px;
                border-left: 4px solid #3498db;
                overflow-x: auto;
                border: 1px solid #e9ecef;
            }}
            
            pre code {{
                background-color: transparent;
                padding: 0;
                border: none;
            }}
            
            blockquote {{
                border-left: 4px solid #3498db;
                margin: 1em 0;
                padding-left: 1em;
                color: #7f8c8d;
                background-color: #f8f9fa;
                padding: 1em;
                border-radius: 5px;
            }}
            
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            th, td {{
                border: 1px solid #ddd;
                padding: 0.8em;
                text-align: left;
            }}
            
            th {{
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }}
            
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            
            tr:hover {{
                background-color: #f5f5f5;
            }}
            
            .toc {{
                background-color: #f8f9fa;
                padding: 1em;
                border-radius: 5px;
                margin: 1em 0;
                border: 1px solid #e9ecef;
            }}
            
            .toc ul {{
                list-style-type: none;
                padding-left: 1em;
            }}
            
            .toc a {{
                text-decoration: none;
                color: #3498db;
            }}
            
            .toc a:hover {{
                text-decoration: underline;
            }}
            
            hr {{
                border: none;
                border-top: 2px solid #ecf0f1;
                margin: 2em 0;
            }}
            
            ul, ol {{
                padding-left: 2em;
            }}
            
            li {{
                margin: 0.5em 0;
            }}
            
            a {{
                color: #3498db;
                text-decoration: none;
            }}
            
            a:hover {{
                text-decoration: underline;
            }}
            
            .emoji {{
                font-size: 1.2em;
            }}
            
            @media print {{
                body {{
                    margin: 1cm;
                }}
                
                h1, h2, h3, h4, h5, h6 {{
                    page-break-after: avoid;
                }}
                
                pre, blockquote {{
                    page-break-inside: avoid;
                }}
                
                table {{
                    page-break-inside: avoid;
                }}
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    try:
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        return True
    except Exception as e:
        print(f"❌ Erro ao criar arquivo HTML: {str(e)}")
        return False

def try_wkhtmltopdf(html_file_path, output_pdf_path):
    """Tenta usar wkhtmltopdf se disponível"""
    try:
        # Verificar se wkhtmltopdf está instalado
        result = subprocess.run(['wkhtmltopdf', '--version'], 
                              capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print("🔄 Usando wkhtmltopdf para conversão...")
            cmd = [
                'wkhtmltopdf',
                '--page-size', 'A4',
                '--margin-top', '1cm',
                '--margin-right', '1cm',
                '--margin-bottom', '1cm',
                '--margin-left', '1cm',
                '--encoding', 'UTF-8',
                html_file_path,
                output_pdf_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ PDF criado com wkhtmltopdf!")
                return True
            else:
                print(f"❌ Erro no wkhtmltopdf: {result.stderr}")
                return False
        else:
            return False
            
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"❌ Erro ao usar wkhtmltopdf: {str(e)}")
        return False

def main():
    """Função principal"""
    md_file = "GUIA_DEPLOYMENT.md"
    
    # Verificar se o arquivo existe
    if not Path(md_file).exists():
        print(f"❌ Arquivo {md_file} não encontrado!")
        print("📁 Certifique-se de estar no diretório correto.")
        return
    
    print("🔄 Convertendo Markdown para HTML...")
    
    # Converter Markdown para HTML
    html_content = convert_md_to_html(md_file)
    if html_content is None:
        return
    
    # Criar arquivo HTML
    html_file = "GUIA_DEPLOYMENT.html"
    if not create_html_file(html_content, html_file):
        return
    
    print(f"✅ HTML criado: {html_file}")
    
    # Tentar criar PDF com wkhtmltopdf
    pdf_file = "GUIA_DEPLOYMENT.pdf"
    if try_wkhtmltopdf(html_file, pdf_file):
        print(f"🎉 PDF criado com sucesso: {pdf_file}")
        print("🗑️ Removendo arquivo HTML temporário...")
        try:
            os.remove(html_file)
            print("✅ Arquivo HTML removido.")
        except:
            pass
    else:
        print("\n📋 **Alternativas para obter PDF:**")
        print("1. 📄 Abra o arquivo HTML no navegador")
        print("2. 🖨️ Use 'Imprimir' → 'Salvar como PDF'")
        print("3. 📱 Use ferramentas online:")
        print("   - https://www.markdowntopdf.com/")
        print("   - https://pandoc.org/try/")
        print(f"4. 🔧 Instale wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")
        print(f"\n📄 Arquivo HTML criado: {html_file}")

if __name__ == "__main__":
    main()
