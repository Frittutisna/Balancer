import os
import math
import random
import re

MODE        = 'NONE'
TEAM_SIZE   = 4
SIMULATIONS = 1000

FILENAMES       = {
    'PLAYERS'   : 'players.txt',
    'REQS'      : 'requests.txt',
    'BL'        : 'blacklists.txt',
    'OUTPUT'    : 'teams.txt',
    'SETUP'     : 'setup.txt'
}

NFL_NAMES = {1: "Texans",   2: "Patriots",  3: "Broncos",   4: "Bills",     5: "Panthers",  6: "Rams",      7: "Eagles",    8: "Niners"}
NBA_NAMES = {1: "Thunder",  2: "Lakers",    3: "Spurs",     4: "Warriors",  5: "Celtics",   6: "Bulls",     7: "Heat",      8: "Knicks"}
MLB_NAMES = {1: "Yankees",  2: "Guardians", 3: "Mariners",  4: "Astros",    5: "Phillies",  6: "Brewers",   7: "Dodgers",   8: "Pirates"}

class Player:
    def __init__(self, name, elo, original_idx = 0):
        self.name           = name
        self.elo            = float(elo)
        self.original_idx   = original_idx

    def __repr__(self): return f"{self.name} ({self.elo})"

def parse_file(filename, file_type):
    if not os.path.exists(filename): return []
    data = []
    with open(filename, 'r', encoding='utf-8') as f: lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()
        if not line: continue
        parts = re.split(r'[,\t\s]+', line)
        parts = [p for p in parts if p]
        if len(parts) >= 2:
            if file_type == 'player':
                try                     : data.append(Player(parts[0], parts[1], i))
                except ValueError       : pass
            elif file_type == 'pair'    : data.append({'p1': parts[0], 'p2': parts[1]})
    
    return data

def parse_setup():
    config          = {
        'MODE'      : 'NONE',
        'CHALLONGE' : '[Insert Challonge link here]',
        'LOBBY'     : '[Insert lobby link(s) here]',
        'NAMES'     : {}
    }
    
    if not os.path.exists(FILENAMES['SETUP']): return config
    with open(FILENAMES['SETUP'], 'r', encoding='utf-8') as f: lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line or ':' not in line: continue
        
        key, val    = line.split(':', 1)
        key         = key.strip().lower()
        val         = val.strip()
        
        if key == 'mode':
            if val.upper() in ['NFL', 'NBA', 'MLB', 'NONE'] : config['MODE']            = val.upper()
        elif key == 'challonge'                             : config['CHALLONGE']       = val
        elif key == 'lobby'                                 : config['LOBBY']           = val
        elif key == 'size':
            try:
                size_val = int(val)
                if 2 <= size_val <= 4                       : config['TEAM_SIZE']       = size_val
            except ValueError: pass
        elif key == 'names':
            names = [n.strip() for n in val.split(',')]
            for i, name in enumerate(names):
                if name                                     : config['NAMES'][i + 1]    = name
                    
    return config

def get_stats_block(teams_data):
    if not teams_data: return 0.0, 0.0
    scores  = [t['total_elo'] for t in teams_data]
    avg_elo = sum(scores) / len(scores)
    spread  = max(scores) - min(scores)
    return avg_elo, spread

