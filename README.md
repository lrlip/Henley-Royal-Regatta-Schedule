# Henley Royal Regatta - Daily Race Schedule
THe Henley Royal Regatta is one of the most prestigious races in rowing. A lot of crews compete and it can be hard to keep track of your favorite team.
This script fetches and displays the race timetable for the Henley Royal Regatta. It allows users to search for specific crews and displays the race schedule in both GB and local times based on the specified GMT offset. Run this script after the draw is published to get the latest results.


## Installation
```
pyton -m venv .venv
.\.venv\Script\activate
pip install -r .\requirements.txt
```

## Usage 

```
python henley_scheduler.py [--crew <search_string1> <search_string2> ...] [--gmt <offset>]
```

### Arguments
- `--crew`: List of substring that should be matched with the name of the crews. Can be country code (_NED_) for Non-UK contenders, the number of the crew (_123_) or every crew from one particular club (_'Thames R.C.'_ or _Brookes_) separated by spaces (capital insensitive)
- `--gmt`: GMT offset for local time display (default: 1 for NL time)
- Without arguments, the whole schedule is shown.



Example to show the schedule for Dutch Crews, crew 123 and every crew from Oxford Brookes.
```
python henley_scheduler.py --crew NED 123 'Oxford brookes' --gmt +1
```


Example Output:
```
Race Schedule for Tuesday 02 July 2024
GB time   Local Time  Berks station                            Bucks station                            Trophy
09:45     10:45       132 Edinburgh Univ. 'A'                  120 A.S.R. Nereus 'B', NED               Temple
11:10     12:10       159 Orange Coast Coll., USA              127 D.S.R. Laga 'B', NED                 Temple
14:45     15:45       600 K.A.R.Z.V. 'De Hoop', NED            610 Nottingham R.C.                      Britannia
14:50     15:50       119 A.S.R. Nereus 'A', NED               133 Edinburgh Univ. 'B'                  Temple
16:05     17:05       138 G.S.R. Aegir, NED                    175 St. Paul's Sch.                      Temple
17:35     18:35       181 University of Bristol                147 K.S.R.V. Njord, NED                  Temple
19:00     20:00       126 D.S.R. Laga 'A', NED                 171 Southampton Univ.                    Temple
```



## Rights

All rights to the race schedule data are owned by the Henley Royal Regatta. The data is fetched from the official [Henley Royal Regatta Race TimeTable](https://www.hrr.co.uk/2024-competition/race-timetable/)
