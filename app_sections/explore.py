from typing import Dict, Any


def show_free_exploration(dados: Dict[str, Any]) -> None:
    """Exibe a seção de Exploração Livre dos Dados.

    Esta função atua como um wrapper, importando e chamando a implementação
    real da função `show_free_exploration` do script principal. Isso permite
    a modularização da aplicação, onde cada seção é carregada sob demanda.

    Args:
        dados (Dict[str, Any]): Um dicionário contendo todos os DataFrames
                                 carregados, que estarão disponíveis para
                                 a exploração do usuário.
    """
    from dashboard_completo_v2 import show_free_exploration as _impl
    _impl(dados)


