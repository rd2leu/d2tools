# src/api.py

import json, time
import numpy as np

from .utilities import rank2mmr
from .network import cached_requests, stored_requests
#cache = cached_requests()
cache = stored_requests()

_opendota_delay = 1
_steamweb_delay = 0

## opendota api
def _opendota_get(method, force, **parameters):
    url = 'https://api.opendota.com/api/{}{}'
    params = ''
    if parameters:
        params = '?' + '&'.join('{}={}'.format(k, v) for k, v in parameters.items())
    data, cached = cache.request(url.format(method, params), force)
    if not cached:
        time.sleep(_opendota_delay + np.random.rand())
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

def resolve_id(custom_id, force = False):
    """resolve steam custom ID"""
    url = 'ISteamUser/ResolveVanityURL'
    res = _steam_get(url, force, vanityurl = custom_id)['response']
    return res['steamid']

def get_matches(force = False, **parameters):
    """league_id, hero_id, game_mode... see steamwebapi.azurewebsites.net for options"""
    url = 'IDOTA2Match_570/GetMatchHistory'
    return _steam_get(url, force, **parameters)

def get_league_matches(league_id, force = False, **parameters):
    matches = []
    # do while
    request = get_matches(force, league_id = league_id, **parameters)
    matches.extend(request['result']['matches'])
    
    remaining = request['result']['results_remaining']
    match_ids = [m['match_id'] for m in request['result']['matches']]
    last_match_id = sorted(match_ids)[0] # they are sorted, but just in case

    parameters.pop('start_at_match_id', None) # after the first request, no longer pass this argument

    while remaining > 0:
        request = get_matches(
            force, league_id = league_id,
            start_at_match_id = last_match_id,
            **parameters
            )
        matches.extend(request['result']['matches'])

        remaining = request['result']['results_remaining']
        match_ids = [m['match_id'] for m in request['result']['matches']]

        if remaining > 0:
            if len(match_ids) != 0:
                # they are sorted, but just in case
                last_match_id = sorted(match_ids)[0]
            else:
                # there are remaining matches, but request returned none
                # so repeat the last request but 1 match id earlier
                last_match_id = matches[-2:][0]
                # will repeat the same request if len(matches) == 1
        
    # find duplicates
    matches = np.array(matches)
    match_ids = [m['match_id'] for m in matches]
    u, c = np.unique(match_ids, return_counts = True)
    # sort u from most recent to oldest match id
    order = np.argsort(u)[::-1]
    u, c = u[order], c[order]
    # drop duplicates
    first = matches[[match_ids.index(m) for m in u]]
    return first.tolist()
