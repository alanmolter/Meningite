from typing import Dict, Any


def show_etiologia_analysis(dados: Dict[str, Any]) -> None:
    """Exibe a seção de Análise por Etiologia.

    Esta função atua como um wrapper, importando e chamando a implementação
    real da função `show_etiologia_analysis` do script principal. Isso permite
    a modularização da aplicação, onde cada seção é carregada sob demanda.

    Args:
        dados (Dict[str, Any]): Um dicionário contendo todos os DataFrames
                                 carregados e processados, necessários para
                                 a análise por etiologia.
    """
    from dashboard_completo_v2 import show_etiologia_analysis as _impl
    _impl(dados)


