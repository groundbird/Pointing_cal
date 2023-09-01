import numpy as np
import matplotlib.pyplot as plt
import pickle
import sys

def read_pkl(path):
    with open(path, 'rb') as p:
        data = pickle.load(p)
    return data

# in weka

#RESULTP = '/data/sueno/home/workspace/GB/jupyter/202206/pointing_params_202205.pkl'
#RESULTP = '/data/sueno/home/workspace/script/gb_cal/pointing_params_202205.pkl'
#RESULTP = '/data/ysueno/home/workspace/script/gb_cal/pointing/pointing_params_202205.pkl'
#RESULTP = '/data/ysueno/home/workspace/script/Pointing_cal/pointing_params_20230703.pkl'
#RESULTP = '/data/ysueno/home/workspace/script/Pointing_cal/pointing_params_20230706.pkl'
#RESULTP = '/data/ysueno/home/workspace/script/Pointing_cal/pointing_params_20230722.pkl'
RESULTP = '/data/ysueno/home/workspace/script/Pointing_cal/pointing_params_20230826.pkl'

#KIDIDS = np.array([ 0,  1,  2,  3,  4,  5,  6,  7, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25])
#KIDIDS = np.array([ 0,  2,  3,  4,  5,  6,  7, 8, 10, 11, 12, 14, 16, 19, 20, 21, 22, 23, 25]) # from 20230706

def delA(el, az, IA, AN, AW):
    return IA + AN*np.tan(np.deg2rad(el))*np.sin(np.deg2rad(az)) - AW*np.tan(np.deg2rad(el))*np.cos(np.deg2rad(az))

def delA_til(el, az, AN, AW):
    return AN*np.tan(np.deg2rad(el))*np.sin(np.deg2rad(az)) - AW*np.tan(np.deg2rad(el))*np.cos(np.deg2rad(az))

def delE(az, IE, AN, AW):
    return IE + AN*np.cos(np.deg2rad(az)) + AW*np.sin(np.deg2rad(az))

def delE_til(az, AN, AW):
    return AN*np.cos(np.deg2rad(az)) + AW*np.sin(np.deg2rad(az))

def cal_encoder2model(az, el, chip_kidid, fitr):
    az1 = az - delA(el, az, fitr['IA' + chip_kidid], fitr['AN'], fitr['AW'])
    el1 = el - delE(az, fitr['IE' + chip_kidid], fitr['AN'], fitr['AW'])
    return az1%360, el1%360

def cal_encoder2model_rep_dif(az, el, fitr):
    azdif = delA_til(el, az, fitr['AN'], fitr['AW'])
    eldif = delE_til(az, fitr['AN'], fitr['AW'])
    return azdif,eldif

def pointing_cal_new(az, el, chip, kidid, num = 3, encoder = True, resultp = RESULTP):
    '''Calculate Az/El after pointing calibration.
    Parameters
    ----------
    az: array-like
        Azimuth value [deg]
    el: array-like
        Elevation value [deg]
    chip : str
        Chip ID (1A, 1B, 2A, ..., 220)
    kidid: int
        KIDID for calculation.
    num: int
        The number of repeats for calculating pointing offset.
    encoder : Boolean
        Whether azimuth data is raw data from encoder or not. Default : True

    Returns
    -------
    azimuth: array-like
        Azimuth array after pointing calibration
    elevation: array-like
        Elevation array after pointing calibration
    '''
    fitr = read_pkl(resultp)
    chip_kidid = chip + f'kid{kidid:02}'
    assert 'IA' + chip_kidid in fitr.keys(), 'There is no poinitng cal data. Please make sure the chipID and kidid.'
    
    # Azimuth direction of GroundBIRD encoder is opposite direction to AltAz coordinate.
    if encoder:
        az = (-az)%360

    az1 = (az-fitr['IA' + chip_kidid])%360
    el1 = (el-fitr['IE' + chip_kidid])%360
    for i in range(num):
        if i ==0:
            azdif, eldif = cal_encoder2model_rep_dif(az1, el1, fitr)
            az2 = az1 - azdif
            el2 = el1 - eldif
        else:
            azdif, eldif = cal_encoder2model_rep_dif(az2, el2, fitr)
            az2 = az1 - azdif
            el2 = el1 - eldif
    return (az2)%360, (el2)%360



###### script for validation ########

def cal_model2encoder(az, el, chip, kidid, fitr):
    chip_kidid = chip + f'kid{kidid:02}'
    az1 = az + delA(el, az, fitr['IA' + chip_kidid], fitr['AN'], fitr['AW'])
    el1 = el + delE(az, fitr['IE' + chip_kidid], fitr['AN'], fitr['AW'])
    return az1%360, el1%360

def compare_input_manytime(az, el, chip, kidid, fitr, num):
    chip_kidid = chip + f'kid{kidid:02}'
    az1, el1 = cal_model2encoder(az, el, chip, kidid, fitr)
    az2 = (az1-fitr['IA' + chip_kidid])%360
    el2 = (el1-fitr['IE' + chip_kidid])%360
    for i in range(num):
        if i ==0:
            azdif, eldif = cal_encoder2model_rep_dif(az2, el2, fitr)
            az3 = az2 - azdif
            el3 = el2 - eldif
        else:
            azdif, eldif = cal_encoder2model_rep_dif(az3, el3, fitr)
            az3 = az2 - azdif
            el3 = el2 - eldif
    if num ==0:
        if az > 180:
            difaz = (az2)%360 - az
        else:
            difaz = az2 - az        
        difel = (el2)%360 - el
        return [difaz, difel]
    else:
        if az > 180:
            difaz = (az3)%360 - az
        else:
            difaz = az3 - az
        difel = (el3)%360 - el
        return [difaz, difel]
