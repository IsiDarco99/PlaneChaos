import random
import copy
from typing import List, Tuple, Dict
from src.environment.environment import Environment
from src.environment.aircraft import Aircraft
from src.environment.grid import Grid
from src.utils.a_star import astar_path, astar_path_temporal
from src.utils.metrics import calculate_fitness, check_collisions
from config.config import (
    POPULATION_SIZE,
    MAX_GENERATIONS,
    TOURNAMENT_SIZE,
    MUTATION_RATE,
    CONVERGENCE_GENERATIONS,
    MAX_SIMULATION_TIME
)


class GeneticAlgorithm:
    def __init__(self, environment: Environment, seed: int = None, save_snapshots: bool = False, snapshot_interval: int = 5):
        if seed is not None:
            random.seed(seed)
        
        self.environment = environment
        self.grid = environment.grid
        self.population: List[List[Aircraft]] = []
        self.best_solution: List[Aircraft] = None
        self.best_fitness: float = float('-inf')
        self.fitness_history: List[float] = []
        self.save_snapshots = save_snapshots
        self.snapshot_interval = snapshot_interval
        self.snapshots: Dict[int, List[Aircraft]] = {}  # {generation: best_solution}
    
    def initialize_population(self):
        print("Inizializzazione popolazione...")
        
        for _ in range(POPULATION_SIZE):
            individual = [
                Aircraft(
                    aircraft.id,
                    aircraft.start_airport_id,
                    aircraft.destination_airport_id,
                    aircraft.start_position,
                    aircraft.destination_position
                )
                for aircraft in self.environment.aircraft
            ]
            
            # Raggruppa aerei per aeroporto di partenza
            aircraft_by_airport = {}
            for aircraft in individual:
                if aircraft.start_airport_id not in aircraft_by_airport:
                    aircraft_by_airport[aircraft.start_airport_id] = []
                aircraft_by_airport[aircraft.start_airport_id].append(aircraft)
        
            # Assegna tempi di partenza scaglionati per aeroporto
            for airport_id, aircraft_list in aircraft_by_airport.items():
                for i, aircraft in enumerate(aircraft_list):
                    route = astar_path(self.grid, aircraft.start_position, aircraft.destination_position)
                    if route is None:
                        raise ValueError(f"Impossibile trovare percorso per aereo {aircraft.id}")
                    aircraft.set_route(route)
                    # Ogni aereo parte con 1 tick di ritardo rispetto al precedente dello stesso aeroporto
                    aircraft.set_departure_time(i)
        
            self.population.append(individual)
        
        print(f"Popolazione iniziale creata: {POPULATION_SIZE} individui")
    
    def tournament_selection(self) -> List[Aircraft]:
        tournament = random.sample(self.population, TOURNAMENT_SIZE)
        winner = max(tournament, key=lambda ind: calculate_fitness(ind))
        return copy.deepcopy(winner)
    
    def single_point_crossover(
        self,
        parent1: List[Aircraft],
        parent2: List[Aircraft]
    ) -> Tuple[List[Aircraft], List[Aircraft]]:
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        if len(child1) <= 1:
            return child1, child2
        
        crossover_point = random.randint(1, len(child1) - 1)
        
        for i in range(crossover_point, len(child1)):
            child1[i].route, child2[i].route = child2[i].route[:], child1[i].route[:]
            child1[i].departure_time, child2[i].departure_time = (
                child2[i].departure_time,
                child1[i].departure_time
            )
        
        return child1, child2
    
    def mutate_departure_time(self, individual: List[Aircraft]):
        for aircraft in individual:
            if random.random() < MUTATION_RATE:
                max_delay = MAX_SIMULATION_TIME // 4  # Ritardo massimo ragionevole
                aircraft.set_departure_time(random.randint(0, max_delay))
    
    def mutate_with_astar_deviation(self, individual: List[Aircraft], grid: Grid):
        num_collisions, collisions_detail = check_collisions(individual)
        
        if num_collisions == 0:
            return
        
        aircraft_with_collisions = set()
        for _, aid1, aid2 in collisions_detail:
            aircraft_with_collisions.add(aid1)
            aircraft_with_collisions.add(aid2)
        
        if aircraft_with_collisions:
            aircraft_id = random.choice(list(aircraft_with_collisions))
            aircraft = individual[aircraft_id]

            # Costruisci mappa spazio-temporale
            occupied_cells = {}
            for other in individual:
                if other.id != aircraft.id and len(other.route) > 0:
                    for t_idx, pos in enumerate(other.route):
                        time_step = other.departure_time + t_idx
                        key = (pos[0], pos[1], time_step)
                        occupied_cells[key] = other.id

            # Usa A* spazio-temporale
            new_route = astar_path_temporal(
                grid,
                aircraft.start_position,
                aircraft.destination_position,
                aircraft.departure_time,
                occupied_cells
            )
            
            if new_route is not None:
                aircraft.set_route(new_route)
    
    def evolve(self):
        self.initialize_population()
        
        best_fitness_in_generation = max(calculate_fitness(ind) for ind in self.population)
        self.fitness_history.append(best_fitness_in_generation)
        
        # Salva snapshot generazione 0
        if self.save_snapshots:
            best_ind = max(self.population, key=lambda ind: calculate_fitness(ind))
            self.snapshots[0] = copy.deepcopy(best_ind)
        
        generations_without_improvement = 0
        previous_best_fitness = best_fitness_in_generation
        
        print(f"\nGen 0: Best Fitness = {best_fitness_in_generation:.2f}")
        
        for generation in range(1, MAX_GENERATIONS+1):
            new_population = []

            # ELITISMO: mantieni i migliori k individui
            elite_size = max(1, POPULATION_SIZE // 10)
            elite = sorted(self.population, key=lambda ind: calculate_fitness(ind), reverse=True)[:elite_size]
            new_population.extend([copy.deepcopy(ind) for ind in elite])
            
            while len(new_population) < POPULATION_SIZE:
                # Selezione
                parent1 = self.tournament_selection()
                parent2 = self.tournament_selection()
                
                # Crossover
                child1, child2 = self.single_point_crossover(parent1, parent2)
                
                # Mutazione tempo di partenza
                self.mutate_departure_time(child1)
                self.mutate_departure_time(child2)
                
                # Mutazione con A* (deviazioni per evitare collisioni)
                self.mutate_with_astar_deviation(child1, self.grid)
                self.mutate_with_astar_deviation(child2, self.grid)
                
                new_population.append(child1)
                if len(new_population) < POPULATION_SIZE:
                    new_population.append(child2)
            
            self.population = new_population
            
            # Valutazione
            current_best_fitness = max(calculate_fitness(ind) for ind in self.population)
            self.fitness_history.append(current_best_fitness)
            
            # Aggiorna miglior soluzione
            if current_best_fitness > self.best_fitness:
                self.best_fitness = current_best_fitness
                self.best_solution = max(self.population, key=lambda ind: calculate_fitness(ind))
            
            # Salva snapshot ogni N generazioni
            if self.save_snapshots and generation % self.snapshot_interval == 0:
                best_ind = max(self.population, key=lambda ind: calculate_fitness(ind))
                self.snapshots[generation] = copy.deepcopy(best_ind)
            
            # Convergenza
            if abs(current_best_fitness - previous_best_fitness) < 1e-6:
                generations_without_improvement += 1
            else:
                generations_without_improvement = 0
            
            previous_best_fitness = current_best_fitness
            
            # Stampa progresso
            if generation % 10 == 0 or generation == MAX_GENERATIONS:
                print(f"Gen {generation}: Best Fitness = {current_best_fitness:.2f}")
            
            # Stopping condition: convergenza
            if generations_without_improvement >= CONVERGENCE_GENERATIONS:
                print(f"\nConvergenza raggiunta dopo {generation} generazioni")
                # Salva ultimo snapshot se non già salvato
                if self.save_snapshots and generation not in self.snapshots:
                    best_ind = max(self.population, key=lambda ind: calculate_fitness(ind))
                    self.snapshots[generation] = copy.deepcopy(best_ind)
                break
        
        print(f"\nAlgoritmo terminato. Best Fitness = {self.best_fitness:.2f}")
        return self.best_solution, self.fitness_history
