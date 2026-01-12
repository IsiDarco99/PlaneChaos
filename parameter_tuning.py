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

# Directory per salvare risultati
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
    
    print(f"🚀 Avvio Grid Search... (seed={seed})")
    print(f"💾 Checkpoint salvati in: {checkpoint_file}\n")
    
    for idx, combination in enumerate(all_combinations, 1):
        params = dict(zip(param_names, combination))
        
        print(f"[{idx}/{total_combinations}] Testing: {params}")
        
        try:
            # Imposta seed per riproducibilità
            random.seed(seed)
            # Aggiorna configurazione con i parametri del test
            config.POPULATION_SIZE = params['POPULATION_SIZE']
            config.MAX_GENERATIONS = 1000
            config.TOURNAMENT_SIZE = params['TOURNAMENT_SIZE']
            config.MUTATION_RATE = params['MUTATION_RATE']
            config.CONVERGENCE_GENERATIONS = params['CONVERGENCE_GENERATIONS']
            
            # Crea environment (legge da config)
            env = Environment()
            
            # Esegui GA
            ga = GeneticAlgorithm(env, seed=seed, save_snapshots=False)
            best_solution, fitness_history = ga.evolve()
            
            # Calcola statistiche finali
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
            print(f"  ✅ Fitness: {ga.best_fitness:.2f}, Generazioni: {len(fitness_history)}, Collisioni: {final_stats['num_collisions']}")
            
        except Exception as e:
            print(f"  ❌ Errore: {e}")
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
    
    # Salva risultati finali
    df = pd.DataFrame(results)
    csv_file = f"{RESULTS_DIR}/grid_search_results_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    print(f"\n✅ Grid Search completato!")
    print(f"📁 Risultati salvati in: {csv_file}")
    
    return df

