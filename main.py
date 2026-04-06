
import requests
import math
from datetime import datetime
from adts import Pathqueue
from typing import Dict, List, Tuple, Optional

"""
Program Overview:

This program helps users plan an optimal route through Canada's Wonderland.

Core Algorithms:
- Shortest Path (_find_route): Uses a ADT similar to queue (Level order visit) to find the shortest walking path between rides.
- Optimization (_best_order): Recursively explores all ride orders to find the optimal sequence within a time limit.
- Greedy Approach (most_optimal_path_short): Quickly selects rides that fit within time without optimizing order.

Additional Features:
- Real-time or backup ride data
- Save and load trips using text files
"""

class RideDataSource:
    """A RideDataSource: an abstract data source for retrieving ride information.

    This class defines a common interface for accessing ride wait times.
    Subclasses implement different ways of retrieving ride data, such as
    from a live API or from a backup dataset.

    This class should not be instantiated directly.

    === Public Methods ===
    get_available_rides:
        Return a dictionary mapping ride names to their wait times.

    === Representation Invariants ===
    - All returned wait times are integers >= 0
    - All ride names are strings
    """
    def get_available_rides(self) -> Dict[str, int]:
        """
        function that returns available ride times.
        """
        raise NotImplementedError


class WonderlandAPIData(RideDataSource):
    """A WonderlandAPIData: a data source that retrieves live ride data from an API.

    This class fetches real-time ride wait times from an external API and
    returns only rides that are currently open.

    === Public Methods ===
    get_available_rides:
        Return a dictionary mapping ride names to wait times for all open rides.

    === Representation Invariants ===
    - All returned rides are currently open
    - All wait times are integers >= 0
    """
    def get_available_rides(self)-> Dict[str, int]:
        url = 'https://queue-times.com/parks/58/queue_times.json'
        data = requests.get(url) #uses the requests library to return a dictionary of the data
        rides = {} #data contains information
        #not needed like lands and rides that are not open so we make new dict with info needed
        if data.status_code == 200: #sucess!
            for land in data.json()['lands']:
                for ride in land['rides']:
                    if ride['is_open']:#checks if ride is open then adds it
                        rides[ride['name']] = ride['wait_time'] #saves ride name with wait time
        return rides #returns dict


class WonderlandBackupData(RideDataSource):
    """A WonderlandBackupData: a data source that provides static ride data.

    This class returns a predefined set of ride wait times and is used when
    live data is unavailable (e.g., when the park is closed).

    === Public Methods ===
    get_available_rides:
        Return a dictionary mapping ride names to predefined wait times.

    === Representation Invariants ===
    - All ride names are strings
    - All wait times are integers >= 0
    """
    def get_available_rides(self) -> Dict[str, int]:
        """
        returns a dictionary with the average wait time found on the same website as WonderlandAPIData
        """
        return {
            'AlpenFury': 108,
            'Leviathan': 40,
            'Yukon Striker': 40,
            'Vortex': 32,
            'Backlot Stunt Coaster': 30,
            'Behemoth': 30,
            'Ghoster Coaster': 28,
            'The Fly': 28,
            'Boo Blasters on Boo Hill': 27,
            'Thunder Run': 23,
            'Mighty Canadian Minebuster': 22,
            'Klockwerks': 19,
            'Drop Tower': 18,
            'Flying Eagles': 18,
            'Taxi Jam': 17,
            'Timberwolf Falls': 16,
            'Psyclone': 15,
            'Wilde Beast': 15,
            'Beagle Brigade Airfield': 14,
            'PEANUTS 500': 14,
            'Flight Deck': 13,
            'Sledge Hammer': 13,
            'WindSeeker': 13,
            'Character Carrousel': 11,
            'Skyhawk': 11,
            "Viking's Rage": 11,
            "Sally's Love Buggies": 10,
            "Snoopy's Revolution": 10,
            "Lucy's Tugboat": 9,
            'Antique Carrousel': 8,
            'Flying Canoes': 8,
            'The Pumpkin Patch': 8,
            'Woodstock Whirlybirds': 8,
            'Lumberjack': 7,
            'Sugar Shack': 7,
            "Snoopy's Space Race": 6,
            'Swing of the Century': 6,
            'Tundra Twister': 10
        }

