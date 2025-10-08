from typing import Dict, Any


def show_attack_rate_analysis(dados: Dict[str, Any]) -> None:
    """Exibe a seção de Análise de Taxa de Ataque e Força de Infecção.

    Esta função atua como um wrapper, importando e chamando a implementação
    real da função `show_attack_rate_analysis` do script principal. Isso permite
    a modularização da aplicação, onde cada seção é carregada sob demanda.

    Args:
        dados (Dict[str, Any]): Um dicionário contendo todos os DataFrames
                                 carregados e processados, necessários para
                                 as análises de taxa de ataque.
    """
    from dashboard_completo_v2 import show_attack_rate_analysis as _impl
    _impl(dados)


