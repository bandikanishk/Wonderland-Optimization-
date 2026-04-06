# CANADA'S WONDERLAND TRIP PLANNER
Author: Kanishk Bandi
## PROGRAM OVERVIEW
This program helps users plan an efficient route through Canada's Wonderland.

It considers:

- Ride wait times
- Walking distances between rides
- A user-defined time limit

The program provides two planning options:

1. A fast greedy method
2. An advanced optimization method

## FEATURES

- Shortest path between rides using a priority-based traversal
- Advanced route optimization using recursive traversal
- Fast greedy approximation option
- Save and load trips using text files
- Interactive command-line interface

## HOW TO RUN

1. Make sure Python 3.11 is installed

2. Install required library:
   pip install requests

3. Run the program:
   python main.py

---

## HOW TO USE

1. Start a new trip
2. Select rides from the available list
3. Choose one of the following:
   - Short method (fast)
   - Advanced method (optimal)
4. Optionally save your trip

## FILES INCLUDED
- main.py       (main program)
- adts.py            (priority queue ADT)
- requirements.txt   (dependencies)
- README.txt         (this file)
- USER_GUIDE.txt     (detailed user instructions)

## NOTES
- Walking speed is assumed to be 5 km/h
- Backup data is used when the park is closed
- Ride availability may vary in real-time
