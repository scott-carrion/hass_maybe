"""Platform for sensor integration."""
from __future__ import annotations
import logging
from datetime import timedelta

import async_timeout
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_URL, CURRENCY_DOLLAR, PERCENTAGE
import httpx

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    url = config_entry.data[CONF_URL]
    api_key = config_entry.data[CONF_API_KEY]

    # The coordinator object is responsible for fetching data from the API endpoint
    # The URL is expected to be the base URL of the Maybe instance (path is appended later)
    coordinator = MaybeFinanceCoordinator(hass, url, api_key)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as e:
        raise ConfigEntryNotReady("Failed to contact Maybe finance") from e

    # Sensors capturing data from "totals" tree of API endpoint payload data
    _LOGGER.debug("Creating TotalSensors")
    entities = [
        # For "money_allocated" (Total budgeted spending for the month)
        MaybeFinanceTotalSensor(coordinator, "money_allocated",
                                "Total Budget"),

        # For "money_spent" (Total money spent for the month)
        MaybeFinanceTotalSensor(coordinator, "money_spent", "Total Money Spent"),

        # For "money_available" (Total money left in budget for the month)
        MaybeFinanceTotalSensor(coordinator, "money_available",
                                "Total Budget Remaining"),

        # For "percent_spent" (Percent of budget remaining for the month)
        MaybeFinanceTotalSensor(coordinator, "percent_spent",
                                "Percent of Total Budget Spent", unit=PERCENTAGE),

        # For "percent_overage" (Budget overage percent)
        MaybeFinanceTotalSensor(coordinator, "percent_overage",
                                "Total Budget Overage Percent", unit=PERCENTAGE)
    ]

    # Create sensors for each budget category
    if coordinator.data and "categories" in coordinator.data:
        _LOGGER.debug("Creating CategorySensors")
        for category in coordinator.data["categories"]:
            category_name = category["name"]

            # For "money_spent" (Money spent for the month in this category)
            entities.append(
                MaybeFinanceCategorySensor(coordinator, category_name, f"Money Spent: '{category_name}'",
                                           "money_spent")
            )

            # For "money_available" (Money left in budget for the month in this category)
            entities.append(
                MaybeFinanceCategorySensor(coordinator, category_name, f"Budget Remaining: '{category_name}'",
                                           "money_available")
            )

            # For "percent_spent" (Percent of budget reamining for the month in this category)
            entities.append(
                MaybeFinanceCategorySensor(coordinator, category_name, f"Percent Budget Spent: '{category_name}'",
                                           "percent_spent", unit=PERCENTAGE)
            )

    async_add_entities(entities)

class MaybeFinanceCoordinator(DataUpdateCoordinator):
    """A coordinator to fetch data from the Maybe Finance API."""

    def __init__(self, hass, url, api_key):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Maybe Finance Sensor",
            update_interval=timedelta(minutes=15),
        )
        self.api_url = f"{url}/api/v1/budget/summary"
        self.headers = {"X-Api-Key": api_key}

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            # FIXME: The httpx.AsyncClient apparently contains a blocking call to verify SSL certificates which hurts performance
            # Home Assistant complains about this. Warning message is below
            # WARNING (MainThread) [homeassistant.util.loop] Detected blocking call to load_verify_locations with args (<ssl.SSLContext object at 0x7ff1bd9300f0>,
            #'/usr/local/lib/python3.13/site-packages/certifi/cacert.pem', None, None) inside the event loop by custom integration 'hass_maybe' at
            # custom_components/hass_maybe/sensor.py, line 102: async with httpx.AsyncClient() as client, async_timeout.timeout(10):
            # (offender: /usr/local/lib/python3.13/ssl.py, line 717: context.load_verify_locations(cafile, capath, cadata))
            async with httpx.AsyncClient() as client, async_timeout.timeout(10):
                response = await client.get(self.api_url, headers=self.headers)
                response.raise_for_status()
                _LOGGER.debug(f"API response JSON dump: {response.json()}")
                return response.json()
        except httpx.HTTPStatusError as err:
            raise UpdateFailed(f"Error communicating with Maybe Finance API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"An unexpected error occurred: {err}") from err


class MaybeFinanceTotalSensor(CoordinatorEntity, SensorEntity):
    """Representation of a total budget sensor."""

    def __init__(self, coordinator, data_key, name, unit=CURRENCY_DOLLAR):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = name
        self._attr_unique_id = f"maybe_finance_{data_key.replace('.', '_')}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = "mdi:cash"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            ret = self.coordinator.data["totals"][self._data_key]
            _LOGGER.debug(f"Value for TotalSensor '{self.name}' : {ret}")
            return ret
        _LOGGER.error(f"TotalSensor for '{self.name}' did not find corresponding data in API response!")
        return None

class MaybeFinanceCategorySensor(CoordinatorEntity, SensorEntity):
    """Representation of a budget category sensor."""

    def __init__(self, coordinator, category_name, name, data_key, unit=CURRENCY_DOLLAR):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._category_name = category_name
        self._attr_name = name
        self._data_key = data_key
        self._attr_unique_id = f"maybe_finance_{category_name.replace(' ', '_')}_{data_key.replace('.', '_')}"
        # TODO: ADD EURO SUPPORT
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = "mdi:cash-multiple"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and "categories" in self.coordinator.data:
            for category in self.coordinator.data["categories"]:
                if category["name"] == self._category_name:
                    ret = category[self._data_key]
                    _LOGGER.debug(f"Value for CategorySensor '{category["name"]}' : {ret}")
                    return ret
        else:
            _LOGGER.error("API response did not contain 'categories'!")

        _LOGGER.error(f"CategorySensor for '{self._category_name}' did not find corresponding data in API response!")
        return None
