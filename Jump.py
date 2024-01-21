import pygame
from pygame.locals import *
import pickle
from os import path
from pygame import mixer
pygame.init()

clock = pygame.time.Clock()
fps=60
screen_width = 1000
screen_height = 800
text_screen = pygame.display.set_mode((screen_width , screen_height))
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Jail break Jump")

#adding background music to the game
mixer.music.load('BGM.mp3')
mixer.music.play(-1)
mixer.music.set_volume(1.8)
#define game variables
main_menu = True
level=1
game_over = 0
tile_size = 50
max_levels = 10

#setting the image
back_img = pygame.image.load('pictures/prison2.jpg')
grey_img = pygame.image.load('pictures/stone.jpg')
replay_img = pygame.image.load('pictures/replay.png')
play_img = pygame.image.load('pictures/play.png')
exit_img = pygame.image.load('pictures/exit.png')
portal_img = pygame.image.load('pictures/portal.jpg')

#text_font
text_font = pygame.font.SysFont('Arial',30 )

def draw_text(text, font, text_col, x, y):
     img = font.render(text, True, text_col)
     screen.blit(img, (x, y))

     
def reset_level(level):
     player.reset(100,screen_height - 130)
     portal_group.empty()
     # load in level data and create world
     if path.exists(f'level_{level}.data'):
          pickle_in = open (f'level_{level}.data','rb')
          world_data = pickle.load(pickle_in)
     world=World(world_data)

     return world

# #drawing a grid for each tile(not using this in actual game)
# def draw_grid():
# 	for line in range(0, 20):
# 		pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
# 		pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))
          
class Button():
     def __init__(self,x,y,image):
          self.image = image
          self.rect = self.image.get_rect()
          self.rect.x =  x
          self.rect.y = y 
          self.clicked = False
          
          

     def draw(self):
          action = False

          #get mouse position
          pos = pygame.mouse.get_pos()

          #check mouseover and clicked conditions
          if self.rect.collidepoint(pos):
               if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False :
                    action = True
                    self.clicked = True

          if pygame.mouse.get_pressed()[0] == 0 :
               self.clicked = False

          #draw button
          screen.blit(self.image,self.rect)

          return action

class Player():
     def __init__(self,x,y) :
          self.reset(x,y)
          self.images_right = []
          self.images_left = []
          self.index = 0
          self.counter = 0
          for num in range(1, 3):
               img_right = pygame.image.load(f'pictures/walking{num}.png')
               img_right = pygame.transform.scale(img_right,(40,80))
               img_left = pygame.transform.flip(img_right, True, False)
               self.images_right.append(img_right)
               self.images_left.append(img_left)
               self.image = self.images_right[self.index]
          self.rect = self.image.get_rect()
          self.rect.x =x 
          self.rect.y =y
          self.width= self.image.get_width()
          self.height= self.image.get_height()
          self.velo_y = 0
          self.jump_state = 0
          self.jumped = False
          self.direction = 0 

     #updating the player movement
     def update (self,game_over):

          dx = 0
          dy = 0
          walk_cooldown = 5
          
               #detect if key is pressed
          if game_over == 0:   
               key = pygame.key.get_pressed()
               #adding a condition for not double jumping
               if key[pygame.K_SPACE] and self.jumped == False and self.jump_state >=15:                
                    self.velo_y = -15
                    self.jump_state = 0
                    self.jumped = True
                    if self.sprint:
                         self.velo_y = -18
          
               if key[pygame.K_SPACE]  == False:
                    self.jump_state += 1
                    self.jumped = False
                    
               #adding a sprint status to make the player jump further
               if key[pygame.K_a] and key[pygame.K_LSHIFT]:
                    dx -=3
                    self.sprint = True
                    self.counter += 1
                    self.direction = -1
               if key[pygame.K_d] and key[pygame.K_LSHIFT]:
                    dx +=3
                    self.sprint = True
                    self.counter += 1
                    self.direction = 1
               #horizontal movement
               if key [pygame.K_a]:
                    dx -=2
                    self.sprint = False
                    self.counter += 1
                    self.direction = -1
               if key [pygame.K_d]:
                    dx +=2
                    self.sprint = False
                    self.counter += 1
                    self.direction = 1
               #adding gravity to player
               self.velo_y +=0.9
               if self.velo_y > 10:
                    self.velo_y = 10
               dy += self.velo_y
               if key[pygame.K_a] == False and key[pygame.K_d] == False :
                    self.counter = 0
                    self.index = 0
                    self.image = self.images_right[self.index] 

               # handle animation  
               if self.counter > walk_cooldown:
                    self.counter = 0
                    self.index += 1
               if self.index >= len(self.images_right):
                    self.index = 0

               if self.direction == 1:
                    self.image = self.images_right[self.index]
               if self.direction == -1:
                    self.image = self.images_left[self.index]

               #check for collision 
               self.in_air = True
               for tile in world.tile_list:
                    #check collision in horizontal direction
                    if tile[1].colliderect(self.rect.x+dx,self.rect.y, self.width,self.height):
                         dx = 0
                    #check collision in vertical direction
                    if tile[1].colliderect(self.rect.x,self.rect.y+dy, self.width,self.height):
                    #check if below the ground  -jumping
                         if self.velo_y < 0:
                              dy = tile[1].bottom -self.rect.top
                              self.velo_y = 0
                         #check if above the ground  -falling
                         if self.velo_y > 0:
                              dy = tile[1].top -self.rect.bottom
                              self.velo_y = 0
                              self.in_air = False
                         
                    #determine if a player is collide with portal and change his level
                    if pygame.sprite.spritecollide(self,portal_group,False):
                              game_over = 1
                  #           print('changing level')          
              
               y_threshold = screen_height + 100
               if self.rect.y > y_threshold :
                    game_over = -1

               #update player position
               self.rect.x += dx
               self.rect.y += dy

               screen.blit(self.image,self.rect)
               

               return game_over

     def reset(self,x,y):
          img = pygame.image.load('pictures/blue.jpg')
          self.image = pygame.transform.scale(img,(40,70))
          self.rect = self.image.get_rect()
          self.rect.x =x 
          self.rect.y =y
          self.width= self.image.get_width()
          self.height= self.image.get_height()
          self.velo_y = 0
          self.jump_state = 0
          self.jumped = False
          self.in_air = True

