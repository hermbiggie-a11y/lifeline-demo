# Lifeline: earthquake rescue planning on a Dell Pro Precision GB10

Lifeline is a rescue-planning agent that works in a Telegram group. Using open data from a past
earthquake (the 6 February 2023 earthquake in Türkiye), it ranks damaged buildings by how likely they
are to hold people, proposes dispatches for three rescue teams and tracks simulated life-sign sensors
at each site. Every model call runs locally on one Dell Pro Precision GB10, and the incident commander
approves every dispatch and every survivor alert.

## Watch it first

The overview video is under [Releases](../../releases).

## The stages

| Stage | What happens | Check or human gate |
|---|---|---|
| 1. Load the incident | The toolbox ranks graded buildings for the chosen region (Copernicus EMS damage grading, occupancy estimate, time since the earthquake). | Check: `curl localhost:8090/brief` returns a ranked brief from replay data. |
| 2. Plan who goes first | OR-Tools routes teams T1-T3; the agent posts the dispatch proposals in the group on its own. | Human gate: no team moves until the commander replies `ack <building>` or `ack all`. |
| 3. Signs of life | A team member reports `report 8 tapping heard`, or a simulated sensor picks up a signal (`replay_sensors.py --trigger`). Two reports at least 20 s apart, or two sensors, confirm a survivor and the routes are re-planned. | Check: an alert with "NEEDS YOUR ACK" within one loop and a map pulse within 5 s. Human gate: the commander acks the new plan. |
| 4. Escalation | Simulated breathing falls (`replay_sensors.py --decline`); the site goes to priority 1 without being asked. | Check: automatic escalation and alert. Human gate: the commander acks. |
| 5. Questions | `status`, `who is alive`, or a free question such as "Is Building 12 empty?". | Check: `status` in Telegram matches `brief.json` exactly. The agent never calls a building empty, clear or safe. |
| 6. Second opinion (optional) | The local model reads before/after satellite chips of a building (`/assess`). | Check: shown as a second opinion only, never used in ranking. Needs imagery you build yourself (Setup, step 7). |
| 7. Live drill (optional) | `go live` links Building 1 to a live WiFi sensor near your GB10. | Check: movement only; see Known limits. |
| 8. Nothing leaves the box | `./leak_test.sh` asks the agent to send the survivor list to an outside URL, then tries it directly from the sandbox. | Check: the agent refuses and OpenShell logs the request as DENIED. |

## Hardware

**Built and run on**

| Component | Built and run on |
|---|---|
| System | Dell Pro Precision GB10 |
| GPU (with memory) | NVIDIA GB10 Grace Blackwell superchip, 128 GB unified LPDDR5x (shared by CPU and GPU) |
| CPU | 20-core NVIDIA Grace Arm CPU |
| Memory | 128 GB unified LPDDR5x (shared by CPU and GPU) |
| Storage | 4 TB NVMe SSD |
| OS | NVIDIA DGX OS |
| Software | Ollama qwen3.5:9b-128k (local), OpenClaw agent in OpenShell sandbox, Google OR-Tools routing, FastAPI toolbox, RuView v1 WiFi pipeline, Telegram Bot API |

## What's in this repo

| Path | What |
|---|---|
| `engine.py` | Ranking, occupancy estimate, reports, survivor logic, escalation, alerts and the Telegram text |
| `routing.py` | OR-Tools vehicle-routing model for the three rescue teams |
| `toolbox.py` | FastAPI toolbox on port 8090: API, dashboard and front end |
| `sync.py`, `run_loop.sh` | Loop that moves the brief into the agent sandbox and reads the commander's commands every 30 s |
| `replay_sensors.py` | Simulated life-sign sensors (labeled `replay`) and the demo controls |
| `ruview_live.py` | Optional live WiFi sensing near the GB10 with RuView's RSSI classifier |
| `start.sh`, `stop.sh`, `reset.sh` | Start, stop and reset the replay to 04:17 |
| `install_agent.sh` | Uploads the agent files into the OpenClaw sandbox |
| `leak_test.sh` | Security check: the agent refuses and OpenShell blocks an outside URL |
| `build_sites.py` | Builds `data/regions/<region>/sites.json` from Copernicus EMS EMSR648 grading |
| `make_chips.py`, `make_tiles.py` | Optional: cut before/after chips and map tiles from Maxar Open Data imagery |
| `build_live.py` | Optional: builds the live-drill region from your building's OpenStreetMap footprint |
| `validate_vision.py` | Blind test of the local vision model against Copernicus grades |
| `skill/` | The agent brief and prompts: `AGENTS.md`, `HEARTBEAT.md`, `SKILL.md`, `playbook.md`, sample `brief.json` |
| `map/` | Dashboard (`index.html`), Lifeline Command front end (`command.html`) and vendored Leaflet 1.9.4 |
| `data/regions/` | Pre-built sites for Kahramanmaras, Malatya, Adiyaman, Antakya and Gaziantep |
| `data/validation_*.json` | Recorded results of the vision test and the live WiFi test |
| `demo/backup/` | OpenClaw's default workspace files, kept for restoring the sandbox |
| `HANDOFF.md` | Technical notes: architecture, data, measured results, sandbox configuration |
| `docs/CHECKLIST.md` | Run-and-reset checklist with fallbacks |

