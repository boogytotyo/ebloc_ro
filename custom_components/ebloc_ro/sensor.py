
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ATTRIBUTION
from .coordinator import EBlocCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: EBlocCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []
    # Migrate old entity_ids that had the "e_bloc_" prefix
    try:
        from homeassistant.helpers import entity_registry as er
        er_reg = er.async_get(hass)
        rename_map = {
            "ebloc_date_utilizator": "sensor.ebloc_date_utilizator",
            "ebloc_factura_restanta": "sensor.ebloc_factura_restanta",
            "ebloc_index_contor": "sensor.ebloc_index_contor",
            "ebloc_istoric_facturi": "sensor.ebloc_istoric_facturi",
            "ebloc_update_sensor": "sensor.ebloc_update",
        }
        for unique_id, target_eid in rename_map.items():
            ent = er_reg.async_get_entity_id("sensor", DOMAIN, unique_id)
            if ent and ent.startswith("sensor.e_bloc_"):
                er_reg.async_update_entity(ent, new_entity_id=target_eid)
    except Exception:
        pass

    entities.append(EblocDateUtilizatorSensor(coordinator))
    entities.append(EblocFacturaRestantaSensor(coordinator))
    entities.append(EblocIndexContorSensor(coordinator))
    entities.append(EblocIstoricFacturiSensor(coordinator))
    
    entities.append(EblocDateUtilizatorSensor(coordinator))
    entities.append(EblocFacturaRestantaSensor(coordinator))
    entities.append(EblocIndexContorSensor(coordinator))
    entities.append(EblocIstoricFacturiSensor(coordinator))
    
    async_add_entities(entities)


class BaseEBlocSensor(CoordinatorEntity[EBlocCoordinator], SensorEntity):
    _attr_has_entity_name = False

    @property
    def attribution(self) -> str | None:
        return ATTRIBUTION


class EblocDateUtilizatorSensor(BaseEBlocSensor):
    _attr_name = "eBloc Date Utilizator"
    _attr_icon = "mdi:account"
    _attr_unique_id = "ebloc_date_utilizator"

    @property
    def native_value(self):
        home = (self.coordinator.data or {}).get("home", {})
        return home.get("cod_client")

    @property
    def extra_state_attributes(self):
        h = (self.coordinator.data or {}).get("home", {})
        def fmt_lei(val):
            try:
                return f"{float(str(val).replace(',', '.')):.2f} RON"
            except Exception:
                return str(val)

        attrs = {
            "Cod client": h.get("cod_client"),
            "Apartament": h.get("ap"),
            "Persoane declarate": h.get("nr_pers_afisat"),
            "Restanță de plată": fmt_lei(h.get("datorie", "0")),
            "Ultima zi de plată": h.get("ultima_zi_plata"),
            "Contor trimis": "Da" if str(h.get("contoare_citite", "0")) in ("1", "true", "True") else "Nu",
            "Începere citire contoare": h.get("citire_contoare_start"),
            "Încheiere citire contoare": h.get("citire_contoare_end"),
            "Luna afișată": h.get("luna_afisata"),
        }
        return {k: v for k, v in attrs.items() if v not in (None, "")}


class EblocFacturaRestantaSensor(BaseEBlocSensor):
    _attr_name = "eBloc Factura Restanta"
    _attr_icon = "mdi:file-document-alert"
    _attr_unique_id = "ebloc_factura_restanta"

    @property
    def native_value(self):
        h = (self.coordinator.data or {}).get("home", {})
        try:
            return round(float(str(h.get("datorie", "0")).replace(",", ".")), 2)
        except Exception:
            return 0.0

    @property
    def extra_state_attributes(self):
        h = (self.coordinator.data or {}).get("home", {})
        return {
            "Luna afișată": h.get("luna_afisata"),
            "Ultima zi de plată": h.get("ultima_zi_plata"),
            "Nivel restanță": h.get("nivel_restanta"),
        }


class EblocIndexContorSensor(BaseEBlocSensor):
    _attr_name = "eBloc Index Contor"
    _attr_icon = "mdi:counter"
    _attr_unique_id = "ebloc_index_contor"

    @property
    def native_value(self):
        # latest index value computed in coordinator
        return (getattr(self.coordinator, 'data', {}) or {}).get('latest_index')

    @property
    def extra_state_attributes(self):
        # month -> index mapping for configured history
        return (getattr(self.coordinator, 'data', {}) or {}).get('index_history', {})

class EblocIstoricFacturiSensor(BaseEBlocSensor):
    _attr_name = "eBloc Istoric Facturi"
    _attr_icon = "mdi:history"
    _attr_unique_id = "ebloc_istoric_facturi"

    @property
    def native_value(self):
        pl = (self.coordinator.data or {}).get("plati", {})
        if not pl:
            return None
        first = next(iter(pl.values()))
        try:
            return round(float(first.get("suma", "0")) / 100.0, 2)
        except Exception:
            return None

    @property
    def extra_state_attributes(self):
        pl = (self.coordinator.data or {}).get("plati", {})
        months = {}
        for row in pl.values():
            luna = row.get("luna", "n/a")
            try:
                suma = float(row.get("suma", "0")) / 100.0
            except Exception:
                suma = 0.0
            months[luna] = f"{suma:.2f} RON"
        # order desc by month key
        ordered = dict(sorted(months.items(), key=lambda kv: kv[0], reverse=True))
        return ordered


