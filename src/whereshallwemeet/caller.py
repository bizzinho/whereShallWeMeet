import os
import pathlib
import sys


def getDirections(configPath: str = None):
    if (configPath is None) and (os.environ.get("APITOKEN") is None):
        raise ValueError("configPath or APITOKEN env variable must exist.")
    elif configPath is not None:
        # user passes apitoken via config file

        # add parent path to path
        path = pathlib.Path(configPath)
        sys.path.append(str(path.parent.absolute()))

        # import module (infer module name from filename)
        cfg = __import__(path.stem)

        apitoken = cfg.apitoken
    elif os.environ.get("APITOKEN") is not None:
        # user passes apitoken via env variable
        apitoken = os.environ.get("APITOKEN")

    print(apitoken)
