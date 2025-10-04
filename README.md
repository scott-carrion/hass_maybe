# Maybe Finance HA Integration

This integration adds all datapoints from the Maybe Finance API endpoint `/api/v1/budget/summary` to Home Assistant.

While the original Maybe Finance project was discontinued, Scott Carrion's actively maintained fork is available.

The monthly budget checking API endpoint is only available via [this fork](https://github.com/scott-carrion/maybe).

### Installation

Copy this folder to `<config_dir>/custom_components/hass_maybe/`.

Restart Home Assistant, then go to "Settings > Devices and Services > Add Integration" and search for "Maybe Finance"

A dialog box will appear prompting for a URL and an API key. The URL is the base url of where Maybe is hosted, e.g. "https://maybe.example.com"

The API key is generated from within Maybe itself. See the above link to the fork for more information.
