from project_types import Piece, GameStateProtocol, Location, GridID, Team, PieceID


class Goblin(Piece):
    def __init__(self, i: int, j: int, team: Team):
        super().__init__(i, j, team)

        self._path = "icon_images/goblin.png"
        self._movement = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        self._pieceid = PieceID.GOBLIN


class Dragon(Piece):
    def __init__(self, i: int, j: int, team: Team):
        super().__init__(i, j, team)

        self._path = "icon_images/dragon.png"
        self._movement = [
            (0, -2),
            (0, -1),
            (0, 1),
            (0, 2),
            (-2, 0),
            (-1, 0),
            (1, 0),
            (2, 0),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]
        self._pieceid = PieceID.DRAGON


class Slime(Piece):
    def __init__(self, i: int, j: int, team: Team):
        super().__init__(i, j, team)

        self._path = "icon_images/slime.png"
        self._movement = [(1, 0)] if self._team == Team.Player1 else [(-1, 0)]
        self._pieceid = PieceID.SLIME

    def update_piece_team(self, newteam: Team):
        self._movement = [(1, 0)] if newteam == Team.Player1 else [(-1, 0)]
        self._team = newteam


class Summoner(Piece):
    def __init__(self, i: int, j: int, team: Team):
        super().__init__(i, j, team)

        self._path = "icon_images/summoner.png"
        self._movement = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        self._pieceid = PieceID.SUMMONER


class Centaur(Piece):
    def __init__(self, i: int, j: int, team: Team):
        super().__init__(i, j, team)

        self._path = "icon_images/centaur.png"
        self._movement = [
            (0, -2),
            (0, -1),
            (0, 1),
            (0, 2),
            (-2, 0),
            (-1, 0),
            (1, 0),
            (2, 0),
        ]
        self._pieceid = PieceID.CENTAUR


class GameState(GameStateProtocol):
    def __init__(self):
        t1 = Team.Player1
        t2 = Team.Player2
        self.board_state = [
            [
                Centaur(0, 0, t1),
                Summoner(0, 1, t1),
                Dragon(0, 2, t1),
                Summoner(0, 3, t1),
                Centaur(0, 4, t1),
            ],
            [Goblin(1, 0, t1), None, Slime(1, 2, t1), None, Goblin(1, 4, t1)],
            [None, None, None, None, None],
            [Goblin(3, 0, t2), None, Slime(3, 2, t2), None, Goblin(3, 4, t2)],
            [
                Centaur(4, 0, t2),
                Summoner(4, 1, t2),
                Dragon(4, 2, t2),
                Summoner(4, 3, t2),
                Centaur(4, 4, t2),
            ],
        ]
        self.captured1_state = [[None, None, None]]
        self.captured2_state = [[None, None, None]]
        self.chosen_piece = None
        self.possible_move = []
        self.curr_player = Team.Player1
        self.moves_left = 3
        self.winner = None


