import random
from typing import List
from src.environment.grid import Grid
from src.environment.airport import Airport
from src.environment.aircraft import Aircraft
from src.utils.a_star import astar_path
from config.config import (
    GRID_SIZE,
    NUM_AIRPORTS,
    MIN_AIRPORT_DISTANCE,
    NUM_AIRCRAFT
)


class Environment:
    def __init__(self):        
        self.grid = Grid(GRID_SIZE)
        self.airports: List[Airport] = []
        self.aircraft: List[Aircraft] = []
        
        self._generate_airports()
        self._generate_aircraft()
    
    def _generate_airports(self):
        attempts = 0
        max_attempts = 10000
        
        while len(self.airports) < NUM_AIRPORTS and attempts < max_attempts:
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - 1)
            position = (row, col)
            
            valid = True
            for airport in self.airports:
                if self.grid.manhattan_distance(position, airport.position) < MIN_AIRPORT_DISTANCE:
                    valid = False
                    break
            
            if valid:
                airport = Airport(len(self.airports), position)
                self.airports.append(airport)
            
            attempts += 1
        
        if len(self.airports) < NUM_AIRPORTS:
            raise ValueError(
                f"Impossibile generare {NUM_AIRPORTS} aeroporti con distanza minima "
                f"{MIN_AIRPORT_DISTANCE}. Ridurre NUM_AIRPORTS o MIN_AIRPORT_DISTANCE."
            )
    
    def _generate_aircraft(self):
        aircraft_per_airport = [1] * NUM_AIRPORTS
        remaining = NUM_AIRCRAFT - NUM_AIRPORTS
        
        for _ in range(remaining):
            airport_idx = random.randint(0, NUM_AIRPORTS - 1)
            aircraft_per_airport[airport_idx] += 1
        
        aircraft_id = 0
        for airport_idx, count in enumerate(aircraft_per_airport):
            start_airport = self.airports[airport_idx]
            start_airport.aircraft_count = count
            
            for _ in range(count):
                dest_idx = random.choice([i for i in range(NUM_AIRPORTS) if i != airport_idx])
                dest_airport = self.airports[dest_idx]
                
                aircraft = Aircraft(
                    aircraft_id=aircraft_id,
                    start_airport_id=start_airport.id,
                    destination_airport_id=dest_airport.id,
                    start_position=start_airport.position,
                    destination_position=dest_airport.position
                )
                
                self.aircraft.append(aircraft)
                aircraft_id += 1
    
    def initialize_routes_with_astar(self):
        for aircraft in self.aircraft:
            route = astar_path(
                self.grid,
                aircraft.start_position,
                aircraft.destination_position
            )
            
            if route is None:
                raise ValueError(
                    f"Impossibile trovare un percorso per l'aereo {aircraft.id} "
                    f"da {aircraft.start_position} a {aircraft.destination_position}"
                )
            
            aircraft.set_route(route)
            aircraft.set_departure_time(0)