./update.sh step_multiplier 1

# Update Setting

### Step Multiplier

```
./update.sh step_multiplier 1
```

### Declination
Takes in DMS format: `36°8\'40.629\"N`

```
./update-declination.sh ${VALUE}
```

```    
./update-declination.sh 36°8\'40.629\"N 
```

```
curl -X PUT http://10.0.0.200:8765/settings \
    -H 'Content-Type: application/json' \
    -d '{"declination":"$1"}'
```