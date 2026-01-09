from typing import List, Tuple, Dict, Set
from src.environment.aircraft import Aircraft
from config.config import MAX_SIMULATION_TIME, LAMBDA_WEIGHT


def check_collisions(aircraft_list: List[Aircraft]) -> Tuple[int, List[Tuple[int, int, int]]]:
    collisions_detail = []
    
    for t in range(MAX_SIMULATION_TIME):
        positions: Dict[Tuple[int, int], List[int]] = {}
        
        for aircraft in aircraft_list:
            pos = aircraft.get_position_at_time(t)
            if pos is not None:
                if pos not in positions:
                    positions[pos] = []
                positions[pos].append(aircraft.id)
        
        for pos, aircraft_ids in positions.items():
            if len(aircraft_ids) > 1:
                for i in range(len(aircraft_ids)):
                    for j in range(i + 1, len(aircraft_ids)):
                        collisions_detail.append((t, aircraft_ids[i], aircraft_ids[j]))
    
    return len(collisions_detail), collisions_detail


def calculate_completion_time(aircraft_list: List[Aircraft]) -> int:
    max_time = 0
    for aircraft in aircraft_list:
        if len(aircraft.route) > 0:
            arrival_time = aircraft.departure_time + len(aircraft.route) - 1
            max_time = max(max_time, arrival_time)
    return max_time


def calculate_total_route_length(aircraft_list: List[Aircraft]) -> float:
    return sum(aircraft.calculate_route_length() for aircraft in aircraft_list)


def calculate_fitness(
    aircraft_list: List[Aircraft],
    lambda_weight: float = LAMBDA_WEIGHT,
    collision_penalty: float = 10000.0
) -> float:
    
    num_collisions, _ = check_collisions(aircraft_list)
    
    completion_time = calculate_completion_time(aircraft_list)
    total_length = calculate_total_route_length(aircraft_list)
    
    fitness = -(completion_time + lambda_weight * total_length) # Fitness negativo perché vogliamo massimizzare
    
    if num_collisions > 0:
        fitness -= collision_penalty * num_collisions
    
    return fitness


def get_solution_statistics(aircraft_list: List[Aircraft]) -> Dict:
    num_collisions, collisions_detail = check_collisions(aircraft_list)
    completion_time = calculate_completion_time(aircraft_list)
    total_length = calculate_total_route_length(aircraft_list)
    fitness = calculate_fitness(aircraft_list)
    
    return {
        "num_aircraft": len(aircraft_list),
        "num_collisions": num_collisions,
        "completion_time": completion_time,
        "total_route_length": total_length,
        "avg_route_length": total_length / len(aircraft_list) if aircraft_list else 0,
        "fitness": fitness,
        "collisions_detail": collisions_detail
    }
