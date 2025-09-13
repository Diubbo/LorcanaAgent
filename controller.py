import random

from action import DrawAction, FirstPlayerAction, PassAction

class Controller:
    def __init__(self, name, print_logs=False):
        self.name = name
        self.print_logs = print_logs

    def logMessage(self,msg):
        if self.print_logs:
            print(f'{self.name}: {msg}')
            
    def chooseAction(self, actions, game_state= None):
        raise NotImplementedError("This method should be overridden by subclasses")

class HumanController(Controller):
    def __init__(self, name, print_logs=False):
        super().__init__(name,print_logs)

    def chooseAction(self, actions,game_state=None):
        for i,a in enumerate(actions):
            print(f'[{i+1}]. {a}')
        while True:
            try:
                choice = int(input("Choice: "))-1
                if choice >= 0 and choice < len(actions):
                    break
            except ValueError:
                #try again
                pass
        return actions[choice]
    

class RandomController(Controller):
    def __init__(self, name, print_logs=False):
        super().__init__(name,print_logs)

    def chooseAction(self, actions, game_state=None):
        act = random.choice(actions)
        return act


def create_controller():
    name = input("Name:")
    print('Controller')
    print('[1]. Human')
    print('[2]. Random')
    while True:
        choice = int(input("Choice: "))
        if choice >=0 and choice <= 2:
            break
    if choice == 1:
        return HumanController(name, print_logs=True)
    else:
        return RandomController(name, print_logs=True)

    
class EnvironmentController(Controller):
    def __init__(self, name="env", print_logs=False):
        super().__init__(name, print_logs)

    def chooseAction(self, actions, gamestate=None):
        # Mulligan phase → non mulligare mai
        for a in actions:
            if isinstance(a, PassAction):
                return a

        # Die roll → scegli sempre di NON swappare
        for a in actions:
            if isinstance(a, FirstPlayerAction):
                return FirstPlayerAction(False)

        # Draw → prendi sempre la prima carta
        for a in actions:
            if isinstance(a, DrawAction):
                return a

        # Fallback 
        return random.choice(actions)