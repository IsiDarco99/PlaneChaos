from typing import List, Tuple, Dict, Optional
from src.environment.aircraft import Aircraft
from src.utils.metrics import check_collisions


class SimulationManager:
    def __init__(self, aircraft_list: List[Aircraft], max_time: int = 200):
        self.aircraft_list = aircraft_list
        self.max_time = max_time
        self.current_tick = 0
        self.is_playing = False
        self.play_speed = 5  # Tick per secondo quando in play
        
        # Pre-calcola tutte le collisioni
        self._precompute_collisions()
        
        # Calcola tick massimo effettivo (quando l'ultimo aereo arriva)
        self._calculate_max_tick()
    
    def _precompute_collisions(self):
        _, collisions_detail = check_collisions(self.aircraft_list)
        
        # Organizza collisioni per tick: {tick: [(aid1, aid2), ...]}
        self.collisions_by_tick: Dict[int, List[Tuple[int, int]]] = {}
        for tick, aid1, aid2 in collisions_detail:
            if tick not in self.collisions_by_tick:
                self.collisions_by_tick[tick] = []
            self.collisions_by_tick[tick].append((aid1, aid2))
    
    def _calculate_max_tick(self):
        max_tick = 0
        for aircraft in self.aircraft_list:
            if len(aircraft.route) > 0:
                arrival_tick = aircraft.departure_time + len(aircraft.route) - 1
                max_tick = max(max_tick, arrival_tick)
        self.effective_max_tick = min(max_tick + 10, self.max_time)  # +10 per vedere dopo l'arrivo
    
    def get_aircraft_positions(self, tick: int) -> Dict[int, Optional[Tuple[int, int]]]:
        positions = {}
        for aircraft in self.aircraft_list:
            positions[aircraft.id] = aircraft.get_position_at_time(tick)
        return positions
    
    def get_collisions_at_tick(self, tick: int) -> List[Tuple[int, int]]:
        return self.collisions_by_tick.get(tick, [])
    
    def get_aircraft_in_collision(self, tick: int) -> set:
        """
        Ritorna il set di ID degli aerei in collisione al tick specificato
        """
        collisions = self.get_collisions_at_tick(tick)
        aircraft_ids = set()
        for aid1, aid2 in collisions:
            aircraft_ids.add(aid1)
            aircraft_ids.add(aid2)
        return aircraft_ids
    
    def next_tick(self):
        """Avanza al tick successivo"""
        if self.current_tick < self.effective_max_tick:
            self.current_tick += 1
    
    def previous_tick(self):
        """Torna al tick precedente"""
        if self.current_tick > 0:
            self.current_tick -= 1
    
    def reset_to_start(self):
        """Resetta al tick 0"""
        self.current_tick = 0
        self.is_playing = False
    
    def set_tick(self, tick: int):
        """Imposta un tick specifico"""
        self.current_tick = max(0, min(tick, self.effective_max_tick))
    
    def toggle_play(self):
        """Attiva/disattiva la riproduzione automatica"""
        self.is_playing = not self.is_playing
    
    def update(self, dt: float):
        """
        Aggiorna lo stato se in modalità play
        
        Args:
            dt: Delta time in secondi dall'ultimo frame
        """
        if self.is_playing:
            # Avanza automaticamente in base alla velocità
            if hasattr(self, '_play_timer'):
                self._play_timer += dt
            else:
                self._play_timer = 0
            
            time_per_tick = 1.0 / self.play_speed
            if self._play_timer >= time_per_tick:
                self.next_tick()
                self._play_timer = 0
                
                # Ferma se raggiunto il massimo
                if self.current_tick >= self.effective_max_tick:
                    self.is_playing = False
    
    def get_info_lines(self) -> List[str]:
        """Ritorna linee di testo con informazioni sulla simulazione"""
        lines = [
            f"Tick: {self.current_tick}/{self.effective_max_tick}",
            f"Aerei totali: {len(self.aircraft_list)}",
        ]
        
        # Conta aerei attivi al tick corrente
        positions = self.get_aircraft_positions(self.current_tick)
        active_count = sum(1 for pos in positions.values() if pos is not None)
        lines.append(f"Aerei in volo: {active_count}")
        
        # Collisioni al tick corrente
        collisions = self.get_collisions_at_tick(self.current_tick)
        if collisions:
            lines.append(f"⚠ COLLISIONI: {len(collisions)}")
            for aid1, aid2 in collisions[:3]:  # Max 3
                lines.append(f"  Aereo {aid1} ↔ Aereo {aid2}")
        
        return lines
    
    def has_collisions(self) -> bool:
        """Ritorna True se ci sono collisioni nella simulazione"""
        return len(self.collisions_by_tick) > 0
    
    def get_total_collisions(self) -> int:
        """Ritorna il numero totale di collisioni"""
        return sum(len(collisions) for collisions in self.collisions_by_tick.values())
