from flask import make_response, jsonify


def returnResponse(data, status=200):
    response = make_response(jsonify(data))
    response.status_code = status
    return response
