import pygame as pg
pg.init()
import random
from math import sqrt

random.randint(1,10)

class random_class:
    def randint(min,max):
        return 0 #random number

random = random_class()

window = pg.display.set_mode([800, 600])

class button_class:
    def __init__(self, rgb, pos, radius):
        self.rgb, self.pos, self.radius = rgb, pos, radius
    def draw(self, window):
        pg.draw.circle(window, self.rgb, self.pos, self.radius, 0)
    def check_if_clicked_on(self, mouse_position):
        x_diff = mouse_position[0] - self.pos[0]
        y_diff = mouse_position[1] - self.pos[1]
        bob = sqrt(x_diff**2 + y_diff**2)
        if bob <= self.radius:
            print("Click")



button = button_class([100,100,200], [300,300], 10)

button.draw(window)

print(button.rgb)

running = True
rgb = [0,255,0]
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            running = False
            pg.quit()
            break
        if event.type == pg.KEYDOWN and event.key == pg.K_r:
            pg.KEYUP
            rgb = [255,0,0]
        elif event.type == pg.KEYUP and event.key == pg.K_r:
            rgb = [0,255,0]
        elif event.type == pg.MOUSEBUTTONDOWN:
            pos = pg.mouse.get_pos()
            print("pos", pos)
            button.check_if_clicked_on(pos)
    pg.draw.circle(window, rgb, [100,150], 30, 0)
    
    button.draw(window)
    pg.display.flip()



