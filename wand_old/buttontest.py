import pygame
import pygame_gui
import os
import random

# Initialize pygame
pygame.init()

# Spell mp3 list
spell = ['audio/riddikulus.mp3','audio/oppugno.mp3','audio/lumos.mp3','audio/incendio.mp3','audio/immobilus.mp3','audio/expulso.mp3',
         'audio/expelliarmus.mp3','audio/cistem-aperio.mp3','audio/avada-kedavra.mp3','audio/arania-exumai.mp3','audio/alohomora.mp3','audio/Training-mode.mp3']


# Set up the screen
screen_width = 640
screen_height = 320
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Audio Player")

# Set up the GUI manager
gui_manager = pygame_gui.UIManager((screen_width, screen_height))

training_audio_file = "audio/Training-mode.mp3"

# Create a button
button_training_width = 200
button_training_height = 50
button_training_x = 1#(screen_width - button_width) // 2
button_training_y = 1#(screen_height - button_height) // 2
button_training = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(button_training_x, button_training_y, button_training_width, button_training_height),
    text="Training",
    manager=gui_manager,
)

# Load the audio file
spell_audio_file = "audio/expulso.mp3"
pygame.mixer.music.load(training_audio_file)

# Create a button
button_spell_width = 200
button_spell_height = 50
button_spell_x = 201#(screen_width - button_width) // 2
button_spell_y = 1#(screen_height - button_height) // 2
button_spell = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(button_spell_x, button_spell_y, button_spell_width, button_spell_height),
    text="Random Spell",
    manager=gui_manager,
)


# Main loop
clock = pygame.time.Clock()
is_running = True
while is_running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == button_spell:
                    # Load random spell audio file  
                    spell_audio_file = spell[random.randint(0,len(spell)-1)]
                    pygame.mixer.music.load(spell_audio_file)
                    pygame.mixer.music.play()
                if event.ui_element == button_training:                    
                    pygame.mixer.music.load(training_audio_file)
                    pygame.mixer.music.play()

        gui_manager.process_events(event)

    gui_manager.update(time_delta)

    screen.fill((255, 255, 255))
    gui_manager.draw_ui(screen)

    pygame.display.update()

pygame.quit()