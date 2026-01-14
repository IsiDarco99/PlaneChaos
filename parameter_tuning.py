import itertools
import json
import os
import random
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import pandas as pd

from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.environment.environment import Environment
from src.utils.metrics import get_solution_statistics
from config.config import GRID_SIZE, NUM_AIRPORTS, NUM_AIRCRAFT
import config.config as config

PARAM_GRID = {
    'POPULATION_SIZE': [50, 100, 150],
    'TOURNAMENT_SIZE': [3, 5, 7, 10],
    'MUTATION_RATE': [0.2, 0.4, 0.6, 0.8],
    'CONVERGENCE_GENERATIONS': [30, 50, 70]
}

total_combinations = 1
for values in PARAM_GRID.values():
    total_combinations *= len(values)

RESULTS_DIR = "experiments/results"
PLOTS_DIR = "experiments/plots"
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

def run_grid_search(seed: int = 43636543) -> pd.DataFrame:
    # Genera tutte le combinazioni
    param_names = list(PARAM_GRID.keys())
    param_values = list(PARAM_GRID.values())
    all_combinations = list(itertools.product(*param_values))
    
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    checkpoint_file = f"{RESULTS_DIR}/checkpoint_{timestamp}.json"
    
    print(f"Avvio Grid Search... (seed={seed})")
    print(f"Checkpoint salvati in: {checkpoint_file}\n")
    
    for idx, combination in enumerate(all_combinations, 1):
        params = dict(zip(param_names, combination))
        
        print(f"[{idx}/{total_combinations}] Testing: {params}")
        
        try:
            random.seed(seed)
            config.POPULATION_SIZE = params['POPULATION_SIZE']
            config.MAX_GENERATIONS = 1000
            config.TOURNAMENT_SIZE = params['TOURNAMENT_SIZE']
            config.MUTATION_RATE = params['MUTATION_RATE']
            config.CONVERGENCE_GENERATIONS = params['CONVERGENCE_GENERATIONS']
            
            env = Environment()
            
            ga = GeneticAlgorithm(env, seed=seed, save_snapshots=False)
            best_solution, fitness_history = ga.evolve()
            
            final_stats = get_solution_statistics(best_solution)
            
            result = {
                **params,
                'completion_time': final_stats['completion_time'],
                'avg_departure_delay': final_stats['avg_departure_delay'],
                'best_fitness': ga.best_fitness,
                'generations': len(fitness_history),
                'num_collisions': final_stats['num_collisions']
            }
            
            results.append(result)
            print(f"  OK - Fitness: {ga.best_fitness:.2f}, Generazioni: {len(fitness_history)}, Collisioni: {final_stats['num_collisions']}")
            
        except Exception as e:
            print(f"  ERRORE: {e}")
            import traceback
            traceback.print_exc()
            result = {
                **params,
                'completion_time': -1,
                'avg_departure_delay': -1,
                'best_fitness': -999999,
                'generations': -1,
                'num_collisions': 999,
                'error': str(e)
            }
            results.append(result)
    
    df = pd.DataFrame(results)
    csv_file = f"{RESULTS_DIR}/grid_search_results_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    print(f"\nGrid Search completato!")
    print(f"Risultati salvati in: {csv_file}")
    
    return df

