import pygame as pg
import pygame_widgets
from pygame_widgets.slider import Slider as pg_slider
from pygame_widgets.textbox import TextBox as pg_text_box


class button_class:
    def __init__(self, pos, font, text="", stored_value="", box_rgb=[250, 250, 250], text_rgb=[0, 0, 0]) -> None:
        '''Class for a text input box.'''
        self.font, self.text, self.stored_value = font, text, stored_value
        self.txt_surface = self.font.render(self.text, True, pg.Color(text_rgb))
        size = [max(200, self.txt_surface.get_width()+10), self.txt_surface.get_height()+10]
        self.rect = pg.Rect(pos[0], pos[1], size[0], size[1])
        self.box_rgb, self.text_rgb = box_rgb, text_rgb
        self.border_rgb = [5,5,5] if self.box_rgb[0]+self.box_rgb[1]+self.box_rgb[2] > 255*3/2 else [250,250,250]
        self.pressed = False
    def __update_width(self:pg.display) -> None:
        '''Resizes the box if the text is too long.'''
        self.rect.w = max(200, self.txt_surface.get_width()+10)
    def draw(self, window) -> None:
        '''Draws the text imput box and the 'Enter your username' prompt to the PyGame window. The window still needs to be updated, e.g. using pg.display.flip() for this to appear.'''
        self.__update_width()
        if self.pressed: # Inverts colours if the button is held down (tracked with self.pressed)
            curr_box_rgb = [255-self.box_rgb[0], 255-self.box_rgb[1], 255-self.box_rgb[2]]
            curr_text_rgb = [255-self.text_rgb[0], 255-self.text_rgb[1], 255-self.text_rgb[2]]
            curr_border_rgb = [255-self.border_rgb[0], 255-self.border_rgb[1], 255-self.border_rgb[2]]
        else:
            curr_box_rgb = self.box_rgb
            curr_text_rgb = self.text_rgb
            curr_border_rgb = self.border_rgb
        pg.draw.rect(window, pg.Color(curr_box_rgb), self.rect) # Draw the rect
        pg.draw.rect(window, pg.Color(curr_border_rgb), self.rect, 2) # Draw the rect border
        window.blit(self.font.render(self.text, True, pg.Color(curr_text_rgb)), (self.rect.x+5, self.rect.y+2)) # Draw the text
    def handle_event(self, event) -> tuple[bool, str]:
        '''Returns a bool indicating whether the button has been clicked, followed by either self.stored_value (if button was clicked) or "" (if it wasn't)'''
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.pressed = False
            if self.rect.collidepoint(event.pos):
                return True, self.stored_value
        return False, ""
        
def init_slider(window, slider_range):
    slider = pg_slider(window, 100, 80, 800, 40, min=slider_range[0], max=slider_range[1], step=1)
    output_box = pg_text_box(window, 475, 150, 50, 50, fontSize=30)
    output_box.disable()  # Act as label instead of textbox

    difficulty = 0 
    font = pg.font.SysFont("Arial", 40)
    button = button_class([410, 220], font, "Submit")
    
    return slider, output_box, button



def main(slider_range=[0,99]):
    window = pg.display.set_mode([1000, 300])
    slider, output_box, button = init_slider(window, slider_range)

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
                running = False
                pg.quit()
                quit()
            button_click, difficulty_level = button.handle_event(event)
            if button_click:
                print("Difficulty:", slider.getValue())
                return slider.getValue()
                
            

        window.fill((250, 250, 250))
        output_box.setText(slider.getValue())

        pygame_widgets.update(event)
        button.draw(window)
        window.blit(pg.font.SysFont("arial", 45).render("Select Game Size:", True, pg.Color(0, 0, 0)), [300,10])
        pg.display.update()
    return


if __name__ == "__main__":
    pg.init()
    #print(pg.font.get_fonts())
    main()