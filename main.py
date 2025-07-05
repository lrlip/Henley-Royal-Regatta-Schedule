#!/usr/bin/env python3
import argparse
from typing import List, Optional

from HenleySchedule.henley_scheduler import HenleySchedule


def main():
    parser = argparse.ArgumentParser(
        description='Fetch and display Henley Royal Regatta race timetable.')
    
    parser.add_argument('-crew', '--crew', type=str, nargs='+', default=None, required=False,
                        help='List of strings to match crew names, separated by spaces')
    
    parser.add_argument('-gmt', '--gmt', type=int, default=1, required=False,
                        help='GMT offset for local time display (default: 1 for NL time)')
    
    parser.add_argument('-boat', '--boat', type=str, required=False,
                        help='Filter races by boat type (e.g., M8+, W4x)')
    
    parser.add_argument('-trophy', '--trophy', type=str, required=False,
                        help='Filter races by trophy name')
        
    args = parser.parse_args()
    
    scheduler = HenleySchedule(
        crew=args.crew, 
        gmt_offset=args.gmt, 
        boat_type=args.boat, 
        trophy=args.trophy,
    )
    scheduler.show_race_schedule()


if __name__ == "__main__":
    main()
