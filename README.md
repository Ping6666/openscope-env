# openScope WebSocket Environment

This repository contains a Docker-based runtime for running experiments against [openScope](https://github.com/openscope/openscope), the browser air traffic control simulator. It adds a Socket.IO bridge to openScope v6.28.0 so Python code can reset the simulator, send controller commands, advance simulation time, and save state/action/reward traces.

The upstream openScope source is not committed here. The local `openscope/` directory is ignored by Git, and this repository keeps only the reproducible patch in [`os.patch`](./os.patch). Build steps clone openScope separately, check out `v6.28.0`, and apply that patch before building the Docker image.

## What Is Included

- Dockerfiles for a CUDA, Python, Chrome, ChromeDriver, Node, and openScope runtime.
- A small Flask-SocketIO relay in [`websocket/server.py`](./websocket/server.py).
- Python environment wrappers under [`src/simulation`](./src/simulation) that drive openScope through Selenium and Socket.IO.
- [`src/interaction.py`](./src/interaction.py), an example data-collection entry point that runs multiple simulator workers and writes tapes to `save/`.
- [`os.patch`](./os.patch), the patch applied to upstream openScope v6.28.0.

## Requirements

- Git
- Docker with Docker Compose
- NVIDIA Container Toolkit, if you want GPU access from the container

Docker is the recommended setup because the project depends on CUDA, Chrome, ChromeDriver, Python, Node, and the openScope build toolchain.

## Quick Start

### 1. Clone This Repository

```bash
git clone <repo-url>
cd openscope-env
```

### 2. Prepare openScope

Clone upstream openScope next to this repository, check out the supported tag, copy it into the `openscope/` folder, and apply the local patch:

```bash
git clone https://github.com/openscope/openscope.git /tmp/openscope-v6.28.0
cd /tmp/openscope-v6.28.0
git checkout tags/v6.28.0

cd /path/to/openscope-env
cp -R /tmp/openscope-v6.28.0 ./openscope
cd openscope
git apply -p2 ../os.patch
```

See [openScope setup](./document/openscope.md) for patch maintenance notes.

### 3. Prepare Local Build Config

```bash
cp .env.dev.example .env.dev
cp .env.prod.example .env.prod
```

The example values build two images:

- `openscope-env-base:latest`: development/base image with openScope built in.
- `openscope-env:latest`: runtime image for the Python experiment code.

Edit `.env.dev` or `.env.prod` only if you want different image names, tags, or Dockerfiles.

### 4. Build Images

```bash
bash ./build.sh dev
bash ./build.sh prod
```

### 5. Run the Runtime Container

Create an output folder on the host:

```bash
mkdir -p ./save
```

Start an interactive container:

```bash
docker run -it --rm --shm-size 32G --gpus all \
  -v ./save:/home/user/save \
  openscope-env:latest
```

Inside the container, start the openScope web server and Socket.IO relay:

```bash
bash /workspace/script/init_check.sh
```

Then run the example interaction script:

```bash
cd /workspace
python3 ./src/interaction.py --num-proc 5 --save-folder /home/user/save/test --num-exp 10
```

The script writes JSON tapes under the selected save folder.

## Documentation

- [Docker](./document/docker.md): build modes, runtime container usage, service startup, volumes, and display forwarding.
- [openScope](./document/openscope.md): how the upstream simulator copy is prepared and how to refresh the patch.

## Repository Notes

- The Socket.IO server defaults to `127.0.0.1:5000`.
- The patched openScope app defaults to `localhost:3003`.
- The default airport in the example script is `RJTT`; change `icao` in [`src/interaction.py`](./src/interaction.py) if you want a different airport.

## License

This repository is released under the GPL-3.0 License. openScope is a separate upstream project; review its repository for its own license and notices.

---

*Disclaimer: This readme was AI-generated.*
(Created using Codex GPT-5.5 with medium reasoning.)
