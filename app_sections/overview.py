import streamlit as st
from typing import Dict, Any


def show_overview_2024(dados: Dict[str, Any]) -> None:
    """Exibe a seção "Visão Geral 2024".

    Esta função atua como um wrapper, importando e chamando a implementação
    real da função `show_overview_2024` do script principal. Isso permite
    a modularização da aplicação, onde cada seção é carregada sob demanda.

    Args:
        dados (Dict[str, Any]): Um dicionário contendo todos os DataFrames
                                 carregados e processados, necessários para
                                 a visão geral de 2024.
    """
    from dashboard_completo_v2 import show_overview_2024 as _impl
    _impl(dados)


