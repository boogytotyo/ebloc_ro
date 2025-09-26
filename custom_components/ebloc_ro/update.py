from __future__ import annotations

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, INTEGRATION_VERSION, RELEASES_URL
from .coordinator import EBlocCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: EBlocCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([EBlocRoUpdateEntity(coordinator)], True)
    async_add_entities([EBlocRoUpdateEntity(coordinator)], True)


class EBlocRoUpdateEntity(CoordinatorEntity, UpdateEntity):
    _attr_has_entity_name = False
    _attr_name = "eBloc RO Update"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_unique_id = "ebloc_ro_update"
    _attr_installed_version = INTEGRATION_VERSION
    _attr_latest_version = INTEGRATION_VERSION
    _attr_release_url = RELEASES_URL
    _attr_supported_features = UpdateEntityFeature(0)

    @property
    def supported_features(self) -> UpdateEntityFeature:
        val = getattr(self, "_attr_supported_features", UpdateEntityFeature(0))
        if isinstance(val, UpdateEntityFeature):
            return val
        try:
            return UpdateEntityFeature(int(val or 0))
        except Exception:
            return UpdateEntityFeature(0)
