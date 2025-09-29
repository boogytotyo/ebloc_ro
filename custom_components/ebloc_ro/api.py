
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

import aiohttp

from .const import HEADER_UA

_LOGGER = logging.getLogger(__name__)


class EBlocAuthError(Exception):
    pass


class EBlocAPI:
    BASE = "https://www.e-bloc.ro"
    AJAX = BASE + "/ajax"

    def __init__(self, session: aiohttp.ClientSession, cookie: str) -> None:
        self._session = session
        self._cookie = cookie.strip()
        self.id_asoc: Optional[str] = None
        self.id_ap: Optional[str] = None

    def headers(self) -> Dict[str, str]:
        return {
            "User-Agent": HEADER_UA,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.BASE,
            "Referer": self.BASE + "/index.php",
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": self._cookie,
        }

    def _extract_ids_from_cookie(self) -> None:
        ck = self._cookie
        parts = {}
        for p in ck.split(";"):
            p = p.strip()
            if "=" in p:
                k, v = p.split("=", 1)
                parts[k.strip()] = v.strip()
        asoc = parts.get("asoc-cur")
        home = parts.get("home-ap-cur")
        if asoc:
            self.id_asoc = asoc
        if home and "_" in home:
            try:
                self.id_ap = home.split("_", 1)[1]
            except Exception:
                pass

    async def discover(self) -> None:
        """Validate cookie and extract asoc/ap identifiers by pinging an endpoint."""
        self._extract_ids_from_cookie()
        if not self.id_asoc:
            raise EBlocAuthError("Cookie invalid: lipseste asoc-cur")
        url = f"{self.AJAX}/AjaxGetHomeAp.php"
        data = f"pIdAsoc={self.id_asoc}"
        async with self._session.post(url, headers=self.headers(), data=data, timeout=20) as resp:
            txt = await resp.text()
            if resp.status != 200:
                raise EBlocAuthError(f"HTTP {resp.status}")
            if "login" in txt.lower() and "password" in txt.lower():
                raise EBlocAuthError("Autentificare eșuată (redirect la login)")

    async def get_home_info(self) -> Dict[str, Any]:
        """AjaxGetHomeApInfo.php -> user & month info."""
        url = f"{self.AJAX}/AjaxGetHomeApInfo.php"
        if not self.id_asoc or not self.id_ap:
            self._extract_ids_from_cookie()
        data = f"pIdAsoc={self.id_asoc}&pIdAp={self.id_ap or '0'}"
        async with self._session.post(url, headers=self.headers(), data=data, timeout=30) as resp:
            raw = await resp.text()
            try:
                js = json.loads(raw)
            except Exception as err:
                _LOGGER.debug("Home info raw: %s", raw[:200])
                raise EBlocAuthError("Răspuns invalid la HomeApInfo") from err
            return js.get("1", js)

    async def get_plati_chitante(self, months: int = 12) -> Dict[str, Any]:
        url = f"{self.AJAX}/AjaxGetPlatiChitante.php"
        if not self.id_asoc or not self.id_ap:
            self._extract_ids_from_cookie()
        data = f"pIdAsoc={self.id_asoc}&pIdAp={self.id_ap or '-1'}"
        async with self._session.post(url, headers=self.headers(), data=data, timeout=30) as resp:
            raw = await resp.text()
            try:
                js = json.loads(raw)
            except Exception as err:
                _LOGGER.debug("Plati raw: %s", raw[:200])
                raise EBlocAuthError("Răspuns invalid la PlatiChitante") from err
            rows = [v for v in js.values() if isinstance(v, dict)]
            rows.sort(key=lambda r: r.get("luna", ""), reverse=True)
            limited = rows[:months] if months else rows
            return {str(i + 1): r for i, r in enumerate(limited)}

    async def get_index_luni(self) -> Dict[str, Any]:
        url = f"{self.AJAX}/AjaxGetIndexLuni.php"
        if not self.id_asoc:
            self._extract_ids_from_cookie()
        data = f"pIdAsoc={self.id_asoc}"
        async with self._session.post(url, headers=self.headers(), data=data, timeout=30) as resp:
            raw = await resp.text()
            try:
                js = json.loads(raw)
            except Exception as err:
                _LOGGER.debug("Index luni raw: %s", raw[:200])
                raise EBlocAuthError("Răspuns invalid la IndexLuni") from err
            return js

    async def get_index_contoare(self, luna: str, pIdAp: str | int = -1) -> Dict[str, Any]:
        url = f"{self.AJAX}/AjaxGetIndexContoare.php"
        if not self.id_asoc:
            self._extract_ids_from_cookie()
        data = f"pIdAsoc={self.id_asoc}&pLuna={luna}&pIdAp={pIdAp}"
        async with self._session.post(url, headers=self.headers(), data=data, timeout=30) as resp:
            raw = await resp.text()
            try:
                js = json.loads(raw)
            except Exception as err:
                _LOGGER.debug("Index contoare raw: %s", raw[:200])
                raise EBlocAuthError("Răspuns invalid la IndexContoare") from err
            return js
