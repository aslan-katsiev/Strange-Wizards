import pygame
from constants import fontUI, fontGameOver, window, HEIGHT, WIDTH, objects


class Menu:
    def __init__(self, screen, options, font_size=36):
        self.screen = screen
        self.options = options
        self.font = pygame.font.Font(None, font_size)
        self.selected_index = 0

    def draw(self):
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i != self.selected_index else (255, 0, 0)
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, 100 + i * 50))
            self.screen.blit(text, text_rect)
            if i == self.selected_index:
                pygame.draw.rect(self.screen, (255, 0, 0), text_rect, width=2)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.selected_index

        return None

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return None

                selection = self.handle_input(event)
                if selection is not None:
                    return selection

            self.screen.fill((0, 0, 0))
            self.draw()
            pygame.display.flip()

        return None


class UI:
    def draw(self):
        i = 0
        mags = 0
        for obj in objects:
            if obj.type == 'mag':
                mags += 1
                pygame.draw.rect(window, obj.color, (i * 65, 20, 22, 22))

                text = fontUI.render(str(obj.hp), 1, obj.color)
                rect = text.get_rect(center=(5 + i * 65 + 32, 20 + 11))
                window.blit(text, rect)
                i += 1
        if mags < 2:
            text = fontGameOver.render('Игра окончена.', 1, 'white')
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            window.blit(text, rect)
