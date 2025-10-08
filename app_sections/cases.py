from typing import Dict, Any


def show_cases_analysis(dados: Dict[str, Any]) -> None:
    """Exibe a seção de Análise de Casos Notificados.

    Esta função atua como um wrapper, importando e chamando a implementação
    real da função `show_cases_analysis` do script principal. Isso permite
    a modularização da aplicação, onde cada seção é carregada sob demanda.

    Args:
        dados (Dict[str, Any]): Um dicionário contendo todos os DataFrames
                                 carregados e processados, necessários para
                                 a análise de casos.
    """
    from dashboard_completo_v2 import show_cases_analysis as _impl
    _impl(dados)


