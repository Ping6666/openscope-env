#!/bin/bash

port1=3003
port2=5000

check_port() {
    netstat -tulnp | grep $1 | grep LISTEN
}

if ! (node -v && npm -v); then
    echo "ERROR | can't find node or npm!"
    exit 2
fi

if ! (google-chrome --version && chromedriver --version); then
    echo "ERROR | can't find google-chrome or chromedriver!"
    exit 3
fi

if check_port $port1 || check_port $port2; then
    echo "ERROR | ports being occupied!"
    exit 4
fi

cd /workspace/websocket && python3 ./server.py > /dev/null 2>&1 &
cd /workspace/openscope && bash ./run.sh > /dev/null 2>&1 &

while ! (check_port $port1 && check_port $port2); do
    sleep 0.1
done

echo "ALL SERVICES UP!"
