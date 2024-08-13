#!/usr/bin/env python
# coding: utf-8

import json
import os
import pandas as pd
import itertools
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import time
from pathlib import Path
import glob
import seaborn as sns
from scipy import stats
import matplotlib.patches as mpatches
import shutil
import re
from unpcap import *
from utilities import *

# Tournament info
is_boost = False
tournament_number = 495
top_filter = 100
leaderboard_file = BASE_DIR + 'out/leaderboard{0}.json'.format(tournament_number)
leaderboard_cache_file = BASE_DIR + 'com.ludia.jw2/files/Leaderboard_{0}_ScoresCache.3300000000001.json'.format(tournament_number)
use_cache_file = True

# received, _ = extract_pcap(BASE_DIR + 'PCAPdroid_21_мар._12_11_43.pcap')
# received1, _ = extract_pcap(BASE_DIR + 'PCAPdroid_21_мар._12_12_45.pcap')
# received += received1
with open(JSON_DIR + "pcap_out.json") as f:
  received = json.load(f)

# File info
dinocard_dir = BASE_DIR + 'Img'
player_group_description = 'Tournament_' + str(tournament_number)
output_dir = BASE_DIR + 'plots/' + player_group_description


# Load files
Path(output_dir).mkdir(parents=True, exist_ok=True)
if use_cache_file:
    with open(leaderboard_cache_file, "r") as f:
        leaderboard = json.load(f)
else:
    with open(leaderboard_file, "r") as f:
        leaderboard = json.load(f)


def extract_command(ms, searchcmd='j.cguap'):
    cmdms = []
    for mi in ms:
        m = mi
        if isinstance(m, dict):
            if m['c']:  # its a command
                pl = m['p']
                a = m['a']  # whatever?
                cmd = pl['c']
                cmdpl = pl['p']
                if cmd == searchcmd:
                    cmdms.append(m['p'])
        elif isinstance(m, list):
            m1 = m
            for m in m1:
                if isinstance(m, dict):
                    if m['c']:  # its a command
                        pl = m['p']
                        a = m['a']  # whatever?
                        cmd = pl['c']
                        cmdpl = pl['p']
                        if cmd == searchcmd:
                            cmdms.append(m['p'])
    return cmdms


def parse_player_data(mdict):
    if 'spl' in mdict['p'].keys():
        pldatas = mdict['p']['spl']
        players, dinoss, teamss = [], [], []
        for pldata in pldatas:
            dinoss.append(pd.json_normalize(pldata['cl']))
            teamss.append(pd.json_normalize(pldata['cdl']))
            pc = ['lvl', 'nxexp', 'lgt', 'id', 'title', 'exp']
            players.append(pd.DataFrame([[pldata[k] for k in pc]], columns=pc))
        return list(zip(players, dinoss, teamss))
    else:
        return list()


def find_name(guid):
    if guid in guid_map.keys():
        entry = guid_map[guid]
        fname = DATA_DIR + "/../../" + entry
        with open(fname) as f:
            creature = json.load(f)
            name = creature["lkn"]
            return localization[name] if name in localization.keys() else ""


def find_img(guid):
    if guid in guid_map.keys():
        entry = guid_map[guid]
    elif guid in guid_map2.keys():
        entry = guid_map2[guid]
    else:
        print(guid)
        return []
    fname = DATA_DIR + "/../../" + entry
    with open(fname) as f:
        creature = json.load(f)
        img_guid = creature["i"]["guid"]
        return asset_map[img_guid]["Path"]



def find_rarity(guid):
    if guid in guid_map.keys():
        entry = guid_map[guid]
        fname = DATA_DIR + "/" + entry.split("/", maxsplit=2)[-1]
        with open(fname) as f:
            creature = json.load(f)
            rarity = creature['r']['guid']
            rp = guid_map[rarity]
            if rp:
                return os.path.split(rp)[1][1:-5]


rarity_colors = {'Common': '#A5ADB5',
                 'Rare': '#1DAAFF',
                 'Epic': '#FAC91C',
                 'Legendary': '#FF395A',
                 'Unique': '#08E763',
                 'Apex': '#374048',
                 'Omega': '#3090B0'}