def park_closed() -> bool:
    """
    Returns True if park is closed or False otherwise.
    """
    now = datetime.now()
    #If the current month is not in the opening months or 
    #the current time is too early or later than the parks opening hours
    #return True signaling the park is closed
    if now.month < 5 or now.month > 10: 
        return True
    if now.hour < 10 or now.hour > 20:
        return True

    return False


class WonderlandTrip:
    """A WonderlandTrip: represents a user's planned trip through Canada's Wonderland.

        This class stores the user's selected rides and provides functionality
        to compute efficient routes through the park based on ride wait times
        and walking distances.

        === Public Attributes ===
        None

        === Private Attributes ===
        _user_rides:
            A list of ride names selected by the user.
        _data_set:
            A dictionary mapping ride names to their wait times.
        _ride_locations:
            A dictionary mapping ride names to (x, y) coordinates in the park.
        _map:
            A dictionary representing the park layout as a graph, where each ride
            maps to a list of adjacent rides.

        === Representation Invariants ===
        - All rides in _user_rides are keys in _data_set
        - All rides in _map are keys in _ride_locations
        - All adjacent rides in _map exist in _ride_locations

        - _data_set[ride] >= 0 for all rides

        - _user_rides contains no duplicates

        - If a ride is in _map, then all its neighbours are also valid rides
        """
    _user_rides: List[str]
    _data_set: Dict[str, int]
    _ride_locations: Dict[str, Tuple[int, int]]
    _map: Dict[str, List[str]]
    def __init__(self, rides, data_source: RideDataSource):
        """
        Initializes a WonderlandTrip object.
        """
        self._user_rides = rides
        self._data_set = data_source.get_available_rides()
        self._ride_locations = {
            "Entrance": (0, 0),
            "Snoopy's Space Race": (-80, 80),
            "Lucy's Tugboat": (-120, 100),
            "PEANUTS 500": (-160, 120),
            "Sally's Love Buggies": (-180, 160),
            "Snoopy's Revolution": (-200, 200),
            "Woodstock Whirlybirds": (-220, 240),
            "Taxi Jam": (-120, 180),
            "The Pumpkin Patch": (-160, 240),
            "Beagle Brigade Airfield": (-180, 280),
            "Boo Blasters on Boo Hill": (40, 100),
            "Flying Canoes": (80, 160),
            "Character Carrousel": (0, 200),
            "Flying Eagles": (40, 260),
            "Timberwolf Falls": (100, 300),
            "Sugar Shack": (160, 340),
            "Antique Carrousel": (200, 380),
            "Ghoster Coaster": (80, 240),
            "Wilde Beast": (140, 360),
            "Mighty Canadian Minebuster": (180, 420),
            "Thunder Run": (180, 280),
            "Klockwerks": (260, 420),
            "Psyclone": (240, 360),
            "Sledge Hammer": (320, 420),
            "Skyhawk": (340, 360),
            "WindSeeker": (400, 360),
            "Drop Tower": (320, 280),
            "Swing of the Century": (420, 280),
            "Tundra Twister": (460, 360),
            "Flight Deck": (220, 500),
            "Vortex": (260, 580),
            "Behemoth": (340, 520),
            "Leviathan": (360, 600),
            "Yukon Striker": (460, 500),
            "Backlot Stunt Coaster": (400, 240),
            "AlpenFury": (440, 580),
            "The Fly": (460, 180),
            "Lumberjack": (500, 220),
        }
        self._map = { "Entrance": [ "Snoopy's Space Race","Boo Blasters on Boo Hill"],
    "Snoopy's Space Race": [
        "Entrance",
        "Lucy's Tugboat",
        "PEANUTS 500"
    ],
    "Lucy's Tugboat": [
        "Snoopy's Space Race",
        "PEANUTS 500",
        "Sally's Love Buggies"
    ],
    "PEANUTS 500": [
        "Snoopy's Space Race",
        "Lucy's Tugboat",
        "Sally's Love Buggies",
        "Taxi Jam"
    ],
    "Sally's Love Buggies": [
        "Lucy's Tugboat",
        "PEANUTS 500",
        "Snoopy's Revolution"
    ],
    "Snoopy's Revolution": [
        "Sally's Love Buggies",
        "Woodstock Whirlybirds"
    ],
    "Woodstock Whirlybirds": [
        "Snoopy's Revolution",
        "The Pumpkin Patch",
        "Beagle Brigade Airfield"
    ],
    "Taxi Jam": [
        "PEANUTS 500",
        "The Pumpkin Patch",
        "Character Carrousel"
    ],
    "The Pumpkin Patch": [
        "Taxi Jam",
        "Woodstock Whirlybirds",
        "Beagle Brigade Airfield"
    ],
    "Beagle Brigade Airfield": [
        "Woodstock Whirlybirds",
        "The Pumpkin Patch",
        "Flying Eagles"
    ],
    "Boo Blasters on Boo Hill": [
        "Entrance",
        "Flying Canoes",
        "Thunder Run"
    ],
    "Flying Canoes": [
        "Boo Blasters on Boo Hill",
        "Character Carrousel",
        "Ghoster Coaster"
    ],
    "Character Carrousel": [
        "Taxi Jam",
        "Flying Canoes",
        "Flying Eagles"
    ],
    "Flying Eagles": [
        "Character Carrousel",
        "Beagle Brigade Airfield",
        "Timberwolf Falls"
    ],
    "Timberwolf Falls": [
        "Flying Eagles",
        "Sugar Shack",
        "Wilde Beast"
    ],
    "Sugar Shack": [
        "Timberwolf Falls",
        "Antique Carrousel",
        "Psyclone"
    ],
    "Antique Carrousel": [
        "Sugar Shack",
        "Wilde Beast",
        "Klockwerks"
    ],
    "Ghoster Coaster": [
        "Flying Canoes",
        "Wilde Beast",
        "Mighty Canadian Minebuster"
    ],
    "Wilde Beast": [
        "Timberwolf Falls",
        "Antique Carrousel",
        "Ghoster Coaster",
        "Mighty Canadian Minebuster",
        "Thunder Run"
    ],
    "Mighty Canadian Minebuster": [
        "Ghoster Coaster",
        "Wilde Beast",
        "Thunder Run",
        "Flight Deck"
    ],
    "Thunder Run": [
        "Boo Blasters on Boo Hill",
        "Wilde Beast",
        "Mighty Canadian Minebuster",
        "Drop Tower"
    ],
    "Klockwerks": [
        "Antique Carrousel",
        "Psyclone",
        "Sledge Hammer"
    ],
    "Psyclone": [
        "Sugar Shack",
        "Klockwerks",
        "Skyhawk"
    ],
    "Sledge Hammer": [
        "Klockwerks",
        "Skyhawk",
        "Behemoth"
    ],
    "Skyhawk": [
        "Psyclone",
        "Sledge Hammer",
        "WindSeeker",
        "Backlot Stunt Coaster"
    ],
    "WindSeeker": [
        "Skyhawk",
        "Drop Tower",
        "Tundra Twister"
    ],
    "Drop Tower": [
        "Thunder Run",
        "WindSeeker",
        "Swing of the Century",
        "Backlot Stunt Coaster"
    ],
    "Swing of the Century": [
        "Drop Tower",
        "Tundra Twister",
        "Lumberjack"
    ],
    "Tundra Twister": [
        "WindSeeker",
        "Swing of the Century",
        "Yukon Striker"
    ],
    "Flight Deck": [
        "Mighty Canadian Minebuster",
        "Vortex",
        "Behemoth"
    ],
    "Vortex": [
        "Flight Deck",
        "Leviathan",
        "Behemoth"
    ],
    "Behemoth": [
        "Flight Deck",
        "Vortex",
        "Leviathan",
        "Sledge Hammer"
    ],
    "Leviathan": [
        "Vortex",
        "Behemoth",
        "Yukon Striker",
        "AlpenFury"
    ],
    "Yukon Striker": [
        "Leviathan",
        "Tundra Twister",
        "AlpenFury"
    ],
    "Backlot Stunt Coaster": [
        "Skyhawk",
        "Drop Tower",
        "The Fly"
    ],
    "AlpenFury": [
        "Leviathan",
        "Yukon Striker",
        "The Fly"
    ],
    "The Fly": [
        "Backlot Stunt Coaster",
        "AlpenFury",
        "Lumberjack"
    ],
    "Lumberjack": [
        "The Fly",
        "Swing of the Century"
    ]
    }

    def _calculate_dist(self, a:str, b:str) -> float:
        """
         Return distance between two rides.

         >>> g = WonderlandTrip([], WonderlandBackupData())
         >>> g._calculate_dist("Entrance", "Entrance")
         0.0
         """
        x1, y1 = self._ride_locations[a]
        x2, y2 = self._ride_locations[b]
        #Euclidean distance formula
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def _find_route(self, r1:str, r2:str) -> Optional[Tuple[List[str], float]]:
        """
        Return the shortest path from r1 to r2.
        >>> g = WonderlandTrip([], WonderlandBackupData())
        >>> g._find_route("Entrance", "Entrance")
        (['Entrance'], 0)
        """
        queue = Pathqueue()
        queue.push((r1,0,[r1])) #keeps track of posibilites, format: (ride,distance,path), starts with entrance
        best_dist = {r1 : 0} #keeps track of best distance to know when we reached the end
        while not queue.is_empty(): #while there are more possibilities
            current = queue.pop() #removes the smallest distance or possibility with most potential
            current_ride = current[0]
            current_dist = current[1]
            current_path = current[2]
            if current_ride == r2: #found the best ride return it with its total distance
                return current_path,current_dist
            else:
                for pathway in self._map[current_ride]: #continue traversing through graph
                    #calculate each possibile distance
                    new_dist = self._calculate_dist(current_ride,pathway) + current_dist 
                    #If this is a new ride or this new distance is less than the rides previous calculated distance
                    if pathway not in best_dist or new_dist < best_dist[pathway]: 
                        best_dist[pathway] = new_dist #update the dict
                        queue.push((pathway,new_dist,current_path + [pathway])) #add new possibility to the queue
        return None

    def show_available_rides(self) -> None:
        """
        Prints available rides.
        """
        print("\nAvailable Rides:\n")
        for ride in self._user_rides:
            print(f"{ride} — {self._data_set[ride]} min")

    def get_ride_times(self) -> None:
        """
        Prints wait times for rides in _user_rides.
        """
        print("\nSelected Ride Wait Times:\n")
        for ride in self._user_rides:
            if ride in self._data_set:
                print(f"{ride} — {self._data_set[ride]} min")
            else:
                print(f"{ride} is not available")

    def remove_ride(self, ride) -> None:
        """
            Remove a ride from the trip.

            >>> g = WonderlandTrip(['Leviathan'], WonderlandBackupData())
            >>> g.remove_ride('Leviathan')
            Removed Leviathan
            """
        if ride not in self._user_rides:
            print("Ride wasn't in your trip.")
        else:
            self._user_rides.remove(ride)
            print(f"Removed {ride}")

    def most_optimal_path_short(self, max_time: int) -> None:
        """
        Print a quick path using greedy approach.

        >>> g = WonderlandTrip(['Leviathan'], WonderlandBackupData())
        >>> g.most_optimal_path_short(100)
        ===== TRIP RESULTS =====
        """
        total_time = 0 #Time used
        path = [] #path
        rides_missed = [] #Rides that couldn't be added to the path because it went over the time
        for ride in self._user_rides:
            wait_time = self._data_set[ride]#Wait time for the ride
            if total_time + wait_time <= max_time: #checks if the total time is less than max time
                total_time += wait_time #add wait-time to the time accumulator
                path.append(ride) #add ride to path
            else:
                rides_missed.append(ride) #add to missed rides if went over limit

        time_left = max_time - total_time #time that was left over
        #Prints path, time used, remaining and any rides left over
        print("\n===== TRIP RESULTS =====\n")
        print("Ride Path:")
        for ride in range(len(path) - 1):
            print(f"{path[ride]} ---> {path[ride+1]}", end=" ")

        print(f"\nTotal Time Used: {total_time} minutes")
        print(f"Time Remaining: {time_left} minutes")

        if len(rides_missed) > 0:
            print("\nRides that could not fit in your time:")
            for ride in rides_missed:
                print(f"• {ride}")

    def _best_order(self, current_ride:str, path:List[str], time_used:float, max_time:int) -> Optional[Tuple[List[str], float]]:
        """
            Return best ride order within time limit.

            >>> g = WonderlandTrip(['Leviathan'], WonderlandBackupData())
            >>> g._best_order("Entrance", [], 0, 200)[0]
            ['Leviathan']
            """
        if time_used >= max_time:
            return None
        elif len(path) == len(self._user_rides):
            return path, time_used
        else:
            best_path = None
            best_time = float('inf')
            for i in self._user_rides:
                if i not in path: #Checks if this is a new ride not added to the path
                    route = self._find_route(current_ride,i) #gets the best route
                    route_path,distance = route #saves the path and distance
                    new_time_used = time_used + (distance/1000)/5 + self._data_set[i] #converts distance in m to km and finds the new time used
                    result = self._best_order(i,path + [i],new_time_used,max_time) #recursive cal with new path and time and current ride
                    if result is not None and result[1] < best_time: #checks if the result is not none and if the new time has improved
                        best_path = result[0] #set new best path
                        best_time = result[1] #set new best time
            if best_path is not None: #return the best_path if it is not None(meaning there is no path)
                return best_path, best_time
            else:
               return None #return None since there is no best path

    def most_optimal_path_long(self, max_time: int) -> None:
        """
           Print best ride order and full path.

        >>> g = WonderlandTrip([],WonderlandBackupData())
        >>> g._user_rides = ['Leviathan', 'Klockwerks']
        >>> g.most_optimal_path_long(200)

        """
        current = 'Entrance'
        full_path = ['Entrance']
        result = self._best_order(current,[], 0, max_time) #best order of user rides
        if result is None:
            print("No valid route")
            return

        best_path, time_used = result
        for ride in best_path: #calculates the path between each ride and adds to full_path
            route, distance = self._find_route(current,ride)
            full_path.extend(route[1:])
            current = ride

        print("Best ride order: ")
        print(" → ".join(best_path))
        print("\nFull path (Shows path from entrance and what rides to go past):")
        print(" → ".join(full_path))
        print("\nTotal time:", round(time_used, 2))

    def get_user_rides(self) -> List[str]:
        return self._user_rides

