# Home Assistant + Lights3D

Control your desk from Home Assistant. Lights3D owns the USB devices. HA talks to a small LAN bridge on the PC running Lights3D.

## What you get

- **Desk blob**: one device for the whole desktop (on/off, brightness, scene, desk effect, pause, next/previous buttons, health sensors).
- **Each device**: one HA device per online controller, with brightness and an effect select (including **Use desk effect**).

## Setup in Lights3D

1. Open **Settings → Remote**.
2. Turn on **Allow Home Assistant to control this desk**.
3. Copy the **token**.
4. Note the port (**14224**) and this PC’s LAN IP (the address other machines on your network use to reach it).

Leave the bridge off when you are not using Home Assistant.

## Install the HA integration

Preferred: add this GitHub repo as a HACS custom repository (category **Integration**), install **RGBJunkie Lights3D**, restart, then add the integration.

Manual: copy `custom_components/rgbjunkie` into Home Assistant’s `custom_components` folder, restart, then add the integration.

1. **Settings → Devices & services → Add integration → RGBJunkie Lights3D**
2. Enter host (PC LAN IP), port `14224`, and the token

## Notes

- State updates about every 2 seconds.
- Device brightness scales the parts bound to that controller. Desk brightness is still the global scale.
- Per-device effects use the same scopes as Controllers / Effects in Lights3D.
- Do not run another lighting app against the same hardware while Lights3D is driving it.
- If the token changes, use **Reconfigure** on the integration (or accept the reauth prompt).

## Diagnostics

Download diagnostics from the integration’s device page. The token is redacted.
