curl --request PATCH http://10.0.0.200:8765/api/settings/ra_time_scale/$1 \
    | python -m json.tool \
    | pygmentize -l javascript