def save_trip(trip: WonderlandTrip) -> None:
    """
    Saves trip in a file
    """
    name = input("Enter trip name: ")
    with open(name + '.txt', 'w') as f:
        for ride in trip.get_user_rides():
            f.write(ride + '\n')
    print("Trip saved! Please remember the trip name.")

def load_trip(data: RideDataSource) -> Optional[WonderlandTrip]:
    """
    Loads trip from a file
    """
    name = input("Enter the trip name to load: ").strip()
    filename = name + '.txt'
    rides = []
    try:
        with open(filename, "r") as f:
            for line in f.readlines():
                rides.append(line.strip())

        print(f"✅ Loaded trip '{filename}'")

        return WonderlandTrip(rides,data)

    except FileNotFoundError:
        print("❌ Trip not found.")
        return None

def start_trip() -> None:
    """
    Menu for adding trips
    """
    if park_closed():
        data_source = WonderlandBackupData()
        print("\nUsing historical backup dataset.")
        print("Ride status may not reflect real park conditions.")
        print("Assuming all rides are available.\n")
    else:
        data_source = WonderlandAPIData()

    available_rides = data_source.get_available_rides()

    print("\n🎢 Available Rides:\n")
    for ride in available_rides:
        print(f"{ride} — {available_rides[ride]} minutes")

    rides = []
    print("\nAdd rides to your trip.")
    print("Type 'done' when finished.\n")

    while True:
        ride = input("Ride name: ").strip()

        if ride.lower() == "done":
            break

        if ride in available_rides:
            if ride not in rides:
                rides.append(ride)
                print("✅ Added:", ride)
            else:
                print("⚠️ Already added.")
        else:
            print("❌ Ride not found.")

    if not rides:
        print("\nNo rides selected. Returning to main menu.")
        return

    trip = WonderlandTrip(rides, data_source)
    trip_menu(trip)


