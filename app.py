import io
import os
import json
import requests
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from flask import Flask, request, send_file
from collections import OrderedDict
from matplotlib import rcParams
from datetime import datetime

matplotlib.use('Agg')
rcParams.update({'figure.autolayout': True}) 

app = Flask(__name__)

# https://api.github.com/users/yohanesgultom/repos?type=owner&sort=updated&direction=desc
# Accept: application/vnd.github.v3+json

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/github/<username>/top-forks')
def github_forks(username):
    now = datetime.now().strftime('%Y%m%d%H')
    cache_path = os.path.join('tmp', f'{username}_{now}.json')
    if os.path.isfile(cache_path):
        with open(cache_path) as f:
            repos = json.load(f)
    else:
        # get github repo
        url = f'https://api.github.com/users/{username}/repos?type=owner&sort=updated&direction=desc'
        r = requests.get(url, headers={'Accept': 'application/vnd.github.v3+json'})
        repos = r.json()
        with open(cache_path, 'w') as f:
            json.dump(repos, f)

    # args
    top = request.args.get('top', type=int, default=5)
    w = request.args.get('w', type=int, default=8)
    h = request.args.get('h', type=int, default=3)

    # sort repos
    top_forked = sorted(repos, key=lambda x: x['forks'], reverse=True)
    title = 'Most forked'
    x = []
    y = []
    for repo in top_forked[:top]:
        x.insert(0, repo['name'])
        y.insert(0, repo['forks'])

    # draw plot
    cmap = cm.get_cmap('jet')
    norm = Normalize()
    plt.figure(figsize=(w, h))
    plt.tight_layout()
    plt.title(title + '\n' + username)
    plt.barh(x, y, color=cmap(norm(y)))

    # save to io
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')
