from view import GameView
from model import GameModel
from project_types import GameStateProtocol, GameStateChangeObserver, Location


class GameController:
    def __init__(self, model: GameModel, view: GameView):
        self._model = model
        self._view = view
        self._game_state_change_observers: list[GameStateChangeObserver] = []

    def start(self):
        view = self._view
        self.register_game_state_change_observer(view)
        view.register_on_click_observer(self)
        view.register_game_state_initialize_observer(self)

        view.run()

    def on_click(self, location: Location | None):
        """
        Whenever a click occurs, check if valid
        Check if selecting piece or moving piece
        """
        if not location:
            return
        if not self._model.state.chosen_piece:
            self._model.validate_piece(location)
        else:
            self._model.check_movement(location)
        self._on_state_change(self._model.state)

    def initialize_p2_game(self, strgamestate: str):
        self._model.read_gamestate(strgamestate)
        self._on_state_change(self._model.state)

    def register_game_state_change_observer(self, observer: GameStateChangeObserver):
        self._game_state_change_observers.append(observer)

    def _on_state_change(self, state: GameStateProtocol):
        for observer in self._game_state_change_observers:
            observer.on_state_change(state)
