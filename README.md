# pointing_calibration

- Application for pointing calibration from encoder data(Az/El).\
- Only LT221 can be calibrated.\
- Summary page about pointing calibration in Growi.
  - https://growi.rockhopper.riken.jp/user/yoshinori0778/memo/2022/06/23/Pointing_calibration

## Desctiption
### pointing_param_202205.pkl
- Parameter dictionary of pointing calibration result.
- `IA**` : Zero offset of azimuth encoder at each detector.
- `IE**` : Zero offset of elevation encoder at each detector.  
- `IA**err` : Fitting error of zero offset of azimuth encoder at each detector.
- `IE**err` : Fitting error of zero offset of elevation encoder at each detector.  
- `AN` : Tilt of the telescope north - south direction.
- `AW` : Tilt of the telescope east - west direction.

### pointing.py
- This is for LT221 with 23 Si lenslet.
```pointing.py
def pointing_cal(az, el, kidid, num = 2, encoder = True, resultp = RESULTP):
```

- `pointing_cal` is Main function for calculating Az/El after pointing calibration.
  - arguments:
    - `az` : Azimuth value [deg].
    - `el` : Elevation value [deg].
    - `kidid` : KIDID for calculation.
    - `num` : The number of repeats. Default : `2`.
    - `encoder` : The number of repeats for calculating pointing offset. Default : `True`.
    - `RESULTP` : path of `pointing_param_202205.pkl`.

### pointing_new.py
- This is for full array observations.

```pointing_new.py
def pointing_cal_new(az, el, chip, kidid, num = 2, encoder = True, resultp = RESULTP):
```

- `pointing_cal_new` is Main function for calculating Az/El after pointing calibration.
  - arguments:
    - `az` : Azimuth value [deg].
    - `el` : Elevation value [deg].
    - `chip` : chip ID for calculation.
    - `kidid` : KIDID for calculation.    
    - `num` : The number of repeats. Default : `2`.
    - `encoder` : The number of repeats for calculating pointing offset. Default : `True`.
    - `RESULTP` : path of `pointing_param_20230826.pkl`.


## Usage
```
from Pointing_cal.pointing import pointing_cal
paz, pel = pointing_cal(rawaz, rawel, kidid = 0, num = 2, encoder=True)
```

```
from Pointing_cal.pointing import pointing_cal_new
paz, pel = pointing_cal(rawaz, rawel, chip = '1A', kidid = 0, num = 2, encoder=True)
```