# Script per rigenerare grafici da CSV esistente

import sys
import os
import pandas as pd
from pathlib import Path

# Importa funzioni di plot da parameter_tuning
from parameter_tuning import (
    plot_parameter_importance,
    plot_fitness_boxplots,
    plot_generations_distribution,
    plot_avg_fitness_by_param,
    RESULTS_DIR,
    PLOTS_DIR
)


def list_available_csvs():
    csv_files = list(Path(RESULTS_DIR).glob("grid_search_results_*.csv"))
    return sorted(csv_files, key=lambda x: x.stat().st_mtime, reverse=True)


def select_csv_interactive():
    csv_files = list_available_csvs()
    
    if not csv_files:
        print(f"Nessun file CSV trovato in {RESULTS_DIR}/")
        return None
    
    print("\nFile CSV disponibili:")
    print("="*70)
    for idx, csv_file in enumerate(csv_files, 1):
        size_mb = csv_file.stat().st_size / (1024 * 1024)
        mtime = pd.Timestamp(csv_file.stat().st_mtime, unit='s').strftime('%Y-%m-%d %H:%M:%S')
        print(f"  [{idx}] {csv_file.name}")
        print(f"      Dimensione: {size_mb:.2f} MB | Ultima modifica: {mtime}")
    print("="*70)
    
    while True:
        try:
            choice = input(f"\nSeleziona file (1-{len(csv_files)}) o [ENTER] per il più recente: ").strip()
            
            if choice == "":
                return csv_files[0]
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(csv_files):
                return csv_files[choice_idx]
            else:
                print(f"Scelta non valida. Inserisci un numero tra 1 e {len(csv_files)}")
        except ValueError:
            print("Input non valido. Inserisci un numero.")
        except KeyboardInterrupt:
            print("\nOperazione annullata")
            return None


def regenerate_all_plots(csv_path: str):
    print(f"\n{'='*70}")
    print(f"RIGENERAZIONE GRAFICI DA CSV")
    print(f"{'='*70}")
    print(f"File CSV: {csv_path}")
    
    # Carica dati
    try:
        df = pd.read_csv(csv_path)
        print(f"Dati caricati: {len(df)} righe")
    except Exception as e:
        print(f"Errore durante il caricamento del CSV: {e}")
        return
    
    # Verifica colonne necessarie
    required_cols = ['best_fitness', 'completion_time', 'avg_departure_delay', 'generations', 'num_collisions']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"Colonne mancanti nel CSV: {missing_cols}")
        print(f"   Colonne disponibili: {list(df.columns)}")
        return
    

    print(f"\n📈 Statistiche rapide:")
    print(f"  • Fitness media:      {df['best_fitness'].mean():.2f}")
    print(f"  • Tempo medio:        {df['completion_time'].mean():.1f} tick")
    print(f"  • Ritardo medio:      {df['avg_departure_delay'].mean():.2f}")
    print(f"  • Collisioni medie:   {df['num_collisions'].mean():.2f}")
    print(f"  • Configurazioni 0 collisioni: {(df['num_collisions'] == 0).sum()}/{len(df)}")
    

    print(f"\nTOP 3 CONFIGURAZIONI:")
    top_3 = df.nsmallest(3, 'completion_time')
    for rank, (idx, row) in enumerate(top_3.iterrows(), 1):
        print(f"\n  #{rank}:")
        param_cols = [col for col in df.columns if col in ['POPULATION_SIZE', 'TOURNAMENT_SIZE', 'MUTATION_RATE', 'CONVERGENCE_GENERATIONS']]
        params_str = ", ".join([f"{col.replace('_', ' ').title()}={row[col]:.2f}" if isinstance(row[col], float) else f"{col.replace('_', ' ').title()}={int(row[col])}" for col in param_cols])
        print(f"     {params_str}")
        print(f"     → Tempo: {row['completion_time']:.0f} tick | "
              f"Ritardo: {row['avg_departure_delay']:.2f} | "
              f"Fitness: {row['best_fitness']:.2f} | "
              f"Collisioni: {int(row['num_collisions'])}")
    
    # Genera grafici
    print(f"\nGenerazione grafici in {PLOTS_DIR}/...")
    print("-"*70)
    
    try:
        plot_parameter_importance(df)
        plot_fitness_boxplots(df)
        plot_generations_distribution(df)
        plot_avg_fitness_by_param(df)
        
        print("-"*70)
        print(f"\nTutti i grafici rigenerati con successo!")
        print(f"Grafici salvati in: {PLOTS_DIR}/")
        print(f"\nGrafici generati:")
        print(f"  - parameter_importance.png")
        print(f"  - fitness_boxplots.png")
        print(f"  - generations_distribution.png")
        print(f"  - avg_fitness_by_param.png")
        
    except Exception as e:
        print(f"\nErrore durante la generazione dei grafici: {e}")
        import traceback
        traceback.print_exc()


def main():
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        if not os.path.exists(csv_path):
            print(f"File non trovato: {csv_path}")
            return
    else:
        # Selezione interattiva
        csv_path = select_csv_interactive()
        if csv_path is None:
            return
    
    regenerate_all_plots(str(csv_path))


if __name__ == "__main__":
    main()
