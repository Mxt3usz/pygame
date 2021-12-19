from typing import Tuple
import os
import pygame
pygame.font.init()
import math
from pygame import Vector2
from pygame import Rect, mouse
from pygame.constants import BUTTON_RIGHT, KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, K_e
from pygame.draw import rect

Width, Height = 1000,600
Window = pygame.display.set_mode((Width,Height))
pygame.display.set_caption("First PyGame")
White = (255,255,255)
Red = (255,0,0)
Fps = 60
font = pygame.font.SysFont("comicsans",20)
selected = False
buttonDown_Right = False
buttonDown_Left = False
in_motion = False
slider_selected = False
dist = 0
count = 0
Background_Image = pygame.image.load(os.path.join("Assets","snowbackground.png")).convert()
Background_Image = pygame.transform.scale(Background_Image,(1000,600)).convert()
Square_Image = pygame.image.load(os.path.join("Assets","snowman_red.png"))
Snowball_Image = pygame.image.load(os.path.join("Assets","snowball.png"))
Skellet_Image = pygame.image.load(os.path.join("Assets","skellet.png"))
Slider_Head = pygame.image.load(os.path.join("Assets","sliderheadred.png"))
Slider = pygame.image.load(os.path.join("Assets","sliderred.png"))
slider_rect = pygame.Rect(594,92,Slider_Head.get_width(),Slider_Head.get_height())

Black = (0,0,0)
class Button():

    def __init__(self,pos,string,state):
        self.texture = pygame.image.load(os.path.join("Assets",string))
        self.pos = pygame.Rect(pos.x,pos.y,self.texture.get_width(),self.texture.get_height())
        self.mouse = pygame.Rect(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1],1,1)
        self.mouse_pressed = pygame.mouse.get_pressed()
        self.state = state

    def update_button(self):
        global currState
        if self.pos.colliderect(self.mouse):
            self.texture.set_alpha(75) # hover effect
            if self.mouse_pressed[0]:
                currState = self.state
                
           
    def draw_button(self):
        Window.blit(self.texture,self.pos)

