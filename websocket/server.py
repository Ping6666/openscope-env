import argparse
from typing import Dict

from multiprocessing import Process

from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, emit


def websocket_args():
    parser = argparse.ArgumentParser()

    # ----- host ----- #
    # default: '0.0.0.0', '127.0.0.1'
    parser.add_argument('--host',
                        type=str,
                        default='127.0.0.1',
                        help='The port that Flask run on.')

    # ----- port ----- #
    parser.add_argument('--port',
                        type=int,
                        default=5000,
                        help='The port that Flask listen to.')

    args = parser.parse_args()
    return args


class SocketIOServer():
    _app: Flask
    _socketio: SocketIO

    def __init__(self, host='127.0.0.1', port=5000, ping_timeout=600):
        print(f'SocketIO Server run on host {host} port {port}')

        # in sec.
        self.ping_timeout = ping_timeout

        self._init_server()

        self.p = Process(target=self._socketio.run,
                         args=(self._app, host, port))
        self.p.start()
        return

    def __del__(self):
        self.p.kill()
        del self.p

        del self._socketio
        del self._app
        return

    def _init_server(self):

        app = Flask(__name__)

        socketio = SocketIO(
            app,
            cors_allowed_origins='*',
            ping_timeout=self.ping_timeout,
        )

        # ---------- Flask ---------- #

        @app.route("/")
        def root_page():
            return '/'

        @app.route("/close")
        def close_page():
            socketio.stop()
            return 'close'

        # ---------- SocketIO ---------- #

        @socketio.on('connect')
        def handle_connect():
            print("connect", request.sid)
            return

        @socketio.on('disconnect')
        def handle_disconnect():
            print("disconnect", request.sid)
            return

        @socketio.on('join')
        def handle_join(data: Dict):
            uid = data.get('uid')
            _is_ctl = data.get('is_ctl')
            print(f"room {uid} | join", request.sid, data)

            join_room(uid)

            # --- emit complete if both ctl was connected --- #
            # curr implementation need to guarantee on below points:
            #   1. is_ctl=True (aka. _sio_client) connect first
            #   2. no collision on the uid

            if _is_ctl is not None and not _is_ctl:
                emit('complete', {}, to=uid)

            return

        @socketio.on('leave')
        def handle_leave(data: Dict):
            uid = data.get('uid')
            print(f"room {uid} | leave", request.sid, data)

            leave_room(uid)
            return

        ## ----- RL agent -> openscope ----- ##

        @socketio.on('reset')
        def handle_reset(data: Dict):
            uid = data.get('uid')
            print(f"room {uid} | reset", request.sid, data)

            emit('reset', data, to=uid)
            return

        @socketio.on('action')
        def handle_action(data: Dict):
            uid = data.get('uid')
            print(f"room {uid} | action", request.sid, data)

            emit('action', data, to=uid)
            return

        @socketio.on('step')
        def handle_step(data: Dict):
            uid = data.get('uid')
            print(f"room {uid} | step", request.sid, data)

            emit('step', data, to=uid)
            return

        ## ----- openscope -> RL agent ----- ##

        @socketio.on('reset_res')
        def handle_reset_res(data: Dict):
            uid = data.get('uid')
            print(f"room {uid} | reset_res", request.sid, data)

            emit('reset_res', data, to=uid)
            return

        @socketio.on('action_res')
        def handle_action_res(data: Dict):
            uid = data.get('uid')
            print(f"room {uid} | action_res", request.sid, data)

            emit('action_res', data, to=uid)
            return

        @socketio.on('step_res')
        def handle_step_res(data: Dict):
            uid = data.get('uid')
            print(f"room {uid} | step_res", request.sid, data)

            emit('step_res', data, to=uid)
            return

        # ---------- var ---------- #

        self._app = app
        self._socketio = socketio

        return


def main(args):
    sio_server = SocketIOServer(host=args.host, port=args.port)
    sio_server.p.join()
    return


if __name__ == '__main__':
    args = websocket_args()
    main(args)
