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



Example to show the schedule for Dutch Crews, crew 123 and every crew from Oxford Brookes in Housten, USA
```
python henley_scheduler.py --crew NED 123 'Oxford brookes' --gmt -6
```


Example Output:
```
Race Schedule for Wednesday 03 July 2024
----------------------------------------
  Race #  GB time    Local Time    Berks station                            Bucks station                             Trophy
--------  ---------  ------------  ---------------------------------------  ----------------------------------------  --------
      15  09:50      10:50         438 Ever Green B.C., USA                 433 A.A.S.R. Skøll, NED                   P. Wales
      17  10:05      11:05         127 D.S.R. Laga 'B', NED                 161 Oxford Brookes Univ. 'B'              Temple
      22  10:35      11:35         348 Univ. California, Berkeley 'B', USA  328 A.R.S.R. Skadi & D.S.R. Laga, NED     Visitors
      33  11:40      12:40         119 A.S.R. Nereus 'A', NED               138 G.S.R. Aegir, NED                     Temple
      35  11:50      12:50         723 S.N.B. Cox, ZIM                      718 J. Bakker, NED                        Diamonds
      40  12:20      13:20         456 T.S.S. & Proteus-Eretes, NED         445 Ormsund R.K. & Christiania R.K., NOR  P. Wales
      41  14:00      15:00         733 D. Junge, GER                        735 L. Kreiter, NED                       Diamonds
      46  14:30      15:30         162 Oxford Brookes Univ. 'C'             120 A.S.R. Nereus 'B', NED                Temple
      51  15:00      16:00         61 Nonesuch B.C.                         47 K.A.R.Z.V. 'De Hoop', NED              Thames
      59  15:45      16:45         734 L. Keijzer, NED                      752 R. Spelman, IRL                       Diamonds
      63  16:10      17:10         204 G.S.R. Aegir, NED                    195 Drexel Univ., USA                     Island
      70  17:50      18:50         725 J.D. Free, AUS                       746 B.A.G. Poll, NED                      Diamonds
      75  18:20      19:20         126 D.S.R. Laga 'A', NED                 181 University of Bristol                 Temple
      80  18:50      19:50         453 R.G. Hansa Hamburg & R.V. Kappeln    459 U.S.R. Triton, NED                    P. Wales
      83  19:10      20:10         339 Nottingham & Union & Oxford Univ.    344 Okeanos & Vidar, NED                  Visitors
```



## Rights

All rights to the race schedule data are owned by the Henley Royal Regatta. The data is fetched from the official [Henley Royal Regatta Race TimeTable](https://www.hrr.co.uk/2024-competition/race-timetable/)
