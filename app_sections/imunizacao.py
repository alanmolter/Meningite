from typing import Dict, Any


def show_imunizacao_analysis(dados: Dict[str, Any]) -> None:
    from dashboard_completo_v2 import show_imunizacao_analysis as _impl
    _impl(dados)


