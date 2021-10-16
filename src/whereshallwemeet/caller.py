import os
import pathlib
import sys
import googlemaps
from datetime import datetime as dt

from typing import Union, Tuple, List


def _establishConnection(configPath: str = None) -> googlemaps.client.Client:
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

    # establish connection
    gmaps = googlemaps.Client(key=apitoken)

    return gmaps


def getDirections(
    startAddress: str,
    destinationAddress: str,
    transitMode: str = "transit",
    departureTime: Union[str, dt] = dt.now(),
    configPath: str = None,
) -> Tuple[dict, int]:
    gmaps = _establishConnection(configPath=configPath)

    # Geocoding an address
    # geocode_start = gmaps.geocode(startAddress)

    # use directions api
    dir_results = gmaps.directions(
        startAddress,
        destinationAddress,
        mode=transitMode,
        departure_time=departureTime,
    )[0]

    # travel duration in seconds
    duration = dir_results["legs"][0]["duration"]["value"]

    # this is a json-like dict containing the
    # output from the directions api
    return dir_results, duration


def getDistMatrix(
    startAddresses: Union[str, List[str]],
    destinationAddresses: Union[str, List[str]],
    transitMode: str = "transit",
    departureTime: Union[str, dt] = dt.now(),
    configPath: str = None,
) -> Tuple[dict, int]:

    gmaps = _establishConnection(configPath=configPath)

    dist_results = gmaps.distance_matrix(
        startAddresses,
        destinationAddresses,
        mode=transitMode,
        departure_time=departureTime,
    )

    duration = dist_results["rows"][0]["elements"][0]["duration"]["value"]

    return dist_results, duration
