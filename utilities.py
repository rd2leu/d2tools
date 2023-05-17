# src/utilities.py

import pandas as pd
import numpy as np

def extract_account_id(profile_url, index = 0, kwd = 'players/'):
    try:
        splt = profile_url[index:].split(kwd)
        a = splt[1]
        for i, c in enumerate(a):
            if not c.isdigit():
                a = a[:i]
                break
        return a, index + len(kwd) + len(splt[0]) + i + 1 # FIXME needs testing
    except:
        raise SyntaxError('Invalid account url: ' + profile_url)

def extract_account_id2(profile_url):
    try:
        return extract_account_id(profile_url)[0]
    except:
        return 105248644 # Miracle-

def extract_account_ids(profile_url):
    # euh idk why
    try:
        acc, idx = extract_account_id(profile_url)
    except:
        acc, idx = '', 0
    if acc == '':
        return []
    return [acc] + extract_account_ids(profile_url[idx:])

def extract_account_ids2(profile_url):
    # euh idk why
    acc, idx = '', 0
    for k in ['players/', 'player/']:
        try:
            acc, idx = extract_account_id(profile_url, kwd = k)
            break
        except:
            pass
    if acc == '':
        return []
    return [acc] + extract_account_ids2(profile_url[idx:])

def shorttime(s):
    """seconds to short time string"""
    frmt = '%#Hh%#Mm%#Ss'
    if s < 3600:
        frmt = '%#Mm%#Ss'
    return pd.to_datetime([s], unit = 's').strftime(frmt).values[0]

def datestr(s, timezone = 'CET'):
    """seconds to date string"""
    frmt = '%B %d, %Y - %H:%M'
    return pd.to_datetime(s, unit = 's').tz_localize('UTC').tz_convert(timezone).strftime(frmt)

def datetoseconds(datestr, timezone = 'CET'):
    """date string to seconds"""
    return int(pd.to_datetime([datestr]).tz_localize(timezone).tz_convert('UTC').values[0].astype(np.uint64) / 1000000000)
