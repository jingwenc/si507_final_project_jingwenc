##cache.py##
import json
import requests

CACHE_FNAME = 'cache_jobs.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def get_unique_key(url,param=None):
    if param is None:
        return url
    else:
        alphabetized_keys = sorted(param.keys())
        res = []
        for k in alphabetized_keys:
            res.append("{}-{}".format(k, param[k]))
        return url + "_".join(res)

def make_request_using_cache(url,param=None):
    global CACHE_FNAME
    unique_ident = get_unique_key(url,param)

    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        print("Making a request for new data...")
        resp = requests.get(url,param)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_ident]
