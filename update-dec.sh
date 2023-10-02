curl --request POST http://10.0.0.200:8765/api/settings/slew/dec/10 \
    | python -m json.tool \
    | pygmentize -l javascript