import numpy as np
import matplotlib.pyplot as plt
import pickle
import sys
import datetime
sys.path.append('/data/ysueno/home/workspace/script/')
from gb_cal.misc.misc import read_pkl, save_pkl, _moon_pos
from lmfit import minimize, Parameters, fit_report
from Pointing_cal.pointing_new import delA, delE
# pointing fit for full array


def calc_moon_altaz(ts):
    alt = []
    az = []
    for it in ts:
        moon_altaz = _moon_pos(datetime.datetime.fromtimestamp(it, tz = datetime.timezone.utc))
        alt.append(moon_altaz.alt.deg)
        az.append(moon_altaz.az.deg)        
    return alt, az

def set_params(chips, kidids):
    chip_kidids = []
    for ichip, ikidid in zip(chips, kidids):
        ichip_kidid = ichip + f'kid{ikidid:02}'
        if ichip_kidid in chip_kidids:
            pass
        else:
            chip_kidids.append(ichip_kidid)
    params = Parameters()
    for iy, ichip_kidid in enumerate(chip_kidids):
        params.add('IA' + ichip_kidid, value = 55, min = 0, max = 120)
        params.add('IE' + ichip_kidid, value = 0, min = -11, max = 11)
        #params.add('IA' + ichip_kidid, value = 50.5 - 360)
        #params.add('IE' + ichip_kidid, value = 0)
    
    params.add('AN', value = 0 , min = -1, max = 1)
    params.add('AW', value = 0, min = -1, max = 1)
    return params

def set_params_fix(chips, kidids, AN = -0.03067157, AW = -0.04660315):
    chip_kidids = []
    for ichip, ikidid in zip(chips, kidids):
        ichip_kidid = ichip + f'kid{ikidid:02}'
        if ichip_kidid in chip_kidids:
            pass
        else:
            chip_kidids.append(ichip_kidid)
    params = Parameters()
    for iy, ichip_kidid in enumerate(chip_kidids):
        params.add('IA' + ichip_kidid, value = 55, min = 0, max = 120)
        params.add('IE' + ichip_kidid, value = 0, min = -11, max = 11)
        #params.add('IA' + ichip_kidid, value = 50.5 - 360)
        #params.add('IE' + ichip_kidid, value = 0)
    
    params.add('AN', value = AN, vary = False)
    params.add('AW', value = AW, vary = False)
    return params

def residual_single(params, chip, kidid, el_diff, az_diff, el_moon, az_moon, theta_errmax = 1, phi_errmax = 1):
    chip_kidid = chip + f'kid{kidid:02}'
    IA = params['IA' + chip_kidid]
    IE = params['IE' + chip_kidid]
    AN = params['AN']
    AW = params['AW'] 
    az_model = delA(el_moon, az_moon, IA, AN, AW)
    el_model = delE(az_moon, IE, AN, AW)
    
    err = np.sqrt(phi_errmax**2 + theta_errmax**2)
    #err = 0.053    
    #err = 1
    el_resi = (el_diff - el_model)/err
    az_resi = np.cos(np.deg2rad(el_moon))*(az_diff - az_model)/err
    
    #return np.sqrt(el_resi**2 + az_resi**2)
    return el_resi, az_resi

def residual(params, chips, kidids, el_diffs, az_diffs, el_moons, az_moons):
    resis = [residual_single(params, ichip, ikidid, iel_diff, iaz_diff, iel_moon, iaz_moon)
             for ichip, ikidid, iel_diff, iaz_diff, iel_moon, iaz_moon
             in zip(chips, kidids, el_diffs, az_diffs, el_moons, az_moons)]
    #print(resis)
    #print(len(resis))
    #return np.array(resis)
    return np.array(np.concatenate(resis))

def fit_exe(dffit):
    params = set_params(dffit['chip'], dffit['kidid'])
    out = minimize(residual, 
                   params, 
                   args = (dffit['chip'],dffit['kidid'],dffit['el_diff'],dffit['az_diff'],dffit['el_moon'],dffit['az_moon']), 
                   scale_covar=False)
    return out
    
    
def fit_exe_fix(dffit, AN = -0.03067157, AW = -0.04660315):
    params = set_params_fix(dffit['chip'], dffit['kidid'], AN, AW)
    out = minimize(residual, 
                   params, 
                   args = (dffit['chip'],dffit['kidid'],dffit['el_diff'],dffit['az_diff'],dffit['el_moon'],dffit['az_moon']), 
                   scale_covar=False)
    return out