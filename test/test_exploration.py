# test_exploration.py
import pygame
import exploration

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Создаём тестовую зону
zone = exploration.ExplorationZone(1000, 1000)

# Добавляем тестового моба
mob = exploration.Mob(500, 500, "тестовый_враг", 1)
zone.add_mob(mob)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    zone.update(keys)
    zone.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()