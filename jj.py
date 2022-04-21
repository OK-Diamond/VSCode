import pygame as pg
from random import choice as rand_choice
pg.init()

surface = pg.display.set_mode((400, 300))
floor_colour_bank = [[140, 100, 100], [100, 140, 100], [100, 100, 140]]

class scene:
    def __init__(self, floor_x, floor_col):
        self.floor_x = floor_x
scene(100, rand_choice(floor_colour_bank))

pg.draw.rect(surface, [48, 141, 70], pg.Rect(30, 30, 60, 90),  2, 16)
pg.display.flip()

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
            running = False
            pg.quit()
            break