class GameModel:
    def __init__(self):
        self.state = GameState()
        self._summoners = self._get_summoner()
        self._team_opposites = {Team.Player1: Team.Player2, Team.Player2: Team.Player1}
        self._team_captured = {
            Team.Player1: self.state.captured1_state,
            Team.Player2: self.state.captured2_state,
        }

    def _get_summoner(self):
        """
        Acquires a list of all Summoners in play
        """
        summoners: list[Piece] = []
        board = self.state.board_state
        for i in range(5):
            for j in range(5):  # Specifications
                piece = board[i][j]
                if piece is not None and piece.pieceid == PieceID.SUMMONER:
                    summoners.append(piece)
        return summoners

    def check_movement(self, location: Location):
        """
        Checks if location to move is valid for current chosen piece
        Move if valid and check if winning after action
        """
        if (
            location.gridid == GridID.BOARD
            and (location.loci, location.locj) in self.state.possible_move
        ):
            self._move_piece(location)
            self._check_if_lost()  # Call just for checking if it works, ilipat pa somewhere
        else:
            self._refresh_chosen_state()

    def _move_piece(self, location: Location):
        """
        Given chosen_piece not None from controller
        Give valid location to move to:
        Move piece to empty spot/
        Move piece and capture another
        """
        state = self.state
        chosen_piece = state.chosen_piece
        assert chosen_piece is not None

        if chosen_piece.gridid is not GridID.BOARD:
            self._move_captured_piece(location)
        else:
            possible_piece = state.board_state[location.loci][location.locj]
            if not possible_piece:
                self._move_piece_to_empty_location(location)
            else:
                self._capture_piece(location, possible_piece)
        self._refresh_chosen_state()
        self.state.moves_left -= 1
        self._check_action()

    def _check_action(self):
        if self.state.moves_left == 0:
            self._next_round()

    def _next_round(self):
        self.state.curr_player = self._team_opposites[self.state.curr_player]
        self.state.moves_left = 3

    def _refresh_chosen_state(self):
        self.state.chosen_piece = None
        self.state.possible_move = []

    def _move_captured_piece(self, location: Location):
        """
        Given chosen_piece not None from move_piece()
        Move captured piece from Captured grid to Board
        """
        state = self.state
        chosen_piece = state.chosen_piece
        assert chosen_piece is not None
        captured_grid = self._team_captured[state.curr_player]

        captured_grid[chosen_piece.loci][chosen_piece.locj] = None
        state.board_state[location.loci][location.locj] = chosen_piece
        chosen_piece.update_piece_location(location)

    def _move_piece_to_empty_location(self, location: Location):
        """
        Given chosen_piece not None from move_piece()
        Move board piece to empty board space
        """
        state = self.state
        chosen_piece = state.chosen_piece
        assert chosen_piece is not None
        state.board_state[chosen_piece.loci][chosen_piece.locj] = None
        state.board_state[location.loci][location.locj] = chosen_piece
        chosen_piece.update_piece_location(location)

    def _capture_piece(self, location: Location, to_capture_piece: Piece):
        """
        Given chosen_piece not None from move_piece()
        Move board piece to occupied space
        Move captured piece to proper Captured grid space
        """
        state = self.state
        chosen_piece = state.chosen_piece
        assert chosen_piece is not None
        board = state.board_state

        board[chosen_piece.loci][chosen_piece.locj] = None
        board[location.loci][location.locj] = chosen_piece
        chosen_piece.update_piece_location(location)

        captured_grid = self._team_captured[state.curr_player]
        for i in range(1):
            for j in range(3):  # Specifications
                if not captured_grid[i][j]:
                    captured_grid[i][j] = to_capture_piece
                    new_location = location
                    new_location.gridid = (
                        GridID.CAPTURED1
                        if state.curr_player == Team.Player1
                        else GridID.CAPTURED2
                    )
                    new_location.loci = i
                    new_location.locj = j
                    to_capture_piece.update_piece_location(location)
                    to_capture_piece.update_piece_team(state.curr_player)
                    return

    def validate_piece(self, location: Location):
        """
        Gets chosen piece for the current player if possible
        """
        state = self.state

        match location.gridid:
            case GridID.CAPTURED1:
                grid = state.captured1_state
            case GridID.BOARD:
                grid = state.board_state
            case GridID.CAPTURED2:
                grid = state.captured2_state
            case _:
                return

        piece = grid[location.loci][location.locj]
        if piece:
            if piece.team == state.curr_player and state.chosen_piece == None:
                state.chosen_piece = piece
                self._get_piece_moves(piece)

    def _get_piece_moves(self, piece: Piece):
        """
        Gets the possible movement of a piece
        """
        state = self.state
        gridid = piece.gridid
        if gridid == GridID.BOARD:
            moves = piece.move()
            state.possible_move = self._clean_board_moves(piece, moves)
        else:
            state.possible_move = []
            summoner = self._all_summoner_moves()
            board = state.board_state
            for i in range(5):  # Specifications
                for j in range(5):
                    if board[i][j] == None and (i, j) not in summoner:
                        state.possible_move.append((i, j))

    def _all_summoner_moves(self) -> set[tuple[int, int]]:
        """
        gets all moves of all summoners, even if invalid
        """
        moves: set[tuple[int, int]] = set()
        for summo in self._summoners:
            move = summo.move()
            moves.update(move)
        return moves

    def _clean_board_moves(
        self, piece: Piece, moves: list[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        """
        Gets all movement of a piece
        and removes invalid ones
        """
        state = self.state
        board = state.board_state
        full_capture = True
        captured_grid = self._team_captured[piece.team]
        for i in range(1):  # Specifications
            for j in range(3):
                if captured_grid[i][j] == None:
                    full_capture = False
                    break

        for i, j in moves[:]:
            if not (0 <= i and i < 5 and 0 <= j and j < 5):  # Specification
                moves.remove((i, j))
            else:
                check_piece = board[i][j]
                if check_piece:
                    if check_piece.team == piece.team:
                        moves.remove((i, j))
                    elif check_piece.pieceid == PieceID.SUMMONER:
                        moves.remove((i, j))
                    elif piece.pieceid == PieceID.SUMMONER:
                        moves.remove((i, j))
                    elif full_capture:
                        moves.remove((i, j))
        pi, pj = piece.loci, piece.locj
        for i, j in moves[:]:  # Removes jumps
            if (
                (pi + 2 == i and isinstance(board[pi + 1][j], Piece))
                or (pi - 2 == i and isinstance(board[pi - 1][j], Piece))
                or (pj + 2 == j and isinstance(board[i][pj + 1], Piece))
                or (pj - 2 == j and isinstance(board[i][pj - 1], Piece))
            ):
                moves.remove((i, j))

        return moves

    def _check_if_lost(self):
        """
        Acquires a winner
        """
        state = self.state
        summoners = self._summoners
        p1_moves: list[tuple[int, int]] = []
        p2_moves: list[tuple[int, int]] = []

        for summ in summoners:
            valid_moves = self._clean_board_moves(summ, summ.move())
            if valid_moves:
                if summ.team == Team.Player1:
                    p1_moves.extend(valid_moves)
                else:
                    p2_moves.extend(valid_moves)

        if not p1_moves and not p2_moves:
            state.winner = Team.Neutral
        elif not p1_moves:
            state.winner = Team.Player2
        elif not p2_moves:
            state.winner = Team.Player1

    def read_gamestate(self, strgamestate: str):
        """
        Converts a string gamestate into a proper GameState
        """
        state = self.state

        def char_to_piece(
            char: str, loci: int, locj: int, grid: GridID
        ) -> Piece | None:
            chpiece = char[0]
            if chpiece == "N":
                return None
            team = char_to_team(char[1:3])
            if team is None:
                return None

            location = Location(grid, loci, locj)
            match chpiece:
                case "C":
                    piece = Centaur(loci, locj, team)
                case "D":
                    piece = Dragon(loci, locj, team)
                case "G":
                    piece = Goblin(loci, locj, team)
                case "S":
                    piece = Slime(loci, locj, team)
                case "K":
                    piece = Summoner(loci, locj, team)
                case _:
                    return None
            piece.update_piece_location(location)
            return piece

        def char_to_team(team: str) -> Team | None:
            match team:
                case "P1":
                    return Team.Player1
                case "P2":
                    return Team.Player2
                case _:
                    return None

        def char_to_grid(grid: str) -> GridID | None:
            match grid:
                case "BO":
                    return GridID.BOARD
                case "C1":
                    return GridID.CAPTURED1
                case "C2":
                    return GridID.CAPTURED2
                case _:
                    ...

        def chosen_char_to_piece(char: str) -> Piece | None:
            chpiece = char[0]
            if chpiece == "N":
                return None
            team = char_to_team(char[1:3])
            if team is None:
                return None
            grid = char_to_grid(char[3:5])
            loci = int(char[5])
            locj = int(char[6])
            location = Location(grid, loci, locj)
            match chpiece:
                case "C":
                    piece = Centaur(loci, locj, team)
                case "D":
                    piece = Dragon(loci, locj, team)
                case "G":
                    piece = Goblin(loci, locj, team)
                case "S":
                    piece = Slime(loci, locj, team)
                case "K":
                    piece = Summoner(loci, locj, team)
                case _:
                    return None
            piece.update_piece_location(location)
            return piece

        stateinfo = strgamestate.split("#")

        boardstr = stateinfo[0]
        board1 = boardstr.split(";")
        board2 = list(map(lambda s: s.split(","), board1))

        for i in range(5):
            for j in range(5):
                state.board_state[i][j] = char_to_piece(
                    board2[i][j], i, j, GridID.BOARD
                )

        stateinfo = strgamestate.split("#")

        captured1str = stateinfo[1]
        captured2str = stateinfo[2]
        captured1 = [captured1str.split(",")]
        captured2 = [captured2str.split(",")]

        for i in range(1):
            for j in range(3):
                state.captured1_state[i][j] = char_to_piece(
                    captured1[i][j], i, j, GridID.CAPTURED1
                )
                state.captured2_state[i][j] = char_to_piece(
                    captured2[i][j], i, j, GridID.CAPTURED2
                )

        self._refresh_chosen_state()
        state.chosen_piece = chosen_char_to_piece(stateinfo[3])
        pos_move = stateinfo[4]
        coords = pos_move.split(",")
        coords.pop()
        if coords:
            for loc in coords:
                self.state.possible_move.append((int(loc[0]), int(loc[1])))

        current_player = char_to_team(stateinfo[5])
        assert current_player is not None
        state.curr_player = current_player
        state.moves_left = int(stateinfo[6])
        state.winner = char_to_team(stateinfo[7])
        self._summoners = self._get_summoner()
