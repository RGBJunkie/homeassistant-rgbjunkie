# RGBJunkie Lights3D for Home Assistant

Control [RGBJunkie Lights3D](https://github.com/RGBJunkie/RGBJunkie-Layout3D) from Home Assistant over your LAN.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Validate](https://github.com/RGBJunkie/homeassistant-rgbjunkie/actions/workflows/validate.yml/badge.svg)](https://github.com/RGBJunkie/homeassistant-rgbjunkie/actions/workflows/validate.yml)
[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=rgbjunkie)

Lights3D keeps owning USB. This integration only talks to the token-gated bridge on your PC.

## What you get

- **The whole desk** as one device: on/off, brightness, scene, desk effect, pause, next/previous, health sensors
- **Each controller** as its own device: brightness + effect (including **Use desk effect**)

## Requirements

- Lights3D with the Home Assistant bridge enabled (**Settings → Remote**)
- Home Assistant **2024.11** or newer on the same network
- Bridge port **14224** and the token from Lights3D

## Install with HACS

1. HACS → Integrations → ⋮ → **Custom repositories**
2. Add `https://github.com/RGBJunkie/homeassistant-rgbjunkie` as category **Integration**
3. Install **RGBJunkie Lights3D**
4. Restart Home Assistant
5. **Settings → Devices & services → Add integration → RGBJunkie Lights3D**
6. Enter the PC’s LAN IP, port `14224`, and the token from Lights3D

Or use the My Home Assistant button above after the integration is installed.

## Manual install

1. Copy `custom_components/rgbjunkie` into your Home Assistant `config/custom_components/` folder
2. Restart Home Assistant
3. Add the integration as above

## Lights3D setup

1. Open **Settings → Remote** in Lights3D
2. Turn on **Allow Home Assistant to control this desk**
3. Copy the token
4. Use this PC’s LAN IP (not `127.0.0.1` unless Home Assistant runs on the same machine)

Leave the bridge off when you are not using Home Assistant.

## Entities

| Area | Entities |
| --- | --- |
| Desk | Light (on/off + brightness), Scene select, Effect select, Paused switch, Next/Previous effect & scene, Devices online/total, Effect FPS |
| Each device | Brightness light, Effect select |

State refreshes about every 2 seconds. Scene and effect lists come from Lights3D’s catalogs.

## Troubleshooting

- **Could not reach Lights3D**: bridge off, wrong IP, or firewall blocking TCP `14224`
- **Token rejected**: copy a fresh token from **Settings → Remote**, or use **Reconfigure** / reauth on the integration
- **Empty scene/effect lists**: wait a few polls after Lights3D finishes loading, or restart Lights3D with the bridge on
- **Off then on jumps to a low brightness**: fixed in current builds; update Lights3D and this integration

More detail: [INFO.md](INFO.md)

## Support

- Lights3D app: [RGBJunkie-Layout3D issues](https://github.com/RGBJunkie/RGBJunkie-Layout3D/issues)
- This integration: [Issues](https://github.com/RGBJunkie/homeassistant-rgbjunkie/issues)

## License

MIT
