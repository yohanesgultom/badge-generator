import io
import os
import matplotlib
from circlify import circlify
import numpy as np
from matplotlib import font_manager as fm, pyplot as plt, patches as pltp, cm, rcParams
from matplotlib.colors import Normalize
from flask import Flask, request, send_file, jsonify
from matplotlib import rcParams
from collections import Counter

import github

# prevent gui
matplotlib.use('Agg')

# load fonts
font_path = os.path.join('fonts','Open_Sans', 'OpenSans-Light.ttf')
font_prop = fm.FontProperties(fname=font_path)
rcParams['font.family'] = font_prop.get_name()

# prevent clipped labels
rcParams['figure.autolayout'] = True

# flask
app = Flask(__name__)

# https://api.github.com/users/yohanesgultom/repos?type=owner&sort=updated&direction=desc
# Accept: application/vnd.github.v3+json

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/github/<username>/top-forks')
def github_forks(username):
    # args
    cmap_name = request.args.get('cmap', type=str, default='jet')
    top = request.args.get('top', type=int, default=5)
    w = request.args.get('w', type=int, default=8)
    h = request.args.get('h', type=int, default=3)

    # get repos
    repos = github.get_github_repos(username)

    # sort repos
    top_forked = sorted(repos, key=lambda x: x['forks'], reverse=True)
    title = 'Most forked'
    x = []
    y = []
    for repo in top_forked[:top]:
        x.insert(0, repo['name'])
        y.insert(0, repo['forks'])

    # plot styling
    cmap = cm.get_cmap(cmap_name)
    norm = Normalize()
    plt.figure(figsize=(w, h))
    plt.tight_layout()
    ax = plt.subplot(111)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.grid(False)
    ax.xaxis.set_visible(False)
    ax.tick_params(bottom=False, left=False)
    ax.tick_params(axis='y', colors='#555555')

    # add value labels
    for i, v in enumerate(y):
        ax.text(v - 1.0, i - 0.1, str(v), color='white', fontweight='bold')

    # actual plot
    ax.set_title(title, size='xx-large', weight='bold')        
    ax.barh(x, y, color=cmap(norm(y)))

    # save to io
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/github/<username>/bubble-lang')
def github_lang(username):
    # args
    cmap_name = request.args.get('cmap', type=str, default='rainbow')

    # get repos
    repos = github.get_github_repos(username)

    # extract data
    lang_counter = Counter()
    for r in repos:
        if r['language']:
            lang_counter.update({r['language']: 1})
    
    data = []
    labels = []
    for k, v in sorted(lang_counter.items(), key=lambda x: x[1]):
        data.append(v)
        labels.append(k)
    n = len(labels)

    title = 'Languages'
    circles = circlify(data)
    cmap = cm.get_cmap(cmap_name, n)
    norm = Normalize()
    colors_float = cmap(norm(np.array(data)))
    colors = [matplotlib.colors.rgb2hex(c[:3]) for c in colors_float]

    # plot
    plt.figure()
    fig, ax = plt.subplots(figsize=(8.0, 8.0))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.grid(False)    
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)
    ax.set_title(title, size='xx-large', weight='bold')        

    for c, label, color in zip(circles, labels, colors):
        x, y, r = c.circle
        ax.add_patch(pltp.Circle((x, y), r-0.007, alpha=0.7, linewidth=1, color=color))
        label_wrap = label.replace(' ', '\n')
        datum = c.ex['datum']
        ax.text(x, y, f"{label_wrap}\n{datum}", ha='center', va='center', size=r*80, weight='bold', color='white')

    lim = max([max(abs(circle.circle.x) + circle.circle.r, abs(circle.circle.y) + circle.circle.r) for circle in circles])
    plt.xlim(-lim, lim)
    plt.ylim(-lim, lim)

    # save to io
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')
