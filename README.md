# Balancer v1.1 for Sports Modes (MLB, NBA, NFL) and NGMC Tours

1. List players and their relevant **Elos** ([Watched](https://docs.google.com/spreadsheets/d/1JZvb8iIo6Nq01SkEvEPMrzd-vnlsNNVhv9QZOnaG4k4/edit?gid=1870982262#gid=1870982262), [Random](https://docs.google.com/spreadsheets/d/1JZvb8iIo6Nq01SkEvEPMrzd-vnlsNNVhv9QZOnaG4k4/edit?gid=1899407725#gid=1899407725)) in each line of `players.txt` with the format `player, Elo` (e.g., `HakoHoka, 5.897`).
2. (Optional) List pairs of players that want to **team up** 
in each line of `requests.txt` (e.g., `HakoHoka, florenz`).
Make sure this **only** lists players from `players.txt`.
3. (Optional) List pairs of players that **don't want to team up** 
in each line of `blacklists.txt` (e.g., `chommy, FeyFey`).
Make sure this also **only** lists players from `players.txt`, 
and ensure that **no request/blacklist pairs are the same** 
(e.g., `HakoHoka, florenz` in `requests.txt`, 
but also `florenz, HakoHoka` in `blacklists.txt`). 
4. **Download** `Balancer.py`, then gather all the TXT files in the **same folder** as `Balancer.py`
5. Change **`MODE`** to `MLB`, `NBA`, `NFL`, or `NONE` if you're just hosting a normal NGMC tour
6. Run `Balancer.py` and check the output in `teams.txt`
7. **Copy** the output in `teams.txt` and **send** it to `#tour-information`