./update.sh step_multiplier 1

# Update Setting

## API

### Calibrate Example
curl -XPOST 10.0.0.200:8765/api/calibrate/20h21m36.071s/0.978054rad
curl -XPOST 10.0.0.200:8765/api/calibrate/
### Settings

### `(PATCH)` => /api/settings/`[$setting]`/`[$value]`

`tracking`

    boolean

    True: Mount is actively tracking a target

`ra_current_position` | `dec_current_position`

    integer

    This is manually set during initial alignment only


`ra_step_multiplier` | `dec_step_multiplier`

    1 | 2 | 4 | 8

    This is manually set during initial alignment only
    First Needs to be set manually with the stepper motor DIP switches.

    - `1` *Full Step*
    - `2` *Half Step*
    - `4` *Quarter Step*
    - `8` *Eighth Step*

`declination`

    DMS format

    ie. 36°8\'40.629\"N

    This is manually set during initial alignment only (typically)


`ra_time_scale` | `dec_time_scale`
    
    integer not equal to 0
     
    Forward= Positive number
    Backward= Negative number

#### Local Scripts

```
./update.sh $setting $value
```

## Functions

### GOTO
Directs the mount at the given RA/DEC Coordinates

`./goto.sh $RA $DEC`

#### Examples

```
./goto.sh $ra $dec 

./goto.sh 02h31m49.09s 36°8\'40.629\"N 
```
---

### PAN
Pans the mount by the given amount of steps

### `(PATCH)` => /api/functions/pan/$motor/$dir/$value

    Motor
    a | b

    Dir
    1 | 0

    Value
    integer (Number of steps)


#### Examples

`./pan.sh $RA $DEC`

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
---

### Polar Align
(Used on setup) Does not move mount, only tells the api
that RA and DEC are set to celestial north pole

### `(PATCH)` => /api/functions/polar-align

---