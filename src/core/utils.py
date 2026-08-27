import pathlib
import json


def mkdir(save_folder, can_exists: bool = False, verbose: bool = False):
    p = pathlib.Path(save_folder)

    if p.exists():
        if not can_exists:
            print("ERROR | mkdir found save folder: " +
                  f"{save_folder} exists!")
            raise FileExistsError

        if verbose:
            print("WARNING | mkdir found save folder: " +
                  f"{save_folder} exists, OVERWRITE NOW!")

    p.mkdir(parents=True, exist_ok=True)
    return


def dump_json(_data, f_name: str):
    with open(f_name, 'w') as f:
        json.dump(_data, f, indent=2)

        print(f"dump_json: {f_name} SAVED!")
    return
