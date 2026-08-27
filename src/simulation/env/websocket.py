from typing import List, Dict
import threading, copy
import random, string

from socketio import Client
from socketio.exceptions import ConnectionError


class OpenScope_Websocket():
    """
    SocketIOClient
    """

    _sio: Client
    complete: bool

    lock: threading.Lock
    buffer: Dict[str, List]

    def __init__(self, port: str, uid: str, verbose: bool = False):
        self.lock = threading.Lock()
        self.buffer = {}

        self.uid = uid
        self.uuid_len = 15

        self.verbose = verbose
        self.complete = False

        self._init_client()
        self._sio_connect(url=f'ws://localhost:{port}')
        return

    def __del__(self):
        return

    def _init_client(self):
        sio = Client()

        @sio.event
        def connect():
            if self.verbose:
                print(f"room {self.uid} | connect")
            return

        @sio.event
        def connect_error(data):
            if self.verbose:
                print(f"room {self.uid} | connect_error", data)
            return

        @sio.event
        def disconnect():
            if self.verbose:
                print(f"room {self.uid} | disconnect")
            return

        ## ----- response ----- ##

        @sio.on('complete')
        def handle_complete(data: Dict):
            if self.verbose:
                print(f"room {self.uid} | complete", data)

            self.complete = True
            return 'ACK'

        @sio.on('reset_res')
        def handle_reset_res(data: Dict):
            if self.verbose:
                print(f"room {self.uid} | reset_res", data)

            self.push_buffer('reset_res', data)
            return 'ACK'

        @sio.on('action_res')
        def handle_action_res(data: Dict):
            if self.verbose:
                print(f"room {self.uid} | action_res", data)

            self.push_buffer('action_res', data)
            return 'ACK'

        @sio.on('step_res')
        def handle_step_res(data: Dict):
            if self.verbose:
                print(f"room {self.uid} | step_res", data)

            self.push_buffer('step_res', data)
            return 'ACK'

        # ---------- var ---------- #

        self._sio = sio
        return

    def _sio_connect(self, url):
        try:
            self._sio.connect(url)
            self._sio.emit('join', {'uid': self.uid, 'is_ctl': True})

        except ConnectionError:
            print("Start the SocketIO server first!")
        except Exception as e:
            print("SocketIOClient._sio_connect | Exception", e)
            raise

        return

    def make_emit(self, event, data):
        self._sio.emit(event, data)
        return

    def push_buffer(self, event: str, data):
        ### ---------- ###
        self.lock.acquire()

        ctx = self.buffer.get(event)
        if ctx == None:
            ctx = []

        ctx.append(data)
        self.buffer[event] = ctx

        self.lock.release()
        ### ---------- ###
        return

    def pop_buffer(self, event: str, uuid: str) -> Dict | None:
        """
        pop the buffer with the event
        """
        _ctx: Dict

        ### ---------- ###
        self.lock.acquire()

        ctx = self.buffer.get(event)

        res_i, res = None, None
        if ctx is not None:
            for i, _ctx in enumerate(ctx):
                if _ctx.get('uuid') == uuid:
                    res_i = i
                    break

            if res_i is not None:
                _res = self.buffer[event].pop(res_i)
                res = copy.deepcopy(_res)

        self.lock.release()
        ### ---------- ###
        return res

    def gen_uuid(self):
        _bucket = string.ascii_letters
        _str = ''.join(random.choice(_bucket) for _ in range(self.uuid_len))
        return _str

    def get_sync_buffer(self, event: str, uuid: str):
        res = None
        try:
            while res is None:
                res = self.pop_buffer(event, uuid)

                if res is not None:
                    return res

        except Exception as e:
            print('SocketIOClient.get_sync_buffer', e)
        return res
