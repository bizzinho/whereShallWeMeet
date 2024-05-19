import os
import pathlib
import sys
import googlemaps
from datetime import datetime as dt

from typing import Union

MODES = ("transit", "driving", "walking")


class WhereShallWeMeet:
    def __init__(self, friendsFile: str = None, configPath: str = None):

        self.configPath = configPath

        self._gmaps = None

        self.friendsFile = friendsFile
        self._friends = None

        self._DM = {}

    @property
    def friends(self):

        if self._friends is None:
            self._loadFriends()

        return self._friends

    @property
    def gmaps(self):

        if self._gmaps is None:
            self._establishConnection()

        return self._gmaps

    def friendsMatrix(self, transitMode="transit", verbose=True):

        # remove people that can't host from destination
        startAddresses = [friend["address"] for friend in self.friends]

        potentialHosts = [
            addie
            for i, addie in enumerate(startAddresses)
            if self.friends[i]["availableToHost"]
        ]

        if transitMode == "best":
            for mode in MODES:
                self._DM[mode] = self._getDistMatrix(
                    startAddresses=startAddresses,
                    destinationAddresses=potentialHosts,
                    transitMode=mode,
                )
        elif transitMode == "custom":
            friendModes = {
                friend["name"]: friend["preferredTransitMode"]
                for friend in self.friends
            }
            modes = set(friendModes.values())
            for mode in modes:
                # calc dist matrix for everyone with this mode
                startPoints = [
                    startAddresses[i]
                    for i, friend in enumerate(friendModes)
                    if friendModes[friend] == mode
                ]
                self._DM[mode] = self._getDistMatrix(
                    startAddresses=startPoints,
                    destinationAddresses=potentialHosts,
                    transitMode=mode,
                )
        else:
            self._DM[transitMode] = self._getDistMatrix(
                startAddresses=startAddresses,
                destinationAddresses=potentialHosts,
                transitMode=transitMode,
            )

        # return dist matrix
        # (rows = startpoint, cols = destination)
        self._M = self._json2Matrix(DM)

    def _loadFriends(self):
        path = pathlib.Path(self.friendsFile)

        if path.suffix == ".csv":
            import csv

            friends = []
            with open(self.friendsFile, "r") as f:
                csvfile = list(csv.reader(f))

            # first row is header
            header = csvfile[0]

            def findCol(word):
                shoeFits = list(
                    filter(
                        lambda i: [word in col.lower() for col in header][i],
                        range(len(header)),
                    )
                )

                if len(shoeFits) > 1:
                    raise ValueError(
                        f"More than one column header contains {word}."
                    )
                elif len(shoeFits) == 0:
                    raise ValueError(
                        f"No column header contains keyword {word}"
                    )

                return shoeFits[0]

            nameCol = findCol("name")
            addressCol = findCol("address")
            transitCol = findCol("preferred")
            hostCol = findCol("host")
            joinsCol = findCol("joins")

            for row in csvfile[1:]:

                friends.append(
                    {
                        "name": row[nameCol],
                        "address": row[addressCol],
                        "preferredTransitMode": row[transitCol],
                        "availableToHost": row[hostCol],
                        "joinsParty": row[joinsCol],
                    }
                )
        elif (path.suffix == ".yaml") or (path.suffix == ".yml"):
            import yaml

            with open(self.friendsFile, "r") as f:
                ff = yaml.load(f, Loader=yaml.FullLoader)

            friends = ff["friends"]

        # remove people that don't join
        friends = list(filter(lambda x: x["joinsParty"], friends))

        # sort by name
        friends = sorted(friends, key=lambda elem: elem["name"])

        self._friends = friends

    def _establishConnection(
        self,
    ) -> googlemaps.client.Client:
        if (self.configPath is None) and (os.environ.get("TOKEN") is None):
            raise ValueError("configPath or TOKEN env variable must exist.")
        elif self.configPath is not None:
            # user passes apitoken via config file

            # add parent path to path
            path = pathlib.Path(self.configPath)
            sys.path.append(str(path.parent.absolute()))

            # import module (infer module name from filename)
            cfg = __import__(path.stem)

            apitoken = cfg.apitoken
        elif os.environ.get("TOKEN") is not None:
            # user passes apitoken via env variable
            apitoken = os.environ.get("TOKEN")

        # establish connection
        gmaps = googlemaps.Client(key=apitoken)

        self._gmaps = gmaps

    def _getDirections(
        self,
        startAddress: str,
        destinationAddress: str,
        transitMode: str = "transit",
        departureTime: Union[str, dt] = dt.now(),
    ) -> tuple[dict, int]:

        # Geocoding an address
        # geocode_start = gmaps.geocode(startAddress)

        # use directions api
        dir_results = self.gmaps.directions(
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

    def _getDistMatrix(
        self,
        startAddresses: Union[str, list[str]],
        destinationAddresses: Union[str, list[str]],
        transitMode: str = "transit",
        departureTime: Union[str, dt] = dt.now(),
    ) -> tuple[dict, int]:

        dist_results = self.gmaps.distance_matrix(
            startAddresses,
            destinationAddresses,
            mode=transitMode,
            departure_time=departureTime,
        )

        return dist_results

    @classmethod
    def _json2Matrix(cls, jsonMatrix: dict) -> list[list[int]]:

        matrix = []

        # returns a #Start x #Destination matrix
        for row in jsonMatrix["rows"]:
            rowList = []
            for elem in row["elements"]:
                if elem["status"] == "OK":
                    rowList.append(elem["duration"]["value"])
                else:
                    rowList.append(0)
            matrix.append(rowList)

        return matrix
