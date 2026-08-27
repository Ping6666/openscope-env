# openScope Patch

This repository uses [openScope v6.28.0](https://github.com/openscope/openscope/tree/v6.28.0) as the simulator base.

## Prepare the Local Simulator Copy

From outside this repository:

```bash
git clone https://github.com/openscope/openscope.git /tmp/openscope-v6.28.0
cd /tmp/openscope-v6.28.0
git checkout tags/v6.28.0
```

From this repository:

```bash
cp -R /tmp/openscope-v6.28.0 ./openscope
cd openscope
git apply -p2 ../os.patch
```

After this, build the dev Docker image:

```bash
cd ..
bash ./build.sh dev
```

## What the Patch Does

The patch adds the browser-side pieces needed for Socket.IO control. In normal use, Python connects to the local relay, Selenium opens the patched openScope page, and the two sides exchange reset, action, and step events through a room identified by `uid`.

The current Python wrapper expects:

- openScope at `http://localhost:3003`
- Socket.IO relay at `ws://localhost:5000`
- ChromeDriver at `/chromedriver/chromedriver-linux64/chromedriver` inside the Docker image

## Run openScope Directly

After applying the patch, you can run openScope itself from the `openscope/` directory:

```bash
cd openscope
bash ./run.sh
```

For experiments, prefer the Docker flow so Chrome, ChromeDriver, Node, and Python dependencies match the expected runtime.

## Refresh the Patch

If you intentionally change the local `openscope/` copy, regenerate the patch by
comparing a clean v6.28.0 checkout with the modified checkout:

```bash
git diff --no-index /tmp/openscope-v6.28.0 ./openscope > os.patch
```

Review the patch before committing it. It should contain only changes required for the Socket.IO bridge and should not include local build output, dependency folders, secrets, or editor files.
