from typing import Tuple


class Airport:
    def __init__(self, airport_id: int, position: Tuple[int, int]):
        self.id = airport_id
        self.position = position
        self.aircraft_count = 0
    
    def __repr__(self):
        return f"Airport(id={self.id}, pos={self.position})"
