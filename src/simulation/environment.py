from typing import List

from simulation.env import OpenScope_Webdriver, OpenScope_Websocket


class Env():
    uid: str

    def __init__(self):
        self.uid = ''
        return

    def reset(self):
        raise NotImplementedError

    def step(self):
        raise NotImplementedError


class OpenScope_Env(Env):

    _websocket: OpenScope_Websocket
    _webdriver: OpenScope_Webdriver

    def __init__(
        self,
        #
        uid: str,
        icao: str,
        #
        driver_path: str,
        ws_port: str = 5000,
        os_port: str = 3003,
        render: bool = False,
        #
        step_length: int = 60,
    ):
        """
        Args:
            icao: the icao of the airport in OpenScope
        """

        super().__init__()

        # --- var --- #

        self.uid = uid
        self.icao = icao

        self.step_length = step_length

        _os_url = f'http://localhost:{os_port}?port={ws_port}&uid={self.uid}'

        self._websocket = None
        self._webdriver = None

        # --- init SocketIO Client --- #

        self._websocket = OpenScope_Websocket(port=ws_port, uid=self.uid)

        # --- init OpenScope Webdriver --- #

        self._webdriver = OpenScope_Webdriver(driver_path, _os_url, render)

        # --- check complete --- #

        # wait until both _websocket & _webdriver complete
        while True:
            if self._websocket.complete and self._webdriver.complete:
                break

        print(f"\nEnv | {self.uid} init completed!")
        return

    def __del__(self):
        del self._websocket
        del self._webdriver

        print(f"\nEnv | {self.uid} has been closed!")
        return

    def reset(self):
        print('+', end='', flush=True)

        # --- reset --- #

        uuid = self._websocket.gen_uuid()
        self._websocket.make_emit(
            'reset',
            {
                'uid': self.uid,
                'uuid': uuid,
                'icao': self.icao,
            },
        )
        res = self._websocket.get_sync_buffer('reset_res', uuid=uuid)

        # --- response --- #

        state = None
        if res is not None:
            state = res.get('state')
        return state

    def step(self, actions: List[str]):
        print('.', end='', flush=True)

        # --- actions --- #

        parsed_actions = []
        for action in actions:
            _action = action.strip()

            if _action == '':
                continue

            parsed_actions.append(_action)

        _len = len(parsed_actions)
        if _len > 0:
            uuid = self._websocket.gen_uuid()
            self._websocket.make_emit('action', {
                'uid': self.uid,
                'uuid': uuid,
                'actions': parsed_actions
            })
            res = self._websocket.get_sync_buffer('action_res', uuid=uuid)
            assert _len == res.get('act_len')

        # --- step --- #

        uuid = self._websocket.gen_uuid()
        self._websocket.make_emit('step', {
            'uid': self.uid,
            'uuid': uuid,
            'step_size': self.step_length
        })
        res = self._websocket.get_sync_buffer('step_res', uuid=uuid)

        # --- response --- #

        state, reward, done, info = None, None, None, None
        if res is not None:
            state = res.get('state')
            reward = res.get('reward')
            done = res.get('done')
            info = res.get('info')
        return state, reward, done, info
