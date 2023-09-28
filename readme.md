./update.sh step_multiplier 1

# Update Setting

## API

### `(PATCH)` => /api/settings/`[$setting]`/`[$value]`

#### Setting Keys

`right_ascension` - HMS Format (*ie. 02h31m49.09s*)

    Normally used for initial alignment only.


`declination` - DMS Format (*ie. 36°8'40.629"N*)

    Normally used for initial alignment only.

`step_multiplier` - 1 | 2 | 4 | 8

    First Needs to be set manually with the stepper motor DIP switches.

    - `1` *Full Step*
    - `2` *Half Step*
    - `4` *Quarter Step*
    - `8` *Eighth Step*

`time_scale`

`pan_speed`

#### Local Scripts

```
./update.sh step_multiplier 1
./update.sh declination 36°8\'40.629\"N 
./update.sh time_scale 1 
./update.sh pan_speed 2 
```


### GOTO
Directs the mount at the given RA/DEC Coordinates

`./goto.sh $RA $DEC`
```
./goto.sh 02h31m49.09s 36°8\'40.629\"N 
```

### PAN
Pans the mount by the given amount of steps

`./pan.sh $RA $DEC`

#### Examples

- *Moves the Right Ascension forward by 2 steps*
    ```
    ./pan.sh 2 0
    ```

- *Moves the Declination backwards by 2 steps*
    ```
    ./pan.sh 0 -2
    ```

- *Moves both RA and Declination forward by 2 steps*
    ```
    ./pan.sh 2 2
    ```

### TRACKING
#### Start Tracking
```
./update.sh tracking True
```
#### Stop Tracking
```
./update.sh tracking False 
```

#### Set current position
(Used on setup) Does not move mount, only tells the api
the current position of `Right Ascension Motor`
```
./update.sh current_position 0 
```