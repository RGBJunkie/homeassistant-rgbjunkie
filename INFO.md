# Home Assistant + Lights3D

Control your desk from Home Assistant without OpenRGB. Lights3D owns the USB devices. HA talks to a small LAN bridge.

## What you get

- **Desk blob**: one device for the whole desktop (on/off, brightness, scene, desk effect, pause, next/previous buttons, health sensors).
- **Each device**: one HA device per online controller, with brightness and an effect select (including **Use desk effect**).

## Setup in Lights3D

1. Open **Settings → Remote**.
2. Turn on **Allow Home Assistant to control this desk**.
3. Copy the **token**.
4. Note the port (**14224**) and this PC’s LAN IP.

Leave the bridge off when you are not using Home Assistant.

## Install the HA integration

1. Copy `homeassistant/custom_components/rgbjunkie` into your Home Assistant `custom_components` folder (or add this repo as a HACS custom repository pointing at that folder).
2. Restart Home Assistant.
3. **Settings → Devices & services → Add integration → RGBJunkie Lights3D**.
4. Enter host (PC IP), port `14224`, and the token.

## Notes

- State updates about every 2 seconds.
- Device brightness scales the parts bound to that controller. Desk brightness is still the global scale.
- Per-device effects use the same scopes as the Controllers / Effects UI in Lights3D.
- Do not run OpenRGB against the same hardware while Lights3D is driving it.
