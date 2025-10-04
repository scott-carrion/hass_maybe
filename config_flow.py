"""Config flow for Maybe Finance integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_URL

class MaybeFinanceConfigFlow(config_entries.ConfigFlow, domain="maybe_finance"):
    """Handle a config flow for Maybe Finance."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # You can add validation here if needed
            return self.async_create_entry(title="Maybe Finance", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_URL): str,
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors
        )
