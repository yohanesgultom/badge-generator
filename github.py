import os
import json
import requests
from datetime import datetime

def get_github_repos(username):
    repos = []
    now = datetime.now().strftime('%Y%m%d%H')
    cache_path = os.path.join('tmp', f'{username}_{now}.json')
    if os.path.isfile(cache_path):
        with open(cache_path) as f:
            repos = json.load(f)
    else:
        # get github repo
        url = f'https://api.github.com/users/{username}/repos?type=owner&sort=updated&direction=desc&per_page=100'
        r = requests.get(url, headers={'Accept': 'application/vnd.github.v3+json'})
        repos = r.json()
        with open(cache_path, 'w') as f:
            json.dump(repos, f)
    return repos