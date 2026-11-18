# LinknLink iSG

Home Assistant custom integration for LinknLink iSG. It controls the screen and media volume of the iSG that is running this Home Assistant instance, by calling the local `isgandroidcontrol` service on `127.0.0.1`. It does not use ADB.

## Requirements

1. Home Assistant on the iSG (Termux / proot), with [HACS](https://hacs.xyz/) installed.
2. The `isgandroidcontrol` service installed and running on the same device, managed by isgservicemanager. It listens on `http://127.0.0.1:18951`.

## Install

1. In iSG (isgmanager / 版本管理), install or upgrade the **iSG Android Control** (`isgandroidcontrol`) extension and start it if it is not already running.
2. In Home Assistant, open HACS → Integrations → Custom repositories, add:

   `https://github.com/linknlink/isg-ha`

   as an Integration, then download **LinknLink iSG**.
3. Restart Home Assistant.
4. Go to Settings → Devices & services → Add integration → **LinknLink iSG**. Keep the default host `127.0.0.1` and port `18951` unless you changed the service listen address.

## Entities

| Entity | Description |
| --- | --- |
| Screen (switch) | Turns the iSG display on or off |
| Volume (number, 0–100%) | Media volume (STREAM_MUSIC). On iSG SE this is the HDMI volume |
| Brightness (number, 0–255) | Display brightness, when the device reports it |

## Notes

This integration is for Home Assistant running **on the iSG itself**. It talks only to localhost and never opens an ADB port.