def plot_parameter_importance(df: pd.DataFrame):
    """Mostra correlazione parametri con metriche reali"""
    param_cols = [col for col in PARAM_GRID.keys()]
    metrics = ['completion_time', 'avg_departure_delay']
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        
        # Calcola correlazione tra parametri e metrica
        correlations = {}
        for param in param_cols:
            corr = df[param].corr(df[metric])
            correlations[param] = corr  # Mantieni segno per capire direzione
        
        # Ordina per valore assoluto
        sorted_params = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
        params, values = zip(*sorted_params)
        
        # Colori: rosso=positivo (aumenta metrica), verde=negativo (riduce metrica)
        colors = ['red' if v > 0 else 'green' for v in values]
        
        bars = ax.barh(params, values, color=colors, alpha=0.7)
        ax.axvline(0, color='black', linestyle='-', linewidth=0.8)
        ax.set_xlabel('Correlazione (Verde=Riduce, Rosso=Aumenta)')
        ax.set_title(f'Impatto su {metric.replace("_", " ").title()}')
        ax.set_xlim(-1, 1)
        ax.grid(axis='x', alpha=0.3)
        
        # Aggiungi valori
        for bar, val in zip(bars, values):
            width = bar.get_width()
            x_pos = width + 0.05 if width > 0 else width - 0.05
            ha = 'left' if width > 0 else 'right'
            ax.text(x_pos, bar.get_y() + bar.get_height()/2, 
                   f'{val:.3f}', ha=ha, va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/parameter_importance.png", dpi=300)
    plt.close()
    print("📊 Grafico 'parameter_importance.png' creato")


def plot_convergence_heatmap(df: pd.DataFrame):
    """
    Heatmap: metriche medie per ogni coppia di parametri
    """
    param_cols = list(PARAM_GRID.keys())
    
    # Crea subplot per le 2 metriche principali
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Usa prime due coppie più interessanti
    if 'POPULATION_SIZE' in param_cols and 'TOURNAMENT_SIZE' in param_cols:
        param1 = 'POPULATION_SIZE'
        param2 = 'TOURNAMENT_SIZE'
    else:
        param1 = param_cols[0]
        param2 = param_cols[1] if len(param_cols) > 1 else param_cols[0]
    
    metrics = [
        ('completion_time', 'Tempo Completamento (tick)', 'RdYlGn_r'),  # _r = reversed (rosso=peggio)
        ('avg_departure_delay', 'Ritardo Medio Partenza', 'RdYlGn_r')
    ]
    
    for idx, (metric, title, cmap) in enumerate(metrics):
        ax = axes[idx]
        
        # Crea pivot table per heatmap
        pivot = df.pivot_table(
            values=metric,
            index=param1,
            columns=param2,
            aggfunc='mean'
        )
        
        sns.heatmap(pivot, annot=True, fmt='.1f', cmap=cmap, 
                   cbar_kws={'label': title}, ax=ax)
        ax.set_title(f'{title}\\n{param1} vs {param2}')
    
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/fitness_heatmap.png", dpi=300)
    plt.close()
    print("📊 Grafico 'fitness_heatmap.png' creato")


def plot_best_configurations(df: pd.DataFrame, top_n: int = 10):
    """
    Mostra top N configurazioni con metriche reali
    """
    # Ordina per tempo di completamento (più basso = migliore)
    top_configs = df.nsmallest(top_n, 'completion_time')
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    metrics = [
        ('completion_time', 'Tempo Completamento (tick)'),
        ('avg_departure_delay', 'Ritardo Medio Partenza')
    ]
    
    for idx, (metric, label) in enumerate(metrics):
        ax = axes[idx]
        x = range(len(top_configs))
        values = top_configs[metric].values
        
        # Normalizza per colormap (più basso = verde)
        val_min, val_max = df[metric].min(), df[metric].max()
        norm = 1 - (values - val_min) / (val_max - val_min) if val_max != val_min else np.ones(len(values))
        colors = plt.cm.RdYlGn(norm)
        
        bars = ax.bar(x, values, color=colors, alpha=0.7)
        ax.set_xlabel('Configurazione')
        ax.set_ylabel(label)
        ax.set_title(f'Top {top_n} per Tempo\\n{label}')
        ax.set_xticks(x)
        ax.set_xticklabels([f'#{i+1}' for i in x])
        ax.grid(axis='y', alpha=0.3)
        
        # Aggiungi valori sulle barre
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height, 
                   f'{val:.1f}', ha='center', va='bottom', fontsize=8)
    
    # Aggiungi legenda con parametri in basso
    param_text = "\\n".join([
        f"#{i+1}: Pop={int(row['POPULATION_SIZE'])}, Tour={int(row['TOURNAMENT_SIZE'])}, "
        f"Mut={row['MUTATION_RATE']:.2f}, Conv={int(row['CONVERGENCE_GENERATIONS'])} | "
        f"T={row['completion_time']:.0f}, D={row['avg_departure_delay']:.1f}"
        for i, (_, row) in enumerate(top_configs.iterrows())
    ])
    
    plt.figtext(0.02, 0.02, param_text, fontsize=7, family='monospace', 
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.25)
    plt.savefig(f"{PLOTS_DIR}/top_configurations.png", dpi=300)
    plt.close()
    print(f"📊 Grafico 'top_configurations.png' creato")


def plot_generations_distribution(df: pd.DataFrame):
    """
    Distribuzione numero di generazioni per convergenza
    """
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
    print("📊 Grafico 'generations_distribution.png' creato")


