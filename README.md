# DoorDash Tracker for Home Assistant

Follow a **DoorDash Drive** tracking link (the `doordash.com/orders/drive?urlCode=…` link sent by SMS) inside Home Assistant, with an optional blueprint that shows a temporary takeover on a **Vestaboard Note**.

> Unofficial. DoorDash has no consumer API; this reads the public tracking page that the link opens. It works only for Drive links (merchant-dispatched orders), not orders placed in the DoorDash app.

## Install (HACS custom repository)

1. HACS → ⋮ → **Custom repositories** → add `https://github.com/thrivestorm2/ha-doordash-tracker`, category **Integration**.
2. Install **DoorDash Tracker**, then restart Home Assistant.
3. Settings → Devices & Services → **Add Integration** → DoorDash Tracker.

The integration's icon ships in `custom_components/doordash_tracker/brand/` and appears in Home Assistant 2026.3 or later. Older versions show a placeholder.

## Entities

| Entity | Purpose |
|---|---|
| `text.doordash_tracker_tracking_url` | Paste the tracking link here, or call `text.set_value`. Clears itself when done. |
| `sensor.doordash_tracker_status` | `1`–`4` (step), `idle`, or `error`. Attributes: `label`, `detail`, `eta`, `destination` (drop-off address, when the page shows one), `tracking`. |

**Polling:** once a minute, only while a link is set.

**Auto-reset:** the link clears itself in three cases:
- 10 minutes after delivery
- after 10 minutes of continuous errors
- 2 hours after the link was set

`error` with `detail: no step found` usually means an expired link or an anti-bot challenge.

## Vestaboard Note blueprint

[![Import blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fthrivestorm2%2Fha-doordash-tracker%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fdoordash_tracker%2Fvestaboard_note_display.yaml)

**Manual import:** if the button doesn't open your Home Assistant, go to **Settings → Automations & scenes → Blueprints → Import blueprint** and paste this URL:

```
https://github.com/thrivestorm2/ha-doordash-tracker/blob/main/blueprints/automation/doordash_tracker/vestaboard_note_display.yaml
```

Or copy the file into your config as `blueprints/automation/doordash_tracker/vestaboard_note_display.yaml`, then reload automations under **Developer tools → YAML**.

**What it shows**, on each status, label or ETA change, for a configurable time (default 3 minutes):

```
{63} ETA 12:41 PM{63}
{63} TO THE STORE{63}
{66}{66}{66} {65}{65}{65} {69}{69}{69} {69}{69}{69}
```

**Handing the board back:** when the time is up, it re-runs your chosen day or night automation with that automation's own conditions in force.

**ETA rate limit:** an ETA-only change that arrives within the minimum interval (default 120 s) of the last board write is ignored. Status and label changes always go through.

**Address filter:** set **Only for deliveries to this address** to the house number and street where the Note hangs, e.g. `123 Main`, and orders going anywhere else leave the board alone. Matching ignores case, spaces and punctuation, and starts at a whole word, so `12 Main` won't match `112 Main`. If the page doesn't show an address, the takeover is skipped by default; you can change that to **Show anyway**.

**Exclusions:** any `input_boolean` helpers you list, such as ninja mode, storm alert or a live game, skip the takeover entirely.

## iOS: drop the link automatically

Create a Shortcuts automation with these steps:
1. **Trigger:** Message received, with "doordash.com/orders/drive" in the text.
2. **Get URLs from Input.**
3. **Home Assistant → Perform Action:** `text.set_value` on `text.doordash_tracker_tracking_url`.

## License

MIT
