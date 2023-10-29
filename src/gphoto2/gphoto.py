import os
import requests
import trio
from datetime import date
from api.capture.util import set_config, set_bulb_capture, set_filename
from exiftool import ExifToolHelper
from gphoto2.util import getCurrentConfigValueFromCamera, setConfigValueOnCamera, getAllConfigFromCamera, setMultipleValuesOnCamera
from gphoto2.canon550d import FocalLengths

WEATHER_API_URL = 'http://wttr.in?format="%t+%w+%m+%M+%P+%z+%h+%C"'


class GPhoto:
    weather = {}
    meta = {}
    stackStatus = {
        "in_progress": False,
        "taken": 0,
        "total": 0
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

    # def initLens(self, focalLength=None):
    #     fl = self.getSetting('lensname')
    #     for length in FocalLengths[fl]:
    #         self.meta['focalLengths'].append(length)
    #     if (len(self.meta['focalLengths']) == 1):
    #         self.meta['focalLength'] = self.meta['focalLengths'][0]
    #     elif focalLength != None:
    #         if (focalLength in self.meta['focalLengths']):
    #             self.meta['focalLength'] = focalLength
    #         else:
    #             raise Exception(
    #                 focalLength + "mm is not available for the current lens")
    #     else:
    #         self.meta['focalLength'] = "Not Set"
    #     return self.meta

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

    async def captureStack(self, scope: trio.CancelScope, settings):
        print(settings)

        with_histogram = ("histogram" in settings) and (settings['histogram'] == True)
        if (with_histogram):
            imageformat = "6"
        else:
            imageformat = "7"
        if ("jpeg" in settings) and (settings['jpeg'] == True):
            imageformat = "6"
        if ("jpegonly" in settings) and (settings['jpegonly'] == True):
            imageformat = "0"
        
        exposure = str(settings['exposure']) + 's'

        with scope:
            for i in range(settings['frames']):
                res = await trio.run_process([
                    'gphoto2',
                    *set_filename(i),
                    *set_config(
                        aperture=settings['aperture'],
                        iso=settings['iso'],
                        imageformat=imageformat,
                    ),
                    *set_bulb_capture(exposure),
                ], capture_stdout=True, capture_stderr=True)

                lines = res.stdout.splitlines()
                if (res.stderr):
                    # print("ERROR!")
                    for line in res.stderr.splitlines():
                        print(line.decode())
                    # if ("An error occurred in the io-library" in res.stderr):
                    # if ('Could not claim the USB device' in res.stderr):
                    # reset_usb()
                    # toggle camera relay via gpio

                for line in lines:
                    if "Saving file" in line.decode():
                        capturedPhoto = line.decode()
                        print(capturedPhoto)
                        if (with_histogram == True) and ('.jpg' in capturedPhoto):
                            print('Generating histogram...')
                            src_file = capturedPhoto.replace('Saving file as ', '')
                            dest_filename = os.path.splitext(src_file)[0] + '-hist.jpg'
                            res = await trio.run_process(['sh', '/home/pi/astrophotography/src/gphoto2/histogram.sh', src_file, dest_filename])
                            print("Histogram success: " + dest_filename)

            # TODO: Call a "post stack capture" function here to begin pre-processing


    # def capture(self):
    #     print("TODO CAPTURE")
    #     currentDate = date.today()
    #     print(currentDate)
    #     print("iso: todo")
    #     print("aperture: todo")
    #     print("exposure: todo")
    #     print(self.weather)
    #     print(self.meta['focalLength'] + 'mm')

        # Confirm self.focalLength has been set

        # Use a new thread for this?
        # TODO: Connect Exif to self.capture()
        # with ExifToolHelper() as et:
        #     for d in et.get_metadata("/home/pi/astrophotography/gphoto2/example.jpg"):
        #         for k, v in d.items():
        #             print(f"Dict: {k} = {v}")
