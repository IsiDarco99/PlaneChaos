GRID_SIZE = 50

NUM_AIRPORTS = 5 
MIN_AIRPORT_DISTANCE = 10 

NUM_AIRCRAFT = 20  
MAX_SIMULATION_TIME = 200

DIRECTIONS = [
    (-1, 0),   # Nord
    (-1, 1),   # Nord-Est
    (0, 1),    # Est
    (1, 1),    # Sud-Est
    (1, 0),    # Sud
    (1, -1),   # Sud-Ovest
    (0, -1),   # Ovest
    (-1, -1),  # Nord-Ovest
]

ENERGY_COST_STRAIGHT = 1.0
ENERGY_COST_DIAGONAL = 1.414