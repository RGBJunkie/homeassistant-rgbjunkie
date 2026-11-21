# RGBJunkie Lights3D for Home Assistant

Control [RGBJunkie Lights3D](https://github.com/RGBJunkie/RGBJunkie-Layout3D) from Home Assistant.

Home Assistant sees:

- **The whole desk** as one device (on/off, brightness, scene, desk effect, pause)
- **Each controller** as its own device (brightness + effect, including “Use desk effect”)

Lights3D keeps owning USB. This integration only talks to the LAN bridge.

## Requirements

- Lights3D with the Home Assistant bridge enabled (**Settings → Remote**)
- Home Assistant on the same network
- Bridge port **14224** and the token from Lights3D

## Install with HACS

1. HACS → Integrations → ⋮ → **Custom repositories**
2. Add `https://github.com/RGBJunkie/homeassistant-rgbjunkie` as category **Integration**
3. Install **RGBJunkie Lights3D**
4. Restart Home Assistant
5. **Settings → Devices & services → Add integration → RGBJunkie Lights3D**
6. Enter the PC’s IP, port `14224`, and the token from Lights3D

## Manual install

Copy `custom_components/rgbjunkie` into your Home Assistant `config/custom_components/` folder, restart, then add the integration.

## Lights3D setup

1. Open **Settings → Remote** in Lights3D
2. Turn on **Allow Home Assistant to control this desk**
3. Copy the token

More detail: [INFO.md](INFO.md)

## Support

- App issues: [RGBJunkie-Layout3D](https://github.com/RGBJunkie/RGBJunkie-Layout3D/issues)
- Integration issues: use this repo’s Issues
