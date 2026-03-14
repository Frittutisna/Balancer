# Balancer v2.0.0 for Sports Modes (MLB, NBA, NFL) and NGMC Tours

1. List players and their relevant Elos ([Watched](https://docs.google.com/spreadsheets/d/1Fm6pMyXv7qhOQkLah4yX9HNow4WaDR4HJuAVMukQl34/edit?gid=2040874005#gid=2040874005), [Random](https://docs.google.com/spreadsheets/d/1Fm6pMyXv7qhOQkLah4yX9HNow4WaDR4HJuAVMukQl34/edit?gid=0#gid=0)) in each line of `players.txt` with the format `player, Elo` (e.g., `HakoHoka, 59.413`)
2. List pairs of players that want to team up in each line of `requests.txt` (e.g., `HakoHoka, florenz`). Make sure this only lists players from `players.txt`
3. List pairs of players that don't want to team up in each line of `blacklists.txt` (e.g., `chommy, FeyFey`). Make sure this also only lists players from `players.txt`, and ensure that no request/blacklist pairs are the same (e.g., `HakoHoka, florenz` in `requests.txt`, but also `florenz, HakoHoka` in `blacklists.txt`)
4. Fill in `setup.txt`. The Balancer defaults to `NONE` mode (for normal tours), team size of 4 players, placeholder links, and no team names where applicable
5. Download the [Balancer](https://github.com/Frittutisna/Balancer/blob/main/Balancer.py), then gather all the `*.txt` files in the same folder as the Balancer
6. Run the Balancer and copy-paste `codes.txt` to `#tour-information`