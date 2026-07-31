"""Cliente da API oficial da ANA (HidroWebService) — atrás de flag.

A credencial é individual e chega por e-mail (ver README). Enquanto ela não
existe no .env, o módulo reporta e sai sem erro. Quando chegar, é só ligar:
o token OAuth dura 60 minutos e é renovado automaticamente.
"""

from __future__ import annotations

import datetime as dt
import os
from pathlib import Path

import httpx

from .common import ROOT, load_config, make_client

BASE_URL = "https://www.ana.gov.br/hidrowebservice"


def _carregar_env() -> None:
    env = ROOT / ".env"
    if env.exists():
        for linha in env.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if linha and not linha.startswith("#") and "=" in linha:
                chave, valor = linha.split("=", 1)
                os.environ.setdefault(chave.strip(), valor.strip())


def habilitado() -> bool:
    _carregar_env()
    return bool(os.environ.get("ANA_IDENTIFICADOR") and os.environ.get("ANA_SENHA"))


class HidroWebServiceClient:
    """Autentica, renova token a cada <60 min e consulta séries telemétricas."""

    def __init__(self) -> None:
        if not habilitado():
            raise RuntimeError(
                "Credencial da ANA ausente. Defina ANA_IDENTIFICADOR e ANA_SENHA "
                "no .env (ver README para solicitar à ANA)."
            )
        self._client = make_client()
        self._token: str | None = None
        self._token_expira: dt.datetime | None = None

    def _autenticar(self) -> None:
        resp = self._client.get(
            f"{BASE_URL}/EstacoesTelemetricas/OAUth/v1",
            headers={
                "Identificador": os.environ["ANA_IDENTIFICADOR"],
                "Senha": os.environ["ANA_SENHA"],
            },
        )
        resp.raise_for_status()
        self._token = resp.json()["items"]["tokenautenticacao"]
        # Renova com folga de 5 min sobre a validade de 60.
        self._token_expira = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=55)

    def _headers(self) -> dict:
        agora = dt.datetime.now(dt.timezone.utc)
        if self._token is None or self._token_expira is None or agora >= self._token_expira:
            self._autenticar()
        return {"Authorization": f"Bearer {self._token}"}

    def serie_telemetrica_adotada(
        self, codigo: int, inicio: dt.date, fim: dt.date
    ) -> list[dict]:
        resp = self._client.get(
            f"{BASE_URL}/EstacoesTelemetricas/HidroinfoanaSerieTelemetricaAdotada/v1",
            headers=self._headers(),
            params={
                "Código da Estação": str(codigo),
                "Tipo Filtro Data": "DATA_LEITURA",
                "Data de Busca (yyyy-MM-dd)": inicio.isoformat(),
                "Range Intervalo de busca": "MES",
            },
        )
        resp.raise_for_status()
        return resp.json().get("items", [])


def run() -> None:
    if not habilitado():
        print("[ana_hws] credencial ausente — módulo desligado (esperado até a ANA responder)")
        return
    cliente = HidroWebServiceClient()
    hoje = dt.date.today()
    amostra = cliente.serie_telemetrica_adotada(86510000, hoje - dt.timedelta(days=3), hoje)
    print(f"[ana_hws] credencial OK — amostra de Muçum devolveu {len(amostra)} registros")


if __name__ == "__main__":
    run()
