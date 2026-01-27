# PlaneChaos - Air Traffic Management

Progetto di gestione del traffico aereo utilizzando un algoritmo memetico.

# Obiettivo del Progetto

Il progetto risolve il problema di coordinare un certo numero di aerei in uno spazio aereo (griglia NxN) tra un certo numero di aeroporti, minimizzando il tempo di completamento, i ritardi di partenza ed evitando collisioni.

## Struttura del Repository

- config.py: parametri configurabili
- src
    - algorithms
        - genetic_algorithm.py: implementazione GA
    - environment
        - aircraft.py: classe aereo
        - airport.py: classe aeroporto
        - environment.py: setup ambiente
        - grid.py: griglia di simulazione
    - utils
        - a_star.py: algoritmi A* classico e spazio-temporale
        - metrics.py: calcolo fitness
        - serialization: salvataggio e caricamento delle simulazioni (usato per la demo)
    - visualization
        - renderer.py: rendering grafico
        - ui_components.py: interfaccia grafica della demo
        - simulation_manager: gestione parametri simulazione
- experiments
    - results
        - grid_searc_results_*.csv: risultati tuning dei parametri
    - plots: immagini per risultati sotto formaa di grafico
- visualization.py: interfaccia grafica
- parameter_tuning.py: grid search per tuning dei parametri
- regenerate_plots.py: rigenerazione grafici da CSV (per evitare di rifare tutta la simulazione nel caso si cambi tipo di grafici)
- requirements.txt: dipendenze Python

## Installazione

### Setup

```bash
# Clona il repository
git clone "https://github.com/IsiDarco99/PlaneChaos"
cd PlaneChaos

# Installa le dipendenze
pip install -r requirements.txt
```

## Come Replicare il Lavoro

Per vedere graficamente l'evoluzione della simulazione:

```bash
python visualization.py
```

- Inserisci un seed o clicca "Random Seed"
- Aspetta che l'algoritmo finisca
- Scegli la generazione usando il menu
- Play/Pause per vedere l'animazione
- Freccia destra/sinistra per andare avanti/indietro di un tick

### Parameter Tuning (Grid Search)

Per replicare l'ottimizzazione dei parametri:

```bash
python parameter_tuning.py
```

Output:
- CSV con tutti i risultati in "experiments/results/"
- Grafici di analisi in "experiments/plots/"
- Top 10 configurazioni stampate a console

### Rigenerazione Grafici

Se c'è già un CSV dei risultati e vuoi rigenerare i grafici:

```bash
python regenerate_plots.py
```

### Configurazione

I parametri possono essere modificati in "config/config.py":

```python
GRID_SIZE = 20                 # Dimensione griglia
NUM_AIRPORTS = 15              # Numero aeroporti
MIN_AIRPORT_DISTANCE = 4       # Distanza minima tra aeroporti
NUM_AIRCRAFT = 50              # Numero aerei
POPULATION_SIZE = 100          # Popolazione GA
TOURNAMENT_SIZE = 10           # Dimensione torneo
MUTATION_RATE = 0.2            # Probabilità mutazione
CONVERGENCE_GENERATIONS = 70   # Criterio convergenza
```
