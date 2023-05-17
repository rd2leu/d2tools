# src/network.py

import requests
from db import storage

class caching:
    def request(self, url, force = False):
        cached = True
        if force or url not in self:
            print('GET', url)
            cached = False
            self[url] = requests.get(url)
        print('CACHE', url)
        return self[url], cached

def file_io(path):
    return path

class cached_requests(dict, caching):
    pass

class stored_requests(storage, caching):
    pass
