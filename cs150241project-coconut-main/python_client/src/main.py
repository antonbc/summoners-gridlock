from view import GameView
from model import GameModel
from controller import GameController
from cs150241project_networking import CS150241ProjectNetworking


def main():
    network = CS150241ProjectNetworking.connect("localhost", 15000)

    model = GameModel()
    view = GameView(model.state, network)
    controller = GameController(model, view)

    controller.start()


if __name__ == "__main__":
    main()
