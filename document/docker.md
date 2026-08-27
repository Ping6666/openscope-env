# Docker

The Docker setup builds two images through `docker compose`:

- `dev`: CUDA, Python, Chrome, ChromeDriver, Node, Python dependencies, and the patched openScope build.
- `prod`: the runtime project image layered on top of the dev/base image.

The dev build expects the `openscope/` directory to exist. Prepare it first by following [openScope setup](./openscope.md).

## Local Environment Files

Create local dotenv files from the public templates:

```bash
cp .env.dev.example .env.dev
cp .env.prod.example .env.prod
```

## Build

```bash
bash ./build.sh dev
bash ./build.sh prod
```

The dev build installs dependencies and runs `npm run build` inside `/workspace/openscope`. The prod build copies this repository into `/workspace` and uses the dev image as its base by default.

`Dockerfile.prod` creates a container user with uid/gid `1000`. If your host user id is different and you need matching file ownership on mounted volumes, update those values before building the prod image.

## Run

Create a host output folder:

```bash
mkdir -p ./save
```

Run an interactive GPU container:

```bash
docker run -it --rm --shm-size 32G --gpus all \
  -v ./save:/home/user/save \
  openscope-env:latest
```

If you do not need GPU access, remove `--gpus all`.

`--shm-size 32G` gives Chrome and PyTorch more shared memory and helps avoid runtime crashes during larger experiments.

## Start Services

Inside the container:

```bash
bash /workspace/script/init_check.sh
```

The script checks for Node, npm, Chrome, ChromeDriver, and free ports, then
starts:

- openScope on port `3003`
- the Socket.IO relay on port `5000`

After it prints `ALL SERVICES UP!`, run experiment code from `/workspace`.

## Runtime Volumes

The common volume is:

```bash
-v ./save:/home/user/save
```

Use this for generated logs and JSON tapes. If you want to copy a separate source tree into the image at build time, place it in `new-src/`.

## Display Forwarding

Display forwarding is only needed when you run the Selenium-controlled Chrome
window with rendering enabled.

On the host:

```bash
echo "$DISPLAY"
xauth list
```

In the container:

```bash
xauth add <xauth-list-entry-from-host>
export DISPLAY=<display-from-host>
```

The default example runs Chrome headlessly unless `--render` is passed to
`src/interaction.py`.
