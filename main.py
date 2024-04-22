import pygame
from ui_src.start import start

pygame.init()

win = pygame.display.set_mode((1280, 720))

pygame.display.set_caption("Game Of Go")

start(win=win)

pygame.quit()