## Setup

Linux (NVIDIA DGX OS on the Dell Pro Precision GB10). Internet is needed only for installing and building.

1. Install **Ollama** and make the model `qwen3.5:9b-128k` available to it. `start.sh` keeps it loaded on the GPU.
2. Install **NemoClaw** with **OpenClaw** and **OpenShell**, and create a sandbox named `my-assistant`
   (the scripts use `LIFELINE_SANDBOX`, default `my-assistant`; the dashboard's free-question box always
   uses `my-assistant`). Leave only the `local-inference` and `telegram` network policy presets active.
   See [HANDOFF.md](HANDOFF.md), section 6, for the sandbox settings used.
3. Create your own Telegram bot with **BotFather**. Put its token in an environment variable for the
   sandbox's Telegram channel set-up (`channels add telegram`) and rebuild the sandbox; the token then lives
   only in the OpenShell credential store. Create a group, add the bot, send a message, find the group ID
   in the OpenClaw session list and set it in `LIFELINE_CHAT_ID`. No bot, token or group ID ships with this
   repo. `start.sh` and `run_loop.sh` clear any `*_TOKEN` and `*API_KEY*` variables from Lifeline's own processes.
4. Create the Python environment in the repo folder:
   ```bash
   python3 -m venv .venv && .venv/bin/pip install fastapi uvicorn numpy pillow pyshp httpx rasterio scikit-image ortools
   ```
5. Upload the agent files into the sandbox: `./install_agent.sh`.
6. Start it: `./start.sh --reset`, then open `http://localhost:8090/` (dashboard) or `http://localhost:8090/app`.
   Demo controls from another terminal:
   ```bash
   .venv/bin/python replay_sensors.py --trigger B-06 --bpm 14 --moving false   # signs of life
   .venv/bin/python replay_sensors.py --decline B-06 --to 8 --over 60          # breathing falls
   ./reset.sh                                                                 # back to 04:17
   ./stop.sh
   ```
   Telegram commands: `help`, `status`, `who is alive`, `ack 5`, `ack all`, `scan 7`, `report 7 tapping heard`,
   `go Malatya`, `go live`.
7. Optional, satellite imagery: the Maxar imagery is not included (it is licensed CC BY-NC 4.0, non-commercial
   only). Get it from the **Maxar Open Data Program** (collection `Kahramanmaras-turkey-earthquake-23`):
   save the collection index as `data/raw/maxar.tsv` (the STAC fields `make_chips.py` reads), then run
   `.venv/bin/python make_chips.py --all` and `.venv/bin/python make_tiles.py --all`. Without imagery the map
   uses a dark background and `/assess` returns the Copernicus grade.
8. Optional, rebuild the sites: put the Copernicus EMS EMSR648 grading products in `data/raw/aoiXX/` and run
   `.venv/bin/python build_sites.py --all`. The five regions are already built in `data/regions/`.
9. Optional, RuView sensing server (simulated CSI), localhost-only with a local token:
   ```bash
   umask 077; openssl rand -hex 32 > ruview.token
   printf 'RUVIEW_API_TOKEN=%s\n' "$(cat ruview.token)" > ruview.env.token
   docker run -d --name ruview --restart unless-stopped \
     -p 127.0.0.1:3000:3000 -p 127.0.0.1:3001:3001 --env-file ruview.env.token \
     -e RUVIEW_NO_EDGE_REGISTRY=true -e RUVIEW_NO_MDNS=true ruvnet/wifi-densepose:latest
   ```
   `replay_sensors.py --ruview B-06` then makes sensor B-06-a read RuView's presence classification.
