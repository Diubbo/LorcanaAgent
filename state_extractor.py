from game_state import GameState, PlayerState, CardState

def extract_player_state(player):
    return PlayerState(
        name=player.controller.name,
        hand_size=len(player.hand),
        ink=player.ready_ink,
        exerted_ink=player.exerted_ink,
        lore=player.lore,
        in_play_characters=[
            CardState(
                name=ch.card.name,
                cost=ch.card.cost,
                inkable=ch.card.inkable,
                lore=getattr(ch.card, "lore", 0),
                strength=getattr(ch.card, "strength", 0),
                willpower=getattr(ch.card, "willpower", 0),
                ready=ch.ready,
                exerted=not ch.ready
            )
            for ch in player.in_play_characters
        ],
        in_play_items=[
            CardState(
                name=item.card.name,
                cost=item.card.cost,
                inkable=item.card.inkable
            )
            for item in player.in_play_items
        ],
        discard_size=len(player.discard)
    )

def extract_game_state(game):
    return GameState(
        currentPlayer=extract_player_state(game.currentPlayer),
        currentOpponent=extract_player_state(game.currentOpponent),
        turn_number=game.turn,
        original_game=game
    )
