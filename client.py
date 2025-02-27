import pygame
from network import Network

width = 800
height = 800
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")


def redrawWindow(win, player, player2):
    win.fill((255, 255, 255))
    player.draw(win)
    player2.draw(win)
    pygame.display.update()


def main():
    run = True

    n = Network()
    p = n.getP()

    clock = pygame.time.Clock()  # add clock

    while run:
        clock.tick(60)  # Limit to 60 fps
        p2 = n.send(p)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        p.move()  # Move player 1 based on input
        redrawWindow(win, p, p2)  # Draw both players' positions


if __name__ == "__main__":
    main()
