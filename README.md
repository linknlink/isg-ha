# LinknLink iSG

<img src="custom_components/isg/brand/icon.png" width="96" alt="LinknLink iSG icon">

Home Assistant custom integration for LinknLink iSG. It controls the screen, media volume, and brightness of the iSG that is running this Home Assistant instance, by calling the local `isgandroidcontrol` service on `127.0.0.1`. It does not use ADB.

This integration is preinstalled by isgservicemanager on the iSG. It is only for Home Assistant running on the iSG itself. It is not installed or updated through HACS.

## Requirements

1. Home Assistant on the iSG (Termux / proot).
2. The `isgandroidcontrol` service on the same device. It is a default-installed infrastructure service managed by isgservicemanager, and listens on `http://127.0.0.1:18951`.

## Install

On current iSG firmware, **LinknLink iSG** is installed and configured automatically by isgservicemanager as a default infrastructure service, together with `isgandroidcontrol`. After Home Assistant is running, the integration appears under Settings → Devices & services with the default host `127.0.0.1` and port `18951`.

You do not need to add a HACS custom repository or install this integration by hand. Updates are delivered through iSG version management, not HACS.

## Entities

| Entity | Description |
| --- | --- |
| Screen (switch) | Turns the iSG display on or off |
| Volume (number, 0–100%) | Media volume (STREAM_MUSIC). On iSG SE this is the HDMI volume |
| Brightness (number, 0–255) | Display brightness, when the device reports it |

## Notes

This integration is for Home Assistant running **on the iSG itself**. It talks only to localhost and never opens an ADB port.
