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
python henley_scheduler.py --crew <search_string1> <search_string2> ... [--gmt <offset>]
```

### Arguments
- `--crew`: List of substring that should be matched with the name of the crews. Can be country code (_NED_) for Non-UK contenders, the number of the crew (_123_) or every crew from one particular club (_'Thames R.C.'_ or _Brookes_) separated by spaces (capital insensitive)
- `--gmt`: GMT offset for local time display (default: 1 for NL time)
- Without arguments, the whole schedule is shown.



Example to show the schedule for Dutch Crews, crew 123 and every crew from Oxford Brookes.
```
python henley_scheduler.py --crew NED 123 'Oxford brookes' --gmt -1
```


Example Output
```
Race Schedule for Tuesday 02 July 2024
GB time   Local time  Berks station                            Bucks station
09:05     10:05       162 Oxford Brookes Univ. 'C'             139 Hampton Sch.
10:10     11:10       394 Thames R.C. 'B'                      356 City of Oxford R.C.
10:20     11:20       163 Oxford Brookes Univ. 'D'             130 Durham Univ. 'A'
11:10     12:10       159 Orange Coast Coll., USA              127 D.S.R. Laga 'B', NED
12:00     13:00       156 Nottingham Univ.                     161 Oxford Brookes Univ. 'B'
18:05     19:05       160 Oxford Brookes Univ. 'A'             121 Bedford Sch.
19:00     20:00       126 D.S.R. Laga 'A', NED                 171 Southampton Univ.
19:35     20:35       635 Oxford Brookes Univ. 'B'             638 Univ. of London 'B'
```

## Rights

All rights of the schedule belong to the Henley Royal Regatta. Data is fetched from [Henley Royal Regatta Race TimeTable](https://www.hrr.co.uk/2024-competition/race-timetable/)