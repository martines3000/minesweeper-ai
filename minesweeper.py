import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.cells if len(self.cells) == self.count else set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.cells if self.count == 0 else set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        neighbours = self.get_neighbours(cell)
        new_knowledge = set()
        for neighbour in neighbours:
            if neighbour in self.mines:
                count -= 1
            elif neighbour not in self.safes:
                new_knowledge.add(neighbour)

        if len(new_knowledge) > 0:
            self.knowledge.append(Sentence(new_knowledge, count))

        self.mines_safes()

        while(len(self.moves_made) == len(self.safes)):
            new_knowledge = self.inferences()
            if len(new_knowledge) != 0:
                for sentence in new_knowledge:
                    print(sentence.__str__())
                    self.knowledge.append(sentence)
                self.mines_safes()
            else:
                break

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move not in self.moves_made:
                return move

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        maybe_safe_moves = []
        for i in range(self.height):
            for j in range(self.width):
                possible_move = (i, j)
                if possible_move not in self.moves_made and possible_move not in self.mines:
                    maybe_safe_moves.append(possible_move)

        if len(maybe_safe_moves) != 0:
            return random.choice(maybe_safe_moves)
        return None

    def get_neighbours(self, cell):
        """
        Returns all the neighbours of a given cell
        """
        neighbours = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                if 0 <= i < self.height and 0 <= j < self.width:
                    neighbours.add((i, j))
        return neighbours

    def inferences(self):
        """
        Returns all the new sentences that we can infer from current knowledge if any
        """
        new_knowledge = []
        for i in range(len(self.knowledge)-1):
            for j in range(i+1, len(self.knowledge)):
                a = self.knowledge[i]
                b = self.knowledge[j]
                if a.cells.issubset(b.cells):
                    new_sentence = Sentence(
                        b.cells.difference(a.cells), b.count-a.count)
                    if new_sentence not in self.knowledge and len(new_sentence.cells) > 0:
                        new_knowledge.append(new_sentence)
                elif b.cells.issubset(a.cells):
                    new_sentence = Sentence(
                        a.cells.difference(b.cells), a.count - b.count)
                    if new_sentence not in self.knowledge and len(new_sentence.cells) > 0:
                        new_knowledge.append(new_sentence)

        return new_knowledge

    def mines_safes(self):
        """
        Adds all new known mines and safes. 
        Also deletes empty sentences
        """
        changes = True
        while(changes):
            changes = False
            empty_sentences = []
            for sentence in self.knowledge:
                # Remove empty sentence
                if len(sentence.cells) == 0:
                    empty_sentences.append(sentence)
                    continue

                known_mines = sentence.known_mines().copy()
                known_safes = sentence.known_safes().copy()

                for mine in known_mines:
                    changes = True
                    self.mark_mine(mine)

                for safe in known_safes:
                    changes = True
                    self.mark_safe(safe)

            for sentence in empty_sentences:
                self.knowledge.remove(sentence)
