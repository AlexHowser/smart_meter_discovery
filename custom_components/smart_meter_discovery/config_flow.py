from homeassistant import config_entries
import voluptuous as vol
from .const import *

class SmartMeterDiscoveryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._schema = vol.Schema({
            vol.Required(CONF_SOURCE_BROKER): str,
            vol.Required(CONF_SOURCE_PORT, default=8883): int,
            vol.Optional(CONF_SOURCE_USER): str,
            vol.Optional(CONF_SOURCE_PASS): str,
            vol.Required(CONF_SOURCE_TOPIC): str,
            vol.Required(CONF_TARGET_BROKER): str,
            vol.Required(CONF_TARGET_PORT, default=1883): int,
            vol.Optional(CONF_TARGET_USER): str,
            vol.Optional(CONF_TARGET_PASS): str,
            vol.Required(CONF_TARGET_TOPIC): str,
        })

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Smart Meter Bridge", data=user_input)
        return self.async_show_form(step_id="user", data_schema=self._schema)
