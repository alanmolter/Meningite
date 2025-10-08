from typing import Dict, Any


def show_reports(dados: Dict[str, Any]) -> None:
    """Exibe a seção de Relatórios e Downloads.

    Esta função atua como um wrapper, importando e chamando a implementação
    real da função `show_reports` do script principal. Isso permite
    a modularização da aplicação, onde cada seção é carregada sob demanda.

    Args:
        dados (Dict[str, Any]): Um dicionário contendo todos os DataFrames
                                 carregados, que serão usados para gerar relatórios
                                 e disponibilizados para download.
    """
    from dashboard_completo_v2 import show_reports as _impl
    _impl(dados)


