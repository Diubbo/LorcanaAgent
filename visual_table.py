import re
from heuristic import get_heuristic_scores_for_action
import pygame, sys
from decklists import CharacterCard, ActionCard, ItemCard
from setup_algorithm import bot1, bot2, lorcana_game
import os

############## Load Images ##############
CARD_WIDTH, CARD_HEIGHT = 100, 150

# --- MODIFICATO ---
def load_card_images(asset_dir="assets"):
    print("Caricamento immagini...")
    images = {}
    for fname in os.listdir(asset_dir):
        # only png files at the moment
        if fname.endswith(".png"):
            
            filename_key = fname.replace(".png", "")
            
            key = ""

            if filename_key == "card-back":
                key = "card-back"
            elif filename_key == "default":
                key = "default"
            else:
                key = filename_key.replace("-", "/", 1)

            path = os.path.join(asset_dir, fname)
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
                images[key] = img 
            except Exception as e:
                print(f"Errore caricamento {fname}: {e}")

    print(f"Caricate {len(images)} immagini.")
    if "card-back" not in images:
        print("ATTENZIONE: 'card-back.png' non trovato.")
    
    return images

########### Draw Table ###########

# --- FUNZIONE HELPER ---
def draw_text(screen, text, pos, font, color=pygame.Color("white")):
    """Helper per disegnare testo con un'ombra nera per leggibilità."""
    shadow = font.render(text, True, pygame.Color("black"))
    obj = font.render(text, True, color)
    screen.blit(shadow, (pos[0] + 1, pos[1] + 1))
    screen.blit(obj, pos)

