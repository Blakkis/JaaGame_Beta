from __future__ import division

import pygame
from pygame.locals import *
from sys import exit as sys_exit
from collections import deque

# There is a another method to do day/night cycle
# which is based on the new Surface special_flags(BLEND_RGBA_MULT)
# During initial tests, it had much better framerate 

# Example of the new method: (Requires Pygame 1.8.0)

# overlay = pygame.Surface((500, 500), pygame.SRCALPHA)
# overlay.fill((16, 16, 77)); "(16, 16, 77) is NIGHT: (0.065, 0.065, 0.3)"
# screen.blit(overlay, (0, 0), special_flags=BLEND_RGBA_MULT)

# NOTE: Above still needs more testing


"""
    This is what i used in JaaRPG.(Tho im using older/slower version than this)

    the thunder/rain is just an extension of this idea
    keep in mind that this effect will drain alot of performance
    (You need to have room for other game logic)

    the above idea gives better fps but not sure how well it covers the shift spectrum
    (Not fully tested)
    
"""

class Main(object):
    def __init__(self):
        pygame.init()
        self.resolution = 500, 500
        self.screen = pygame.display.set_mode(self.resolution)
        self.clock = pygame.time.Clock()

        # A test texture which the lighting is going to affect
        self.test_texture = pygame.image.load('texture_of_lava.jpg').convert()

        self.cycle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.cycle_timer, 5)
        self.day_cycle = deque(('DAWN', 'NOON', 'DUSK', 'NIGHT'))
        # [Accumulator, time of the day length(Edit this to make the shifts longer)]
        self.shift_len = [0, 50]
        self.shifts = {'DAWN': (1.0, 1.0, 1.0),
                       'NOON': (0.8, 0.8, 0.8),
                       'DUSK': (0.9, 0.7, 0.3),
                       'NIGHT': (0.065, 0.065, 0.3)}


    def calc_light(self):
        """
            Create a surfarray for faster pixel modifying than get_pixel() and set_pixel()
            converted to float32 to allow -additive mult- to work on greater resolution
            (There is more room for research about this)

            then converted back to 'uint8' which is the 0-255 range for RGB and blitted to
            the screen.

            return -> None

        """
        r, g, b = self.shifts[self.day_cycle[0]]
        fr, fg, fb = self.interpolate()
        array = pygame.surfarray.pixels3d(self.screen).astype('float32')
        
        array[:,:,0] *= r - fr  
        array[:,:,1] *= g - fg 
        array[:,:,2] *= b - fb
        
        pygame.surfarray.blit_array(self.screen, array.astype('uint8'))

    def interpolate(self):
        """
            Interpolate between 2 values to provide smooth
            transit between different time of the day colors

            Smoothly transit to the next time of the day color

            return -> RGB
        """
        old_rgb = self.shifts[self.day_cycle[0]]
        new_rgb = self.shifts[self.day_cycle[1]]
        r = (old_rgb[0] - new_rgb[0]) / self.shift_len[1] * self.shift_len[0]
        g = (old_rgb[1] - new_rgb[1]) / self.shift_len[1] * self.shift_len[0]
        b = (old_rgb[2] - new_rgb[2]) / self.shift_len[1] * self.shift_len[0]
        return r, g, b


    def calc_shift_length(self):
        """
            Call'd by the 'self.cycle_timer' UserEvent to make the timing time based rather
            than framerate based

            return -> None
        """ 
        if self.shift_len[0] >= self.shift_len[1]:
            self.day_cycle.rotate(-1)
            self.shift_len[0] = 0
        else:
            self.shift_len[0] += 1


    def mainloop(self):
        while 1:
            self.clock.tick(8192)   # Just to get framerate
            self.screen.fill((0xff, 0xff, 0xff))
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys_exit()
                elif event.type == self.cycle_timer:
                    self.calc_shift_length()

            self.screen.blit(self.test_texture, (0, 0))

            # Everything you want the lighting to affect, should be above this function call.
            self.calc_light()

            pygame.display.set_caption('FPS: {}'.format(self.clock.get_fps()))
            
            pygame.display.flip()


if __name__ == '__main__':
    main = Main().mainloop()
            
