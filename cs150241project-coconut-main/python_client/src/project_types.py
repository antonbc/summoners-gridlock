from __future__ import annotations
from typing import Protocol
from enum import StrEnum, auto


class ClickObserver(Protocol):
    def on_click(self, location: Location | None): ...


class GameStateChangeObserver(Protocol):
    def on_state_change(self, state: GameStateProtocol): ...


class GameStateInitializeObserver(Protocol):
    def initialize_p2_game(self, strgamestate: str): ...


class Piece:
    def __init__(self, i: int, j: int, team: Team):
        self._team = team
        self._gridid = GridID.BOARD
        self._loci = i
        self._locj = j
        self._path: str
        self._movement: list[tuple[int, int]]
        self._pieceid: PieceID

    def move(self) -> list[tuple[int, int]]:
        moves: list[tuple[int, int]] = []
        for k in self._movement:
            moves.append((k[0] + self._loci, k[1] + self._locj))
        return moves

    def update_piece_location(self, location: Location):
        self._gridid = location.gridid
        self._loci = location.loci
        self._locj = location.locj

    def update_piece_team(self, newteam: Team):
        self._team = newteam

    @property
    def team(self):
        return self._team

    @property
    def loci(self):
        return self._loci

    @property
    def locj(self):
        return self._locj

    @property
    def path(self):
        return self._path

    @property
    def gridid(self):
        return self._gridid

    @property
    def pieceid(self):
        return self._pieceid


class GameStateProtocol(Protocol):
    def __init__(self):
        self.board_state: list[list[Piece | None]]
        self.captured1_state: list[list[Piece | None]]
        self.captured2_state: list[list[Piece | None]]
        self.chosen_piece: None | Piece
        self.possible_move: list[tuple[int, int]]
        self.curr_player: Team
        self.moves_left: int
        self.winner: None | Team


class Location:
    def __init__(self, gridid: GridID | None, loci: int, locj: int):
        self.gridid = gridid
        self.loci = loci
        self.locj = locj


class GridID(StrEnum):
    BOARD = auto()
    CAPTURED1 = auto()
    CAPTURED2 = auto()


class PieceID(StrEnum):
    GOBLIN = auto()
    DRAGON = auto()
    SLIME = auto()
    SUMMONER = auto()
    CENTAUR = auto()


class Team(StrEnum):
    Player1 = auto()
    Player2 = auto()
    Neutral = auto()
