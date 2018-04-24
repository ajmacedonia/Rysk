
class Gamestate:
    def __init__(self):
        # a reference to the controlling Gamestate Manager
        self._gsm = None
        self.name = "Generic State"

    def initialize(self, core):
        """Initializes the state. Must be defined by the deriving class."""
        print("{0} initialize undefined".format(self.name))
        return False
        
    def update(self):
        """Updates the state. Must be defined by the deriving class."""
        print("{0} update undefined".format(self.name))
        
    def draw(self, display):
        """Draws the state. Must be defined by the deriving class."""
        print("{0} draw undefined".format(self.name))
        
class GamestateManager:

    def __init__(self):
        # the states that have been added to the GSM
        self._states = {}
        
        # the current state
        self._current_state = None
        
        # the next state
        self._next_state = None
        
        # whether or not to shutdown
        self.shutdown = False
    
    def register_state(self, key, state):
        """Registers a game state with the game state manager."""
        state._gsm = self
        self._states[key] = state
    
    def set_next_state(self, key):
        """Sets the next state."""
        if key in self._states:
            self._next_state = self._states[key]
        else:
            raise SystemExit("{0} is not a registered state".format(key))
    
    def initialize_state(self, core):
        """Initializes the current state."""
        
        # if the state was recently changed, initialize the new state
        if self._current_state != self._next_state:
            self._current_state = self._next_state
        return self._current_state.initialize(core)
        
    def update_state(self):
        """Updates the current state."""
        self._current_state.update()
        
    def draw_state(self, display):
        """Draws the current state."""
        self._current_state.draw(display)
        