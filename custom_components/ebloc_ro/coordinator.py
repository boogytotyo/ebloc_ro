
from __future__ import annotations

import logging
from datetime import timedelta, datetime
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_COOKIE,
    CONF_HISTORY_MONTHS,
    CONF_SCAN_INTERVAL_MIN,
    DEFAULT_HISTORY_MONTHS,
    DEFAULT_SCAN_INTERVAL_MIN,
)
from .api import EBlocAPI, EBlocAuthError

_LOGGER = logging.getLogger(__name__)


class EBlocCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        session = async_get_clientsession(hass)
        cookie = entry.data.get(CONF_COOKIE, "")
        self.api = EBlocAPI(session, cookie)

        scan_min = entry.options.get(CONF_SCAN_INTERVAL_MIN, entry.data.get(CONF_SCAN_INTERVAL_MIN, DEFAULT_SCAN_INTERVAL_MIN))
        super().__init__(
            hass,
            _LOGGER,
            name="e-Bloc Romania",
            update_interval=timedelta(minutes=int(scan_min)),
        )

        self.history_months = int(entry.options.get(CONF_HISTORY_MONTHS, entry.data.get(CONF_HISTORY_MONTHS, DEFAULT_HISTORY_MONTHS)))

    async def _async_update_data(self):
        try:
            await self.api.discover()
            home = await self.api.get_home_info()
            luna = home.get("luna_afisata") or datetime.utcnow().strftime("%Y-%m")
            await self.api.get_index_contoare(luna=luna, pIdAp='-1')
            # Build index history for configured months
            from datetime import datetime as _dt
            def _prev_months(start_ym: str, count: int):
                y, m = [int(x) for x in start_ym.split('-')[:2]]
                res = []
                for i in range(count):
                    yy, mm = y, m - i
                    while mm <= 0:
                        yy -= 1
                        mm += 12
                    res.append(f"{yy:04d}-{mm:02d}")
                return res

            months = _prev_months(luna, max(1, int(self.history_months)))
            index_history = {}
            latest_index = None
            latest_date = None
            for ym in months:
                try:
                    idx = await self.api.get_index_contoare(luna=ym, pIdAp="-1")
                except asyncio.CancelledError:
                    idx = {}  # soft-skip month on cancellation
                except Exception:
                    idx = {}

                month_val = None
                month_date = None
                if isinstance(idx, dict):
                    for row in idx.values():
                        if isinstance(row, dict):
                            try:
                                val = int(str(row.get("index_nou", "0")).strip() or 0)
                            except Exception:
                                val = None
                            dstr = row.get("data")
                            try:
                                dt = _dt.strptime(dstr, "%Y-%m-%d") if dstr else None
                            except Exception:
                                dt = None
                            if val is not None:
                                if month_date is None and month_val is None:
                                    month_val, month_date = val, dt
                                else:
                                    if dt and (month_date is None or dt > month_date):
                                        month_val, month_date = val, dt
                                    elif month_date is None and (month_val is None or (isinstance(val, int) and val > month_val)):
                                        month_val = val
                if month_val is not None:
                    index_history[ym] = month_val
                    if latest_date is None and latest_index is None:
                        latest_index, latest_date = month_val, month_date
                    else:
                        if month_date and (latest_date is None or month_date > latest_date):
                            latest_index, latest_date = month_val, month_date
                        elif latest_date is None and (latest_index is None or (isinstance(month_val, int) and month_val > latest_index)):
                            latest_index = month_val

            plati = await self.api.get_plati_chitante(months=self.history_months)

            return {
                "home": home,
                "index_history": index_history,
                "latest_index": latest_index,
                "plati": plati,
                "luna": luna,
            }
        except EBlocAuthError as err:
            raise UpdateFailed(f"Auth error: {err}") from err
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(str(err)) from err
