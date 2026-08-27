from typing import Dict, List

import numpy as np

from core.utils import mkdir, dump_json
from simulation.environment import Env


class Tape():
    storage: Dict[str, List]

    def __init__(self, save_folder: str):
        self.save_folder = save_folder

        self.keys = [
            'state',
            'action',
            'reward',
            'info',
        ]
        self.storage = {}

        for k in self.keys:
            self.storage[k] = []
        return

    def push_next(self, args: Dict):
        for k in self.keys:
            arg = args.get(k)
            self.storage[k].append(arg)
        return

    def save(self):
        f_folder = self.save_folder
        mkdir(f_folder, can_exists=True)

        for k in self.keys:
            obj = self.storage[k]
            ck_f_name = f"{f_folder}/{k}.json"
            dump_json(obj, ck_f_name)
        return


class Game():

    def __init__(self, env: Env, tape: Tape, save_folder: str):
        self.env = env
        self.tape = tape
        self.save_folder = save_folder

        self.reset_worker()
        return

    @property
    def terminal(self) -> bool:
        if self.done:
            return True
        return False

    def reset_worker(self):
        self.done = False
        _state = self.env.reset()

        args = {'state': _state, 'action': [], 'reward': 0, 'info': []}
        self.tape.push_next(args)
        return

    def step_worker(self, parsed_commands: List[np.ndarray]):
        if self.terminal:
            print("Game | The game has been terminated!")
            raise AssertionError

        _state, _reward, _, info = self.env.step(actions=parsed_commands)

        args = {
            'state': _state,
            'action': parsed_commands,
            'reward': _reward,
            'info': info,
        }
        self.tape.push_next(args)
        return

    def close_worker(self):
        print(f"\nGame | {self.env.uid} done, will close peacefully!")

        del self.env
        self.env = None
        self.done = True
        return

    def save(self, idx: int):
        self.tape.save()
        return
