class Document:
    def __init__(self):
        self.cursor = (0, 0)

    def move_to(self, x, y) -> None:
        self.cursor = (x, y)
        print(f"move_to({x}, {y})")
