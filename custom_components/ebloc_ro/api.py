from __future__ import annotations

from typing import Any, Dict, Optional
import json
import logging

from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://www.e-bloc.ro"

# Excepții specifice integrării
class EBlocAuthError(Exception):
    """Ridicată când sesiunea/cookie-urile nu sunt valide sau răspunsul nu poate fi decodat."""


class EBlocApi:
    """Client minimal pentru API-urile utilizate din e-bloc.ro."""

    def __init__(
        self,
        session: ClientSession,
        cookies: Dict[str, str],
        user_agent: str = "HomeAssistant/ebloc_ro",
    ) -> None:
        self._session = session
        self._cookies = cookies or {}
        self._ua = user_agent

    # --- helpers -----------------------------------------------------------------

    def headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/",
            "User-Agent": self._ua,
            "X-Requested-With": "XMLHttpRequest",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

    # --- endpoints ----------------------------------------------------------------

    async def get_home_info(self) -> Dict[str, Any]:
        """
        /ajax/AjaxGetHomeApInfo.php
        Returnează date generale și luna afișată.
        """
        url = f"{BASE_URL}/ajax/AjaxGetHomeApInfo.php"
        async with self._session.post(url, headers=self.headers(), cookies=self._cookies, timeout=30) as resp:
            resp.raise_for_status()
            raw = await resp.text()

        try:
            js = json.loads(raw)
        except Exception as err:  # B904: păstrăm cauza
            _LOGGER.debug("Home info raw: %s", raw[:200])
            raise EBlocAuthError("Răspuns invalid la HomeApInfo") from err

        # uneori răspunsul e în cheie "1"
        return js.get("1", js)

    async def get_plati_chitante(self, months: int) -> list[dict[str, Any]]:
        """
        /ajax/AjaxGetPlatiChitante.php
        Returnează plățile/chitanțele, sortate descendent după 'luna'.
        """
        url = f"{BASE_URL}/ajax/AjaxGetPlatiChitante.php"
        data = {"months": str(months)}
        async with self._session.post(
            url, headers=self.headers(), cookies=self._cookies, data=data, timeout=30
        ) as resp:
            resp.raise_for_status()
            raw = await resp.text()

        try:
            js = json.loads(raw)
        except Exception as err:  # B904
            _LOGGER.debug("Plati raw: %s", raw[:200])
            raise EBlocAuthError("Răspuns invalid la PlatiChitante") from err

        rows = [v for v in js.values() if isinstance(v, dict)]
        rows.sort(key=lambda r: r.get("luna", ""), reverse=True)
        return rows

    async def get_index_luni(self) -> Dict[str, Any]:
        """
        /ajax/AjaxGetIndexLuna.php (ori echivalent)
        Returnează lunile pentru care există index.
        """
        url = f"{BASE_URL}/ajax/AjaxGetIndexLuna.php"
        async with self._session.post(url, headers=self.headers(), cookies=self._cookies, timeout=30) as resp:
            resp.raise_for_status()
            raw = await resp.text()

        try:
            js = json.loads(raw)
        except Exception as err:  # B904
            _LOGGER.debug("Index luni raw: %s", raw[:200])
            raise EBlocAuthError("Răspuns invalid la IndexLuni") from err

        return js

    async def get_index_contoare(self, luna: str, pIdAp: str = "-1") -> Dict[str, Any]:
        """
        /ajax/AjaxGetIndexContoare.php
        Returnează indexul pe contor(e) pentru luna dată.
        """
        url = f"{BASE_URL}/ajax/AjaxGetIndexContoare.php"
        data = {"pLuna": luna, "pIdAp": pIdAp}
        async with self._session.post(
            url, headers=self.headers(), cookies=self._cookies, data=data, timeout=30
        ) as resp:
            resp.raise_for_status()
            raw = await resp.text()

        try:
            js = json.loads(raw)
        except Exception as err:  # B904
            _LOGGER.debug("Index contoare raw: %s", raw[:200])
            raise EBlocAuthError("Răspuns invalid la IndexContoare") from err

        return js
