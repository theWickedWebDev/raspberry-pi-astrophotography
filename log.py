import json


def settings(data):
    with open('./settings.log', 'a') as convert_file:
        convert_file.write(json.dumps(data) + '\n')
        convert_file.close()


def error(data, code, method):
    with open('./error.log', 'a') as convert_file:
        convert_file.write(str(code) + ' ' + str(method) +
                           ': ' + str(data) + '\n')
        convert_file.close()