def plot_parameter_importance(df: pd.DataFrame):
    param_cols = [col for col in PARAM_GRID.keys()]
    metrics = ['best_fitness', 'completion_time', 'avg_departure_delay']
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        
        correlations = {}
        for param in param_cols:
            corr = df[param].corr(df[metric])
            correlations[param] = corr
        
        sorted_params = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
        params, values = zip(*sorted_params)
        
        colors = ['red' if v > 0 else 'green' for v in values]
        
        bars = ax.barh(params, values, color=colors, alpha=0.7)
        ax.axvline(0, color='black', linestyle='-', linewidth=0.8)
        ax.set_xlabel('Correlazione (Verde=Riduce, Rosso=Aumenta)')
        ax.set_title(f'Impatto su {metric.replace("_", " ").title()}')
        ax.set_xlim(-1, 1)
        ax.grid(axis='x', alpha=0.3)
        
        for bar, val in zip(bars, values):
            width = bar.get_width()
            x_pos = width + 0.05 if width > 0 else width - 0.05
            ha = 'left' if width > 0 else 'right'
            ax.text(x_pos, bar.get_y() + bar.get_height()/2, 
                   f'{val:.3f}', ha=ha, va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/parameter_importance.png", dpi=300)
    plt.close()
    print("Grafico 'parameter_importance.png' creato")


def plot_fitness_boxplots(df: pd.DataFrame):
    param_cols = list(PARAM_GRID.keys())
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    df_no_collision = df[df['num_collisions'] == 0]
    
    if len(df_no_collision) > 0:
        y_min = df_no_collision['best_fitness'].min()
        y_max = df_no_collision['best_fitness'].max()
        y_margin = (y_max - y_min) * 0.15
    else:
        y_min = -200
        y_max = 0
        y_margin = 20
    
    for idx, param in enumerate(param_cols):
        ax = axes[idx]
        
        data_to_plot = [df[df[param] == val]['best_fitness'].values for val in sorted(df[param].unique())]
        labels = [str(val) for val in sorted(df[param].unique())]
        
        bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True, showfliers=False)
        
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
            patch.set_alpha(0.7)
        
        ax.set_xlabel(param, fontsize=11)
        ax.set_ylabel('Fitness', fontsize=11)
        ax.set_title(f'Distribuzione Fitness per {param}', fontsize=12)
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/fitness_boxplots.png", dpi=300)
    plt.close()
    print("Grafico 'fitness_boxplots.png' creato")


