# src/api.py

import json, time
import numpy as np

from .network import cached_requests, stored_requests
#cache = cached_requests()
cache = stored_requests()

_opendota_delay = 4
_steamweb_delay = 0

## opendota utilities
def rank2mmr(rank, immortal = None):
    """
    convert rank_tier to approximate mmr

    param rank rank_tier from opendota
    param immortal return value when medal is immortal and above
    return approximate mmr
    """
    if rank == None:
        return 0
    if rank >= 80:
        return immortal
    mmrm = [10, 770, 1540, 2310, 3080, 3850, 4620, 5630]
    medal = (rank // 10 - 1)
    mmr = mmrm[medal]
    mmr += (mmrm[medal + 1] - mmrm[medal]) * ((((rank % 10) - 1) / 5) + 0.1)
    return mmr

## opendota api
def _opendota_get(method, force, **parameters):
    url = 'https://api.opendota.com/api/{}{}'
    params = ''
    if parameters:
        params = '?' + '&'.join('{}={}'.format(k, v) for k, v in parameters.items())
    data, cached = cache.request(url.format(method, params), force)
    if not cached:
        time.sleep(_opendota_delay)
    return data.json()

def get_player_data(account_id, force = False):
    url = 'players/{}'
    data = _opendota_get(url.format(account_id), force)
    profile = {'name': data['profile']['personaname'],
               'avatar': data['profile']['avatarmedium'],
               #'account_id': data['profile']['account_id'],
               #'steamid': data['profile']['steamid'],
               'country': data['profile']['loccountrycode'],
               'medal': data['rank_tier'],
               'mmr': rank2mmr(data['rank_tier'], 0),
               }
    return profile

def get_player_history(account_id, force = False, **parameters):
    url = 'players/{}/counts'
    return _opendota_get(url.format(account_id), force, **parameters)

def get_player_wordcloud(account_id, force = False, **parameters):
    url = 'players/{}/wordcloud'
    return _opendota_get(url.format(account_id), force, **parameters)

def get_player_pings(account_id, force = False, **parameters):
    url = 'players/{}/histograms/pings'
    return _opendota_get(url.format(account_id), force, **parameters)

def get_player_heroes(account_id, force = False, **parameters):
    url = 'players/{}/heroes'
    return _opendota_get(url.format(account_id), force, **parameters)

def get_player_matches(account_id, force = False, **parameters):
    url = 'players/{}/matches'
    return _opendota_get(url.format(account_id), force, **parameters)

def get_match(match_id, force = False):
    url = 'matches/{}'
    return _opendota_get(url.format(match_id), force)

## steam web api
def _steam_get(method, force, **parameters):
    url = 'https://api.steampowered.com/{}/v1?key={}{}'
    with open('key.txt') as f:
        key = f.read()
    params = ''
    if parameters:
        params = '&' + '&'.join('{}={}'.format(k, v) for k, v in parameters.items())
    data, cached = cache.request(url.format(method, key, params), force)
    if not cached:
        time.sleep(_steamweb_delay)
    return data.json()

def get_matches(force = False, **parameters):
    """league_id, hero_id, game_mode... see steamwebapi.azurewebsites.net for options"""
    url = 'IDOTA2Match_570/GetMatchHistory'
    return _steam_get(url, force, **parameters)

def get_league_matches(league_id, force = False, **parameters):
    matches = [get_matches(force, league_id = league_id, **parameters)]
    while matches[-1]['result']['results_remaining']:
        match_id = matches[-1]['result']['matches'][-1]['match_id']
        matches += [get_matches(force, league_id = league_id, start_at_match_id = match_id, **parameters)]
    matches = [m for mm in matches for m in mm['result']['matches']]
    matches = np.array(matches)
    # drop duplicates
    m_ids = [m['match_id'] for m in matches]
    u, c = np.unique(m_ids, return_counts = True)
    # duplicates = matches[np.isin(m_ids, u[np.where(c == c[np.argmax(c)])])]
    first = matches[np.searchsorted(np.sort(m_ids), u)]
    return first.tolist()
