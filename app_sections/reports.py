from typing import Dict, Any


def show_reports(dados: Dict[str, Any]) -> None:
    from dashboard_completo_v2 import show_reports as _impl
    _impl(dados)


