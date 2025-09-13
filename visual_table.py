import re
import pygame, sys
from decklists import CharacterCard
from setup_algorithm import bot1, bot2, lorcana_game
import os, pygame

############## Load Images ##############
CARD_WIDTH, CARD_HEIGHT = 100, 150

def normalize_name(name: str) -> str:
    # remove special characters
    name = name.replace("--", " ").replace("-", " ")
    name = re.sub(r"\s+", " ", name)
    return name.strip().lower()


def load_card_images(asset_dir="assets"):
    images = {}
    for fname in os.listdir(asset_dir):
        # only png files at the moment
        if fname.endswith(".png"):
            name = fname.replace(".png", "")
            norm_name = normalize_name(name)
            path = os.path.join(asset_dir, fname)
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
            images[norm_name] = img

    return images

########### Draw Table ###########

def draw_table(screen, font, state, images, logs):
    screen.fill((34, 139, 34))  
    
    # PLayer info
    p0 = state.engine.p1
    p1 = state.engine.p2
    text_p0 = font.render(f"Player 0 - Lore: {p0.lore}", True, (255,255,255))
    text_p1 = font.render(f"Player 1 - Lore: {p1.lore}", True, (255,255,255))
    screen.blit(text_p0, (50, 50))
    screen.blit(text_p1, (50, 700))
    
    # Card in play player 0 (below)
    for i, card in enumerate(p0.in_play_characters):
        name_img= (card.card.name+" "+card.card.subtext).lower()
        img = images.get(name_img, images["default"])
        if card.ready == False:            
            img = pygame.transform.rotate(img, 90)
        screen.blit(img, (200 + i*110, 400))
    
    for i, card in enumerate(p0.in_play_items):
        name_img= (card.card.name).lower()
        img = images.get(name_img, images["default"])
        screen.blit(img, (400 + i*110, 400))
    
    for i in range(p0.ready_ink):
        img = images.get("card back", images["default"])
        screen.blit(img, (200 + i*80, 550))
    # move the exerted ink to visually separate it
    for i in range(p0.exerted_ink):
        img = images.get("card back", images["default"])
        img = pygame.transform.rotate(img, 90)
        screen.blit(img, (400 + i*80, 550))

    
    # Card in play player 1 (above) 
    for i, card in enumerate(p1.in_play_characters):
        name_img= (card.card.name+" "+card.card.subtext).lower()
        img = images.get(name_img, images["default"])   
        screen.blit(img, (200 + i*110, 250))
    
    for i, card in enumerate(p1.in_play_items):
        name_img= (card.card.name).lower()
        img = images.get(name_img, images["default"])
        screen.blit(img, (400 + i*110, 250))

    for i in range(p1.ready_ink):
        img = images.get("card back", images["default"])
        screen.blit(img, (200 + i*80, 100))
    # move the exerted ink to visually separate it
    for i in range(p1.exerted_ink):
        img = images.get("card back", images["default"])
        img = pygame.transform.rotate(img, 90)
        screen.blit(img, (400 + i*80, 100))
    
    # Card in hand player 0 (below)
    for i, card in enumerate(p0.hand):
        if isinstance(card, CharacterCard):
            name_img= (card.name+" "+card.subtext).lower()
        else:
            name_img= (card.name).lower()
        img = images.get(name_img, images["default"])
        screen.blit(img, (200 + i*110, 650))
    
    # Card in hand player 1 (above)
    for i, card in enumerate(p1.hand):
        if isinstance(card, CharacterCard):
            name_img= (card.name+" "+card.subtext).lower()
        else:
            name_img= (card.name).lower()
        img = images.get(name_img, images["default"])
        screen.blit(img, (200 + i*110, 10))
    
    # Log moves
    for i, log in enumerate(logs[-10:]):
        txt = font.render(log, True, (255, 255, 0))
        screen.blit(txt, (900, 50 + i*20))
    
    pygame.display.flip()



################ Setup Pygame##############

pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lorcana AI Match")
font = pygame.font.SysFont(None, 24)

# Load card images from local folder 
images = load_card_images("lorcana/assets")

if "default" not in images:  # black card back as default
    default_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    default_surface.fill((100, 100, 100))
    images["default"] = default_surface

# INIT GAME
state = lorcana_game.new_initial_state()
logs = []
clock = pygame.time.Clock()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
    
    if not state.is_terminal():
        current_bot = bot1 if state.current_player() == 0 else bot2
        action = current_bot.step(state)
        action_str = state.action_to_string(state.current_player(), action)
        logs.append(f"P{state.current_player()} -> {action_str}")
        state.apply_action(action)
    
    draw_table(screen, font, state, images, logs)
    clock.tick(1) # move for second