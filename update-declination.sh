# curl -X PUT http://10.0.0.200:8765/settings \
#     -H 'Content-Type: application/json' \
#     -d '{"declination":"36°8'\''40.629\"N"}'

curl -X PUT http://10.0.0.200:8765/settings \
    -H 'Content-Type: application/json' \
    -d '{"declination":"$1"}'
    