# --- FUNZIONE DRAW_TABLE ---
def draw_table(screen, fonts, state, images, logs, paused):
    screen.fill((34, 139, 34))  # Verde tavolo
    font, font_small, font_damage = fonts

    # PLayer info
    p0 = state.engine.p1
    p1 = state.engine.p2

    # --- Info Giocatori Migliorate ---
    p1_info = f"Player 1 - Lore: {p1.lore}"
    p1_counts = f"Mano: {len(p1.hand)} | Mazzo: {p1.deck.get_total_cards()} | Scarti: {len(p1.discard)}"
    p0_info = f"Player 0 - Lore: {p0.lore}"
    p0_counts = f"Mano: {len(p0.hand)} | Mazzo: {p0.deck.get_total_cards()} | Scarti: {len(p0.discard)}"

    draw_text(screen, p1_info, (20, 3), font)
    draw_text(screen, p1_counts, (20, 27), font_small)
    draw_text(screen, p0_info, (20, 740), font)
    draw_text(screen, p0_counts, (20, 765), font_small)

    # --- Info di Gioco ---
    phase_text = f"Turno: {state.engine.turn} | Fase: {state.engine.phase.name}"
    draw_text(screen, phase_text, (WIDTH // 2 - 90, 750), font, pygame.Color("yellow"))
    if paused:
        draw_text(screen, "PAUSA  P = riprendere SPAZIO = avanti", (WIDTH // 2 - 200, 10), font, pygame.Color("red"))

    # --- DISEGNO CARTE MIGLIORATO (con STATS e DANNO) ---
    
    # Overlay per lo stato "non dry" (summoning sickness)
    dry_overlay = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
    dry_overlay.fill((0, 100, 255, 100)) # Blu semi-trasparente

    # Player 0 (Bottom)
    # Personaggi
    for i, char in enumerate(p0.in_play_characters):
        x_pos, y_pos = (250 + i * 110, 400) 
        img = images.get(char.card.num, images["default"])
        if not char.ready:
            img = pygame.transform.rotate(img, 90)
        
        screen.blit(img, (x_pos, y_pos))
        
        # Disegna Stats, Danno e Stato Dry
        if not char.ready: 
            stats_pos = (x_pos + CARD_HEIGHT + 5, y_pos + 40)
        else:
            stats_pos = (x_pos, y_pos + CARD_HEIGHT + 5)
        
        stats = f"S:{char.card.strength} W:{char.card.willpower} L:{char.card.lore}"
        draw_text(screen, stats, stats_pos, font_small, pygame.Color("white"))

        if not char.dry: 
            screen.blit(dry_overlay, (x_pos, y_pos))
            
        if char.damage > 0: 
            dmg_color = "red" if char.damage < char.card.willpower else "orange"
            # --- MODIFICATA Y --- Adatta la posizione del danno
            draw_text(screen, str(char.damage), (x_pos + 75, y_pos + 120), font_damage, pygame.Color(dmg_color)) 

    # Inchiostro (P0)
    for i in range(p0.ready_ink):
        img = images.get("card-back", images["default"])
        screen.blit(img, (20, 430 + i * 20)) 
    for i in range(p0.exerted_ink):
        img = images.get("card-back", images["default"])
        img = pygame.transform.rotate(img, 90)
        screen.blit(img, (80, 430 + i * 20))

    # --- Mano P0 ---
    for i, card in enumerate(p0.hand):
        img = images.get(card.num, images["default"])
        screen.blit(img, (200 + i * 110, 580)) 
    
    # --- Disegna Oggetti Giocatore 0 (in basso) ---
    item_zone_x = 800 # Posiziona la zona Oggetti a destra dei Personaggi
    for i, item in enumerate(p0.in_play_items):
        x_pos = item_zone_x + i * 110
        y_pos = 400 # Stessa riga (Y) dei Personaggi
        
        img = images.get(item.card.num, images["default"])
        
        # Ruota l'oggetto se è "exerted"
        if not item.ready:
            img = pygame.transform.rotate(img, 90)
            
        screen.blit(img, (x_pos, y_pos))
        
        # Disegna il costo dell'oggetto (gli oggetti non hanno stats)
        stats_pos = (x_pos, y_pos + CARD_HEIGHT + 5)
        draw_text(screen, f"Costo: {item.card.cost}", stats_pos, font_small, pygame.Color("white"))

    # Player 1 (Top)
    # Personaggi
    for i, char in enumerate(p1.in_play_characters):
        x_pos, y_pos = (250 + i * 110, 200) 
        img = images.get(char.card.num, images["default"])
        if not char.ready:
            img = pygame.transform.rotate(img, 90)
        
        screen.blit(img, (x_pos, y_pos))
    

        # Disegna Stats, Danno e Stato Dry
        if not char.ready:
            stats_pos = (x_pos + CARD_HEIGHT + 5, y_pos + 40)
        else:
            stats_pos = (x_pos, y_pos + CARD_HEIGHT + 5)
            
        stats = f"S:{char.card.strength} W:{char.card.willpower} L:{char.card.lore}"
        draw_text(screen, stats, stats_pos, font_small, pygame.Color("white"))
        
        if not char.dry: 
            screen.blit(dry_overlay, (x_pos, y_pos))

        if char.damage > 0: 
            dmg_color = "red" if char.damage < char.card.willpower else "orange"
            draw_text(screen, str(char.damage), (x_pos + 75, y_pos + 120), font_damage, pygame.Color(dmg_color))
        # --- Disegna Oggetti Giocatore 1 (in alto) ---
    item_zone_x = 800 # Posiziona la zona Oggetti a destra dei Personaggi
    for i, item in enumerate(p1.in_play_items):
        x_pos = item_zone_x + i * 110
        y_pos = 200 # Stessa riga (Y) dei Personaggi
        
        img = images.get(item.card.num, images["default"])
        
        # Ruota l'oggetto se è "exerted"
        if not item.ready:
            img = pygame.transform.rotate(img, 90)
            
        screen.blit(img, (x_pos, y_pos))
        
        # Disegna il costo dell'oggetto
        stats_pos = (x_pos, y_pos + CARD_HEIGHT + 5)
        draw_text(screen, f"Costo: {item.card.cost}", stats_pos, font_small, pygame.Color("white"))
        

    # Inchiostro (P1)
    for i in range(p1.ready_ink):
        img = images.get("card-back", images["default"])
        screen.blit(img, (20, 180 + i * 20))
    for i in range(p1.exerted_ink):
        img = images.get("card-back", images["default"])
        img = pygame.transform.rotate(img, 90)
        screen.blit(img, (80, 180 + i * 20))

    # Mano (P1)
    for i, card in enumerate(p1.hand):
        img = images.get(card.num, images["default"])
        screen.blit(img, (200 + i * 110, 40)) 

    # Log moves
    log_area_x = WIDTH - 400
    draw_text(screen, "LOG AZIONI:", (log_area_x, 20), font, pygame.Color("yellow"))
    for i, log in enumerate(logs[-20:]): 
        draw_text(screen, log, (log_area_x, 50 + i * 20), font_small)
    
    pygame.display.flip()

################ Setup Pygame##############

pygame.init()
WIDTH, HEIGHT = 1400, 800 # --- Aumentata larghezza per il log ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lorcana AI Match (P = Pausa, SPAZIO = Avanza)")

# --- MODIFICATO: Font Multipli ---
try:
    font = pygame.font.SysFont("Arial", 24)
    font_small = pygame.font.SysFont("Arial", 16)
    font_damage = pygame.font.SysFont("Arial", 30, bold=True)
except Exception: # Fallback
    font = pygame.font.SysFont(None, 24)
    font_small = pygame.font.SysFont(None, 20)
    font_damage = pygame.font.SysFont(None, 30, bold=True)

fonts = (font, font_small, font_damage)

# Load card images from local folder 
images = load_card_images("/Users/diub/PycharmProjects/lorcanaAiProject/lorcana/assets")

# Crea un'immagine di default se manca
if "default" not in images:
    default_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    default_surface.fill((100, 100, 100))
    images["default"] = default_surface
# Controlla specificamente per il dorso
if "card-back" not in images:
    print("ATTENZIONE: 'card-back.png' non trovato. Uso il default.")
    images["card-back"] = images["default"]


# INIT GAME
state = lorcana_game.new_initial_state()
logs = []
clock = pygame.time.Clock()
running = True

# ---  Variabili per Pausa/Avanzamento ---
paused = False
step_mode = False # Per avanzare di un singolo frame

def advance_game_state(state, bot1, bot2, logs):
    """Funzione per avanzare il gioco di un'azione."""
    if state.is_terminal():
        return
    current_bot = bot1 if state.current_player() == 0 else bot2
    player_id = state.current_player() 
    action = current_bot.step(state)
    action_str = state.action_to_string(state.current_player(), action)
    
    winning_heuristic_name, winning_score, all_scores = get_heuristic_scores_for_action(action, state)
    

    log_message = f"P{player_id}: {action_str}"
    if winning_heuristic_name:
        log_message += f" [Heuristic: {winning_heuristic_name}, Score: {winning_score:.2f}]"
    else:
        log_message += f" [Heuristic: N/A (No valid action)]" 
    
    logs.append(log_message)

    #print(log_message)
    state.apply_action(action)

# --- LOOP PRINCIPALE  ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        
        # --- Gestione Pausa/Avanzamento ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p: # Tasto P per Pausa/Riprendi
                paused = not paused
                step_mode = False
            if event.key == pygame.K_SPACE: # Tasto SPAZIO per avanzare di 1
                if paused:
                    step_mode = True # Esegui un passo
    
    # Aggiorna la logica di gioco solo se non è in pausa
    if not state.is_terminal():
        if step_mode:
            advance_game_state(state, bot1, bot2, logs)
            step_mode = False # Torna in pausa dopo un passo
        elif not paused:
            advance_game_state(state, bot1, bot2, logs)

    # Disegna tavolo, anche in pausa
    draw_table(screen, fonts, state, images, logs, paused)
    
    # Limita il frame rate
    clock.tick(10 if paused else 2) # 2 FPS in auto-mode, 10 in pausa