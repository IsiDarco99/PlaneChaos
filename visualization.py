import pygame
import sys
import random
import os
from typing import Optional
from src.environment.environment import Environment
from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.utils.serialization import save_simulation, load_simulation, list_available_simulations
from src.visualization.renderer import Renderer
from src.visualization.ui_components import Button, Dropdown, InfoPanel
from src.visualization.simulation_manager import SimulationManager


class VisualizationApp:
    
    def __init__(self, width: int = 800, height: int = 600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("PlaneChaos - Air Traffic Visualization")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60
        
        # Stato
        self.current_seed: Optional[int] = None
        self.simulation_data: Optional[dict] = None
        self.simulation_manager: Optional[SimulationManager] = None
        self.renderer: Optional[Renderer] = None
        
        # UI Components
        self.generation_dropdown: Optional[Dropdown] = None
        self.reset_button: Optional[Button] = None
        self.exit_button: Optional[Button] = None
        self.play_button: Optional[Button] = None
        self.info_panel: Optional[InfoPanel] = None
        
        # Blink per collisioni
        self.blink_timer = 0
        self.blink_state = False
    
    def cleanup_simulation_files(self):
        """Elimina i file di simulazione salvati"""
        if self.current_seed is not None:
            filename = os.path.join("output", f"simulation_seed{self.current_seed}.json")
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                    print(f"\n🗑️  File di simulazione eliminato: {filename}")
                except Exception as e:
                    print(f"\n⚠️  Errore durante l'eliminazione del file: {e}")
    
    def show_startup_menu(self) -> tuple:
        font = pygame.font.SysFont('Arial', 20)
        font_title = pygame.font.SysFont('Arial', 32, bold=True)
        input_text = ""
        input_active = True
        
        # Bottone solo seed random
        random_button = Button(pygame.Rect(250, 350, 300, 50), "Random Seed", (0, 150, 0), (0, 200, 0))
        
        while True:
            self.screen.fill((240, 240, 240))
            
            # Titolo
            title = font_title.render("PlaneChaos - Setup", True, (0, 0, 0))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))
            
            # Istruzioni
            inst1 = font.render("Inserisci seed (numero):", True, (0, 0, 0))
            self.screen.blit(inst1, (self.width // 2 - inst1.get_width() // 2, 150))
            
            inst2 = font.render("oppure usa Seed Random per generarne uno casuale", True, (100, 100, 100))
            self.screen.blit(inst2, (self.width // 2 - inst2.get_width() // 2, 175))
            
            # Input box
            input_box = pygame.Rect(300, 220, 200, 40)
            color = (100, 100, 255) if input_active else (200, 200, 200)
            pygame.draw.rect(self.screen, (255, 255, 255), input_box)
            pygame.draw.rect(self.screen, color, input_box, 3)
            
            text_surface = font.render(input_text, True, (0, 0, 0))
            self.screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
            
            # Bottone
            random_button.draw(self.screen)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if input_active:
                        if event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        elif event.key == pygame.K_RETURN:
                            if input_text.isdigit():
                                return int(input_text), True
                        elif event.unicode.isdigit():
                            input_text += event.unicode
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    input_active = input_box.collidepoint(event.pos)
                
                if random_button.handle_event(event):
                    # Usa seed inserito o generane uno random
                    if input_text.isdigit():
                        return int(input_text), True
                    else:
                        return random.randint(1, 99999), True
            
            self.clock.tick(30)
    
    def run_genetic_algorithm(self, seed: int):
        print(f"\n{'='*60}")
        print(f"Esecuzione Algoritmo Genetico con seed {seed}")
        print(f"{'='*60}")
        
        random.seed(seed)
        env = Environment()
        
        ga = GeneticAlgorithm(env, seed=seed, save_snapshots=True, snapshot_interval=5)
        best_solution, fitness_history = ga.evolve()
        
        # Prepara dati aeroporti
        airports_data = [
            {'id': airport.id, 'position': airport.position}
            for airport in env.airports
        ]
        
        # Salva simulazione
        save_simulation(
            seed=seed,
            generations_data=ga.snapshots,
            airports_data=airports_data,
            grid_size=env.grid.size,
            fitness_history=fitness_history,
            output_dir="output"
        )
        
        print(f"\n✓ Simulazione completata e salvata!")
    
    def load_simulation_data(self, seed: int):
        """Carica i dati della simulazione"""
        try:
            self.simulation_data = load_simulation(seed)
            self.current_seed = seed
            print(f"\n✓ Simulazione caricata: seed {seed}")
            print(f"  Generazioni disponibili: {self.simulation_data['available_generations']}")
            return True
        except FileNotFoundError:
            print(f"\n✗ Simulazione con seed {seed} non trovata!")
            return False
    
    def setup_visualization(self, generation: int):
        """Configura la visualizzazione per una generazione specifica"""
        if not self.simulation_data:
            return
        
        # Carica soluzione della generazione
        aircraft_list = self.simulation_data['generations'][generation]
        grid_size = self.simulation_data['grid_size']
        
        # Setup simulation manager
        self.simulation_manager = SimulationManager(aircraft_list)
        
        # Setup renderer
        # Layout: 40px top bar, 60px bottom controls, resto per griglia
        grid_area = pygame.Rect(10, 50, self.width - 20, self.height - 120)
        self.renderer = Renderer(self.screen, grid_size, grid_area)
        
        # Setup UI components
        button_y = self.height - 50
        self.reset_button = Button(
            pygame.Rect(10, button_y, 100, 40),
            "RESET",
            (200, 100, 0),
            (255, 150, 0)
        )
        
        self.play_button = Button(
            pygame.Rect(120, button_y, 100, 40),
            "PLAY" if not self.simulation_manager.is_playing else "PAUSE",
            (0, 150, 0),
            (0, 200, 0)
        )
        
        self.exit_button = Button(
            pygame.Rect(self.width - 110, button_y, 100, 40),
            "ESCI",
            (150, 0, 0),
            (200, 0, 0)
        )
        
        # Dropdown generazioni
        available_gens = self.simulation_data['available_generations']
        self.generation_dropdown = Dropdown(
            pygame.Rect(230, button_y, 180, 40),
            available_gens,
            generation,
            "Gen:"
        )
        
        # Info panel (a destra della griglia)
        # self.info_panel = InfoPanel(pygame.Rect(self.width - 180, 50, 170, 200))
    
    def handle_events(self):
        """Gestisce gli eventi pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.simulation_manager.next_tick()
                elif event.key == pygame.K_LEFT:
                    self.simulation_manager.previous_tick()
                elif event.key == pygame.K_SPACE:
                    self.simulation_manager.toggle_play()
                    self.play_button.text = "PAUSE" if self.simulation_manager.is_playing else "PLAY"
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            
            # Bottoni
            if self.reset_button and self.reset_button.handle_event(event):
                self.simulation_manager.reset_to_start()
            
            if self.play_button and self.play_button.handle_event(event):
                self.simulation_manager.toggle_play()
                self.play_button.text = "PAUSE" if self.simulation_manager.is_playing else "PLAY"
            
            if self.exit_button and self.exit_button.handle_event(event):
                self.running = False
            
            # Dropdown generazione
            if self.generation_dropdown and self.generation_dropdown.handle_event(event):
                new_gen = self.generation_dropdown.get_value()
                print(f"Cambio a generazione {new_gen}")
                self.setup_visualization(new_gen)
    
    def render(self):
        """Renderizza la scena"""
        self.screen.fill((200, 200, 200))
        
        if not self.renderer or not self.simulation_manager:
            return
        
        # 1. Disegna sfondo bianco della griglia
        self.renderer.draw_grid()
        
        # 2. Disegna aeroporti (celle colorate)
        for airport_data in self.simulation_data['airports']:
            self.renderer.draw_airport(airport_data['position'], airport_data['id'])
        
        # 3. Disegna linee della griglia sopra tutto
        self.renderer.draw_grid_lines()
        
        # 4. Disegna aerei
        current_tick = self.simulation_manager.current_tick
        positions = self.simulation_manager.get_aircraft_positions(current_tick)
        aircraft_in_collision = self.simulation_manager.get_aircraft_in_collision(current_tick)
        
        for aircraft in self.simulation_manager.aircraft_list:
            pos = positions[aircraft.id]
            if pos is not None:
                in_collision = aircraft.id in aircraft_in_collision
                self.renderer.draw_aircraft(aircraft, pos, in_collision, self.blink_state)
        
        # Info panel
        collisions_at_tick = self.simulation_manager.get_collisions_at_tick(current_tick)
        total_collisions = self.simulation_manager.get_total_collisions()
        current_gen = self.generation_dropdown.get_value()
        self.renderer.draw_info_panel(
            current_tick,
            self.current_seed,
            current_gen,
            collisions_at_tick,
            total_collisions
        )
        
        # UI Components
        self.reset_button.draw(self.screen)
        self.play_button.draw(self.screen)
        self.exit_button.draw(self.screen)
        self.generation_dropdown.draw(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        """Loop principale dell'applicazione"""
        # Menu iniziale
        seed, run_new = self.show_startup_menu()
        
        # Esegui o carica simulazione
        if run_new:
            self.run_genetic_algorithm(seed)
        
        # Carica dati
        if not self.load_simulation_data(seed):
            print("Impossibile caricare la simulazione. Uscita.")
            pygame.quit()
            return
        
        # Setup visualizzazione con generazione 0
        initial_gen = self.simulation_data['available_generations'][0]
        self.setup_visualization(initial_gen)
        
        # Loop principale
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            
            # Update
            if self.simulation_manager:
                self.simulation_manager.update(dt)
            
            # Blink per collisioni
            self.blink_timer += dt
            if self.blink_timer >= 0.5:
                self.blink_state = not self.blink_state
                self.blink_timer = 0
            
            # Handle events
            self.handle_events()
            
            # Render
            self.render()
        
        # Cleanup: elimina file simulazione al termine
        self.cleanup_simulation_files()
        pygame.quit()


def main():
    app = VisualizationApp(width=900, height=700)
    app.run()


if __name__ == "__main__":
    main()