### Tournament Events
leaderboard_id = int(re.findall(r'\d+', leaderboard_file)[0])

tournament_ids = []  # list(team_df.loc[(team_df['did'] == "TOURNAMENT")]['dsid'].unique()) if len(team_df)>0 else []
tournament_id_description = {}
leaderboardid_tid = {}
today = time.time()
p_t = lambda x: datetime.utcfromtimestamp(x).strftime('%d.%m-%H:%M')
for i, evt_data in enumerate(extract_command(received, "x.ef")):
    if isinstance(evt_data['p']['e'], list):
        for evt in sorted(evt_data['p']['e'], key=lambda x: x['as'] + x['d']['sdt'] if 'd' in x and 'sdt' in x['d'] else -1):
            tournament_id_description[evt['i']] = evt['p']
            if evt['n'] == 'TournamentEvent':
                startdelta = evt['d']['sdt'] * 60 * 60
                enddelta = evt['d']['edt'] * 60 * 60
                startdate = evt['as'] / 1000 + startdelta
                enddate = evt['as'] / 1000 + enddelta
                if evt['d']['type'] == 'evt' and (startdate <= today) and (today <= enddate):
                    print('current tournament:')
                print(
                    f"Found Tournament: {p_t(int(startdate))} to {p_t(enddate)} -- {evt['p']} -- {evt['i']} -- {evt['d']['cli']}\n")
                leaderboardid_tid[evt['d']['cli']] = evt['i']


if use_cache_file:
    topplayers = [int(x) for x in leaderboard['MapInfo']["TopScores"].keys()]
else:
    topplayers = [d['accountId'] for d in leaderboard['data']["topLeaderboardScores"]]
selection = topplayers[:top_filter]
ignore_selection = (top_filter == 0)

# Extract player data
dino_df = pd.DataFrame()
team_df = pd.DataFrame()
player_df = pd.DataFrame()
extracted = extract_command(received, "j.csfgpi")
for pld in extracted:
    for player, dinos, teams in parse_player_data(pld):
        if (ignore_selection or player['id'][0] in selection) and (len(player_df) == 0 or not player['id'][0] in player_df['id'].values):
            dinos['player_id'] = player['id'][0]
            teams['player_id'] = player['id'][0]
            dino_df = pd.concat([dino_df, dinos])
            team_df = pd.concat([team_df, teams])
            player_df = pd.concat([player_df, player])

print(f'Captured {len(player_df)} players data.')

dino_df = dino_df.fillna(0)

# Map dino ids to names
name_ids = dino_df['cid'].unique()
name_dict = dict(zip(name_ids, map(lambda x: find_name(x), name_ids)))
name_dict[''] = 'Unknown'
rarity_dict = dict(zip(name_ids, map(lambda x: find_rarity(x), name_ids)))  # .map()
img_dict = dict(zip(name_ids, map(lambda x: os.path.join(dinocard_dir, os.path.split(find_img(x))[1]), name_ids)))
# dino_df['cid'] = dino_df['cid'].apply(lambda x: name_dict[x])
# team_df['cl'] = team_df['cl'].apply(lambda x: [name_dict[i] for i in x])

player_ids = player_df['id'].unique()


def select_team_dino_stats(tid, did=None):
    team_level_boost_df = pd.DataFrame()
    for pid in player_ids:
        t_dino_df = dino_df[dino_df['player_id'] == pid]
        if did is None:
            t_team_df = team_df[(team_df['player_id'] == pid) & (team_df['dsid'] == tid)]
        else:
            t_team_df = team_df[(team_df['player_id'] == pid) & (team_df['dsid'] == tid) & (team_df['did'] == did)]
        if not (t_dino_df.empty or t_team_df.empty):
            team_level_boost_df = pd.concat([team_level_boost_df,
                                             t_dino_df[t_dino_df['cid'].isin(t_team_df['cl'].values[0])]])
    level_1 = team_level_boost_df.loc[team_level_boost_df["level"] < 6].groupby('cid').count()
    level_6 = team_level_boost_df.loc[(6 <= team_level_boost_df["level"]) & (team_level_boost_df["level"] < 11)].groupby('cid').count()
    level_11 = team_level_boost_df.loc[(11 <= team_level_boost_df["level"]) & (team_level_boost_df["level"] < 16)].groupby('cid').count()
    level_16 = team_level_boost_df.loc[(16 <= team_level_boost_df["level"]) & (team_level_boost_df["level"] < 21)].groupby('cid').count()
    level_21 = team_level_boost_df.loc[21 <= team_level_boost_df["level"]].groupby('cid').count()
    return team_level_boost_df.groupby('cid').mean(numeric_only=True).round(1), team_level_boost_df.groupby('cid').std(numeric_only=True).round(1), [level_1, level_6, level_11, level_16, level_21]