#-----------------------------------------------------

def trip_menu(trip) -> None:
    """
    Trip menu
    """
    while True:
        print("\n🎯 TRIP MENU")
        print("____________")
        print("1. Show selected rides")
        print("2. Show ride wait times")
        print("3. Remove a ride")
        print("4. Calculate optimal path (SHORT - fast)")
        print("5. Calculate optimal path (ADVANCED - best)")
        print("6. Save trip")
        print("7. End trip")

        choice = input("Choose an option: ").strip()

        #-------------------------
        if choice == "1":
            print("\nYour rides:")
            for ride in trip._user_rides:
                print("•", ride)

        #-------------------------
        elif choice == "2":
            trip.get_ride_times()

        #-------------------------
        elif choice == "3":
            ride = input("Ride to remove: ").strip()
            trip.remove_ride(ride)

        #-------------------------
        elif choice == "4":
            try:
                time_limit = int(input("Time in park (minutes): "))
                print("\n⚡ Running FAST algorithm...\n")
                trip.most_optimal_path_short(time_limit)
            except ValueError:
                print("❌ Please enter a valid number.")

        #-------------------------
        elif choice == "5":
            try:
                time_limit = int(input("Time in park (minutes): "))
                print("\n🧠 Running ADVANCED algorithm (this may take longer but more accurate)...\n")
                trip.most_optimal_path_long(time_limit)
            except ValueError:
                print("❌ Please enter a valid number.")

        #-------------------------
        elif choice == "6":
            save_trip(trip)

        elif choice == "7":
            print("\nEnding trip...")
            break

        #-------------------------
        else:
            print("❌ Invalid option.")


#-----------------------------------------------------

if __name__ == '__main__':

    while True:

        print("\n🎢 CANADA'S WONDERLAND TRIP PLANNER")
        print("___________________________________")
        print("1. Start a new trip")
        print("2. Continue a saved trip")
        print("3. Exit")


        choice = input("Choose an option: ").strip()

        if choice == "1":
            start_trip()

        elif choice == "2":
            if park_closed():
                data_source = WonderlandBackupData()
            else:
                data_source = WonderlandAPIData()

            trip = load_trip(data_source)

            if trip != None:
                trip_menu(trip)

        elif choice == "3":
            print("\nGoodbye! 👋")
            break

        else:
            print("❌ Invalid option.")
