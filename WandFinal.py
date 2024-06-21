'''{ CAMERA PROPERTIES
'Model': 'ov5647', 'UnitCellSize': (1400, 1400),'ColorFilterArrangement': 2,
'Location': 2,'Rotation': 0,'PixelArraySize': (2592, 1944),
'PixelArrayActiveAreas': [(16, 6, 2592, 1944)],'ScalerCropMaximum': (0, 0, 0, 0),
'SystemDevices': (20748, 20738, 20739, 20740)
}'''
from picamera2 import Picamera2, Preview
import libcamera
import time
import cv2
import numpy as np
import pygame
import pygame_gui
import os
import random
import copy
import asyncio

from wizlightcontrol import Lumos, Nox, Incendio
from wand_classification import predictSpell


def load_overlay(index):
    #overlay
    training_overlay = pygame.image.load(spell_images[index])
    training_overlay.set_colorkey((0,0,0))
    overlay_alpha = 128
    training_overlay.fill((255,255,255,overlay_alpha), None, pygame.BLEND_RGBA_MULT)
    training_overlay = pygame.transform.scale(training_overlay, (screen_width*(1/3),screen_height*(1/3)))
    return training_overlay


#camera--------------------------------------------------------
camera = Picamera2()
#print(camera.sensor_modes)
camera_width = 640
camera_height = 480
config = camera.create_preview_configuration(main={"size": (camera_width,camera_height)}, display="main")
config["transform"] = libcamera.Transform(hflip=1)
camera.configure(config)
camera.set_controls({"AwbEnable":False, "Contrast":1, "Brightness":0, "ExposureValue":0, "AnalogueGain":1})
camera.start()

# Initialize pygame-------------------------------------------
pygame.init()

# Spell mp3 list
spell_audio = ['audio/lumos.mp3',
         'audio/nox.mp3',
         'audio/incendio.mp3',
         'audio/alohomora.mp3',
         'audio/wingardium leviosa.mp3',
         'audio/wingardium leviosa2.mp3']
spell_list = ["Pick a spell",
              "Lumos",
              "Nox",
              "Incendio",
              "Alohomora",
              "Wingardium Leviosa"]
spell_images = ["spells/blank.png",
                "spells/Lumos.png",
                "spells/Nox.png",
                "spells/Incendio.png",
                "spells/Alohomora.png",
                "spells/Wingardium_Leviosa.png"]


# Set up the screen
screen_width = camera_width
screen_height = camera_height+50
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Wand Magic")

# Set up the GUI manager
gui_manager = pygame_gui.UIManager((1024, 600))

training_audio_file = "audio/Training-mode.mp3"

# Create a button
button_training_width = 200
button_training_height = 50
button_training_x = 1#(screen_width - button_width) // 2
button_training_y = 1#(screen_height - button_height) // 2
button_training = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(button_training_x, button_training_y, button_training_width, button_training_height),
    text="Begin Training",
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
button_spell.hide()

#Dropdown Training menu
dropdown_w = 200
dropdown_h = 50
dropdown_x = 401
dropdown_y = 1
dropdown = pygame_gui.elements.ui_drop_down_menu.UIDropDownMenu(
    relative_rect=pygame.Rect(dropdown_x, dropdown_y, dropdown_w, dropdown_h),
    options_list = spell_list,
    starting_option = "Pick a spell",
    manager=gui_manager,
)
dropdown.hide()

#drawing label
drawing_label_w = 250
drawing_label_h = 75
drawing_label_x = 700
drawing_label_y = 380
drawing_label = pygame_gui.elements.ui_text_box.UITextBox(
    relative_rect=pygame.Rect(drawing_label_x, drawing_label_y, drawing_label_w, drawing_label_h),
    html_text = "Awaiting Spell",
    manager=gui_manager,
    visible = True,
)

#drawing label
spell_label_w = 250
spell_label_h = 75
spell_label_x = 700
spell_label_y = 460
spell_label = pygame_gui.elements.ui_text_box.UITextBox(
    relative_rect=pygame.Rect(spell_label_x, spell_label_y, spell_label_w, spell_label_h),
    html_text = "",
    manager=gui_manager,
    visible = True,
)

#image display for training
spell_image = pygame.image.load(spell_images[0])

