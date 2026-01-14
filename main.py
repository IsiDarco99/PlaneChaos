import random
import time
from src.environment.environment import Environment
from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.utils.metrics import get_solution_statistics


def main():
    print("=" * 60)
    print("PlaneChaos - Air Traffic Management con Algoritmo Genetico")
    print("=" * 60)
    
    seed = 420
    random.seed(seed)
    
    print("\nCreazione ambiente...")
    try:
        environment = Environment()
        print(f"   Ambiente creato con {len(environment.airports)} aeroporti")
        print(f"   Generati {len(environment.aircraft)} aerei")
        
        print("\n   Aeroporti:")
        for airport in environment.airports:
            print(f"      - {airport}")
        
    except ValueError as e:
        print(f"   Errore nella creazione dell'ambiente: {e}")
        return
    
    print("\nInizializzazione algoritmo genetico...")
    ga = GeneticAlgorithm(environment, seed=seed)
    
    print("\nEsecuzione algoritmo genetico...")
    print("-" * 60)
    
    start_time = time.time()
    best_solution, fitness_history = ga.evolve()
    elapsed_time = time.time() - start_time
    
    print("-" * 60)
    print(f"\nAlgoritmo completato in {elapsed_time:.2f} secondi")
    
    print("\n" + "=" * 60)
    print("STATISTICHE SOLUZIONE FINALE")
    print("=" * 60)
    
    stats = get_solution_statistics(best_solution)
    
    print(f"Numero aerei:           {stats['num_aircraft']}")
    print(f"Collisioni:             {stats['num_collisions']}")
    print(f"Tempo completamento:    {stats['completion_time']} tick")
    print(f"Ritardo totale partenze: {stats['total_departure_delay']} tick")
    print(f"Ritardo medio partenza:  {stats['avg_departure_delay']:.2f} tick")
    print(f"Fitness finale:         {stats['fitness']:.2f}")
    
    if stats['num_collisions'] > 0:
        print(f"\nATTENZIONE: {stats['num_collisions']} collisioni rilevate!")
        print("   Prime 5 collisioni:")
        for i, (t, aid1, aid2) in enumerate(stats['collisions_detail'][:5]):
            print(f"      - Tick {t}: Aereo {aid1} - Aereo {aid2}")
    else:
        print("\nNessuna collisione! Soluzione valida trovata.")
    
    print(f"\nGenerazioni totali:     {len(fitness_history)}")
    print(f"Fitness iniziale:       {fitness_history[0]:.2f}")
    print(f"Fitness finale:         {fitness_history[-1]:.2f}")
    print(f"Miglioramento:          {fitness_history[-1] - fitness_history[0]:.2f}")
    
    print("\n" + "=" * 60)
    print("Dettagli aerei:")
    print("=" * 60)
    for aircraft in best_solution:
        print(f"Aereo {aircraft.id}:")
        print(f"  Da aeroporto {aircraft.start_airport_id} a {aircraft.destination_airport_id}")
        print(f"  Partenza: tick {aircraft.departure_time}")
        print(f"  Tempo arrivo: tick {aircraft.departure_time + len(aircraft.route) - 1}")
    
    if len(best_solution) > 5:
        print(f"... e altri {len(best_solution) - 5} aerei")
    
    print("\nEsecuzione completata!")
    

if __name__ == "__main__":
    main()
