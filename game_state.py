from dataclasses import dataclass, field
from typing import List
from game import Game
@dataclass
class CardState:
    name: str
    cost: int
    inkable: bool
    lore: int = 0
    strength: int = 0
    willpower: int = 0
    ready: bool = True
    exerted: bool = False

@dataclass
class PlayerState:
    name: str
    hand_size: int
    ink: int
    exerted_ink: int
    lore: int
    in_play_characters: List[CardState] = field(default_factory=list)
    in_play_items: List[CardState] = field(default_factory=list)
    discard_size: int = 0

@dataclass
class GameState:
    currentPlayer: PlayerState
    currentOpponent: PlayerState
    turn_number: int
    original_game: Game