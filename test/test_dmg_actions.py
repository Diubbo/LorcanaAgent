import unittest
import sys
sys.path.insert(1, '/Users/diub/PycharmProjects/lorcanaAiProject/lorcana')
from decklists import ActionCard
from ability import DamageTriggeredAbility

class DummyCharacter:
    def __init__(self, willpower=5):
        self.willpower = willpower
        self.damage = 0
        self.banished = False
    
    def check_banish(self):
        if self.damage >= self.willpower:
            self.banished = True

class TestActionCards(unittest.TestCase):

    def setUp(self):
        self.target = DummyCharacter()  
        self.fire_the_cannons = ActionCard(
            "197/204-EN-1",
            "Fire the Cannon!",
            "Deal 2 damage to chosen character",
            (DamageTriggeredAbility(2),),
            1,
            "steel",
            False,
            tuple()
        )
        self.smash = ActionCard(
            "200/204-EN-1",
            "Smash",
            "Deal 3 damage to a chosen character.",
            (DamageTriggeredAbility(3),),
            3,
            "steel",
            True,
            tuple()
        )

    def test_requires_target(self):
        self.assertTrue(self.fire_the_cannons.requires_target())
        self.assertTrue(self.smash.requires_target())

    def test_fire_the_cannons_damage(self):
        for ability in self.fire_the_cannons.abilities:
            ability.perform_ability(self.target)
        self.assertEqual(self.target.damage, 2)
        self.assertFalse(self.target.banished)

    def test_smash_damage_and_banish(self):
        # prima subisce 2 danni
        for ability in self.fire_the_cannons.abilities:
            ability.perform_ability(self.target)
        # poi 3 danni
        for ability in self.smash.abilities:
            ability.perform_ability(self.target)
        self.assertEqual(self.target.damage, 5)
        self.assertTrue(self.target.banished)  # ha superato la willpower

if __name__ == "__main__":
    unittest.main()