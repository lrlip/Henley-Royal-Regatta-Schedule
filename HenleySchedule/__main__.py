import argparse
from typing import List, Optional

from HenleySchedule.henley_scheduler import HenleySchedule


def main(search_strings: Optional[List[str]] = None, 
         gmt_offset: int = 1,
         boat_type: Optional[str] = None,
         trophy: Optional[str] = None
         ) -> None:
    
    scheduler = HenleySchedule(
        crew=search_strings,
        gmt_offset=gmt_offset,
        boat_type=boat_type,
        trophy=trophy,
    )
    scheduler.show_race_schedule()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Fetch and display Henley Royal Regatta race timetable.')
    
    parser.add_argument('--crew', type=str, nargs='+', default=None, required=False,
                        help='List of strings to match crew names, separated by spaces')
    
    parser.add_argument('--gmt', type=int, default=1, required=False,
                        help='GMT offset for local time display (default: 1 for NL time)')
    
    parser.add_argument('--boat', type=str, required=False,
                        help='Filter races by boat type (e.g., M8+, W4x)')
    
    parser.add_argument('--trophy', type=str, required=False,
                        help='Filter races by trophy name')
        
    args = parser.parse_args()
    
    main(
        args.crew, 
        args.gmt, 
        args.boat, 
        args.trophy,
    )
