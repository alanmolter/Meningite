#!/usr/bin/env python3
"""
Script para converter o GUIA_DEPLOYMENT.md para PDF
Requer: pip install markdown weasyprint
"""

import markdown
import weasyprint
from pathlib import Path
import sys

def convert_md_to_pdf(md_file_path, output_pdf_path=None):
    """Converte um arquivo Markdown em um documento PDF estilizado.

    Lê o conteúdo de um arquivo Markdown, converte-o para HTML, aplica um CSS
    personalizado para formatação profissional e, em seguida, usa a biblioteca
    WeasyPrint para renderizar o HTML como um arquivo PDF.

    Args:
        md_file_path (str): O caminho para o arquivo Markdown de entrada.
        output_pdf_path (str, optional): O caminho para o arquivo PDF de saída.
                                         Se não for fornecido, o PDF será salvo no
                                         mesmo diretório que o arquivo de entrada
                                         com a extensão .pdf. Defaults to None.

    Returns:
        bool: True se a conversão for bem-sucedida, False caso contrário.
    """
    
    try:
        # Ler o arquivo Markdown
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Converter Markdown para HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['tables', 'fenced_code', 'codehilite', 'toc']
        )
        
        # Criar HTML completo com CSS
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
                }}
                
                h2 {{
                    font-size: 2em;
                    border-bottom: 2px solid #ecf0f1;
                    padding-bottom: 0.2em;
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
                }}
                
                pre {{
                    background-color: #f8f9fa;
                    padding: 1em;
                    border-radius: 5px;
                    border-left: 4px solid #3498db;
                    overflow-x: auto;
                }}
                
                pre code {{
                    background-color: transparent;
                    padding: 0;
                }}
                
                blockquote {{
                    border-left: 4px solid #3498db;
                    margin: 1em 0;
                    padding-left: 1em;
                    color: #7f8c8d;
                }}
                
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 1em 0;
                }}
                
                th, td {{
                    border: 1px solid #ddd;
                    padding: 0.5em;
                    text-align: left;
                }}
                
                th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                }}
                
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                
                .toc {{
                    background-color: #f8f9fa;
                    padding: 1em;
                    border-radius: 5px;
                    margin: 1em 0;
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
                
                @page {{
                    size: A4;
                    margin: 2cm;
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
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Definir nome do arquivo de saída se não fornecido
        if output_pdf_path is None:
            output_pdf_path = md_file_path.replace('.md', '.pdf')
        
        # Converter HTML para PDF
        print(f"🔄 Convertendo {md_file_path} para PDF...")
        weasyprint.HTML(string=full_html).write_pdf(output_pdf_path)
        
        print(f"✅ PDF criado com sucesso: {output_pdf_path}")
        return True
        
    except ImportError as e:
        print("❌ Erro: Bibliotecas necessárias não estão instaladas.")
        print("📦 Execute: pip install markdown weasyprint")
        return False
        
    except Exception as e:
        print(f"❌ Erro durante a conversão: {str(e)}")
        return False

def main():
    """Ponto de entrada principal do script.

    Verifica se o arquivo 'GUIA_DEPLOYMENT.md' existe no diretório atual
    e chama a função `convert_md_to_pdf` para iniciar o processo de conversão.
    Imprime mensagens de status para o usuário.
    """
    md_file = "GUIA_DEPLOYMENT.md"
    
    # Verificar se o arquivo existe
    if not Path(md_file).exists():
        print(f"❌ Arquivo {md_file} não encontrado!")
        print("📁 Certifique-se de estar no diretório correto.")
        return
    
    # Converter para PDF
    success = convert_md_to_pdf(md_file)
    
    if success:
        print("\n🎉 Conversão concluída!")
        print("📄 O arquivo PDF foi criado no mesmo diretório.")
        print("🔍 Verifique se o arquivo foi criado corretamente.")

if __name__ == "__main__":
    main()
