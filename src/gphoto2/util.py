import subprocess


# ERROR_NO_CAMERA_PRESENT = '*** Error: No camera found. ***'


# class CameraError(Exception):
#     pass


# def validateGphotoResponse(stderr):
#     if ERROR_NO_CAMERA_PRESENT in str(stderr):
#         raise CameraError("No Camera Found")


def handleGphotoError(stderr):
    lines = stderr.splitlines()
    errors = list()
    for line in lines:
        if ("*** Error" not in line):
            if (line != ""):
                errors.append(line)

    raise Exception(errors)


def getCurrentConfigValueFromCamera(config):
    try:
        res = subprocess.run(
            'gphoto2 --get-config ' + config, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if (res.stderr):
            handleGphotoError(res.stderr)

        lines = res.stdout.splitlines()

        for line in lines:
            if "Current" in line:
                return line.replace("Current: ", '')
    except Exception as e:
        raise e


def setConfigValueOnCamera(config, value):
    try:
        res = subprocess.run(
            "gphoto2 --set-config-value " + config + "=" + value, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if (res.stderr):
            handleGphotoError(res.stderr)
        else:
            return value
    except Exception as e:
        raise e


def getAllConfigFromCamera():
    res = subprocess.run(
        'gphoto2 --list-all-config', shell=True, universal_newlines=True, stdout=subprocess.PIPE)

    lines = res.stdout.splitlines()

    labels = list()
    values = list()
    result = {}

    for line in lines:
        if "/main/" in line:
            labels.append(line)
        if "Current" in line:
            value = line.replace("Current: ", '')
            values.append(value)
    x = 0
    for l in labels:
        result[l] = values[x]
        x = x + 1
    return result


def setMultipleValuesOnCamera(data):
    try:
        cmdString = ""
        for key in data:
            cmdString = cmdString + "--set-config-value " + \
                key + "=" + data[key] + " "

        res = subprocess.run(
            'gphoto2 ' + cmdString,  shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if (res.stderr):
            handleGphotoError(res.stderr)
        else:
            return data
    except Exception as e:
        raise e
