import pygame
from typing import List, Tuple, Callable, Optional


class Button:
    def __init__(self, rect: pygame.Rect, text: str, color: Tuple[int, int, int] = (100, 100, 100),
                 hover_color: Tuple[int, int, int] = (150, 150, 150),
                 text_color: Tuple[int, int, int] = (255, 255, 255)):
        self.rect = rect
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = pygame.font.SysFont('Arial', 14, bold=True)
    
    def draw(self, screen: pygame.Surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=5)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class Dropdown:
    def __init__(self, rect: pygame.Rect, options: List[int], initial_value: int,
                 label: str = ""):
        self.rect = rect
        self.options = options
        self.selected_value = initial_value
        self.label = label
        self.is_open = False
        self.is_hovered = False
        self.scroll_offset = 0  # Per scrolling
        self.max_visible_items = 8
        
        self.font = pygame.font.SysFont('Arial', 14)
        self.item_height = 25
        
        # Colori
        self.bg_color = (255, 255, 255)
        self.border_color = (0, 0, 0)
        self.hover_color = (200, 200, 255)
        self.selected_color = (150, 150, 255)
        self.scrollbar_color = (150, 150, 150)
        self.scrollbar_hover_color = (100, 100, 100)
    
    def draw(self, screen: pygame.Surface):
        # Box principale
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(screen, color, self.rect, border_radius=3)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=3)
        
        # Label + valore selezionato
        text = f"{self.label} {self.selected_value} ▼" if not self.is_open else f"{self.label} {self.selected_value} ▲"
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        # Menu aperto
        if self.is_open:
            # Calcola altezza menu
            visible_options = min(self.max_visible_items, len(self.options))
            menu_height = visible_options * self.item_height
            has_scrollbar = len(self.options) > self.max_visible_items
            
            # Determina se aprire sopra o sotto per non uscire dallo schermo
            screen_height = screen.get_height()
            open_upward = (self.rect.bottom + menu_height) > screen_height
            
            if open_upward:
                menu_rect = pygame.Rect(
                    self.rect.left,
                    self.rect.top - menu_height,
                    self.rect.width,
                    menu_height
                )
            else:
                menu_rect = pygame.Rect(
                    self.rect.left,
                    self.rect.bottom,
                    self.rect.width,
                    menu_height
                )
            
            # Sfondo menu
            pygame.draw.rect(screen, self.bg_color, menu_rect)
            pygame.draw.rect(screen, self.border_color, menu_rect, 2)
            
            # Opzioni (con scroll offset)
            mouse_pos = pygame.mouse.get_pos()
            start_idx = self.scroll_offset
            end_idx = min(start_idx + visible_options, len(self.options))
            
            for i, option_idx in enumerate(range(start_idx, end_idx)):
                option = self.options[option_idx]
                item_rect = pygame.Rect(
                    menu_rect.left,
                    menu_rect.top + i * self.item_height,
                    menu_rect.width - (15 if has_scrollbar else 0),  # Spazio per scrollbar
                    self.item_height
                )
                
                # Evidenzia se selezionato o hover
                if option == self.selected_value:
                    pygame.draw.rect(screen, self.selected_color, item_rect)
                elif item_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, self.hover_color, item_rect)
                
                # Testo opzione
                option_text = self.font.render(str(option), True, (0, 0, 0))
                option_text_rect = option_text.get_rect(center=item_rect.center)
                screen.blit(option_text, option_text_rect)
                
                # Bordo tra opzioni
                pygame.draw.line(
                    screen, 
                    self.border_color,
                    (item_rect.left, item_rect.bottom),
                    (item_rect.right, item_rect.bottom)
                )
            
            # Scrollbar se necessaria
            if has_scrollbar:
                scrollbar_width = 15
                scrollbar_rect = pygame.Rect(
                    menu_rect.right - scrollbar_width,
                    menu_rect.top,
                    scrollbar_width,
                    menu_height
                )
                pygame.draw.rect(screen, (230, 230, 230), scrollbar_rect)
                
                # Calcola dimensione e posizione thumb
                thumb_ratio = visible_options / len(self.options)
                thumb_height = max(20, int(menu_height * thumb_ratio))
                scroll_ratio = self.scroll_offset / max(1, len(self.options) - visible_options)
                thumb_y = menu_rect.top + int((menu_height - thumb_height) * scroll_ratio)
                
                thumb_rect = pygame.Rect(
                    scrollbar_rect.left + 2,
                    thumb_y,
                    scrollbar_width - 4,
                    thumb_height
                )
                pygame.draw.rect(screen, self.scrollbar_color, thumb_rect, border_radius=3)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return False
        
        elif event.type == pygame.MOUSEWHEEL:
            # Scroll con rotella del mouse quando menu aperto
            if self.is_open and len(self.options) > self.max_visible_items:
                max_scroll = len(self.options) - self.max_visible_items
                self.scroll_offset = max(0, min(
                    self.scroll_offset - event.y,
                    max_scroll
                ))
                return False  # Non propagare l'evento
            return False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Ignora click della rotella del mouse (button 2)
            if event.button in (4, 5):  # Scroll wheel su alcuni sistemi
                return False
            
            # Click sul dropdown principale
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return False
            
            # Click su un'opzione del menu
            if self.is_open:
                visible_options = min(self.max_visible_items, len(self.options))
                menu_height = visible_options * self.item_height
                
                # Calcola posizione menu (stesso calcolo di draw)
                screen_height = 700  # Default
                open_upward = (self.rect.bottom + menu_height) > screen_height
                
                if open_upward:
                    menu_rect = pygame.Rect(
                        self.rect.left,
                        self.rect.top - menu_height,
                        self.rect.width,
                        menu_height
                    )
                else:
                    menu_rect = pygame.Rect(
                        self.rect.left,
                        self.rect.bottom,
                        self.rect.width,
                        menu_height
                    )
                
                if menu_rect.collidepoint(event.pos):
                    # Determina quale opzione è stata cliccata (considera scroll)
                    relative_y = event.pos[1] - menu_rect.top
                    clicked_index = relative_y // self.item_height
                    actual_option_index = self.scroll_offset + clicked_index
                    
                    if 0 <= actual_option_index < len(self.options):
                        old_value = self.selected_value
                        self.selected_value = self.options[actual_option_index]
                        self.is_open = False
                        self.scroll_offset = 0  # Reset scroll
                        return old_value != self.selected_value
                
                # Click fuori dal menu, chiudilo
                self.is_open = False
        
        return False
    
    def get_value(self) -> int:
        return self.selected_value
    
    def set_value(self, value: int):
        if value in self.options:
            self.selected_value = value


class InfoPanel:
    def __init__(self, rect: pygame.Rect, bg_color: Tuple[int, int, int] = (240, 240, 240)):
        self.rect = rect
        self.bg_color = bg_color
        self.font = pygame.font.SysFont('Arial', 12)
        self.lines: List[str] = []
    
    def set_text(self, lines: List[str]):
        self.lines = lines
    
    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 1)
        
        y_offset = self.rect.top + 5
        for line in self.lines:
            text_surface = self.font.render(line, True, (0, 0, 0))
            screen.blit(text_surface, (self.rect.left + 5, y_offset))
            y_offset += 15
