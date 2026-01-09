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

# ============================================================================
# A* SPAZIO-TEMPORALE
# ============================================================================

def astar_path_temporal(
    grid: Grid,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    departure_time: int,
    occupied_cells: Dict[Tuple[int, int, int], int]
) -> Optional[List[Tuple[int, int]]]:
    
    start_state = (start[0], start[1], departure_time)
    
    counter = 0
    open_set = [(0, counter, start_state)]
    counter += 1
    
    open_set_hash: Set[Tuple[int, int, int]] = {start_state} # nodi da esplorare
    closed_set: Set[Tuple[int, int, int]] = set() # nodi già esplorati
    
    came_from: Dict[Tuple[int, int, int], Tuple[int, int, int]] = {} # percorso da inizio alla fine
    g_score: Dict[Tuple[int, int, int], float] = {start_state: 0} # costo dal nodo iniziale
    
    
    while open_set:
        _, _, current = heapq.heappop(open_set)
        
        if current in closed_set:
            continue
        
        current_row, current_col, current_time = current
        
        if (current_row, current_col) == goal:
            return reconstruct_path_temporal(came_from, current, start)
        
        open_set_hash.discard(current)
        closed_set.add(current)
        
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        
        for dr, dc in directions:
            new_row = current_row + dr
            new_col = current_col + dc
            new_time = current_time + 1
            
            # Controllo limiti griglia
            if not (0 <= new_row < grid.rows and 0 <= new_col < grid.cols):
                continue
            
            # Controllo ostacoli fissi
            if grid.grid[new_row][new_col] == 1:
                continue
            
            # Controllo celle occupate nel tempo
            if (new_row, new_col, new_time) in occupied_cells:
                continue
            
            neighbor = (new_row, new_col, new_time)
            
            if neighbor in closed_set:
                continue
            
            if abs(dr) == 1 and abs(dc) == 1:
                cost = 1.414
            else:
                cost = 1.0 
            
            tentative_g_score = g_score[current] + cost
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]: # miglior percorso trovato per il vicino
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                
                # Euristica: distanza euclidea
                h = heuristic((new_row, new_col), goal)
                f_score = tentative_g_score + h
                
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score, counter, neighbor))
                    counter += 1
                    open_set_hash.add(neighbor)
    
    return None


# Ritorna solo le coordinate (row, col), senza il tempo.
def reconstruct_path_temporal(
    came_from: Dict[Tuple[int, int, int], Tuple[int, int, int]],
    current: Tuple[int, int, int],
    start: Tuple[int, int]
) -> List[Tuple[int, int]]:
    path = [(current[0], current[1])]  # Solo (row, col)
    
    while current in came_from:
        current = came_from[current]
        path.append((current[0], current[1]))
    
    path.reverse()
    return path