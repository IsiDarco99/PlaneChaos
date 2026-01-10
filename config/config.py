GRID_SIZE = 20 # Dimensione della griglia

NUM_AIRPORTS = 15 # Numero di aeroporti
MIN_AIRPORT_DISTANCE = 4 # Distanza minima tra aeroporti

NUM_AIRCRAFT = 50 # Numero di aerei
MAX_SIMULATION_TIME = 200 # Tempo massimo

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

ENERGY_COST_STRAIGHT = 0.1 # Costo energetico per movimento ortogonale
ENERGY_COST_DIAGONAL = 1.414 # Costo energetico per movimento diagonale

LAMBDA_WEIGHT = 0.1  # Peso per bilanciare tempo vs lunghezza rotte

POPULATION_SIZE = 100  # Dimensione della popolazione
MAX_GENERATIONS = 1000  # Numero massimo di generazioni
TOURNAMENT_SIZE = 5  # Dimensione del torneo per la selezione
MUTATION_RATE = 0.5  # Probabilità di mutazione del tempo di partenza
CONVERGENCE_GENERATIONS = 50  # Generazioni con fitness invariato per convergenza