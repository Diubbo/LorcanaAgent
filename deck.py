import random

class Deck:
    def __init__(self, cards):
        self.cards = list(cards)

    def shuffle(self):
        random.shuffle(self.cards)
    # draw the top card
    def draw(self):
        if self.cards:
            return self.cards.pop(0)
        return None

    def draw_card(self, card):
        if card in self.cards:
            self.cards.remove(card)
            return card
        return None

    def put_card_on_bottom(self, card):
        self.cards.append(card)

    def get_total_cards(self):
        return len(self.cards)

    def get_card_choices(self):
        result = {}
        for c in self.cards:
            result[c] = result.get(c, 0) + 1
        return result
