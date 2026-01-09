from typing import Tuple, List
from config.config import DIRECTIONS


class Grid:
    def __init__(self, size: int):
        self.size = size
    
    def is_valid_position(self, position: Tuple[int, int]) -> bool:
        row, col = position
        return 0 <= row < self.size and 0 <= col < self.size
    
    def get_neighbors(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        row, col = position
        neighbors = []
        
        for dr, dc in DIRECTIONS:
            new_pos = (row + dr, col + dc)
            if self.is_valid_position(new_pos):
                neighbors.append(new_pos)
        
        return neighbors
    
    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def euclidean_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
