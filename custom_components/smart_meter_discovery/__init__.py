from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .mqtt_bridge import start_bridge

DOMAIN = "smart_meter_discovery"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    config = {**entry.data, **(entry.options or {})}
    hass.async_add_job(start_bridge, config)
    return True
