# Third-party notices

## Lifeline (original work)

Created by the Ctrl+Tab team (Rashad Mohammed, Madhan Jothimani, Regina Garfias),
https://github.com/SGGmilagro/lifeline. The original repository has no licence file; Dell shares it with the authors' permission
on the terms in [LICENSE](LICENSE).

## Leaflet 1.9.4 (bundled in `map/vendor/`)

The file header is kept as shipped:

```
/* @preserve
 * Leaflet 1.9.4, a JS library for interactive maps. https://leafletjs.com
 * (c) 2010-2023 Vladimir Agafonkin, (c) 2010-2011 CloudMade
 */
```

Leaflet is released under the BSD 2-Clause License:

```
BSD 2-Clause License

Copyright (c) 2010-2023, Volodymyr Agafonkin
Copyright (c) 2010-2011, CloudMade
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

## Copernicus Emergency Management Service, EMSR648 (data)

The building damage grading in `data/regions/*/sites.json`, `data/sites.json` and `skill/brief.json` is derived
from the Copernicus EMS Rapid Mapping activation EMSR648 (Kahramanmaras earthquake, 6 February 2023),
areas of interest AOI01, AOI02, AOI04, AOI05 and AOI11.

Attribution, as kept in the data files: **Damage grading: Copernicus EMS, (c) European Union.**
Grades are photo-interpretation of post-event satellite imagery, not field inspection.
Use of the data follows the Copernicus EMS data policy of the European Union (see the Copernicus Emergency
Management Service's own terms).

## OpenStreetMap (data, optional live drill)

`build_live.py` builds the optional live-drill region from an OpenStreetMap building footprint you look up
yourself. Footprint data © OpenStreetMap contributors, available under the Open Database License (ODbL);
see https://www.openstreetmap.org/copyright.

## Maxar Open Data (imagery, not included)

`make_chips.py`, `make_tiles.py` and `validate_vision.py` read Maxar Open Data imagery
(collection Kahramanmaras-turkey-earthquake-23) that you download yourself. The imagery is not included in
this repository. Attribution, as kept in the scripts: **Imagery (c) Maxar, CC BY-NC 4.0** (non-commercial use only).

## Google OR-Tools (installed with pip)

`routing.py` uses Google OR-Tools (`ortools`), installed from PyPI under the Apache License 2.0. Lifeline's
routing model is the team's own code built on the OR-Tools routing library. OR-Tools is not bundled; its licence
and notices are in the OR-Tools project (https://github.com/google/or-tools) and in the installed package.

## RuView (optional live sensing)

`ruview_live.py` uses RuView's v1 commodity-WiFi sensing pipeline (`RssiFeatureExtractor`,
`PresenceClassifier`, `WifiSample`) from the folder set by `LIFELINE_RUVIEW_DIR`, and the optional RuView sensing
server runs from the Docker image `ruvnet/wifi-densepose`. RuView is not bundled in this repository: you install
it yourself from its own project (into `vendor/RuView`), and it keeps its own licence and notices, which are in
the RuView project.

## OpenClaw default workspace files (`demo/backup/`)

`demo/backup/AGENTS.md`, `HEARTBEAT.md` and `SOUL.md` are OpenClaw's default workspace files, kept unchanged
so the sandbox can be restored. They remain under OpenClaw's licence.

## Products the customer installs

Ollama, OpenClaw, OpenShell and NemoClaw, Docker, and the Telegram Bot API are installed or used under their
own terms. The model `qwen3.5:9b-128k` is run through Ollama under the model's own licence.
