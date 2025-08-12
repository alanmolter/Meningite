import streamlit as st
from datetime import datetime

# Lazy import of heavy functions from the monolith to keep compatibility
from app_sections.overview import show_overview_2024
from app_sections.cases import show_cases_analysis
from app_sections.sorogrupos import show_sorogrupos_analysis
from app_sections.etiologia import show_etiologia_analysis
from app_sections.imunizacao import show_imunizacao_analysis
from app_sections.regional import show_regional_analysis
from app_sections.advanced import show_advanced_analysis
from app_sections.epidemiologica import show_epidemiological_analysis
from app_sections.attack_rate import show_attack_rate_analysis
from app_sections.explore import show_free_exploration
from app_sections.reports import show_reports

from dashboard_completo_v2 import load_all_data


def main() -> None:
    st.set_page_config(page_title="Dashboard Meningite Brasil", page_icon="🦠", layout="wide")

    dados = load_all_data()

    st.sidebar.title("🧭 Navegação")
    opcao = st.sidebar.selectbox(
        "Selecione a seção:",
        [
            "🏠 Visão Geral 2024",
            "📊 Análise de Casos",
            "🦠 Análise de Sorogrupos",
            "🔬 Análise de Etiologia",
            "💉 Análise de Imunização",
            "🗺️ Análise Regional",
            "🔬 Análises Avançadas",
            "🦠 Análise Epidemiológica",
            "⚡ Taxa de Ataque",
            "🔍 Exploração Livre",
            "📋 Relatórios",
        ],
    )

    if opcao == "🏠 Visão Geral 2024":
        show_overview_2024(dados)
    elif opcao == "📊 Análise de Casos":
        show_cases_analysis(dados)
    elif opcao == "🦠 Análise de Sorogrupos":
        show_sorogrupos_analysis(dados)
    elif opcao == "🔬 Análise de Etiologia":
        show_etiologia_analysis(dados)
    elif opcao == "💉 Análise de Imunização":
        show_imunizacao_analysis(dados)
    elif opcao == "🗺️ Análise Regional":
        show_regional_analysis(dados)
    elif opcao == "🔬 Análises Avançadas":
        show_advanced_analysis(dados)
    elif opcao == "🦠 Análise Epidemiológica":
        show_epidemiological_analysis(dados)
    elif opcao == "⚡ Taxa de Ataque":
        show_attack_rate_analysis(dados)
    elif opcao == "🔍 Exploração Livre":
        show_free_exploration(dados)
    elif opcao == "📋 Relatórios":
        show_reports(dados)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**📅 Última atualização:**")
    st.sidebar.markdown(f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")


if __name__ == "__main__":
    main()


