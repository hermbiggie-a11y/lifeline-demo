# Lifeline: technical notes

How Lifeline is put together, what data it uses and what it has been measured to do. Setup is in
[README.md](README.md); the run-and-reset checklist is in [docs/CHECKLIST.md](docs/CHECKLIST.md).

## 1. What it is

An earthquake rescue-planning agent that runs entirely on the Dell Pro Precision GB10. It ranks damaged
buildings from satellite damage grading, estimates how many people are inside, routes three rescue
teams with OR-Tools, takes signs of life from Telegram reports and (simulated) sensors, and asks a
human to approve every move. The only network traffic at runtime is Telegram delivery.

> Satellites tell you which building. The building tells you how many. The optimiser tells you
> who goes first. People and sensors tell you who is alive.

## 2. Run it

```bash
# optional: export LIFELINE_CHAT_ID set to your Telegram group ID; without it heartbeats print only
./start.sh --reset     # sensors, toolbox (:8090), optional live WiFi sensor, agent loop
./stop.sh
./reset.sh             # replay back to 04:17
./leak_test.sh         # security proof (agent refuses + OpenShell DENIED)
./install_agent.sh     # re-upload agent files after a sandbox rebuild
```

Screens (on the GB10, offline-capable):
- `http://localhost:8090/app`: Lifeline Command front end (designed as a Claude artifact, wired to the backend)
- `http://localhost:8090/`: operations dashboard (Leaflet, zoomable satellite tiles when built, swipe, proof panel, live radar)
- `http://localhost:3000/ui/index.html`: RuView's own UI (Docker container `ruview`, optional)

Telegram: use your own bot (see README, Setup). Add the bot to a group, send a message, find the group
ID in the OpenClaw session list, and start with that ID in `LIFELINE_CHAT_ID`.

Commands (Telegram, the /app chat or the dashboard box): `help`, `status`, `who is alive`,
`ack 5`, `ack all`, `scan 7`, `report 8 tapping heard`, `report 8 silence`, `go Malatya`, `go live`.
Free questions go to the local qwen agent.

## 3. Architecture

```
Copernicus EMSR648 grading -> build_sites.py -> data/regions/<r>/sites.json
Maxar COGs (windowed reads) -> make_chips.py / make_tiles.py -> chips + XYZ tiles (built by you, not shipped)
OSM footprint of your building -> build_live.py -> data/regions/live (optional live drill)
replay_sensors.py (10 s) + ruview_live.py (GB10 WiFi RSSI, RuView classifier) -> sensors
engine.py: ranking, occupancy estimate, reports, survivor logic, escalation, alerts, Telegram text
routing.py: OR-Tools VRP, re-solved on every tick and report
toolbox.py: FastAPI :8090, serves /app, /, all API endpoints
run_loop.sh -> sync.py every 30 s: read commands from the Telegram chat transcript, push brief/status/
  alerts/help files into the sandbox, wake the agent on new alerts, export chat for the screens
OpenClaw agent (qwen3.5:9b-128k via Ollama) inside the NemoClaw/OpenShell sandbox "my-assistant"
```

Key endpoints: `/map /brief /alerts /chat /site /assess /livesignal /regions /proof /livetest`
and POST `/command /ack /scan /report /region /delivered /reset /livetest /calibrate`.

## 4. Data (real, labeled)

| Region | Source | Notes |
|---|---|---|
| Malatya, Adiyaman, Kahramanmaras, Antakya, Gaziantep | Copernicus EMS EMSR648 AOI05/02/04/11/01 grading; Maxar Open Data before/after imagery if you build it | 16 sites each (Gaziantep 14), densest destroyed cluster |
| live (optional) | OpenStreetMap footprint of the building where your GB10 is | live drill, no damage data, no imagery |

Occupancy = footprint x built share (0.5 for blocks) x floors (4 assumed) / 30 m2 per person x
night factor. Labeled "estimate, not a count". Routing weight = occupancy x trapped share
(50/15/3% by grade), decaying with time; a reported or sensed survivor outranks everything.

## 5. Measured results (shown on the dashboard Proof panel)

- Local AI vision vs Copernicus, blind, 60 buildings: 89% of damaged flagged, but 89% false alarms
  on undamaged controls. So the ranking uses expert grades, never the AI.
- Live WiFi test (uncalibrated run): walking caught 15/15 s, false alarms 26/30 s still.
  The test now calibrates on its first 20 s; a calibrated run has not been recorded.
- Leak test: agent refuses; direct curl from the sandbox DENIED by OpenShell policy.

## 6. Sandbox configuration used

- NemoClaw network policy: only the `local-inference` and `telegram` presets active (others such as
  openclaw-pricing, huggingface, brew, npm and pypi removed).
- Telegram channel added to the sandbox (`channels add telegram`, `TELEGRAM_REQUIRE_MENTION=0`), then the
  sandbox rebuilt. The bot token lives only in the OpenShell credential store.
- OpenClaw: `tools.deny = ["message"]` (stops "Message failed"; replies are still delivered).
- Sandbox workspace `AGENTS.md` and `HEARTBEAT.md` replaced by the files in `skill/`; OpenClaw's
  default versions are in `demo/backup/`.
- The user running Lifeline needs Docker group access (use `sg docker -c "..."` in shells opened before
  the group was added).
- RuView container (optional): localhost-only, API token in `ruview.token` (git-ignored), cloud registry
  and mDNS disabled.

## 7. Known limits and gotchas

- The 9B model fumbles tool calls (path prefixes, message tool, empty replies after exec). The design
  works around it: the agent only reads files and replies; commands are read from the chat
  transcript by sync.py; all numbers are pre-rendered by the engine.
- WiFi RSSI sees movement only: no counting, no still people, no breathing. Real CSI needs dedicated
  CSI sensors (for example ESP32-S3).
- Telegram confirmation uses "two reports 20 s apart": the transcript carries no sender ID.
- NemoClaw snapshots fail on symlinks in the workspace; sync.py writes real file copies instead.
- `nemoclaw status`/snapshot need Docker group access.
- /app labels overlap where buildings are close; only its Routes tab was checked in a browser.
