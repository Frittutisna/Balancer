import os
import math
import random
import re

MODE        = 'NONE'
TEAM_SIZE   = 4
SIMULATIONS = 100
THRESHOLD   = 0.05

FILENAMES       = {
    'PLAYERS'   : 'players.txt',
    'REQS'      : 'requests.txt',
    'BL'        : 'blacklists.txt',
    'CODES'     : 'codes.txt',
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

def get_team_elo(members, mode, captains_map):
    total = 0.0
    for m in members:
        if mode != 'NONE' and m.name in captains_map    : total += (m.elo * 2)
        else                                            : total += m.elo
    return total

def get_stats_block(teams_data):
    if not teams_data: return 0.0
    scores  = [t['total_elo'] for t in teams_data]
    avg_elo = sum(scores) / len(scores)
    return avg_elo

def write_output(num_teams, active_players, final_assignments, setup_config):
    captains_map    = {active_players[i].name: True for i in range(num_teams)}
    teams_data      = []
    custom_names    = setup_config['NAMES']

    for t_idx in range(1, num_teams + 1):
        members     = [p for i, p in enumerate(active_players) if final_assignments[i] == t_idx]
        total_elo   = get_team_elo(members, MODE, captains_map)

        members.sort(key = lambda x: x.elo, reverse = True)
        if MODE == 'NFL' and len(members) == 4: members = [members[0], members[3], members[1], members[2]]
        code_mem_strings = [f"{m.name} ({m.elo:.3f})" for m in members]
        team_name = custom_names.get(t_idx)
        if not team_name:
            if      MODE == 'NFL'   : team_name = NFL_NAMES.get(t_idx, f"Team {t_idx}")
            elif    MODE == 'NBA'   : team_name = NBA_NAMES.get(t_idx, f"Team {t_idx}")
            elif    MODE == 'MLB'   : team_name = MLB_NAMES.get(t_idx, f"Team {t_idx}")
            else                    : team_name = f"Team {t_idx}"
        
        if MODE == 'NONE'   : final_line = " ".join(code_mem_strings)
        else                : final_line = f"{team_name} ({total_elo:.3f}): " + " ".join(code_mem_strings)
        teams_data.append({'total_elo': total_elo, 'final_str': final_line})

    avg_elo = get_stats_block(teams_data)

    with open(FILENAMES['CODES'], 'w', encoding = 'utf-8') as f:
        for t in teams_data: f.write(f"{t['final_str']}\n")
        f.write(f"\nAverage: {avg_elo:.3f}\n\n")
        f.write(f"{setup_config['CHALLONGE']}")

    print(f"Codes written to {FILENAMES['CODES']}")

def main():
    global MODE, TEAM_SIZE
    setup_config = parse_setup()

    if      setup_config['MODE'] != 'NONE'  : MODE      = setup_config['MODE']
    elif    setup_config['MODE'] == 'NONE'  : MODE      = 'NONE'
    if      'TEAM_SIZE' in setup_config     : TEAM_SIZE = setup_config['TEAM_SIZE']

    all_players = parse_file(FILENAMES['PLAYERS'],  'player')
    raw_reqs    = parse_file(FILENAMES['REQS'],     'pair')
    raw_bl      = parse_file(FILENAMES['BL'],       'pair')

    if len(all_players) < TEAM_SIZE * 2: return

    original_count  = len(all_players)
    num_selected    = math.floor(original_count / (TEAM_SIZE * 2)) * (TEAM_SIZE * 2)
    active_players  = all_players[:num_selected]
    active_players.sort(key = lambda x: x.elo, reverse = True)

    num_teams       = int(num_selected / TEAM_SIZE)
    captains_map    = {active_players[i].name: True for i in range(num_teams)}

    current_reqs            = list(raw_reqs)
    final_best_assignments  = None
    final_best_spread       = float('inf')

    while True:
        iteration_best_spread       = float('inf')
        iteration_best_assignments  = None

        print(f"Running optimized balancing over {SIMULATIONS} iterations with {len(current_reqs)} request(s)")

        for _ in range(SIMULATIONS):
            assignments = [0] * num_selected
            team_counts = [0] * num_teams
            
            cap_indices = list(range(num_teams))
            random.shuffle(cap_indices)
            for i, t_idx in enumerate(cap_indices):
                assignments[i]      = t_idx + 1
                team_counts[t_idx]  = 1
                
            pool = list(range(num_teams, num_selected))
            random.shuffle(pool)
            for i, p_idx in enumerate(pool):
                t_idx               =   i % num_teams
                assignments[p_idx]  =   t_idx + 1
                team_counts[t_idx]  +=  1

            improved = True
            while improved:
                improved = False
                for i in range(num_teams, num_selected):
                    for j in range(i + 1, num_selected):
                        t1_idx = assignments[i] - 1
                        t2_idx = assignments[j] - 1
                        if t1_idx == t2_idx: continue

                        t1_m = [active_players[k] for k in range(num_selected) if assignments[k] == t1_idx + 1]
                        t2_m = [active_players[k] for k in range(num_selected) if assignments[k] == t2_idx + 1]

                        def has_violation(mems, _):
                            names = [m.name for m in mems]
                            for r in current_reqs:
                                if (r['p1'] in names and r['p2'] not in names) or (r['p2'] in names and r['p1'] not in names):
                                    if any(p.name == (r['p2'] if r['p1'] in names else r['p1']) for p in active_players): return True
                            for b in raw_bl:
                                if b['p1'] in names and b['p2'] in names: return True
                            return False

                        curr_violation = has_violation(t1_m, t1_idx) or has_violation(t2_m, t2_idx)

                        all_elos = []
                        for t in range(1, num_teams + 1):
                            mems = [active_players[k] for k in range(num_selected) if assignments[k] == t]
                            all_elos.append(get_team_elo(mems, MODE, captains_map))
                        curr_spread = max(all_elos) - min(all_elos)

                        assignments[i] = t2_idx + 1
                        assignments[j] = t1_idx + 1

                        new_t1_m = [active_players[k] for k in range(num_selected) if assignments[k] == t1_idx + 1]
                        new_t2_m = [active_players[k] for k in range(num_selected) if assignments[k] == t2_idx + 1]

                        new_violation = has_violation(new_t1_m, t1_idx) or has_violation(new_t2_m, t2_idx)
                        
                        new_elos = []
                        for t in range(1, num_teams + 1):
                            mems = [active_players[k] for k in range(num_selected) if assignments[k] == t]
                            new_elos.append(get_team_elo(mems, MODE, captains_map))
                        new_spread = max(new_elos) - min(new_elos)

                        if (
                            (curr_violation and not new_violation) or 
                            (not new_violation and not curr_violation and new_spread < curr_spread)
                        ): improved = True
                        else:
                            assignments[i] = t1_idx + 1 
                            assignments[j] = t2_idx + 1

            final_elos  = []
            valid       = True
            for t in range(1, num_teams + 1):
                mems = [active_players[k] for k in range(num_selected) if assignments[k] == t]
                if has_violation(mems, t): valid = False
                final_elos.append(get_team_elo(mems, MODE, captains_map))
            
            if valid:
                spread = max(final_elos) - min(final_elos)
                if spread < iteration_best_spread:
                    iteration_best_spread       = spread
                    iteration_best_assignments  = list(assignments)

        if iteration_best_assignments:
            team_elos = []
            for t in range(1, num_teams + 1):
                mems = [active_players[k] for k in range(num_selected) if iteration_best_assignments[k] == t]
                team_elos.append(get_team_elo(mems, MODE, captains_map))
            
            avg_elo         = sum(team_elos) / len(team_elos)
            current_ratio   = iteration_best_spread / avg_elo

            if current_ratio <= THRESHOLD or not current_reqs:
                final_best_assignments  = iteration_best_assignments
                final_best_spread       = iteration_best_spread
                break
            else:
                dropped = current_reqs.pop()
                print(f"Ratio ({current_ratio:.4f}) > Threshold ({THRESHOLD}), dropping: {dropped}")
        else: break

    if final_best_assignments:
        write_output(num_teams, active_players, final_best_assignments, setup_config)
        print(f"Final Spread: {final_best_spread:.3f}")

if __name__ == "__main__": main()