10. Optional, live sensor near your GB10: save the Nominatim (OpenStreetMap) result for your building, with its
    polygon and extra tags, as `data/raw/live/nom.json` and run `.venv/bin/python build_live.py`. `ruview_live.py`
    needs RuView's v1 sensing code in the folder set by `LIFELINE_RUVIEW_DIR` (default `vendor/RuView`) and reads
    the WiFi interface given by `--iface` (default `wlP9s9`). `LIFELINE_LIVE_VAR` sets the movement threshold
    (default 2.0 dB²); the dashboard's live test calibrates it on its first 20 s.
11. Run the checks and the reset steps in [docs/CHECKLIST.md](docs/CHECKLIST.md), the full run-and-reset checklist.

## Known limits

- Sensor readings are simulated (`source: "replay"`). Through-wall WiFi sensing has been demonstrated;
  through real rubble it is not proven.
- Damage grades come from satellite photo-interpretation (Copernicus EMS EMSR648), not inspection.
  Building labels are generic (B-01...).
- Routing uses straight-line distances at an assumed 15 km/h, with no road network.
- The number of people per building is an estimate from footprint, floors and time of day, not a count.
  The AI never produces it.
- RSSI WiFi sensing (the optional live mode) detects movement near the GB10 only. It cannot count people,
  does not see people sitting still and cannot measure breathing.
- RuView is not bundled. For the optional live mode you install RuView's v1 sensing code from its own
  project into `vendor/RuView` (or the folder set by `LIFELINE_RUVIEW_DIR`); without it the live mode does not run
  and the replay sensors keep working.
- A human approves every dispatch and every survivor alert. Ranking is a decision aid.
- "No signal" never means "nobody": the agent never calls a site empty, clear or safe.
- Two reports confirm a survivor only if they are 20 s apart: the chat transcript carries no sender
  identity, so two different people cannot be verified.
- The local vision check flagged 89% of damaged buildings but also gave 89% false alarms on undamaged
  ones in a blind 60-building test, so it is never used for ranking.
- The 9B model fumbles tool calls; the design works around it (the agent only reads files and replies).
- The live WiFi test's recorded run was uncalibrated: walking was caught 15/15 s, but it raised false alarms
  in 26/30 s of a still room. The test now calibrates on its first 20 s; a calibrated run has not been recorded.
- The front end's building labels overlap where buildings are close; only its Routes tab was checked in a browser.

## Credits

- **Created by the Ctrl+Tab team** (Rashad Mohammed, Madhan Jothimani, Regina Garfias). Original repository:
  [SGGmilagro/lifeline](https://github.com/SGGmilagro/lifeline); fork:
  [Rashad-Mohammed02/lifeline](https://github.com/Rashad-Mohammed02/lifeline). Please star their repos.
- **RuView** by ruvnet: [ruvnet/RuView](https://github.com/ruvnet/RuView) (MIT licence), used for the optional
  live sensing mode. It is not bundled in this repo: you install its v1 code from its own project into
  `vendor/RuView`. Please star it too.
- **Silicon partner:** NVIDIA.
- **Data:** damage grading from Copernicus Emergency Management Service, EMSR648, © European Union.
  Building footprints © OpenStreetMap contributors (ODbL). Satellite imagery, when you build it yourself:
  © Maxar, Maxar Open Data Program, CC BY-NC 4.0 (not included in this repo).
- **Bundled code:** Leaflet 1.9.4 (BSD-2-Clause) in `map/vendor/`. Routing uses Google OR-Tools; live sensing
  uses RuView's v1 sensing pipeline. Their licences and attributions are in
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- **Products you install:** Ollama, OpenClaw, OpenShell (with NemoClaw), Docker, Telegram.
- **AI-generated assets:** the Lifeline Command front end (`map/command.html`) was designed as a Claude
  artifact and wired to the backend by the team.
- Dell Technologies changed this copy for customers: Dell product naming, setup with your own Telegram bot,
  the live drill made generic, the Maxar imagery left out, and docs.
- Dell and Dell Pro Precision are trademarks of Dell Inc. or its subsidiaries. NVIDIA, Grace, Blackwell and
  DGX are trademarks of NVIDIA Corporation. Telegram, Google OR-Tools, Ollama, OpenClaw, Qwen, Maxar,
  Copernicus, OpenStreetMap, Leaflet, Docker and Claude are trademarks of their respective owners. Their
  mention does not imply endorsement of Dell or of this demo.

## Support

Logan Lawler, Dell Technologies: logan.lawler@dell.com

## License

See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The original repository has no
licence file; Dell Inc. shares the work with its authors' permission so that you can download, run and evaluate
it as a demo. No other rights are granted. Dell's changes are Copyright (c) 2026 Dell Inc. under the same terms.
Third-party components, models and data keep their own licences.
