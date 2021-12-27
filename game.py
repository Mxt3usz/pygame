import os
import pygame
import time
pygame.font.init()
import math
from pygame import Vector2
import datetime
Width, Height = 1000,600
Window = pygame.display.set_mode((Width,Height))
pygame.display.set_caption("First PyGame")
White = (255,255,255)
Red = (255,0,0)
Fps = 60
font = pygame.font.Font("upheavtt.ttf",20)
selected = False
buttonDown_Right = False
buttonDown_Left = False
has_walked = False
slider_selected = False
in_pause = False
in_motion = False
escape_count = 0
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
        self.string = string
        self.mouse = pygame.Rect(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1],1,1)
        self.mouse_pressed = pygame.mouse.get_pressed()
        self.state = state

    def update_button(self):
        global currState
        if self.pos.colliderect(self.mouse):
            self.texture.set_alpha(75) # hover effect
            if self.mouse_pressed[0]:
                currState = self.state
                if self.string == "resume.png": # count also escape count if resume was pressed
                    global escape_count
                    escape_count += 1
                if self.string == "menubutton.png":
                    global in_pause
                    in_pause = False
                    escape_count += 1
        
    def draw_button(self):
        Window.blit(self.texture,self.pos)

def movement(mouse_pos,square_purple):

    """
    This function is repsonible for the movement of the snowman.
    The has_walked is there so we dont move the snowman by clicking him
    at the first time, the offset has to be counted to his pos because otherwise
    he doesnt move to the center of the mouse but to the upper left.
    The direction is calculated by comparing the current mouse with the current
    snowman pos by also considering the angle. The selected bool keeps track of when
    the snowman is able to move, if the mouse rect collides with the snowmans rect
    and the left mouse button is clicked the snowman is selected, only then 
    he is able to move if the right mouse button was pressed. Note that you only
    can deselect the snowman if he isnt moving rn, deselecting means stopping the current
    move operation so if you would try to reselect the snowman he would try to move to the 
    direction you sent him to before.
    """
    global selected
    global has_walked
    global in_motion
    speed = 10
    dist = 0
    curr_mouse = pygame.mouse.get_pos()
    mouse_vec = Vector2(mouse_pos[0],mouse_pos[1])
    if has_walked:
        square_vec = Vector2(square_purple.x+Square_Image.get_width()//2,square_purple.y+Square_Image.get_height()//2)

    else:
        square_vec = Vector2(square_purple.x,square_purple.y)
    dist = Vector2.distance_to(mouse_vec,square_vec)
    direction = mouse_vec - square_vec
    angle = math.atan2(direction.x,direction.y)
    mouse_rect = pygame.Rect(curr_mouse[0],curr_mouse[1],1,1)

    if mouse_rect.colliderect(square_purple) and pygame.mouse.get_pressed()[0]:
        selected = True

    if mouse_rect.colliderect(square_purple) == False and  pygame.mouse.get_pressed()[0] and in_motion == False:
        selected = False

    if dist > 5 and selected:
        square_purple.x += speed * math.sin(angle)
        square_purple.y += speed * math.cos(angle)
        has_walked = True
        in_motion = True
    if dist < 5:
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
        global achievement_lst
        for enemy in self.enemies:
            if enemy.hp <= 0:
                achievement_lst[3].condition += 1
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
        start = Button(pygame.Vector2(450,150),"christmasbutton.png",GameState())
        options = Button(pygame.Vector2(450,250),"options.png",OptionsMenu())
        achievement = Button(pygame.Vector2(450,350),"achievements.png",AchievementMenu())
        exit = Button(pygame.Vector2(450,450),"exit.png",None)
        buttons = [start,options,achievement,exit]
        Window.fill(Black)
        for button in buttons:
            button.update_button()
            button.draw_button()

currState = MainMenu()
        
class GameState():

    def update(self,enemies,spawn,hp):
        for enemy in enemies:
            enemy.move()
        if len(enemies) == 0:
            spawn.spawn_enemy(Vector2(970,370))
            spawn.spawn_enemy(Vector2(970,270))
            spawn.spawn_enemy(Vector2(970,170))

        hp.change_health()
        hp.is_dead()

    def draw(self,square,hp,bullets,enemies):
        global currState
        global escape_count
        if escape_count % 2 != 0: # check also if ESC wasnt pressed so for example if options were entered
            currState = PauseMenu() # through pausemenu and back was pressed the pausemenu should still appear
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

    def draw(self):
        global slider_selected
        global slider_rect
        Window.fill(Black)
        Window.blit(Slider,(Vector2(365,100)))
        back = Button(pygame.Vector2(450,500),"backbutton.png",MainMenu())
        if in_pause:
            back = Button(pygame.Vector2(450,500),"backbutton.png",GameState())
        back.update_button()
        back.draw_button()
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


class AchievementMenu():

    global achievement_lst
    def draw(self):
        Window.fill(Black)
        Window.blit(pygame.transform.scale(pygame.image.load(os.path.join("Assets","infoground.png")),(900,80)),(50,0))
        Window.blit(pygame.transform.scale(pygame.image.load(os.path.join("Assets","achievementbar.png")),(225,10)),(650,40))
        Window.blit(pygame.transform.scale(pygame.image.load(os.path.join("Assets","achievementfilled.png")),(225*((collected_achievements()/0.04)/100),10)),(650,40))
        Window.blit(font.render(str(collected_achievements()) + " out of 4 " +"Achievements unlocked",1,White),(590,10))
        Window.blit(font.render(str(collected_achievements()/0.04)+ "%",1,White),(885,35))
        Window.blit(font.render("Total play time : " + str(math.floor((achievement_lst[0].condition/60))/100)+" h",1,White),(50,10))
        back = Button(pygame.Vector2(0,550),"backbutton.png",MainMenu())
        back.update_button()
        back.draw_button()
        for achievement in achievement_lst:
            achievement.draw()
        

class AchievementCreator():

    def __init__(self,stringlocked,string,pos,condition,date,health,name,summary):
        self.stringlocked = stringlocked
        self.string = string
        self.pos = pos
        self.condition = condition
        self.date = date
        self.health = health
        self.textground = pygame.transform.scale(pygame.image.load(os.path.join("Assets","textground.png")),(750,40))
        self.name = name
        self.summary = font.render(summary,1,White)

    def draw(self):
        if self.date == "":
            self.texture = pygame.transform.scale(pygame.image.load(os.path.join("Assets",self.stringlocked)),(50,50))
        if self.date != "":
            self.texture = pygame.transform.scale(pygame.image.load(os.path.join("Assets",self.string)),(50,50))
      
        Window.blit(self.texture,self.pos)
        Window.blit(self.textground,(self.pos.x + 60,self.pos.y + 5))
        Window.blit(font.render(self.name,1,White),(self.pos.x + 80,self.pos.y +5))
        Window.blit(self.summary,(self.pos.x + 80,self.pos.y + 25))
        Window.blit(font.render(self.date,1,White),(self.pos.x + 600,self.pos.y + 15))

def calc_meters_walked(new_pos):
   
    """
    This function calculates the meters walked by the snowman
    everytime the snowman moves we look at his position,
    if this position doesnt correlate to
    the current pos we can say that he moved and we can calculate
    the distance between these Vector2's. If the new pos x and y coordinates
    are bigger than the current coordinates we just make the distance positive
    again because there cant be a negative distance. At the end we set the
    new pos to the current pos.
    """
    global curr_pos
    global achievement_lst
    distance = Vector2(0,0)
    if curr_pos != Vector2(new_pos.x,new_pos.y):
        distance = curr_pos - Vector2(new_pos.x,new_pos.y)
        if curr_pos.x < new_pos.x:
            distance.x *= -1
        if curr_pos.y < new_pos.y:
            distance.y *= -1
        curr_pos = Vector2(new_pos.x,new_pos.y)
        achievement_lst[1].condition += (distance.x + distance.y) / 100

def achievement_unlocked():
    global achievement_lst
    now = datetime.datetime.now()
    for achievement in achievement_lst:
        if achievement.date == "":
            if achievement.name == "Never Ending Fun" and achievement.condition >= 60:
                achievement.date = now.strftime("%y-%m-%d %H:%M:%S")
            if achievement.name == "Marathon" and achievement.condition >= 1000:
                achievement.date = now.strftime("%y-%m-%d %H:%M:%S")
            if achievement.name == "Oppressor" and achievement.condition == 10:
                achievement.date = now.strftime("%y-%m-%d %H:%M:%S")
        else:
            if achievement.health > 0:
                achievement_unlocked_draw(achievement)

def achievement_unlocked_draw(achievement):
        offset = (450,380)
        if achievement.name == "Never Ending Fun":
            offset = (420,380)
        Window.blit(font.render("Achievement",1,White),(440,450))
        Window.blit(font.render(achievement.name,1,White),offset)
        Window.blit(pygame.transform.scale(pygame.image.load(os.path.join("Assets",achievement.string)),(50,50)),(475,400))
        achievement.health -= 1

def collected_achievements():
    global achievement_lst
    count = 0
    for achievement in achievement_lst:
        if achievement.date != "":
            count += 1
    return count

"""
AchievementGlobals
"""
curr_pos = Vector2(300,250)
achievement_lst = [AchievementCreator("hourglassLockedD.png","hourglassS.png",Vector2(100,150),0,"",100,"Never Ending Fun","Play for 1 minute."),AchievementCreator("olympiclocked.png","olympic.png",Vector2(100,250),0,"",100,"Marathon","Walk for 100 meters.")
,AchievementCreator("moonlocked.png","moon.png",Vector2(100,350),0,"",100,"Survivor","Survive 3 nights."),AchievementCreator("skelletheadlocked.png","skelletevil.png",Vector2(100,450),0,"",100,"Oppressor","Kill 10 skelletons.")]

class PauseMenu():

    def draw(self):
        Window.blit(pygame.image.load(os.path.join("Assets","pause.png")),(350,50))
        resume = Button(pygame.Vector2(450,200),"resume.png",GameState())
        options = Button(pygame.Vector2(450,300),"options.png",OptionsMenu())
        menu = Button(pygame.Vector2(450,400),"menubutton.png",MainMenu())
        lst = [resume,options,menu]
        for button in lst:
            button.update_button()
            button.draw_button()

def game_loop():
    """
    Simple game loop which handles keyboard input and in which state the player currently is.
    """
    clock = pygame.time.Clock()
    square_purple = pygame.Rect(300,250,Square_Image.get_width(),Square_Image.get_height())
    mouse_pos = square_purple
    curr_mouse = pygame.mouse.get_pressed()
    bullets = []
    enemies = []
    spawn = Spawner(enemies)
    hp = Healthbar(bullets,enemies)
    global currState
    global escape_count
    global in_pause
    global achievement_lst
    start_time = 0
    load_achievements(achievement_lst)
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
              if event.key == pygame.K_ESCAPE and (currState.__class__ == GameState or currState.__class__ == PauseMenu): # switch to PauseMenu if ESC pressed
                  escape_count += 1
                  if escape_count % 2 == 0: # if escape pressed again switch to GameState again
                      currState = GameState()
                      in_pause = False
                  else:
                    currState = PauseMenu() 
                    in_pause = True
            if event.type == pygame.QUIT:
                currState = None
        if currState == None:
            save_achievements(achievement_lst)
            break
        if currState.__class__ == GameState:
            if start_time == 0:
                start_time = time.time()
            achievement_lst[0].condition = time.time() - start_time
            currState.update(enemies,spawn,hp)
            movement(mouse_pos,square_purple)
            calc_meters_walked(square_purple)
            currState.draw(square_purple,hp,bullets,enemies)
            achievement_unlocked()
        else:
            start_time = time.time() - achievement_lst[0].condition
            currState.draw()
        pygame.display.update()
    pygame.quit()


def save_achievements(achievement_lst):
    """
    Goes through the achievement list and saves all important infos
    in a .txt file separated by ,
    """
    with open("achievementsinfo.txt","w") as file:
        for achievement in achievement_lst:
            file.write("," + str(achievement.condition) + "," + achievement.date + "," + str(achievement.health))
        file.close()



def load_achievements(achievement_lst):
    """
    After saving the achievement infos we can retrieve them with the load function.
    Herefor we go through the .txt file and split the line whenever there is a , and we put it into a list.
    After we put all relevant infos in the list we go through it and assign the indexes
    to the correlating achievement attributes, we use the fact that every achievement has 3 attributes to our advantage.
    The curr_achievement counter keeps track of which achievement we are overwriting rn.
    """
    curr_achievement = 0
    try:
        with open("achievementsinfo.txt","r") as file:
            for line in file:
                split_comma = line.split(",")
                    
            for info in range(1,len(split_comma)): #start from 1 because at index 0 is ","
                if info % 3 == 0:
                    achievement_lst[curr_achievement].health = int(split_comma[info])
                    achievement_lst[curr_achievement].date = split_comma[info-1]
                    achievement_lst[curr_achievement].condition = float(split_comma[info-2])
                    curr_achievement += 1
            file.close()
    except:
        file.close()
        


if __name__ == "__main__":
    game_loop()