# UI setup
clock = pygame.time.Clock()
black_background = np.zeros((camera_height, camera_width, 3), dtype=np.uint8)
white_background = np.ones((camera_height, camera_width, 3), dtype=np.uint8)
white_background = 255*white_background
background = pygame.surfarray.make_surface(black_background)
white_back = pygame.surfarray.make_surface(np.rot90(white_background[ ::1, ::-1, :3], k=1, axes = (0,1)))
white_back = pygame.transform.scale(white_back, (screen_width*(1/2)+2,screen_height*(1/2)+2))
screen.blit(white_back, (camera_width+31,100))

drawing_back = pygame.surfarray.make_surface(np.rot90(black_background[ ::1, ::-1, :3], k=1, axes = (0,1)))
drawing_back = pygame.transform.scale(drawing_back, (screen_width*(1/2),screen_height*(1/2)))
screen.blit(drawing_back, (camera_width+32,101))

training_overlay = load_overlay(0)
screen.blit(training_overlay, (camera_width+90,150))

#Wiz light setup
loop = asyncio.get_event_loop()

#loop variables
is_running = True
time_elapsed = 0
time_to_complete = 0
thresh = 200 # min bright spot threshold
steady = False
drawing = False
training = False
cooldown = False
spell_event = False
prevLoc = (int(camera_width/2) , int(camera_height/2))
existing_path = cv2.imread(spell_images[0])#[ ::1, ::-1, :3]