def plot_avg_metrics_by_param(df: pd.DataFrame):
    """
    Metriche medie per ogni valore di parametro
    """
    param_cols = list(PARAM_GRID.keys())
    
    # Crea 2 figure separate per le 2 metriche
    metrics = ['completion_time', 'avg_departure_delay']
    metric_labels = ['Tempo Completamento (tick)', 'Ritardo Medio Partenza']
    
    for metric, label in zip(metrics, metric_labels):
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()
        
        metric_min = df[metric].min()
        metric_max = df[metric].max()
        
        for idx, param in enumerate(param_cols):
            ax = axes[idx]
            
            # Calcola metrica media per ogni valore
            avg_metric = df.groupby(param)[metric].mean()
            
            # Normalizza per colormap (inverso: più basso = verde)
            metric_norm = 1 - (avg_metric - metric_min) / (metric_max - metric_min) if metric_max != metric_min else np.ones(len(avg_metric))
            colors = plt.cm.RdYlGn(metric_norm)
            
            ax.bar(range(len(avg_metric)), avg_metric.values, color=colors, alpha=0.7)
            ax.set_xticks(range(len(avg_metric)))
            ax.set_xticklabels([f'{v:.2f}' if isinstance(v, float) else str(int(v)) for v in avg_metric.index])
            ax.set_xlabel(param)
            ax.set_ylabel(label)
            ax.set_title(f'{label} medio per {param}')
            ax.grid(axis='y', alpha=0.3)
            
            # Aggiungi valori sulle barre
            for i, v in enumerate(avg_metric.values):
                ax.text(i, v, f'{v:.1f}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(f"{PLOTS_DIR}/avg_{metric}_by_param.png", dpi=300)
        plt.close()
        print(f"📊 Grafico 'avg_{metric}_by_param.png' creato")

def print_summary_statistics(df: pd.DataFrame):
    """
    Stampa statistiche riassuntive
    """
    print("\n" + "="*70)
    print("📈 STATISTICHE RIASSUNTIVE")
    print("="*70)
    
    print(f"\n⏱️  Tempo Completamento (tick):")
    print(f"  • Migliore:  {df['completion_time'].min():.0f}")
    print(f"  • Media:     {df['completion_time'].mean():.1f}")
    print(f"  • Peggiore:  {df['completion_time'].max():.0f}")
    print(f"  • Std Dev:   {df['completion_time'].std():.1f}")
    
    print(f"\n🕐 Ritardo Medio Partenza:")
    print(f"  • Migliore:  {df['avg_departure_delay'].min():.2f}")
    print(f"  • Media:     {df['avg_departure_delay'].mean():.2f}")
    print(f"  • Peggiore:  {df['avg_departure_delay'].max():.2f}")
    print(f"  • Std Dev:   {df['avg_departure_delay'].std():.2f}")
    
    print(f"\n💥 Collisioni:")
    zero_collisions = (df['num_collisions'] == 0).sum()
    print(f"  • 0 collisioni: {zero_collisions}/{len(df)} configurazioni ({zero_collisions/len(df)*100:.1f}%)")
    print(f"  • Media:        {df['num_collisions'].mean():.2f}")
    
    print(f"\n🔄 Generazioni:")
    print(f"  • Media:     {df['generations'].mean():.1f}")
    print(f"  • Min:       {df['generations'].min()}")
    print(f"  • Max:       {df['generations'].max()}")
    
    print(f"\n🏆 MIGLIORE CONFIGURAZIONE (per tempo completamento):")
    best = df.loc[df['completion_time'].idxmin()]
    print(f"  • POPULATION_SIZE:            {int(best['POPULATION_SIZE'])}")
    print(f"  • MUTATION_RATE:              {best['MUTATION_RATE']:.2f}")
    print(f"  • CONVERGENCE_GENERATIONS:    {int(best['CONVERGENCE_GENERATIONS'])}")
    print(f"  • Tempo Completamento:        {best['completion_time']:.0f} tick")
    print(f"  • Ritardo Medio Partenza:     {best['avg_departure_delay']:.2f}")
    print(f"  • Generazioni:                {int(best['generations'])}")
    print(f"  • Collisioni:                 {int(best['num_collisions'])}")
    print("="*70 + "\n")


# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    import time
    start_time = time.time()
    
    # Chiedi conferma prima di iniziare
    print(f"⚠️  ATTENZIONE: Questo grid search richiederà ~{total_combinations * 30 / 3600:.1f} ore!")
    response = input("Continuare? (y/n): ")
    
    if response.lower() != 'y':
        print("❌ Grid search annullato")
        exit()
    
    # Chiedi seed
    seed_input = input("Inserisci seed (default=42): ").strip()
    search_seed = int(seed_input) if seed_input else 42
    
    # Esegui grid search
    results_df = run_grid_search(seed=search_seed)
    
    # Genera grafici
    print("\n📊 Generazione grafici...")
    plot_parameter_importance(results_df)
    plot_convergence_heatmap(results_df)
    plot_best_configurations(results_df, top_n=10)
    plot_generations_distribution(results_df)
    plot_avg_metrics_by_param(results_df)
    
    # Stampa statistiche
    print_summary_statistics(results_df)
    
    elapsed = time.time() - start_time
    print(f"⏱️  Tempo totale: {elapsed / 3600:.2f} ore")
    print(f"📁 Grafici salvati in: {PLOTS_DIR}/")
