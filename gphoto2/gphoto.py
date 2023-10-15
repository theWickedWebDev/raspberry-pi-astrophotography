import requests
from exiftool import ExifToolHelper
from gphoto2.util import getCurrentConfigValueFromCamera, setConfigValueOnCamera, getAllConfigFromCamera, setMultipleValuesOnCamera

WEATHER_API_URL = 'http://wttr.in?format="%t+%w+%m+%M+%P+%z+%h+%C"'


class GPhoto:
    weather = {}
    meta = {
        "focalLength": "Not set"
    }

    def __init__(self):
        self.getWeather()

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

    def capture():
        print("todo capture")
        # Use a new thread for this?
        # TODO: Connect Exif to self.capture()
        # with ExifToolHelper() as et:
        #     for d in et.get_metadata("/home/pi/astrophotography/gphoto2/example.jpg"):
        #         for k, v in d.items():
        #             print(f"Dict: {k} = {v}")
