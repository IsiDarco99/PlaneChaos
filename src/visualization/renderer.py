import pygame
from typing import List, Tuple, Dict, Optional
from src.environment.aircraft import Aircraft


class Renderer:
    # Colori
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    RED = (255, 0, 0)
    BLUE = (0, 120, 215)
    GREEN = (0, 200, 0)
    YELLOW = (255, 215, 0)
    ORANGE = (255, 140, 0)
    PURPLE = (147, 51, 234)
    CYAN = (0, 200, 200)
    PINK = (255, 105, 180)
    
    # Colori per aerei
    AIRCRAFT_COLORS = [BLUE, GREEN, ORANGE, PURPLE, CYAN, PINK, YELLOW]
    
    # Colori per aeroporti
    AIRPORT_COLOR = (50, 50, 150)
    
    def __init__(self, screen: pygame.Surface, grid_size: int, grid_area_rect: pygame.Rect):
        self.screen = screen
        self.grid_size = grid_size
        self.grid_area = grid_area_rect
        
        # Calcola dimensione celle
        self.cell_width = grid_area_rect.width // grid_size
        self.cell_height = grid_area_rect.height // grid_size
        
        # Font per testi
        pygame.font.init()
        self.font_small = pygame.font.SysFont('Arial', 10)
        self.font_medium = pygame.font.SysFont('Arial', 14)
        self.font_large = pygame.font.SysFont('Arial', 18, bold=True)
        
    def draw_grid(self):
        """Disegna sfondo bianco della griglia"""
        pygame.draw.rect(self.screen, self.WHITE, self.grid_area)
    
    def draw_grid_lines(self):
        """Disegna le linee della griglia"""
        # Linee verticali
        for col in range(self.grid_size + 1):
            x = self.grid_area.left + col * self.cell_width
            pygame.draw.line(
                self.screen, 
                self.BLACK,
                (x, self.grid_area.top),
                (x, self.grid_area.bottom),
                1
            )
        
        # Linee orizzontali
        for row in range(self.grid_size + 1):
            y = self.grid_area.top + row * self.cell_height
            pygame.draw.line(
                self.screen,
                self.BLACK,
                (self.grid_area.left, y),
                (self.grid_area.right, y),
                1
            )
    
    def grid_to_screen(self, row: int, col: int) -> Tuple[int, int]: # Converte coordinate griglia in coordinate schermo (centro cella)
        x = self.grid_area.left + col * self.cell_width + self.cell_width // 2
        y = self.grid_area.top + row * self.cell_height + self.cell_height // 2
        return (x, y)
    
    def draw_airport(self, position: Tuple[int, int], airport_id: int):
        row, col = position
        
        # Calcola rettangolo della cella
        cell_rect = pygame.Rect(
            self.grid_area.left + col * self.cell_width,
            self.grid_area.top + row * self.cell_height,
            self.cell_width,
            self.cell_height
        )
        
        # Riempie la cella con il colore dell'aeroporto
        pygame.draw.rect(self.screen, self.AIRPORT_COLOR, cell_rect)
        pygame.draw.rect(self.screen, self.BLACK, cell_rect, 2)
        
        # ID dell'aeroporto al centro della cella
        x, y = self.grid_to_screen(row, col)
        text = self.font_large.render(str(airport_id), True, self.WHITE)
        text_rect = text.get_rect(center=(x, y))
        self.screen.blit(text, text_rect)
    
    def draw_aircraft(self, aircraft: Aircraft, position: Tuple[int, int], 
                     collision: bool = False, blink: bool = False):
        if position is None:
            return
        
        row, col = position
        x, y = self.grid_to_screen(row, col)
        
        # Scegli colore
        if collision and not blink:
            color = self.RED
        else:
            color = self.AIRCRAFT_COLORS[aircraft.id % len(self.AIRCRAFT_COLORS)]
        
        # Cerchio piccolo
        radius = min(self.cell_width, self.cell_height) // 3
        pygame.draw.circle(self.screen, color, (x, y), radius)
        pygame.draw.circle(self.screen, self.BLACK, (x, y), radius, 1)
        
        # ID dell'aereo
        text = self.font_small.render(str(aircraft.id), True, self.WHITE)
        text_rect = text.get_rect(center=(x, y))
        self.screen.blit(text, text_rect)
    
    def draw_info_panel(self, tick: int, seed: int, generation: int, 
                       collisions_at_tick: List[Tuple[int, int]], total_collisions: int,
                       avg_departure_delay: float):
        panel_rect = pygame.Rect(0, 0, self.screen.get_width(), 40)
        pygame.draw.rect(self.screen, self.GRAY, panel_rect)
        pygame.draw.rect(self.screen, self.BLACK, panel_rect, 2)
        
        # Testo info
        info_text = f"Tick: {tick}  |  Avg Delay: {avg_departure_delay:.2f}  |  Seed: {seed}  |  Gen: {generation}"
        text_surface = self.font_medium.render(info_text, True, self.BLACK)
        self.screen.blit(text_surface, (10, 10))
        
        # Collisioni totali (sempre visibili)
        collision_color = self.RED if collisions_at_tick else self.BLACK
        collision_text = f"Collisioni Totali: {total_collisions}"
        if collisions_at_tick:
            collision_text += f" (⚠ {len(collisions_at_tick)} ora)"
        text_surface = self.font_medium.render(collision_text, True, collision_color)
        self.screen.blit(text_surface, (400, 10))
    
    def draw_legend(self, x: int, y: int):
        # Aeroporto (quadratino colorato)
        pygame.draw.rect(self.screen, self.AIRPORT_COLOR, pygame.Rect(x-8, y-8, 16, 16))
        pygame.draw.rect(self.screen, self.BLACK, pygame.Rect(x-8, y-8, 16, 16), 2)
        text = self.font_small.render("Aeroporto", True, self.BLACK)
        self.screen.blit(text, (x + 15, y - 6))
        
        # Aereo
        pygame.draw.circle(self.screen, self.BLUE, (x, y + 20), 6)
        text = self.font_small.render("Aereo", True, self.BLACK)
        self.screen.blit(text, (x + 15, y + 14))
        
        # Collisione
        pygame.draw.circle(self.screen, self.RED, (x, y + 40), 6)
        text = self.font_small.render("Collisione", True, self.BLACK)
        self.screen.blit(text, (x + 15, y + 34))
