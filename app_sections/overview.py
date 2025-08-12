import streamlit as st
from typing import Dict, Any


def show_overview_2024(dados: Dict[str, Any]) -> None:
    from dashboard_completo_v2 import show_overview_2024 as _impl
    _impl(dados)


