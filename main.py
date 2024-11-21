# pylint: disable=no-member
import asyncio
import pygame
from typing import Optional, Sequence
from dataclasses import dataclass
import sys
import random

CELL_WIDTH: int = 64
TEXT_SIZE: int = 36
EMPTY_VAL: int = -1


@dataclass
class COLORS:
    WHITE: tuple = (255, 255, 255)
    BLACK: tuple = (0, 0, 0)
    LIGHT_GRAY: tuple = (220, 220, 220)
    GRAY: tuple = (169, 169, 169)
    RED: tuple = (254, 57, 57)


class Cell:
    i: int
    j: int
    val: int = EMPTY_VAL
    is_clickable: bool = True
    is_active: bool = False
    is_valid: bool = True
    _scale: float = 0.99

    def __init__(self, i: int, j: int):
        self.i = i
        self.j = j

    def is_empty(self):
        return self.val == EMPTY_VAL

    @property
    def text(self):
        return str(self.val)

    @property
    def _offset(self):
        return (CELL_WIDTH - CELL_WIDTH * self._scale) / 2

    @property
    def x(self):
        return self.i * CELL_WIDTH + self._offset

    @property
    def y(self):
        return self.j * CELL_WIDTH + self._offset

    @property
    def width(self):
        return CELL_WIDTH * self._scale

    @property
    def Rect(self):
        return pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.width,
        )

    def collidepoint(self, mouse_pos: Sequence):
        return self.Rect.collidepoint(mouse_pos)


class Game:
    active_cell: Optional[Cell] = None
    table: list[list[Cell]]

    def __init__(self):
        pygame.init()
        self.font = pygame.font.Font(None, TEXT_SIZE)
        self.bg = pygame.display.set_mode((CELL_WIDTH * 9, CELL_WIDTH * 9))
        self.fps = pygame.time.Clock()

        self.generate_table()

    def is_sudoku_valid(self):
        rows = [set() for _ in range(9)]
        cols = [set() for _ in range(9)]
        blocks = [set() for _ in range(9)]

        for i in range(9):
            for j in range(9):
                cell = self.table[i][j]
                if cell.is_empty():
                    continue
                if (
                    cell.val in rows[i]
                    or cell.val in cols[j]
                    or cell.val in blocks[i // 3 * 3 + j // 3]
                ):
                    return False
                rows[i].add(cell.val)
                cols[j].add(cell.val)
                blocks[i // 3 * 3 + j // 3].add(cell.val)

        return True

    def is_possible_sudoku_table(self):
        def backtracing(i, j):
            if not self.is_sudoku_valid():
                return False
            if j >= 9:
                i, j = i + 1, 0
            if i >= 9:
                return True

            if not self.table[i][j].is_empty():
                return backtracing(i, j + 1)

            vals = [i for i in range(1, 10)]
            random.shuffle(vals)
            for val in vals:
                self.table[i][j].val = val
                if backtracing(i, j + 1):
                    self.table[i][j].val = EMPTY_VAL
                    return True
                self.table[i][j].val = EMPTY_VAL
            return False

        return backtracing(0, 0)

    def generate_table(self):
        self.table = []
        for i in range(9):
            self.table.append([])
            for j in range(9):
                self.table[-1].append(Cell(i, j))

        self._get_random_table()

        all_pos = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(all_pos)
        keep_num_of_cells = 30
        for k in range(81):
            i, j = all_pos[k]
            cell = self.table[i][j]
            if k < 81 - keep_num_of_cells:
                cell.val = EMPTY_VAL
            else:
                cell.is_clickable = False

    def _get_random_table(self, i=0, j=0):
        if not self.is_sudoku_valid():
            return False
        if j >= 9:
            i, j = i + 1, 0
        if i >= 9:
            return True

        vals = [i for i in range(1, 10)]
        random.shuffle(vals)
        for val in vals:
            self.table[i][j].val = val
            if self._get_random_table(i, j + 1):
                return True
            self.table[i][j].val = EMPTY_VAL
        return False

    def _is_in_even_block(self, i, j):
        return (i // 3 + j // 3) % 2 == 0

    def _draw_text(self, cell: Cell):
        color = COLORS.GRAY
        if cell.is_clickable:
            color = COLORS.BLACK if cell.is_valid else COLORS.RED

        text_surface = self.font.render(cell.text, True, color)
        text_rect = text_surface.get_rect(
            center=(cell.x + cell.width // 2, cell.y + cell.width // 2)
        )
        self.bg.blit(text_surface, text_rect)

    def draw_all_cells(self):
        for i in range(9):
            for j in range(9):
                cell = self.table[i][j]
                color = (
                    COLORS.WHITE if self._is_in_even_block(i, j) else COLORS.LIGHT_GRAY
                )

                pygame.draw.rect(self.bg, color, cell.Rect)
                if not cell.is_empty():
                    self._draw_text(cell)

    def handle_user_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.active_cell is None or not self.active_cell.is_clickable:
                    continue
                match event.key:
                    case pygame.K_1 | pygame.K_KP1:
                        self.active_cell.val = 1
                    case pygame.K_2 | pygame.K_KP2:
                        self.active_cell.val = 2
                    case pygame.K_3 | pygame.K_KP3:
                        self.active_cell.val = 3
                    case pygame.K_4 | pygame.K_KP4:
                        self.active_cell.val = 4
                    case pygame.K_5 | pygame.K_KP5:
                        self.active_cell.val = 5
                    case pygame.K_6 | pygame.K_KP6:
                        self.active_cell.val = 6
                    case pygame.K_7 | pygame.K_KP7:
                        self.active_cell.val = 7
                    case pygame.K_8 | pygame.K_KP8:
                        self.active_cell.val = 8
                    case pygame.K_9 | pygame.K_KP9:
                        self.active_cell.val = 9
                self.active_cell.is_valid = self.is_possible_sudoku_table()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for cells in self.table:
                    for cell in cells:
                        if cell.collidepoint(event.pos):
                            if self.active_cell:
                                self.active_cell.is_active = False

                                if not self.is_possible_sudoku_table():
                                    self.active_cell.val = EMPTY_VAL
                                    self.active_cell.is_valid = True

                            self.active_cell = cell
                            self.active_cell.is_active = True
                            print(f">>> Click on (i, j) = ({cell.i}, {cell.j})")
                            break

    async def start(self):
        while True:
            self.fps.tick(60)
            self.bg.fill(COLORS.BLACK)
            self.handle_user_input()
            self.draw_all_cells()
            pygame.display.flip()
            await asyncio.sleep(0)


async def main():
    game = Game()
    await game.start()


if __name__ == "__main__":
    asyncio.run(main())
