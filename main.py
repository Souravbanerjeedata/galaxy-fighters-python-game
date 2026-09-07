import pygame

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Fighters")

WHITE = (255, 255, 255)

def draw_window():
    WIN.fill(WHITE)
    pygame.display.update()

def main():
    clock = pygame.time.clock()
    run = True

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        draw_window()

    pygame.quit()

if __name__ == '__main__':
    main()