#Main Loop
while is_running:
    #time tracking------------------------------
    time_delta = clock.tick(60) / 1000.0
    time_elapsed += time_delta
    #print('%.2f' % time_elapsed)
    
    screen.fill((0,0,0))
    
    #Button Logic-----------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == button_spell:
                # Load random spell audio file  
                spell_audio_file = spell_audio[random.randint(0,len(spell_audio)-1)]
                #pygame.mixer.music.load(spell_audio_file)
                #pygame.mixer.music.play()
                #
                rand_spell = random.randint(1,len(spell_list)-1)
                dropdown.rebuild()
                spell_image = pygame.image.load(spell_images[rand_spell])
                chosen_path = cv2.imread(spell_images[rand_spell], cv2.IMREAD_GRAYSCALE)#[ ::1, ::-1, :3]
                training_overlay = load_overlay(rand_spell)
            if event.ui_element == button_training:
                if training == False:
                    training = True
                    dropdown.show()
                    button_spell.show()
                    pygame.mixer.music.load(training_audio_file)
                    pygame.mixer.music.play()
                    button_training.set_text("Exit Training")
                else:
                    training = False
                    dropdown.hide()
                    button_spell.hide()
                    training_overlay = load_overlay(0)
                    button_training.set_text("Begin Training")
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            spell_image = pygame.image.load(spell_images[spell_list.index(event.text)])
            chosen_path = cv2.imread(spell_images[spell_list.index(event.text)], cv2.IMREAD_GRAYSCALE)#[ ::1, ::-1, :3]
            training_overlay = load_overlay(spell_list.index(event.text))
        gui_manager.process_events(event)
    gui_manager.update(time_delta)


    # Camera capturage--------------------------------------------------
    rgb_array = camera.capture_array("main") #capture rgb photo
    cv2.rectangle(rgb_array, (prevLoc[0]-20,prevLoc[1]-20), (prevLoc[0]+20,prevLoc[1]+20), (0,0,255), 2)
    gray_array = cv2.cvtColor(rgb_array, cv2.COLOR_BGR2GRAY) #convert that photo into gray scale
    
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(gray_array) #find brightest point in the gray scale
    #print("Brightest Point: " , maxLoc, maxVal) #print brightest point location & data
    if maxVal > thresh:
        cv2.circle(rgb_array, maxLoc, 5, (255, 0, 0), 2) #draw a circle around the brightest point
    rgb_back = np.rot90(rgb_array[ ::1, ::-1, :3], k=1, axes = (0,1))
        
    #Wand Tracking Logic------------------------------------------
    #cooldown to avoid drawing paths to often
    if cooldown == True:
        #clear drawn path
        if time_elapsed > 1:
            black_background = np.zeros((camera_height, camera_width, 3), dtype=np.uint8)
            drawing_back = pygame.surfarray.make_surface(np.rot90(black_background[ ::1, ::-1, :3], k=1, axes = (0,1)))
            drawing_back = pygame.transform.scale(drawing_back, (screen_width*(1/2),screen_height*(1/2)))
            drawing_label.set_text("Awaiting Spell")
        if time_elapsed > 3:
            time_elapsed = 0
            cooldown = False
            
    else: #cooldown == False
        if maxVal > thresh:
            #Check if wand is still, if so start drawing
            if drawing == False:
                if prevLoc[0]-20 <= maxLoc[0] <= prevLoc[0]+20 and prevLoc[1]-20 <= maxLoc[1] <= prevLoc[1]+20:
                    steady = True
                    label_str = "Hold still for "+ f'{str(1-time_elapsed):.3}' + " seconds to begins spell"
                    drawing_label.set_text(label_str)
                else:
                    steady = False
                    time_elapsed = 0
                    prevLoc = maxLoc
                if time_elapsed > 1 and steady == True:
                    drawing = True
                    steady = False
                    prevLoc = maxLoc
                    time_elapsed = 0
                    drawing_label.set_text("Spell Started")
            
            #draw path
            elif drawing == True:
                time_to_complete += time_delta
                cv2.line(black_background, prevLoc, maxLoc, (255, 255, 255), 20)
                drawing_back = pygame.surfarray.make_surface(np.rot90(black_background[ ::1, ::-1, :3], k=1, axes = (0,1)))
                drawing_back = pygame.transform.scale(drawing_back, (screen_width*(1/2),screen_height*(1/2)))
                if prevLoc[0]-10 <= maxLoc[0] <= prevLoc[0]+10 and prevLoc[1]-10 <= maxLoc[1] <= prevLoc[1]+10:
                    steady = True
                    label_str = "Hold still for "+ f'{str(0.5-time_elapsed):.3}' + " seconds to stop spell"
                    drawing_label.set_text(label_str)
                else:
                    prevLoc = maxLoc
                    steady = False
                    time_elapsed = 0
                if time_elapsed > 0.5: # and steady == True
                    drawing = False
                    prevLoc = maxLoc
                    cooldown = True
                    time_elapsed = 0
                    cv2.imwrite('wand_spell.jpg', black_background)
                    drawing_label.set_text("Spell Complete")
                    if time_to_complete > 2:
                        #Analyze User spell
                        spell_event = True
                        spell_index = predictSpell('wand_spell.jpg')
                        spell_str = "Detected spell: " + spell_list[spell_index+1]
                        spell_label.set_text(spell_str)
                    else:
                        spell_str = "Spell too short. Try again."
                        spell_label.set_text(spell_str)
        else:
            time_elapsed = 0
    
    if spell_event == True and training == False:
        spell_event = False
        match spell_index:
            case 0: #Lumos
                loop.run_until_complete(Lumos())
                pygame.mixer.music.load(spell_audio[spell_index])
                pygame.mixer.music.play()
            case 1: #Nox
                loop.run_until_complete(Nox())
                pygame.mixer.music.load(spell_audio[spell_index])
                pygame.mixer.music.play()
            case 2: #Incendio
                loop.run_until_complete(Incendio())
                pygame.mixer.music.load(spell_audio[spell_index])
                pygame.mixer.music.play()
            case 3: #Alohomora
                pygame.mixer.music.load(spell_audio[spell_index])
                pygame.mixer.music.play()
            case 4: #Wingardium Leviosa
                if random.randint(0,1) == 0:
                    pygame.mixer.music.load(spell_audio[spell_index])
                    pygame.mixer.music.play()
                else:
                    pygame.mixer.music.load(spell_audio[spell_index+1])
                    pygame.mixer.music.play()
    
    cam_disp = pygame.surfarray.make_surface(rgb_back) # gray_array
    screen.blit(cam_disp, (0,60))
    if training == True:
        screen.blit(spell_image,(camera_width+100,1))
    screen.blit(white_back, (camera_width+31,100))
    screen.blit(drawing_back, (camera_width+32,101))
    screen.blit(training_overlay, (camera_width+90,150))
    gui_manager.draw_ui(screen)
    pygame.display.update()
pygame.quit()
camera.stop()
camera.stop_preview()