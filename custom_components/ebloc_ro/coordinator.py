from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EBlocApi


class EBlocCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator pentru integrarea e-Bloc RO."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: EBlocApi,
        history_months: int = 6,
        update_interval: timedelta | None = timedelta(minutes=30),
    ) -> None:
        super().__init__(
            hass, logger=None, name="eBloc Coordinator", update_interval=update_interval
        )
        self.api = api
        self.history_months = max(1, int(history_months))

        # (opțional) versiuni pentru update entity
        self.integration_version: str | None = None
        self.latest_version: str | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            home = await self.api.get_home_info()
            luna = home.get("luna_afisata") or datetime.utcnow().strftime("%Y-%m")

            # Build index history pentru ultimele `history_months` luni
            def _last_n_months_utc(n: int) -> list[str]:
                now = datetime.utcnow()
                y, m = now.year, now.month
                out: list[str] = []
                for i in range(n):
                    yy = y - ((m - 1 - i) // 12)
                    mm = ((m - 1 - i) % 12) + 1
                    out.append(f"{yy:04d}-{mm:02d}")
                return out  # [curent .. mai vechi]

            months = _last_n_months_utc(self.history_months)
            index_history: dict[str, int] = {ym: 0 for ym in months}
            latest_index = 0
            latest_month_idx = -1

            async def _fetch_month(ym: str):
                try:
                    res = await asyncio.wait_for(
                        self.api.get_index_contoare(luna=ym, pIdAp="-1"), timeout=10
                    )
                    return ym, res, None
                except Exception as e:  # noqa: BLE001
                    return ym, {}, e

            results = await asyncio.gather(*[_fetch_month(ym) for ym in months])

            for ym, idx, _err in results:
                month_val = 0
                if isinstance(idx, dict):
                    for row in idx.values():
                        if isinstance(row, dict):
                            try:
                                val = int(str(row.get("index_nou", "0")).strip() or 0)
                            except Exception:
                                val = 0
                            if val > month_val:
                                month_val = val
                index_history[ym] = month_val
                i_pos = months.index(ym)
                if month_val > 0 and (latest_month_idx == -1 or i_pos < latest_month_idx):
                    latest_month_idx = i_pos
                    latest_index = month_val

            plati = await self.api.get_plati_chitante(months=self.history_months)

            return {
                "home": home,
                "luna": luna,
                "index_history": index_history,
                "latest_index": latest_index,
                "plati": plati,
            }
        except Exception as err:
            raise UpdateFailed(str(err)) from err