def write_output(num_selected, original_count, num_teams, active_players, final_assignments, reqs, bl, setup_config):
    verified_reqs = 0
    for r in reqs:
        p1 = next((p for p in active_players if p.name == r['p1']), None)
        p2 = next((p for p in active_players if p.name == r['p2']), None)
        if p1 and p2:
            idx1 = active_players.index(p1)
            idx2 = active_players.index(p2)
            if final_assignments[idx1] == final_assignments[idx2]: verified_reqs += 1

    verified_bl = 0
    for b in bl:
        p1 = next((p for p in active_players if p.name == b['p1']), None)
        p2 = next((p for p in active_players if p.name == b['p2']), None)
        if p1 and p2:
            idx1 = active_players.index(p1)
            idx2 = active_players.index(p2)
            if final_assignments[idx1] != final_assignments[idx2]: verified_bl += 1

    captains_map = {active_players[i].name: True for i in range(num_teams)}

    teams_data      = []
    custom_names    = setup_config['NAMES']

    for t_idx in range(1, num_teams + 1):
        members = []
        for i, p in enumerate(active_players):
            if final_assignments[i] == t_idx: members.append(p)
        
        total_elo = 0.0
        for m in members:
            if MODE != 'NONE' and m.name in captains_map    : total_elo += (m.elo * 2)
            else                                            : total_elo += m.elo

        members.sort(key = lambda x: x.elo, reverse = True)
        if MODE == 'NFL' and len(members) == 4:
            members = [members[0], members[3], members[1], members[2]]
        
        mem_strings = []
        for m in members:
            s = "@" + m.name
            if MODE != 'NONE' and m.name in captains_map: s += " (C)"
            mem_strings.append(s)
        
        team_name = custom_names.get(t_idx)
        if not team_name:
            if      MODE == 'NFL'   : team_name = NFL_NAMES.get(t_idx, f"Team {t_idx}")
            elif    MODE == 'NBA'   : team_name = NBA_NAMES.get(t_idx, f"Team {t_idx}")
            elif    MODE == 'MLB'   : team_name = MLB_NAMES.get(t_idx, f"Team {t_idx}")
            else                    : team_name = f"Team {t_idx}"
        
        teams_data.append({
            'id'            : t_idx,
            'name'          : team_name,
            'total_elo'     : total_elo,
            'members_str'   : ", ".join(mem_strings)
        })

    avg_elo, spread = get_stats_block(teams_data)

    with open(FILENAMES['OUTPUT'], 'w', encoding='utf-8') as f:
        f.write(f"Mode: {MODE}\n")
        f.write(f"Balanced {num_selected} out of {original_count} players into {num_teams} teams\n")
        f.write(f"Fulfilled {verified_reqs} out of {len(reqs)} request(s)\n")
        f.write(f"Fulfilled {verified_bl} out of {len(bl)} blacklist(s)\n")
        f.write(f"Average Total Elo: {avg_elo:.2f}\n")
        f.write(f"Final Spread: {spread:.2f}\n\n")

        if num_teams == 8 and MODE != 'NONE':
            if      MODE == 'NFL'   : conf1_name, conf2_name = "AFC",       "NFC"
            elif    MODE == 'NBA'   : conf1_name, conf2_name = "Western",   "Eastern"
            else                    : conf1_name, conf2_name = "AL",        "NL"

            t1_slice    = teams_data[0:4]
            t2_slice    = teams_data[4:8]
            
            f.write(f"{conf1_name}:\n")
            avg1, spread1 = get_stats_block(t1_slice)
            f.write(f"Average Total Elo: {avg1:.2f}\n")
            f.write(f"Conference Spread: {spread1:.2f}\n")
            for t in t1_slice   : f.write(f"{t['name']} ({t['total_elo']:.2f}): {t['members_str']}\n")
            
            f.write(f"\n{conf2_name}:\n")
            avg2, spread2 = get_stats_block(t2_slice)
            f.write(f"Average Total Elo: {avg2:.2f}\n")
            f.write(f"Conference Spread: {spread2:.2f}\n")
            for t in t2_slice   : f.write(f"{t['name']} ({t['total_elo']:.2f}): {t['members_str']}\n")
        else: 
            for t in teams_data:
                elo_str = f"{t['total_elo']:.2f}"
                if num_teams == 2:
                    if      t['id'] == 1: elo_str += ", Slots 1-4"
                    elif    t['id'] == 2: elo_str += ", Slots 5-8"
                f.write(f"{t['name']} ({elo_str}): {t['members_str']}\n")

        f.write(f"\n{setup_config['CHALLONGE']}\n")
        f.write(f"{setup_config['LOBBY']}\n")
        
        mode_msg = "the tour"
        if      MODE == 'NFL': mode_msg = "NFL Mode"
        elif    MODE == 'NBA': mode_msg = "NBA Mode"
        elif    MODE == 'MLB': mode_msg = "MLB Mode"
        f.write(f"Good luck and enjoy {mode_msg}!")

    for_mode_str = f" for {MODE} Mode" if MODE != 'NONE' else ''
    print(f"Success! Teams{for_mode_str} written to {FILENAMES['OUTPUT']}")

