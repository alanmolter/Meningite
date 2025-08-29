@echo off
echo ========================================
echo   Conversor Markdown para PDF
echo   Dashboard IMUNOPREVINIVEIS
echo ========================================
echo.

echo 🔧 Instalando dependencias necessarias...
pip install markdown weasyprint

echo.
echo 🔄 Convertendo GUIA_DEPLOYMENT.md para PDF...
python convert_to_pdf.py

echo.
echo ✅ Processo concluido!
echo 📄 Verifique se o arquivo PDF foi criado.
echo.
pause