def select_team_dinos(tid, did=None):
    team_level_boost_df = pd.DataFrame()
    for pid in player_ids:
        t_dino_df = dino_df[dino_df['player_id'] == pid]
        if did is None:
            t_team_df = team_df[(team_df['player_id'] == pid) & (team_df['dsid'] == tid)]
        else:
            t_team_df = team_df[(team_df['player_id'] == pid) & (team_df['dsid'] == tid) & (team_df['did'] == did)]
        if not (t_dino_df.empty or t_team_df.empty):
            team_level_boost_df = team_level_boost_df.append(
                t_dino_df[t_dino_df['cid'].isin(t_team_df['cl'].values[0])])
    return team_level_boost_df.sort_values(by='cid')


def mark_team_dinos(tid):
    dinos = pd.DataFrame()
    for pid in player_ids:
        t_dino_df = dino_df[dino_df['player_id'] == pid].copy()
        t_team_df = team_df[(team_df['player_id'] == pid) & (team_df['dsid'] == tid)]
        if not (t_dino_df.empty or t_team_df.empty):
            t_dino_df['team'] = t_dino_df['cid'].isin(t_team_df['cl'].values[0])
            dinos = dinos.append(t_dino_df)
    return dinos.sort_values(by='cid')


def bar_plot(group, dino_stats, real_name, boosts=True, limit=100, dino_deviation=None, omega_levels=None):
    dino_counts = list(Counter(itertools.chain.from_iterable(group['cl'])).items())
    dino_counts = list(filter(lambda x: int(x[1] / len(group) * 100) > 0 and x[1] > 1, dino_counts))
    dino, count = zip(*(sorted(dino_counts, key=lambda x: x[1])[:limit]))
    fig = plt.figure(figsize=(20, 20), dpi=150)
    plt.title(real_name + f" (top {len(group)} players) " + datetime.now().strftime('%Y-%m-%d'))
    width = (max(count) - min(count)) / len(dino)
    stat_width = width*3.5
    height = 0.95
    plt.xlim(-width - stat_width, max(count) + 1)
    plt.ylim(-0.5, len(count))
    colors = [rarity_colors[rarity_dict[d]] for d in dino]
    plt.barh(y=[name_dict[x] for x in dino], width=[c + width + stat_width for c in count], height=height,
             left=-(width + stat_width), color=colors,
             align='center', zorder=1)
    for i in range(len(count)):
        v = count[i]
        imgpath = img_dict[dino[i]]
        if not os.path.exists(imgpath):
            imgpath = glob.glob(os.path.join(dinocard_dir, '*Goat.png'))[0]
        # Colors
        if rarity_dict[dino[i]] in ['Epic']:
            color_scheme = ["#474300", "#F51504", "#22CC00", "#0000FF", "#000000"]
        elif rarity_dict[dino[i]] in ['Unique']:
            color_scheme = ["#AA8000", "#F51504", "#0C4700", "#0000FF", "#000000"]
        elif rarity_dict[dino[i]] in ['Legendary']:
            color_scheme = ["#FFFF00", "#8C0C02", "#2BFF00", "#0000FF", "#000000"]
        elif rarity_dict[dino[i]] in ['Rare']:
            color_scheme = ["#FFFF00", "#F51504", "#2BFF00", "#4040FF", "#000000"]
        elif rarity_dict[dino[i]] in ['Apex']:
            color_scheme = ["#FFFF00", "#FC493B", "#2BFF00", "#8080FF", "#C0C0C0"]
        else:
            color_scheme = ["#FFFF00", "#F51504", "#2BFF00", "#0000FF", "#000000"]

        if len(group) == 100:
            text_color = "#0000FF"
            if v > 80:
                v_text = v - (200 // len(count)) if boosts else v - (200 // len(count))
                text_color = color_scheme[3]
            else:
                v_text = v + 1
            plt.text(v_text, i - 0.1, f"{v}", color=text_color, fontweight='bold')
        else:
            text_color = "#0000FF"
            scale = 100 / len(group)
            if v * scale > 80:
                v_text = v - 1 - 10 / scale
                text_color = color_scheme[3]
            else:
                v_text = v + 1 / scale
            plt.text(v_text, i - 0.1, f"{v} ~ {int(v / len(group) * 100)}%", color=text_color, fontweight='bold')
        if boosts:
            # Draw data
            stat_row = dino_stats[dino_stats.index == dino[i]]
            if stat_row['cpl'].values[0] > 0:
                plt.text(-width - stat_width, i - 0.1, "{0}+{1}".format(stat_row['level'].values[0], stat_row['cpl'].values[0]), color=color_scheme[4], fontweight='bold')
            else:
                plt.text(-width - stat_width, i - 0.1, "{0}".format(stat_row['level'].values[0]), color=color_scheme[4], fontweight='bold')
            plt.text(-width - stat_width * 0.45, i - 0.1 - 0.3, f"{stat_row['caeps.aeps'].values[0] / 100:.2f}",
                     color=color_scheme[0],
                     fontweight='bold')
            plt.text(-width - stat_width * 0.45, i - 0.1, f"{stat_row['caeps.aepa'].values[0] / 100:.2f}",
                     color=color_scheme[1],
                     fontweight='bold')
            plt.text(-width - stat_width * 0.45, i - 0.1 + 0.3, f"{stat_row['caeps.aeph'].values[0] / 100:.2f}",
                     color=color_scheme[2],
                     fontweight='bold')
            # Draw legend
            white = mpatches.Patch(color='white', label='Average dino parameters:')
            black = mpatches.Patch(color='black', label='Level')
            green = mpatches.Patch(color='green', label='Health boosts')
            red = mpatches.Patch(color='red', label='Attack boosts')
            yellow = mpatches.Patch(color='yellow', label='Speed boosts')
            plt.legend(handles=[white, black, green, red, yellow])

        elif (dino_deviation is not None) and (omega_levels is None):
            stat_row = dino_stats[dino_stats.index == dino[i]]
            stat_dev = dino_deviation[dino_deviation.index == dino[i]]
            if stat_row['atr.Attack'].values[0] > 0 or stat_row['atr.Health'].values[0] > 0:
                plt.text(-width - stat_width, i - 0.1 + 0.3, f" {stat_row['atr.Health'].values[0]:.1f} ± {stat_dev['atr.Health'].values[0]:.1f}",
                         color='purple',
                         fontweight='bold')
                plt.text(-width - stat_width, i - 0.1, f" {stat_row['atr.Attack'].values[0]:.1f} ± {stat_dev['atr.Attack'].values[0]:.1f}",
                         color='brown',
                         fontweight='bold')
                plt.text(-width - stat_width, i - 0.1 - 0.3, f" {stat_row['atr.Speed'].values[0]:.1f} ± {stat_dev['atr.Speed'].values[0]:.1f}",
                         color='red',
                         fontweight='bold')
                plt.text(-width - stat_width * 0.45, i - 0.1 + 0.3, f" {stat_row['atr.Defense'].values[0]:.1f} ± {stat_dev['atr.Defense'].values[0]:.1f}",
                         color='orange',
                         fontweight='bold')
                plt.text(-width - stat_width * 0.45, i - 0.1, f" {stat_row['atr.CriticalHitChance'].values[0]:.1f} ± {stat_dev['atr.CriticalHitChance'].values[0]:.1f}",
                         color='yellow',
                         fontweight='bold')
                plt.text(-width - stat_width * 0.45, i - 0.1 - 0.3, f" {stat_row['atr.CriticalHitMultiplier'].values[0]:.1f} ± {stat_dev['atr.CriticalHitMultiplier'].values[0]:.1f}",
                         color='limegreen',
                         fontweight='bold')
            white = mpatches.Patch(color='white', label='Average omega points:')
            purple = mpatches.Patch(color='purple', label='Health')
            brown = mpatches.Patch(color='brown', label='Attack')
            red = mpatches.Patch(color='red', label='Speed')
            orange = mpatches.Patch(color='orange', label='Armor')
            yellow = mpatches.Patch(color='yellow', label='Critical Chance')
            green = mpatches.Patch(color='limegreen', label='Critical Multiplier')
            plt.legend(handles=[white, purple, brown, red, orange, yellow, green])
        elif omega_levels is not None:
            stat_row = dino_stats[dino_stats.index == dino[i]]
            [level_row_1, level_row_6, level_row_11, level_row_16, level_row_21] = omega_levels
            level_row_1 = level_row_1[level_row_1.index == dino[i]]
            level_row_6 = level_row_6[level_row_6.index == dino[i]]
            level_row_11 = level_row_11[level_row_11.index == dino[i]]
            level_row_16 = level_row_16[level_row_16.index == dino[i]]
            level_row_21 = level_row_21[level_row_21.index == dino[i]]
            if stat_row['atr.Attack'].values[0] > 0 or stat_row['atr.Health'].values[0] > 0:
                if not level_row_1.empty:
                    plt.text(-width - stat_width, i - 0.1 + 0.3, f" Level 1+: {level_row_1.values[0][0]}",
                             color='black',
                             fontweight='bold')
                if not level_row_6.empty:
                    plt.text(-width - stat_width, i - 0.1, f" Level 6+: {level_row_6.values[0][0]}",
                             color='black',
                             fontweight='bold')
                if not level_row_11.empty:
                    plt.text(-width - stat_width, i - 0.1 - 0.3, f" Level 11+: {level_row_11.values[0][0]}",
                             color='black',
                             fontweight='bold')
                if not level_row_16.empty:
                    plt.text(-width - stat_width * 0.45, i - 0.1 + 0.3, f" Level 16+: {level_row_16.values[0][0]}",
                             color='black',
                             fontweight='bold')
                if not level_row_21.empty:
                    plt.text(-width - stat_width * 0.45, i - 0.1, f" Level 21+: {level_row_21.values[0][0]}",
                             color='black',
                             fontweight='bold')

        img = plt.imread(imgpath)
        plt.imshow(img, extent=[v - width - 0.1, v - 0.1, i - height / 2, i + height / 2], zorder=2, aspect=width / height)
    if omega_levels is not None:
        plot_name = f"{real_name} - Top{len(group)} - Levels.jpg"
    else:
        plot_name = f"{real_name} - Top{len(group)} - Stats.jpg"
    plt.savefig(os.path.join(output_dir, plot_name), transparent=False, dpi=fig.dpi,
                bbox_inches='tight')
    # plt.show()


def matrix_plot(group, real_name):
    unique_dinos = Counter(itertools.chain.from_iterable(group['cl']))
    unique_dinos = sorted([d[0] for d in unique_dinos.items() if d[1] > 1])
    N = len(unique_dinos)
    teams = []
    for team in group['cl'].to_list():
        teams.append(np.array([1 if d in team else 0 for d in unique_dinos]))
    teams = np.stack(teams).T
    plt.figure(figsize=(20, 20))
    height = 1
    plt.xlim(-0.5, N - 0.5 + height)
    plt.ylim(-0.5, N - 0.5 + height)
    plt.title(real_name + f" Teams | Pearson Correlation | ({len(group)} players)")
    cmap = sns.diverging_palette(240, 10, as_cmap=True)
    cmap.set_bad('white', 1.)
    coeff = plt.imshow(np.corrcoef(teams), cmap=cmap, zorder=1)
    plt.xticks(range(len(unique_dinos)), [name_dict[x] for x in unique_dinos], rotation='vertical')
    plt.yticks(range(len(unique_dinos)), [name_dict[x] for x in unique_dinos])
    for i in range(len(unique_dinos)):
        imgpath = img_dict[unique_dinos[i]]
        if not os.path.exists(imgpath):
            imgpath = glob.glob(os.path.join(dinocard_dir, '*Goat.png'))[0]
        img = plt.imread(imgpath)
        l = len(unique_dinos)
        plt.imshow(img, extent=[i - height / 2, i + height / 2, l - height / 2, l + height / 2], zorder=2)
        plt.imshow(img, extent=[l - height / 2, l + height / 2, i - height / 2, i + height / 2], zorder=2)

    plt.colorbar(coeff, fraction=0.037, pad=0.00, aspect=100)
    plt.savefig(os.path.join(output_dir, f'Dinoteam-pearson-{real_name}.jpg'), bbox_inches='tight')
    # plt.show()


# Select tournament
if leaderboard_id in leaderboardid_tid.keys():
    tid = leaderboardid_tid[leaderboard_id]
    name = tid

    # Plot tournament
    group = team_df.loc[(team_df['did'] == "TOURNAMENT") & (team_df['dsid'] == tid)]
    if not group.empty:
        dino_stats, dino_deviation, levels = select_team_dino_stats(tid)
        real_name = tournament_id_description[tid]
        try:
            print(f"Tournament: {tid}")
            print(f"{team_df['did'].values[0]}: {tid}")

            bar_plot(group, dino_stats, real_name, is_boost, dino_deviation=dino_deviation, omega_levels=levels)
            bar_plot(group, dino_stats, real_name, is_boost, dino_deviation=dino_deviation, omega_levels=None)
            matrix_plot(group, real_name)
        except:
            pass


# Plot arena
group = team_df.loc[(team_df['dsid'] == "MainDeck") & (team_df['did'] == "PVP")]
dino_stats, dino_deviation, levels = select_team_dino_stats("MainDeck", 'PVP')
real_name = "Arena"

bar_plot(group, dino_stats, real_name, True, dino_deviation=dino_deviation)
matrix_plot(group, real_name)

dino_df['cid'] = dino_df['cid'].apply(lambda x: name_dict[x])
team_df['cl'] = team_df['cl'].apply(lambda x: [name_dict[i] for i in x])

if top_filter:
    mapping = dict()
    for id in dino_df['player_id'].unique():
        mapping[id] = topplayers.index(id) + 1
else:
    N = len(dino_df['player_id'].unique())
    mapping = dict(zip(dino_df['player_id'].unique(), np.random.choice(range(N), N, replace=False)))

dino_boosts = dino_df
dino_boosts = dino_boosts.reset_index(drop=True).sample(frac=1)
dino_boosts['player_id'] = [mapping[lul] for lul in dino_boosts['player_id']]
dino_boosts = dino_boosts.sort_values('cid').drop(['id', 'dna', 'crboin'], axis=1).reset_index(drop=True)
dino_boosts = dino_boosts.rename(
    {'caeps.aepa': 'attack boosts', 'caeps.aeph': 'health boosts', 'caeps.aeps': 'speed boosts'}, axis=1)

dino_boosts.to_csv(os.path.join(output_dir, player_group_description + '-dino_boosts.csv'), index=False)


dino_teams = team_df
dino_teams = dino_teams.reset_index(drop=True).sample(frac=1)
dino_teams['player_id'] = [mapping[lul] for lul in dino_teams['player_id']]
dino_teams = dino_teams.sort_values('dsid').drop([], axis=1).reset_index(drop=True)
dino_teams = dino_teams.rename(
    {'caeps.aepa': 'attack boosts', 'caeps.aeph': 'health boosts', 'caeps.aeps': 'speed boosts'}, axis=1)


n = len(dino_teams['player_id'].unique())
dino_teams.to_csv(os.path.join(output_dir, player_group_description + f'{n}-dino_teams.csv'), index=False)
