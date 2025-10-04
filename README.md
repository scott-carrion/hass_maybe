# Maybe Finance HA Integration

This integration adds all datapoints from the Maybe Finance API endpoint `/api/v1/budget/summary` to Home Assistant.

While the original Maybe Finance project was discontinued, Scott Carrion's actively maintained fork is available.

The monthly budget checking API endpoint is only available via [this fork](https://github.com/scott-carrion/maybe).

### Installation

Copy this folder to `<config_dir>/custom_components/hass_maybe/`.

Restart Home Assistant, then go to "Settings > Devices and Services > Add Integration" and search for "Maybe Finance"

A dialog box will appear prompting for a URL and an API key. The URL is the base url of where Maybe is hosted, e.g. "https://maybe.example.com"

The API key is generated from within Maybe itself. See the above link to the fork for more information.

### What Becomes Possible

Create dashboards with the Home Assistant UI to get an at-a-glance look at your monthly budget from anywhere.

<img width="1598" height="840" alt="image" src="https://github.com/user-attachments/assets/5bde4a74-1382-4426-a0f4-e645e128360e" />
<img width="1596" height="843" alt="image" src="https://github.com/user-attachments/assets/70e45098-203c-4730-b883-aa6de925ed41" />
<img width="1595" height="837" alt="image" src="https://github.com/user-attachments/assets/aac01aee-a986-4416-9d86-83a8b3aa2a7b" />
