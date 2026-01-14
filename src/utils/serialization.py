import json
import os
from typing import List, Dict, Any
from src.environment.aircraft import Aircraft


def serialize_aircraft(aircraft: Aircraft) -> Dict[str, Any]:
    return {
        'id': aircraft.id,
        'start_airport_id': aircraft.start_airport_id,
        'destination_airport_id': aircraft.destination_airport_id,
        'start_position': aircraft.start_position,
        'destination_position': aircraft.destination_position,
        'route': aircraft.route,
        'departure_time': aircraft.departure_time
    }


def deserialize_aircraft(data: Dict[str, Any]) -> Aircraft:
    aircraft = Aircraft(
        aircraft_id=data['id'],
        start_airport_id=data['start_airport_id'],
        destination_airport_id=data['destination_airport_id'],
        start_position=tuple(data['start_position']),
        destination_position=tuple(data['destination_position'])
    )
    aircraft.route = [tuple(pos) for pos in data['route']]
    aircraft.departure_time = data['departure_time']
    return aircraft


def serialize_solution(aircraft_list: List[Aircraft]) -> List[Dict[str, Any]]:
    """Serializza una lista di Aircraft"""
    return [serialize_aircraft(aircraft) for aircraft in aircraft_list]


def deserialize_solution(data: List[Dict[str, Any]]) -> List[Aircraft]:
    """Deserializza una lista di dizionari in una lista di Aircraft"""
    return [deserialize_aircraft(aircraft_data) for aircraft_data in data]


def save_simulation(seed: int, generations_data: Dict[int, List[Aircraft]], 
                   airports_data: List[Dict], grid_size: int, 
                   fitness_history: List[float], output_dir: str = "output"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Serializza tutte le generazioni
    serialized_generations = {}
    for gen_num, aircraft_list in generations_data.items():
        serialized_generations[str(gen_num)] = serialize_solution(aircraft_list)
    
    simulation_data = {
        'seed': seed,
        'grid_size': grid_size,
        'airports': airports_data,
        'generations': serialized_generations,
        'fitness_history': fitness_history,
        'available_generations': sorted([int(k) for k in serialized_generations.keys()])
    }
    
    filename = os.path.join(output_dir, f"simulation_seed{seed}.json")
    with open(filename, 'w') as f:
        json.dump(simulation_data, f, indent=2)
    
    print(f"\nSimulazione salvata in: {filename}")
    return filename


def load_simulation(seed: int, output_dir: str = "output") -> Dict[str, Any]:
    filename = os.path.join(output_dir, f"simulation_seed{seed}.json")
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Simulazione con seed {seed} non trovata in {output_dir}")
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    # Deserializza le generazioni
    generations = {}
    for gen_num_str, aircraft_data in data['generations'].items():
        generations[int(gen_num_str)] = deserialize_solution(aircraft_data)
    
    # Converte tuple negli aeroporti
    airports = []
    for airport_data in data['airports']:
        airport_data['position'] = tuple(airport_data['position'])
        airports.append(airport_data)
    
    return {
        'seed': data['seed'],
        'grid_size': data['grid_size'],
        'airports': airports,
        'generations': generations,
        'fitness_history': data['fitness_history'],
        'available_generations': data['available_generations']
    }


def list_available_simulations(output_dir: str = "output") -> List[int]:
    if not os.path.exists(output_dir):
        return []
    
    seeds = []
    for filename in os.listdir(output_dir):
        if filename.startswith("simulation_seed") and filename.endswith(".json"):
            try:
                seed = int(filename.replace("simulation_seed", "").replace(".json", ""))
                seeds.append(seed)
            except ValueError:
                continue
    
    return sorted(seeds)