def plot_generations_distribution(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Istogramma generazioni
    axes[0].hist(df['generations'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    axes[0].axvline(df['generations'].mean(), color='red', linestyle='--', 
                   label=f'Media: {df["generations"].mean():.1f}')
    axes[0].set_xlabel('Generazioni per Convergenza')
    axes[0].set_ylabel('Frequenza')
    axes[0].set_title('Distribuzione Generazioni')
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    
    # Boxplot generazioni per CONVERGENCE_GENERATIONS
    df.boxplot(column='generations', by='CONVERGENCE_GENERATIONS', ax=axes[1])
    axes[1].set_xlabel('CONVERGENCE_GENERATIONS (parametro)')
    axes[1].set_ylabel('Generazioni Effettive')
    axes[1].set_title('Generazioni Effettive vs Parametro Convergenza')
    plt.suptitle('')  # Rimuovi titolo auto-generato
    
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/generations_distribution.png", dpi=300)
    plt.close()
    print("Grafico 'generations_distribution.png' creato")


def plot_avg_fitness_by_param(df: pd.DataFrame):
    param_cols = list(PARAM_GRID.keys())
    
    df_no_collision = df[df['num_collisions'] == 0]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    fitness_min = df_no_collision['best_fitness'].min()
    fitness_max = df_no_collision['best_fitness'].max()
    
    for idx, param in enumerate(param_cols):
        ax = axes[idx]
        
        avg_fitness = df_no_collision.groupby(param)['best_fitness'].mean()
        
        fitness_norm = (avg_fitness - fitness_min) / (fitness_max - fitness_min) if fitness_max != fitness_min else np.ones(len(avg_fitness))
        colors = plt.cm.RdYlGn(fitness_norm)
        
        ax.bar(range(len(avg_fitness)), avg_fitness.values, color=colors, alpha=0.7)
        ax.set_xticks(range(len(avg_fitness)))
        ax.set_xticklabels([f'{v:.2f}' if isinstance(v, float) else str(int(v)) for v in avg_fitness.index])
        ax.set_xlabel(param)
        ax.set_ylabel('Fitness Media')
        ax.set_title(f'Fitness Media per {param}')
        ax.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(avg_fitness.values):
            ax.text(i, v, f'{v:.1f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/avg_fitness_by_param.png", dpi=300)
    plt.close()
    print("Grafico 'avg_fitness_by_param.png' creato")

def print_summary_statistics(df: pd.DataFrame):
    print("\n" + "="*70)
    print("STATISTICHE RIASSUNTIVE")
    print("="*70)
    
    print(f"\nTempo Completamento (tick):")
    print(f"  - Migliore:  {df['completion_time'].min():.0f}")
    print(f"  - Media:     {df['completion_time'].mean():.1f}")
    print(f"  - Peggiore:  {df['completion_time'].max():.0f}")
    print(f"  - Std Dev:   {df['completion_time'].std():.1f}")
    
    print(f"\nRitardo Medio Partenza:")
    print(f"  - Migliore:  {df['avg_departure_delay'].min():.2f}")
    print(f"  - Media:     {df['avg_departure_delay'].mean():.2f}")
    print(f"  - Peggiore:  {df['avg_departure_delay'].max():.2f}")
    print(f"  - Std Dev:   {df['avg_departure_delay'].std():.2f}")
    
    print(f"\nCollisioni:")
    zero_collisions = (df['num_collisions'] == 0).sum()
    print(f"  - 0 collisioni: {zero_collisions}/{len(df)} configurazioni ({zero_collisions/len(df)*100:.1f}%)")
    print(f"  - Media:        {df['num_collisions'].mean():.2f}")
    
    print(f"\nGenerazioni:")
    print(f"  - Media:     {df['generations'].mean():.1f}")
    print(f"  - Min:       {df['generations'].min()}")
    print(f"  - Max:       {df['generations'].max()}")
    
    print(f"\nMIGLIORE CONFIGURAZIONE (per tempo completamento):")
    best = df.loc[df['completion_time'].idxmin()]
    print(f"  • POPULATION_SIZE:            {int(best['POPULATION_SIZE'])}")
    print(f"  • TOURNAMENT_SIZE:            {int(best['TOURNAMENT_SIZE'])}")
    print(f"  • MUTATION_RATE:              {best['MUTATION_RATE']:.2f}")
    print(f"  • CONVERGENCE_GENERATIONS:    {int(best['CONVERGENCE_GENERATIONS'])}")
    print(f"  • Tempo Completamento:        {best['completion_time']:.0f} tick")
    print(f"  • Ritardo Medio Partenza:     {best['avg_departure_delay']:.2f}")
    print(f"  • Fitness:                    {best['best_fitness']:.2f}")
    print(f"  • Generazioni:                {int(best['generations'])}")
    print(f"  • Collisioni:                 {int(best['num_collisions'])}")
    
    print(f"\nTOP 3 CONFIGURAZIONI:")
    # Con fitness negativa, nlargest prende i meno negativi (migliori)
    top_3 = df.nlargest(3, 'best_fitness')
    for rank, (idx, row) in enumerate(top_3.iterrows(), 1):
        print(f"\n  #{rank}:")
        print(f"     Pop={int(row['POPULATION_SIZE'])}, Tour={int(row['TOURNAMENT_SIZE'])}, " 
              f"Mut={row['MUTATION_RATE']:.2f}, Conv={int(row['CONVERGENCE_GENERATIONS'])}")
        print(f"     → Tempo: {row['completion_time']:.0f} tick | "
              f"Ritardo: {row['avg_departure_delay']:.2f} | "
              f"Fitness: {row['best_fitness']:.2f} | "
              f"Collisioni: {int(row['num_collisions'])}")
    
    print("="*70 + "\n")


# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    import time
    start_time = time.time()
    
    print(f"ATTENZIONE: Questo grid search richiedera' ~{total_combinations * 30 / 3600:.1f} ore!")
    response = input("Continuare? (y/n): ")
    
    if response.lower() != 'y':
        print("Grid search annullato")
        exit()
    
    seed_input = input("Inserisci seed (default=42): ").strip()
    search_seed = int(seed_input) if seed_input else 42
    
    results_df = run_grid_search(seed=search_seed)
    
    print("\nGenerazione grafici...")
    plot_parameter_importance(results_df)
    plot_fitness_boxplots(results_df)
    plot_generations_distribution(results_df)
    plot_avg_fitness_by_param(results_df)
    
    print_summary_statistics(results_df)
    
    elapsed = time.time() - start_time
    print(f"Tempo totale: {elapsed / 3600:.2f} ore")
    print(f"Grafici salvati in: {PLOTS_DIR}/")
