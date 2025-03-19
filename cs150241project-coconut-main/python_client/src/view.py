import pygame

pygame.init()
from project_types import (
    Piece,
    GameStateProtocol,
    ClickObserver,
    Location,
    GridID,
    Team,
    GameStateInitializeObserver,
    PieceID,
)
from cs150241project_networking import CS150241ProjectNetworking
import copy


class GameScreen:
    def __init__(self, xlen: int, ylen: int):
        self._xlen = xlen
        self._ylen = ylen
        self._screen = pygame.display.set_mode((self._xlen, self._ylen))
        self._color = (30, 30, 30, 255)

    @property
    def screen(self) -> pygame.Surface:
        return self._screen

    @property
    def xlen(self) -> int:
        return self._xlen

    @property
    def ylen(self) -> int:
        return self._ylen

    def fill(self):
        self._screen.fill(self._color)

    def update(self):
        pygame.display.flip()


class GameView:
    def __init__(self, state: GameStateProtocol, network: CS150241ProjectNetworking):
        self._gscreen = GameScreen(1200, 800)
        self._clock = pygame.time.Clock()
        self._fps = 60
        self._init_sizes()
        self._click_observers: list[ClickObserver] = []
        self._initilize_game_observer: list[GameStateInitializeObserver] = []
        self._init_view_state(state)
        self._network = network
        Teamid = {1: Team.Player1, 2: Team.Player2}
        self._playerid = Teamid[network.player_id]

    def _init_view_state(self, state: GameStateProtocol):  # New game
        self._board_state = copy.deepcopy(state.board_state)
        self._captured1_state = copy.deepcopy(state.captured1_state)
        self._captured2_state = copy.deepcopy(state.captured2_state)
        self._chosen_piece = state.chosen_piece
        self._possible_move = state.possible_move
        self._curr_player = state.curr_player
        self._moves_left = state.moves_left
        self._winner = state.winner

    def _init_sizes(self):
        self._gap_size = 2
        self._box_xlen = 75
        self._box_ylen = 75
        self._board_ystart = 100
        self._board_xstart = (
            self._gscreen.xlen - (5 * (self._box_xlen + self._gap_size))
        ) // 2
        self._captured_xstart = {
            0: (self._box_xlen + self._gap_size),
            1: self._gscreen.xlen - (4 * (self._box_xlen + self._gap_size)),
        }

    def register_on_click_observer(self, observer: ClickObserver):
        self._click_observers.append(observer)

    def register_game_state_initialize_observer(
        self, observer: GameStateInitializeObserver
    ):
        self._initilize_game_observer.append(observer)

    def _on_click(self, location: Location | None):
        for observer in self._click_observers:
            observer.on_click(location)

    def _initialize_p2(self, strgamestate: str):
        for observer in self._initilize_game_observer:
            observer.initialize_p2_game(strgamestate)

    def on_state_change(self, state: GameStateProtocol):
        self._board_state = copy.deepcopy(state.board_state)
        self._captured1_state = copy.deepcopy(state.captured1_state)
        self._captured2_state = copy.deepcopy(state.captured2_state)
        self._chosen_piece = state.chosen_piece
        self._possible_move = state.possible_move
        self._curr_player = state.curr_player
        self._moves_left = state.moves_left
        self._winner = state.winner

    def run(self):
        gscreen = self._gscreen
        clock = self._clock
        running = True
        latest_message = None
        started = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and self._playerid == self._curr_player
                ):
                    # Get mouse position
                    mouse_pos = event.pos
                    self._network.send(str(mouse_pos))

            if self._playerid == Team.Player2 and started:
                started = False
                self._network.send("get")

            # For Recieving from network
            for m in self._network.recv():
                latest_message = m
            if latest_message is not None:
                if latest_message.payload == "get":
                    if self._playerid == Team.Player1:
                        self._send_gamestate_message()
                    else:
                        pass
                elif latest_message.payload[0] == "#":
                    self._initialize_p2(latest_message.payload[1:])
                else:
                    mouse_int = self._str_to_pos(latest_message.payload)
                    self._get_click_info(mouse_int[0], mouse_int[1])
                latest_message = None

            gscreen.fill()

            self._display()
            self._display_overhead()
            self._display_underhead()
            if self._winner:
                self._display_winner()

            gscreen.update()
            clock.tick(self._fps)

    def _str_to_pos(self, input_str: str) -> tuple[int, int]:
        """
        Converts the string message into mouse position
        """
        stripped = input_str.strip("()")
        parts = stripped.split(",")
        return int(parts[0].strip()), int(parts[1].strip())

    def _send_gamestate_message(self):
        """
        Converts the GameState into a string message
        """

        def piece_to_char(piece: Piece | None):
            if piece is None:
                return "N"
            match piece.pieceid:
                case PieceID.CENTAUR:
                    return "C" + team_to_char(piece.team)
                case PieceID.DRAGON:
                    return "D" + team_to_char(piece.team)
                case PieceID.GOBLIN:
                    return "G" + team_to_char(piece.team)
                case PieceID.SLIME:
                    return "S" + team_to_char(piece.team)
                case PieceID.SUMMONER:
                    return "K" + team_to_char(piece.team)

        def team_to_char(team: Team | None):
            if team is None:
                return "P0"
            match team:
                case Team.Player1:
                    return "P1"
                case Team.Player2:
                    return "P2"
                case _:
                    return "P0"

        def grid_to_char(grid: GridID | None):
            match grid:
                case GridID.BOARD:
                    return "BO"
                case GridID.CAPTURED1:
                    return "C1"
                case GridID.CAPTURED2:
                    return "C2"
                case _:
                    return "//"

        def chosen_piece_to_char(piece: Piece | None):
            if piece is None:
                return "N"
            match piece.pieceid:
                case PieceID.CENTAUR:
                    piecechar = "C"
                case PieceID.DRAGON:
                    piecechar = "D"
                case PieceID.GOBLIN:
                    piecechar = "G"
                case PieceID.SLIME:
                    piecechar = "S"
                case PieceID.SUMMONER:
                    piecechar = "K"
            return (
                piecechar
                + team_to_char(piece.team)
                + grid_to_char(piece.gridid)
                + str(piece.loci)
                + str(piece.locj)
            )

        message = "#"

        for row in self._board_state:
            for piece in row:
                message = message + piece_to_char(piece) + ","
            message = message + ";"
        message = message + "#"

        for piece in self._captured1_state[0]:
            message = message + piece_to_char(piece) + ","
        message = message + "#"

        for piece in self._captured2_state[0]:
            message = message + piece_to_char(piece) + ","
        message = message + "#"

        message += chosen_piece_to_char(self._chosen_piece)
        message = message + "#"
        for loc in self._possible_move:
            message += str(loc[0]) + str(loc[1]) + ","
        message = message + "#"

        message += team_to_char(self._curr_player)
        message = message + "#"
        message += str(self._moves_left)
        message = message + "#"
        message += team_to_char(self._winner)

        self._network.send(message)

    def _display_winner(self):
        """
        Displays winner on screen
        """
        font = pygame.font.SysFont("", 40)
        if self._winner == Team.Neutral:
            text_obj = font.render(f"Draw!", True, "white")
        else:
            if self._winner == Team.Player1:
                text_obj = font.render(f"Winner: {self._winner.value}", True, "blue")
            elif self._winner == Team.Player2:
                text_obj = font.render(f"Winner: {self._winner.value}", True, "red")
            else:
                return

        xtext, _ = text_obj.get_size()
        screenx = self._gscreen.xlen
        self._gscreen.screen.blit(
            text_obj,
            (screenx // 2 - xtext // 2, 100 + (self._box_ylen + self._gap_size) * 6),
        )

    def _display_overhead(self):
        """
        Displays the Players above the captured grids.
        """
        font = pygame.font.SysFont("", 40)
        if self._curr_player == Team.Player1:
            text_obj1 = font.render(f"Player 1", True, "white")
        else:
            text_obj1 = font.render(f"Player 1", True, "blue")
        if self._curr_player == Team.Player2:
            text_obj2 = font.render(f"Player 2", True, "white")
        else:
            text_obj2 = font.render(f"Player 2", True, "red")
        text_obj3 = font.render(f"Summoner's Gridlock", True, "white")
        
        _, ytext = text_obj1.get_size()
        titlex, _ = text_obj3.get_size()
        grave1l = self._captured_xstart[0]
        grave2l = self._captured_xstart[1]
        screenx = self._gscreen.xlen
        # screeny = self._gscreen.ylen
        self._gscreen.screen.blit(
            text_obj1, (grave1l, self._board_ystart - (ytext + 2))
        )
        self._gscreen.screen.blit(
            text_obj2, (grave2l, self._board_ystart - (ytext + 2))
        )
        self._gscreen.screen.blit(
            text_obj3, ((screenx//2) - (titlex//2), self._board_ystart //2)
        )

    def _display_underhead(self):
        """
        Displays extra information below capture grids
        """
        font = pygame.font.SysFont("", 30)
        if self._curr_player == Team.Player1:
            text_obj1 = font.render(
                f"Current Moves Left: {self._moves_left}", True, "white"
            )
        else:
            text_obj1 = font.render(f"Current Moves Left: 0", True, "blue")
        if self._curr_player == Team.Player2:
            text_obj2 = font.render(
                f"Current Moves Left: {self._moves_left}", True, "white"
            )
        else:
            text_obj2 = font.render(f"Current Moves Left: 0", True, "red")
        if self._playerid == Team.Player1:
            text_obj3 = font.render(f"You are {self._playerid}", True, "blue")
            graveside = self._captured_xstart[0]
        else:
            text_obj3 = font.render(f"You are {self._playerid}", True, "red")
            graveside = self._captured_xstart[1]

        _, _ = text_obj1.get_size()
        grave1l = self._captured_xstart[0]
        grave2l = self._captured_xstart[1]
        # screenx = self._gscreen.xlen
        # screeny = self._gscreen.ylen
        self._gscreen.screen.blit(
            text_obj1,
            (grave1l, self._board_ystart + ((self._box_ylen + self._gap_size) * 2)),
        )
        self._gscreen.screen.blit(
            text_obj2,
            (grave2l, self._board_ystart + ((self._box_ylen + self._gap_size) * 2)),
        )
        self._gscreen.screen.blit(
            text_obj3,
            (graveside, self._board_ystart + ((self._box_ylen + self._gap_size) * 3)),
        )

    def _get_click_info(self, mouse_x: int, mouse_y: int):
        """
        Acquires what grid with follow up grid index before sending info to controller
        """
        if self._winner:  # Freeze
            return
        grave1l = self._captured_xstart[0]
        grave1r = grave1l + (3 * self._box_xlen + 2 * self._gap_size)
        boardl = self._board_xstart
        boardr = boardl + (5 * self._box_xlen + 4 * self._gap_size)
        grave2l = self._captured_xstart[1]
        grave2r = grave2l + (3 * self._box_xlen + 2 * self._gap_size)
        if grave1l <= mouse_x and mouse_x <= grave1r:
            gridid = GridID.CAPTURED1
            coord = self._get_location(self._captured1_state, grave1l, mouse_x, mouse_y)
        elif boardl <= mouse_x and mouse_x <= boardr:
            gridid = GridID.BOARD
            coord = self._get_location(self._board_state, boardl, mouse_x, mouse_y)
        elif grave2l <= mouse_x and mouse_x <= grave2r:
            gridid = GridID.CAPTURED2
            coord = self._get_location(self._captured2_state, grave2l, mouse_x, mouse_y)
        else:
            gridid = GridID.BOARD
            coord = None

        if not coord:
            location = None
        else:
            location = Location(gridid, coord[0], coord[1])
        self._on_click(location)

    def _get_location(
        self, grid: list[list[None | Piece]], xstart: int, mouse_x: int, mouse_y: int
    ) -> tuple[int, int] | None:
        """
        Acquires grid index of click location
        """
        row = len(grid)
        col = len(grid[0])
        y = self._board_ystart
        for i in range(row):
            x = xstart
            for j in range(col):
                if (
                    x <= mouse_x
                    and mouse_x <= x + self._box_xlen
                    and y <= mouse_y
                    and mouse_y <= y + self._box_ylen
                ):
                    return (i, j)

                x = x + (self._box_xlen + self._gap_size)
            y = y + (self._box_ylen + self._gap_size)
        return None

    def _display(self):
        """
        Loops for display
        """
        for i in range(1):
            for j in range(3):  # Specifications
                self._display_grid(i, j, GridID.CAPTURED1)
                self._display_grid(i, j, GridID.CAPTURED2)

        for i in range(5):
            for j in range(5):  # Specifications
                self._display_grid(i, j, GridID.BOARD)

    def _display_grid(self, i: int, j: int, gridid: GridID):
        """
        Displays grids for both Captured and board.
        Correctly shows color depending on the GameState
        """
        match gridid:
            case GridID.CAPTURED1:
                piece = self._captured1_state[i][j]
                xstart = self._captured_xstart[0]
            case GridID.CAPTURED2:
                piece = self._captured2_state[i][j]
                xstart = self._captured_xstart[1]
            case GridID.BOARD:
                piece = self._board_state[i][j]
                xstart = self._board_xstart

        x = xstart + (self._box_xlen + self._gap_size) * j
        y = self._board_ystart + (self._box_ylen + self._gap_size) * i

        if self._chosen_piece and self._chosen_piece.team == self._playerid:
            chosen_grid = self._chosen_piece.gridid
            if (i, j) == (
                self._chosen_piece.loci,
                self._chosen_piece.locj,
            ) and gridid == chosen_grid:
                pygame.draw.rect(
                    self._gscreen.screen,
                    "white",
                    (x, y, self._box_xlen, self._box_ylen),
                )
            elif (i, j) in self._possible_move and gridid == GridID.BOARD:
                pygame.draw.rect(
                    self._gscreen.screen,
                    "yellow",
                    (x, y, self._box_xlen, self._box_ylen),
                )
            else:
                pygame.draw.rect(
                    self._gscreen.screen,
                    "black",
                    (x, y, self._box_xlen, self._box_ylen),
                )
        else:
            pygame.draw.rect(
                self._gscreen.screen, "black", (x, y, self._box_xlen, self._box_ylen)
            )

        self._display_pieces(x, y, piece)

    def _display_pieces(self, x: int, y: int, piece: Piece | None):
        """
        Displays Piece icons with their team color on correct location
        """
        if not piece:
            return
        sizediff = 26
        centering = sizediff // 2
        center_circle = (x + self._box_xlen // 2, y + self._box_ylen // 2)
        circle_radus = 33

        if piece.team == Team.Player1:
            team_color = "blue"
        else:
            team_color = "red"
        pygame.draw.circle(
            self._gscreen.screen, team_color, center_circle, circle_radus
        )
        image_path = piece.path
        image = pygame.image.load(image_path)
        image_size = (self._box_xlen - sizediff, self._box_ylen - sizediff)
        image = pygame.transform.scale(image, image_size)
        self._gscreen.screen.blit(image, (x + centering, y + centering))
