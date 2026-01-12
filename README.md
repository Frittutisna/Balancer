# Balancer for Sports Modes and NGMC Tour

1. List players and their relevant **Elos** ([Watched](https://docs.google.com/spreadsheets/d/1JZvb8iIo6Nq01SkEvEPMrzd-vnlsNNVhv9QZOnaG4k4/edit?gid=1870982262#gid=1870982262), [Random](https://docs.google.com/spreadsheets/d/1JZvb8iIo6Nq01SkEvEPMrzd-vnlsNNVhv9QZOnaG4k4/edit?gid=1899407725#gid=1899407725)) in each line of `players.txt` with the format `players, Elo` (e.g., `HakoHoka, 5.897`).
2. List pairs of players that want to **team up** in each line of `requests.txt` (e.g., `HakoHoka, florenz`).
Make sure this **only** lists players from `players.txt`.
3. List pairs of players that **don't want to team up** in each line of `blacklists.txt` (e.g., `chommy, FeyFey`).
Make sure this also **only** lists players from `players.txt`, 
and ensure that **no request/blacklist pairs are the same** 
(e.g., `HakoHoka, florenz` in `requests.txt`, 
but also `florenz, HakoHoka` in `blacklists.txt`). 
4. Gather all the TXT files in the **same folder** as this script
5. Change **`MODE`** to `MLB`, `NBA`, `NFL`, or `NONE` if you're just hosting a normal tour
6. Run this script
7. Repeat Step 6 until the **Final Spread** is low enough to your liking
8. **Copy** the results and send it to `#tour-information`
9. If you're hosting **NFL Mode**, also **ping** Captains and ask them about **team split**.
**Prepare** your own team splits in case Captain(s) failed to submit their team split(s) in time.
This is purely personal opinion, but I recommend putting it `T2, T3, T1 (C), T4`