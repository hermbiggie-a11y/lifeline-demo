# Lifeline: run-and-reset checklist

Everything here runs on the Dell Pro Precision GB10. Setup is in [../README.md](../README.md#setup).

## Before a run

- [ ] Ollama is running and the model `qwen3.5:9b-128k` is available.
- [ ] The NemoClaw/OpenShell sandbox `my-assistant` (or `LIFELINE_SANDBOX`) is up, with only the
      `local-inference` and `telegram` policy presets active.
- [ ] The agent files are in the sandbox: `./install_agent.sh` (re-run after any sandbox rebuild).
- [ ] Your Telegram bot is in the group and `LIFELINE_CHAT_ID` is set to the group ID.
      Without it the loop still runs, but heartbeats are only printed, not posted.
- [ ] Optional: the RuView container is running (`docker start ruview`). Replay sensors work without it.

## Start

```bash
./start.sh --reset      # replay restarts at 04:17
```

Open `http://localhost:8090/` (dashboard) or `http://localhost:8090/app` (front end). Logs are in `demo/*.log`.

## Checks

- [ ] A: `curl localhost:8090/brief` returns a ranked brief from replay data.
- [ ] B: `status` in Telegram matches `demo/out/brief.json` exactly; `./leak_test.sh` shows the agent
      refusing and OpenShell logging the request as DENIED.
- [ ] C: `.venv/bin/python replay_sensors.py --trigger B-06` gives an alert with "NEEDS YOUR ACK" within one
      loop and a map pulse within 5 s; `--decline B-06 --to 8 --over 60` escalates the site on its own.

## Reset between runs

```bash
./reset.sh              # replay back to 04:17, survivor signals and pending commands cleared
```

To switch region: `go Malatya` (or Kahramanmaras, Adiyaman, Antakya, Gaziantep) in the group or the dashboard
box. Each switch restarts the replay at 04:17.

## Stop

```bash
./stop.sh
```

## Fallbacks

- **The agent does not post an alert:** the alerts stay pending and are retried on the next 30 s cycle
  (see `demo/loop.log`). Acks still take effect, because the loop reads them from the chat transcript.
- **The model fumbles a reply:** ask again, or use the dashboard command box, which answers `status`,
  `who is alive`, `ack`, `scan`, `report` and `go` without the model.
- **No Telegram:** run without `LIFELINE_CHAT_ID` and drive the demo from the dashboard command box.
- **RuView not running:** `start.sh` says so and the replay sensors keep working.
- **No satellite imagery built:** the map uses a dark background and `/assess` returns the Copernicus grade.
- **`nemoclaw status` or the leak test's log step fails:** the user needs Docker group access
  (`sg docker -c "..."` in an older shell).
- **After a sandbox rebuild:** run `./install_agent.sh` again.
