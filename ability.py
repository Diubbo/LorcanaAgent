#!/usr/bin/python3
from dataclasses import dataclass

@dataclass(frozen=True)
class Ability:
    pass

@dataclass(frozen=True)
class PassiveAbility(Ability):
    needs_target : bool = False 

@dataclass(frozen=True)
class GainEvasiveAbility(Ability):
    needs_target : bool = False 

@dataclass(frozen=True)
class PascalGainEvasiveAbility(GainEvasiveAbility):
    def has_evasive(self, game, in_play_character):
        if in_play_character in game.p1.in_play_characters:
            return len(game.p1.in_play_characters) >= 2
        if in_play_character in game.p2.in_play_characters:
            return len(game.p2.in_play_characters) >= 2
        return False

@dataclass(frozen=True)
class OnPlayAbility(Ability):
    needs_target : bool = False 

@dataclass(frozen=True)
class TriggeredAbility(Ability):
    pass

@dataclass(frozen=True)
class HealingTriggeredAbility(TriggeredAbility):
    healing_power: int 
    
    needs_target: bool = True
    needs_to_exert : bool = True
    needs_to_banish: bool = False

    def perform_ability(self, in_play_character, owner=None):
        in_play_character.damage -= self.healing_power
        if in_play_character.damage < 0:
            in_play_character.damage = 0

@dataclass(frozen=True)
class DamageTriggeredAbility(TriggeredAbility):
    damage_power: int

    needs_target: bool = True
    needs_to_exert : bool = True
    needs_to_banish: bool = False

    def perform_ability(self, in_play_character, owner):
        in_play_character.damage += self.damage_power
        owner.check_banish(in_play_character)

@dataclass(frozen=True)
class TargetedHealingAbility(TriggeredAbility):
    healing_power: int

    needs_target: bool = True
    needs_to_exert : bool = True
    needs_to_banish: bool = False

    def perform_ability(self, in_play_character, owner=None): 
        in_play_character.damage -= self.healing_power
        if in_play_character.damage < 0:
            in_play_character.damage = 0

@dataclass(frozen=True)
class BanishItemAbility(TriggeredAbility):

    needs_target: bool = True
    needs_to_exert : bool = True
    needs_to_banish: bool = False
    
    def perform_ability(self, in_play_item, owner):
        owner.banish_item(in_play_item.card)


@dataclass(frozen=True)
class OnQuestAbility(Ability):
    needs_target : bool = False 

@dataclass(frozen=True)
class ReadyPrincessAbility(OnQuestAbility):
    def on_quest(self, game, in_play_character):
        for char in game.currentPlayer.in_play_characters:
            if "Princess" in char.card.traits and char != in_play_character:
                char.cannot_quest_this_turn = True
                char.ready = True

@dataclass(frozen=True)
class DrawCardOnPlayAbility(OnPlayAbility):
    cards_to_draw: int = 1


    def perform_ability(self, game, player):
        player.controller.logMessage(f"Attivata abilità: {player.controller.name} pesca {self.cards_to_draw} carta(e).")
        for _ in range(self.cards_to_draw):
            player.draw_top_card()

@dataclass(frozen=True)
class DrawCardsActionAbility(Ability):
    cards_to_draw: int = 2
    needs_target: bool = False 

    def perform_ability(self, game, player):
        player.controller.logMessage(f"Attivata abilità: {player.controller.name} pesca {self.cards_to_draw} carta(e).")
        for _ in range(self.cards_to_draw):
            player.draw_top_card()

@dataclass(frozen=True)
class HealAllCharactersAbility(Ability):
    healing_power: int = 3
    needs_target: bool = False 

    def perform_ability(self, game, player):
        player.controller.logMessage(f"Attivata abilità: {player.controller.name} cura i suoi personaggi.")
        for char in player.in_play_characters:
            char.damage -= self.healing_power
            if char.damage < 0:
                char.damage = 0

@dataclass(frozen=True)
class InkTopCardAbility(Ability):
    needs_target: bool = False 

    def perform_ability(self, game, player):
        card = player.draw_top_card() 
        if card:
            player.hand.remove(card) 
            player.exerted_ink += 1 
            player.controller.logMessage(f"Attivata abilità: {player.controller.name} inchiostra {card} dal mazzo.")

@dataclass(frozen=True)
class DamageAllOpponentsAbility(Ability):
    damage_power: int = 2
    needs_target: bool = False 

    def perform_ability(self, game, player):
        opponent = game.currentOpponent
        player.controller.logMessage(f"Attivata abilità: {player.controller.name} danneggia tutti i personaggi avversari.")
        for char in list(opponent.in_play_characters):
            char.damage += self.damage_power
            opponent.check_banish(char)