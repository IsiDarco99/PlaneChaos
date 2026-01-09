import heapq
from typing import List, Tuple, Optional, Set, Dict
from src.environment.grid import Grid


def heuristic(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float: #Distance euclidea
    return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5


def astar_path(
    grid: Grid,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    obstacles: Set[Tuple[int, int]] = None
) -> Optional[List[Tuple[int, int]]]:
    
    if obstacles is None:
        obstacles = set()
    
    counter = 0 # counter serve per risolvere i tie-breaking
    open_set = [(0, counter, start)]
    counter += 1
    
    open_set_hash: Set[Tuple[int, int]] = {start} # nodi da esplorare
    closed_set: Set[Tuple[int, int]] = set() # nodi già esplorati
    
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {} # percorso da inizio alla fine
    g_score: Dict[Tuple[int, int], float] = {start: 0} # costo dal nodo iniziale
    
    while open_set:
        _, _, current = heapq.heappop(open_set)
        
        if current in closed_set: # già esplorato
            continue
        
        if current == goal: # percorso trovato
            return reconstruct_path(came_from, current)
        
        open_set_hash.discard(current)
        closed_set.add(current)
        
        for neighbor in grid.get_neighbors(current):
            if neighbor in closed_set or neighbor in obstacles:
                continue
            
            if abs(neighbor[0] - current[0]) + abs(neighbor[1] - current[1]) == 2:
                cost = 1.414  # Diagonale
            else:
                cost = 1.0  # Ortogonale
            
            tentative_g_score = g_score[current] + cost
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal)
                
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score, counter, neighbor))
                    counter += 1
                    open_set_hash.add(neighbor)
    
    return None


def reconstruct_path(
    came_from: Dict[Tuple[int, int], Tuple[int, int]],
    current: Tuple[int, int]
) -> List[Tuple[int, int]]: # ricostruisce il percorso dal dizionario came_from
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path