#create a class for game world and setting the tiles
class World():
      
      def __init__ (self,data):
            self.tile_list = []
            row_count = 0
            for row in data :
                  col_count = 0
                  for tile in row:
                        if tile == 1:
                              img = pygame.transform.scale(grey_img,(tile_size,tile_size))
                              img_rect = img.get_rect()
                              img_rect.x = col_count * tile_size
                              img_rect.y = row_count * tile_size
                              tile = (img,img_rect)
                              self.tile_list.append(tile)
                        if tile == 2:
                             portal = Portal(col_count * tile_size ,row_count * tile_size-(tile_size // 1.5))
                             portal_group.add(portal)
                        col_count += 1
                  row_count += 1
                          

      def draw(self):
        for tile in self.tile_list:
            screen.blit( tile[0],tile[1])
            
#create a class for portal
class Portal(pygame.sprite.Sprite):
          def __init__(self,x,y):
               pygame.sprite.Sprite.__init__(self)
               img = pygame.image.load('pictures/portal.jpg')
               self.image = pygame.transform.scale(img,(tile_size,int(tile_size*1.5)))
               self.rect = self.image.get_rect()
               self.rect.x = x
               self.rect.y = y
               

portal_group = pygame.sprite.Group()

#instance for Player
player = Player(100,screen_height-130)

if path.exists(f'level_{level}.data'):
     pickle_in = open (f'level_{level}.data','rb')
     world_data = pickle.load(pickle_in)
world=World(world_data)
     


#create buttons
replay_button = Button(screen_width // 2 - 70 , screen_height // 2 + 100 , replay_img)
play_button = Button(screen_width // 2 - 350 , screen_height // 2 , play_img)
exit_button = Button(screen_width // 2 + 150 , screen_height // 2 , exit_img) 

run = True
#variable to control when to display the text
show_text = False 
tex_start_time = 0 #store time when the text is shown

while run :
    clock.tick(fps)
    screen.blit(back_img,(0,0))

    if main_menu == True:
      if exit_button.draw():
           run = False
      if play_button.draw():
           main_menu = False
           show_text = True #set show_text to true when play is clicked
    else:
         world.draw()
         player.update(game_over)
         portal_group.draw(screen)
          
         
          #if the player has died
         if game_over == -1:
            replay_action = replay_button.draw()

            if replay_action : 
               level = 1
               world_data = [] 
               world = reset_level(level)
               player.reset(100,screen_height -130)
               game_over = 0
 
         else :
              game_over = player.update(game_over) 
          #if the player has completed the level
              if game_over == 1:
           #reset the game and go to next level
                  level +=1
                  if level <= max_levels:
                   #reset level
                   world_data=[]
                   world=reset_level(level)
                   game_over = 0
                  else:
                   #restart game
                     pass 

    if show_text:
     #display text after play button is clicked 
     Tutorial_text = [
          "Welcome to Jail Breaker Jump!",
          "Press 'A' to move left", 
          "Press 'D' to move right",
          "Press 'Space' to jump" ,
          "Press 'Shift' to sprint and jump further"
     ]
     for text in Tutorial_text :
        draw_text(text, text_font, (255, 255, 255), 155, 50 + Tutorial_text.index(text)*40) 
     #check if 15s have passed since that the text was shown
     current_time = pygame.time.get_ticks()
     if current_time - tex_start_time >= 15000 :
          show_text = False
         
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    pygame.display.update()
    
pygame.quit