def movement(mouse_pos,square_purple):
    speed = 10
    global count
    global selected
    global dist
    global in_motion
    curr_mouse = pygame.mouse.get_pos()
    mouse_vec = Vector2(mouse_pos[0],mouse_pos[1])
    if count > 1:
        square_vec = Vector2(square_purple.x+Square_Image.get_width()//2,square_purple.y+Square_Image.get_height()//2)

    else:
        square_vec = Vector2(square_purple.x,square_purple.y)
    dist = Vector2.distance_to(mouse_vec,square_vec)
    direction = mouse_vec - square_vec
    angle = math.atan2(direction.x,direction.y)
    mouse_rect = pygame.Rect(curr_mouse[0],curr_mouse[1],1,1)
    pygame.draw.rect(Window,Red,mouse_rect)

    if mouse_rect.colliderect(square_purple) and pygame.mouse.get_pressed()[0]:
        selected = True

    if mouse_rect.colliderect(square_purple) == False and  pygame.mouse.get_pressed()[0] and in_motion == False:
        selected = False

    if dist > 5 and selected:
        square_purple.x += speed * math.sin(angle)
        square_purple.y += speed * math.cos(angle)
        in_motion = True
        count += 1

    else:
        in_motion = False

class Bullet:
    def __init__(self,spos,mpos,bullets):
        self.spos = spos
        self.mpos = mpos
        self.vel = 6
        self.pos = pygame.Rect(spos.x + spos.width//2,spos.y + spos.height//2,15,15)
        self.direction = Vector2(mpos[0],mpos[1]) - Vector2(spos.x,spos.y)
        self.angle = 0
        self.bullets = bullets

    def setAngle(self):
        self.angle = math.atan2(self.direction.x,self.direction.y)

    def move(self):
        self.pos.x += self.vel * math.sin(self.angle)
        self.pos.y += self.vel * math.cos(self.angle)

    def getpos(self):
        return self.pos

    def remove_bullet(self):
        for bullet in self.bullets:
            if bullet.getpos().x >= 1000 or bullet.getpos().x <= 0:
                self.bullets.remove(bullet)
            if bullet.getpos().y <= 0 or bullet.getpos().y >= 600:
                self.bullets.remove(bullet)

class Enemy:
    def __init__(self,pos):
        self.pos = pygame.Rect(pos.x,pos.y,Skellet_Image.get_width(),Skellet_Image.get_height())
        self.vel = 8
        self.hp = 48
        self.dmg = 10

    def get_pos(self):
        return self.pos

    def move(self):
        self.pos.x -= 1

class Healthbar:
    def __init__(self,bullets,enemies):
        self.texture = pygame.image.load(os.path.join("Assets","healthground.png"))
        self.health = pygame.image.load(os.path.join("Assets","health.png"))
        self.bullets = bullets
        self.enemies = enemies

    def change_health(self):
        for bullet in self.bullets:
            for enemy in self.enemies:
                if bullet.pos.colliderect(enemy.pos):
                        enemy.hp -= 10
                        self.bullets.remove(bullet)

    def is_dead(self):
        for enemy in self.enemies:
            if enemy.hp <= 0:
                self.enemies.remove(enemy)

    def draw_health(self):
        for enemy in self.enemies:
            Window.blit(self.texture,(enemy.pos.x -7,enemy.pos.y -7))
            self.health = pygame.transform.scale(self.health,(enemy.hp,3)) #change healthbar according to enemy.healh
            Window.blit(self.health,(enemy.pos.x -6,enemy.pos.y -6))

class Spawner:
    def __init__(self,enemies):
        self.enemies = enemies

    def spawn_enemy(self,pos):
        self.enemies += [Enemy(pos)]

class MainMenu():

    def draw(self):
        start = Button(pygame.Vector2(450,150),"christmasbutton.png",GameState)
        options = Button(pygame.Vector2(450,250),"options.png",OptionsMenu)
        exit = Button(pygame.Vector2(450,350),"exit.png",None)
        buttons = [start,options,exit]
        Window.fill(Black)
        for button in buttons:
            button.update_button()
            button.draw_button()

currState = MainMenu()
        
class GameState():

    def update(enemies,spawn,hp):
        for enemy in enemies:
            enemy.move()
        if len(enemies) == 0:
            spawn.spawn_enemy(Vector2(970,370))
            spawn.spawn_enemy(Vector2(970,270))
            spawn.spawn_enemy(Vector2(970,170))

        hp.change_health()
        hp.is_dead()

    def draw(square,hp,bullets,enemies):
        Window.fill(White)
        Window.blit(Background_Image, (0,0))
        mouse = font.render("Mouse: "+ str(pygame.mouse.get_pos()),1,White)
        Window.blit(mouse,(0,0))
        Window.blit(Square_Image,(square.x,square.y))
        for bullet in bullets:
            Window.blit(Snowball_Image,(bullet.getpos().x,bullet.getpos().y))
        for enemy in enemies:
            Window.blit(Skellet_Image,(enemy.get_pos().x,enemy.get_pos().y))
        if len(bullets)>0:
            for bullet in bullets:
                bullet.move()    
                bullet.remove_bullet()
        hp.draw_health()

class OptionsMenu():

    def draw():
        global slider_selected
        global slider_rect
        Window.fill(Black)
        Window.blit(Slider,(Vector2(365,100)))
        mouse_rect = pygame.Rect(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1],1,1)
        text = font.render("Game Volume",1,White)
        Window.blit(text,(430,50))
        if(mouse_rect.colliderect(pygame.Rect(slider_rect.x-5,slider_rect.y,slider_rect.width,slider_rect.height)) and pygame.mouse.get_pressed()[0]):
            slider_selected = True
        if slider_selected:
            if slider_rect.x >= 365 and slider_rect.x <= 594:
                slider_rect = pygame.Rect(mouse_rect.x,92,Slider_Head.get_width(),Slider_Head.get_height())
            if mouse_rect.x >= 370 and mouse_rect.x <= 590:
                slider_rect = pygame.Rect(mouse_rect.x,92,Slider_Head.get_width(),Slider_Head.get_height())
            if slider_rect.x < 365:
                slider_rect.x = 365
            if slider_rect.x > 594:
                slider_rect.x = 594
        if pygame.mouse.get_pressed()[0] == False:
            slider_selected = False
        Window.blit(Slider_Head,(slider_rect.x,slider_rect.y))

def game_loop():
    clock = pygame.time.Clock()
    square_purple = pygame.Rect(300,250,Square_Image.get_width(),Square_Image.get_height())
    mouse_pos = square_purple
    curr_mouse = pygame.mouse.get_pressed()
    bullets = []
    enemies = []
    spawn = Spawner(enemies)
    hp = Healthbar(bullets,enemies)
    while True:
        clock.tick(Fps)
        prev_mouse = curr_mouse
        curr_mouse = pygame.mouse.get_pressed()
        if not curr_mouse[2] and prev_mouse[2] and selected:
            mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
              if event.key == pygame.K_e and len(bullets)<5:
                bullet = Bullet(square_purple,pygame.mouse.get_pos(),bullets)
                bullet.setAngle()
                bullets += [bullet]
            if event.type == pygame.QUIT:
                pygame.quit()
      
        if currState == None:
            break
        if currState == GameState:
            currState.update(enemies,spawn,hp)
            movement(mouse_pos,square_purple)
            currState.draw(square_purple,hp,bullets,enemies)
        else:
            currState.draw()
    
        pygame.display.update()
        print(currState)
    pygame.quit()


if __name__ == "__main__":
    game_loop()