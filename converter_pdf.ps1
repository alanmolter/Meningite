# Conversor Markdown para PDF - Dashboard IMUNOPREVINIVEIS
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Conversor Markdown para PDF" -ForegroundColor Cyan
Write-Host "   Dashboard IMUNOPREVINIVEIS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔧 Instalando dependências necessárias..." -ForegroundColor Yellow
pip install markdown weasyprint

Write-Host ""
Write-Host "🔄 Convertendo GUIA_DEPLOYMENT.md para PDF..." -ForegroundColor Green
python convert_to_pdf.py

Write-Host ""
Write-Host "✅ Processo concluído!" -ForegroundColor Green
Write-Host "📄 Verifique se o arquivo PDF foi criado." -ForegroundColor Green
Write-Host ""
Read-Host "Pressione Enter para continuar..."
