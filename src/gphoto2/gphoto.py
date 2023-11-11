import requests
from datetime import date

from exiftool import ExifToolHelper
from .util import (
    getCurrentConfigValueFromCamera,
    setConfigValueOnCamera,
    getAllConfigFromCamera,
    setMultipleValuesOnCamera,
)
from .canon550d import FocalLengths

WEATHER_API_URL = 'http://wttr.in?format="%t+%w+%m+%M+%P+%z+%h+%C"'


class GPhoto:

    def __init__(self):
        print("todo init")
        # self.getWeather()
        # self.initLens()
        weather = {}
        meta = {
            "focalLengths": list(),
            "focalLength": None
        }

    def getWeather(self):
        r = requests.get(WEATHER_API_URL)
        data = r.json()
        lines = data.split()
        self.weather["temperature"] = lines[0]
        self.weather["wind"] = lines[1]
        self.weather["moonphase"] = lines[2]
        self.weather["moonday"] = lines[3]
        self.weather["precipitation"] = lines[4]
        self.weather["zenith"] = lines[5]
        self.weather["humidity"] = lines[6]
        self.weather["condition"] = lines[7]

    def initLens(self, focalLength=None):
        fl = self.getSetting('lensname')
        for length in FocalLengths[fl]:
            self.meta['focalLengths'].append(length)
        if (len(self.meta['focalLengths']) == 1):
            self.meta['focalLength'] = self.meta['focalLengths'][0]
        elif focalLength != None:
            if (focalLength in self.meta['focalLengths']):
                self.meta['focalLength'] = focalLength
            else:
                raise Exception(
                    focalLength + "mm is not available for the current lens")
        else:
            self.meta['focalLength'] = "Not Set"
        return self.meta

    def getSetting(self, config):
        try:
            return getCurrentConfigValueFromCamera(config)
        except Exception as e:
            raise e

    def setSetting(self, config, value):
        try:
            return setConfigValueOnCamera(config, value)
        except Exception as e:
            raise e

    def getSettings(self):
        try:
            return getAllConfigFromCamera()
        except Exception as e:
            raise e

    def setSettings(self, data):
        try:
            return setMultipleValuesOnCamera(data)
        except Exception as e:
            raise e

    def capture(self):
        print("TODO CAPTURE")
        currentDate = date.today()
        print(currentDate)
        print("iso: todo")
        print("aperture: todo")
        print("exposure: todo")
        print(self.weather)
        print(self.meta['focalLength'] + 'mm')

        # Confirm self.focalLength has been set

        # Use a new thread for this?
        # TODO: Connect Exif to self.capture()
        # with ExifToolHelper() as et:
        #     for d in et.get_metadata("/home/pi/astrophotography/gphoto2/example.jpg"):
        #         for k, v in d.items():
        #             print(f"Dict: {k} = {v}")
