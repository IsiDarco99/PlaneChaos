from typing import List, Tuple, Optional

class Aircraft:
    def __init__(self, aircraft_id: int, start_airport_id: int, destination_airport_id: int, start_position: Tuple[int, int], destination_position: Tuple[int, int]):
        self.id = aircraft_id
        self.start_airport_id = start_airport_id
        self.destination_airport_id = destination_airport_id
        self.start_position = start_position
        self.destination_position = destination_position
        self.route: List[Tuple[int, int]] = []
        self.departure_time = 0
    
    def set_route(self, route: List[Tuple[int, int]]):
        self.route = route
    
    def set_departure_time(self, time: int):
        self.departure_time = time
    
    def get_position_at_time(self, t: int) -> Optional[Tuple[int, int]]:
        if t < self.departure_time:
            return None
        
        time_since_departure = t - self.departure_time
        
        if time_since_departure >= len(self.route):
            return None
        
        return self.route[time_since_departure]
