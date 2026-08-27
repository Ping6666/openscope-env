from argparse import ArgumentParser, Namespace
import random, string
import logging

import torch

from core.utils import mkdir
from simulation import OpenScope_Env, Tape, Game

# --- utils --- #


def gen_uuid(len: int = 10):
    _str = ''.join(random.choice(string.ascii_letters) for _ in range(len))
    return _str


def make_game(env_kwargs, tape_kwargs, game_kwargs):
    # from webdriver_manager.chrome import ChromeDriverManager

    # NOTE: If you use this in parallel, it might lead to a race condition.
    #   related issue: https://github.com/SergeyPirogov/webdriver_manager/issues/290
    # driver_path = ChromeDriverManager().install()
    driver_path = '/chromedriver/chromedriver-linux64/chromedriver'

    env = OpenScope_Env(driver_path=driver_path, **env_kwargs)

    tape = Tape(**tape_kwargs)
    game = Game(env, tape, **game_kwargs)
    return game


# --- args --- #


def get_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument("--num-proc", default=1, type=int)
    parser.add_argument("--save-folder", required=True)

    parser.add_argument("--icao", required=True)

    parser.add_argument("--num-exp", default=1, type=int)
    parser.add_argument("--num-timestamps", default=500, type=int)

    parser.add_argument('--render', action="store_true")

    args = parser.parse_args()
    return args


def create_logger(f_folder: str, logger_name: str):
    """
    ref. https://github.com/facebookresearch/DiT/blob/main/train.py#L67
    """

    logger = logging.getLogger(logger_name)

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(f"{f_folder}/log.txt")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger


# --- #


def worker(
    queue: torch.multiprocessing.Queue,
    uuid: str,
    icao: str,
    save_folder: str,
    num_timestamps: int,
    render: bool = False,
):
    queue.put(uuid)

    mkdir(save_folder)

    kwargs = {
        "uuid": uuid,
        "icao": icao,
        "save_folder": save_folder,
        "num_timestamps": num_timestamps,
        "render": render,
    }

    logger = create_logger(save_folder, uuid)
    logger.info(f'{kwargs = }')

    #

    env_kwargs = dict(uid=uuid, icao=icao, render=render)
    tape_kwargs = dict(save_folder=f"{save_folder}/tape")
    game_kwargs = dict(save_folder=save_folder)
    game = make_game(env_kwargs, tape_kwargs, game_kwargs)
    game.save(0)

    # --- #
    actions_list = []
    for _ in range(num_timestamps):
        game.step_worker(actions_list)
    # --- #

    game.close_worker()
    game.save(-1)
    logger.info("DONE")

    queue.put(uuid)
    return


def main(args):
    num_proc = args.num_proc
    save_folder = args.save_folder

    icao = args.icao

    num_exp = args.num_exp
    num_timestamps = args.num_timestamps

    render = args.render

    #

    mkdir(save_folder)

    uuid = gen_uuid(5)

    main_logger = create_logger(save_folder, uuid)
    main_logger.info(f'{vars(args) = }')

    #

    mp = torch.multiprocessing
    ctx = mp.get_context('spawn')
    pool = ctx.Pool(processes=num_proc)

    manager = mp.Manager()
    queue = manager.Queue()

    map_iterable = []

    for i in range(num_exp):
        _iterable = (
            queue,
            #
            f"{uuid}-{i:05d}",
            icao,
            f"{save_folder}/{i:05d}",
            num_timestamps,
            render,
        )
        map_iterable.append(_iterable)

    # --- main_logger --- #
    for _iter in map_iterable:
        main_logger.info(f'{_iter = }')
    main_logger.info("####################")
    # --- main_logger --- #

    assert len(map_iterable) != 0

    result = pool.starmap_async(worker, map_iterable)

    # --- main_logger --- #
    _num_task = len(map_iterable)
    _start = set()
    _end = set()
    while True:
        _uuid = queue.get()

        if _uuid not in _start:
            _start.add(_uuid)
            main_logger.info(f"Worker: {_uuid} init!")

        else:
            _end.add(_uuid)
            main_logger.info(f"Worker: {_uuid} done!")

        if len(_end) == _num_task:
            break
    # --- main_logger --- #

    result.get()

    pool.close()
    pool.join()

    main_logger.info("ALL DONE")
    return


"""
python3 ./interaction.py --help
usage: interaction.py [-h] [--num-proc NUM_PROC] --save-folder SAVE_FOLDER --icao ICAO [--num-exp NUM_EXP] [--num-timestamps NUM_TIMESTAMPS] [--render]

options:
  -h, --help            show this help message and exit
  --num-proc NUM_PROC
  --save-folder SAVE_FOLDER
  --icao ICAO
  --num-exp NUM_EXP
  --num-timestamps NUM_TIMESTAMPS
  --render


python3 ./src/interaction.py --save-folder ./save/test --icao RJTT
"""
if __name__ == '__main__':
    args = get_args()
    main(args)
