# DoorDash Tracker for Home Assistant

Follow a **DoorDash Drive** tracking link (the `drd.sh/…` short link or `doordash.com/orders/drive?urlCode=…` link sent by SMS) inside Home Assistant, with an optional blueprint that shows a temporary takeover on a **Vestaboard Note**.

> Unofficial. DoorDash has no consumer API; this reads the public tracking page that the link opens. It works only for Drive links (merchant-dispatched orders), not orders placed in the DoorDash app.

## Install (HACS custom repository)

1. HACS → ⋮ → **Custom repositories** → add `https://github.com/thrivestorm2/ha-doordash-tracker`, category **Integration**.
2. Install **DoorDash Tracker**, then restart Home Assistant.
3. Settings → Devices & Services → **Add Integration** → DoorDash Tracker.

The integration's icon ships in `custom_components/doordash_tracker/brand/` and appears in Home Assistant 2026.3 or later. Older versions show a placeholder.

## Entities

| Entity | Purpose |
|---|---|
| `text.doordash_tracker_tracking_url` | Paste the tracking link here, or call `text.set_value`. A `drd.sh` short link or the whole SMS text works too; short links are followed to find the tracking code. Clears itself when done. |
| `button.doordash_tracker_stop_tracking` | Stop tracking now: clears the link and sets the sensor to `idle`. |
| `button.doordash_tracker_refresh_now` | Poll the tracking page now instead of waiting for the next minute. |
| `sensor.doordash_tracker_status` | `1`–`4` (step), `idle`, or `error`. Attributes: `label`, `detail`, `eta`, `destination` (drop-off address, when the page shows one), `tracking`. |

**Entity IDs:** from v0.1.6 they're always the ones above, even if the device is in an area or renamed. Installs from older versions may have a prefix such as `text.outside_doordash_tracker_tracking_url`. Rename those to the IDs above (entity ⚙️ → Entity ID), or the iOS shortcut and the blueprint defaults won't find them.

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

**Stopping early:** pressing **Stop tracking** while the order is on the board hands the board back right away instead of waiting out the display time.

**Exclusions:** any `input_boolean` helpers you list, such as ninja mode, storm alert or a live game, skip the takeover entirely.

## iOS: drop the link automatically

[![Add Shortcut](https://img.shields.io/badge/iOS%20Shortcut-Add%20to%20iPhone-0A84FF?logo=apple&logoColor=white)](https://www.icloud.com/shortcuts/33705eb0d65b4394bebd220537887b53)

1. **Add the shortcut:** tap the button above on your iPhone, then **Add Shortcut**. Choose your own Home Assistant server when asked, or the first time it runs.
2. **Create the trigger** (Apple doesn't allow automations to be shared): Shortcuts → **Automation** → **+** → **Message** → **Message Contains** `drd.sh` → **Run Immediately** → **Run Shortcut: DoorDash → Home Assistant**, with the message as input. Use `doordash.com/orders/drive` instead if your texts carry the long link.

You can also share a DoorDash text to the shortcut from the share sheet.

<details>
<summary>What the shortcut does, or how to build it yourself</summary>

1. **Receive** Text and URLs from Share Sheet.
2. **Get URLs from** Shortcut Input.
3. **Get First Item from** URLs.
4. **Text:**
   ```json
   {"entity_id": "text.doordash_tracker_tracking_url", "value": "<Item from List>"}
   ```
   Insert **Item from List** as a variable between the last two quotes.
5. **Home Assistant → Perform action:** action **Set text value**, with only the **Text** variable from step 4 as the action data.

This is the setup confirmed working: build the JSON in its own Text step, then pass that Text variable as the whole action data.

The integration finds the tracking link inside any text, so sending the whole message works too.
</details>

## License

MIT