def main():
    global MODE, TEAM_SIZE
    setup_config = parse_setup()
    
    if      setup_config['MODE'] != 'NONE'  : MODE      = setup_config['MODE']
    elif    setup_config['MODE'] == 'NONE'  : MODE      = 'NONE'
    if      'TEAM_SIZE' in setup_config     : TEAM_SIZE = setup_config['TEAM_SIZE']

    all_players = parse_file(FILENAMES['PLAYERS'],  'player')
    raw_reqs    = parse_file(FILENAMES['REQS'],     'pair')
    raw_bl      = parse_file(FILENAMES['BL'],       'pair')
    
    if len(all_players) < TEAM_SIZE * 2:
        print(f"Error: Minimum of {TEAM_SIZE} players not met in players.txt")
        return
    
    original_count  = len(all_players)
    num_selected    = math.floor(original_count / (TEAM_SIZE * 2)) * (TEAM_SIZE * 2)
    active_players  = all_players[:num_selected]
    active_players.sort(key = lambda x: x.elo, reverse = True)
    
    reqs        = [r for r in raw_reqs if r['p1'] and r['p2']]
    bl          = [b for b in raw_bl   if b['p1'] and b['p2']]
    num_teams   = int(num_selected / TEAM_SIZE)
    
    best_overall_spread = float('inf')
    best_assignments    = None

    print(f"Running {SIMULATIONS} simulations to find the best balance")

    for sim in range(SIMULATIONS):
        possible            = True
        assignments         = [0]   * num_selected
        teams               = [0.0] * num_teams
        team_counts         = [0]   * num_teams
        captain_assignments = list(range(num_teams))
        random.shuffle(captain_assignments)

        for i in range(num_teams):
            t_idx               = captain_assignments[i]
            assignments[i]      = t_idx + 1
            teams[t_idx]        = active_players[i].elo * 2 if MODE != 'NONE' else active_players[i].elo
            team_counts[t_idx]  = 1

        player_pool = list(range(num_teams, num_selected))
        random.shuffle(player_pool)

        for p in player_pool:
            if assignments[p] == 0:
                target_team     = -1
                min_elo         = float('inf') 
                partners_needed = 0
                forced_team     = -1
                conflict        = False
                my_name         = active_players[p].name
                
                for r in reqs:
                    p_name = ""
                    if r['p1'] == my_name: p_name = r['p2']
                    if r['p2'] == my_name: p_name = r['p1']
                    if p_name:
                        p_idx_l = next((i for i, pl in enumerate(active_players) if pl.name == p_name), -1)
                        if p_idx_l > -1:
                            if assignments[p_idx_l] > 0:
                                if      forced_team == -1                   : forced_team       =   assignments[p_idx_l]
                                elif    forced_team != assignments[p_idx_l] : conflict          =   True
                            else                                            : partners_needed   +=  1
                if conflict:
                    possible = False
                    break
                
                search_order = list(range(num_teams))
                random.shuffle(search_order)

                for t in search_order:
                    if forced_team != -1 and (t + 1) != forced_team: continue
                    
                    if team_counts[t] + partners_needed < TEAM_SIZE:
                        is_compatible = True
                        for mem in range(num_selected):
                            if assignments[mem] == (t + 1):
                                m_name = active_players[mem].name
                                for b in bl:
                                    if ((b['p1'] == m_name and b['p2'] == my_name) or 
                                        (b['p2'] == m_name and b['p1'] == my_name)):
                                        is_compatible = False
                                        break
                            if not is_compatible: break
                        
                        if is_compatible:
                            if forced_team > -1: 
                                target_team = t
                                break
                            elif teams[t] < min_elo:
                                min_elo     = teams[t]
                                target_team = t
                
                if target_team != -1:
                    assignments[p]              =   target_team + 1
                    teams[target_team]          +=  active_players[p].elo
                    team_counts[target_team]    +=  1
                    curr_name                   = active_players[p].name
                    for r in reqs:
                        p_part = ""
                        if r['p1'] == curr_name: p_part = r['p2']
                        if r['p2'] == curr_name: p_part = r['p1']
                        if p_part:
                            pp_idx = next((i for i, pl in enumerate(active_players) if pl.name == p_part), -1)
                            if pp_idx > -1 and assignments[pp_idx] == 0:
                                assignments[pp_idx] = target_team + 1
                                teams[target_team] += active_players[pp_idx].elo
                                team_counts[target_team] += 1
                else:
                    possible = False
                    break

        if possible:
            spread = max(teams) - min(teams)
            if spread < best_overall_spread:
                best_overall_spread = spread
                best_assignments = list(assignments)

    if not best_assignments:
        print("Could not generate valid teams, check constraints")
        return
    
    write_output(num_selected, original_count, num_teams, active_players, best_assignments, reqs, bl, setup_config)

if __name__ == "__main__": main()