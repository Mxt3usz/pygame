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
in_pause = False
shoot = False
night = False
escape_count = 0
Black = (0,0,0)
day_night_timer = 0
clock_time = 0


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


class Bullet:
    def __init__(self,spos,mpos,bullets):
        self.texture = pygame.image.load(os.path.join("Assets","snowball.png"))
        self.spos = spos
        self.mpos = mpos
        self.vel = 6
        self.pos = pygame.Rect(spos.x + spos.width//2,spos.y + spos.height//2,15,15)
        self.direction = Vector2(mpos[0],mpos[1]) - Vector2(spos.x,spos.y)
        self.angle = math.atan2(self.direction.x,self.direction.y)
        self.bullets = bullets

    def move(self):
        self.pos.x += self.vel * math.sin(self.angle)
        self.pos.y += self.vel * math.cos(self.angle)

    def remove_bullet(self):
        try:
            if self.pos.x >= 1000 or self.pos.x <= 0:
                self.bullets.remove(self)
            if self.pos.y <= 0 or self.pos.y >= 600:
                self.bullets.remove(self)
        except:
            pass

    def update(self):
        self.move()
        self.remove_bullet()

    def draw(self):
          for bullet in self.bullets:
            Window.blit(self.texture,(bullet.pos.x,bullet.pos.y))

class Enemy:
    def __init__(self,pos,enemies,player_pos):
        self.texture = pygame.image.load(os.path.join("Assets","skellet.png"))
        self.pos = pygame.Rect(pos.x,pos.y,self.texture.get_width(),self.texture.get_height())
        self.vel = 2
        self.hp = 48
        self.enemies = enemies
        self.player_pos = player_pos

    def set_healthbar(self):
        healthbar = Healthbar(self)
        healthbar.draw_health()

    def get_pos(self):
        return Vector2(self.pos.x,self.pos.y)


    def move(self):
        """
        We determine distance between player and enemy and apply angle onto it,
        this makes the enemy follow the player.
        """
        direction = Vector2(self.player_pos.x,self.player_pos.y) - Vector2(self.pos.x,self.pos.y)
        angle = math.atan2(direction.x,direction.y)
        self.pos.x += self.vel * math.sin(angle)
        self.pos.y += self.vel * math.cos(angle)

    def is_dead(self):
        if self.hp <= 0:
            achievement_lst[3].condition += 1
            self.enemies.remove(self)

    def update(self):
        self.move()
        self.is_dead()

    def draw(self):
        if self.hp > 0:
            self.set_healthbar()
        Window.blit(self.texture,(self.pos.x,self.pos.y))


class Player:
    def __init__(self):
        self.texture = pygame.image.load(os.path.join("Assets","snowman_red.png"))
        self.pos = pygame.Rect(300,250,self.texture.get_width(),self.texture.get_height())
        self.vel = 10
        self.hp = 48
        self.dist = 0
        self.in_motion = False
        self.has_walked = False
        self.mouse_pos = self.pos
        self.curr_mouse_pressed = pygame.mouse.get_pressed()
        self.selected = False
    
    def get_pos(self):
        return self.pos

    def set_Healthbar(self):
        healthbar = Healthbar(self)
        healthbar.draw_health()

    def movement(self):
        """
        This method is repsonible for the movement of the snowman.
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
        prev_mouse_pressed = self.curr_mouse_pressed
        self.curr_mouse_pressed = pygame.mouse.get_pressed()
        if not self.curr_mouse_pressed[2] and prev_mouse_pressed[2] and self.selected:
            self.mouse_pos = pygame.mouse.get_pos()
        curr_mouse = pygame.mouse.get_pos()
        mouse_vec = Vector2(self.mouse_pos[0],self.mouse_pos[1])
        if self.has_walked:
            player_vec = Vector2(self.pos.x + self.texture.get_width()/2,self.pos.y + self.texture.get_height()/2)
        else:
            player_vec = Vector2(self.pos.x,self.pos.y)
        dist = Vector2.distance_to(mouse_vec,player_vec)
        direction = mouse_vec - player_vec
        angle = math.atan2(direction.x,direction.y)
        mouse_rect = pygame.Rect(curr_mouse[0],curr_mouse[1],1,1)
        if mouse_rect.colliderect(self.pos) and pygame.mouse.get_pressed()[0]:
            self.selected = True
        if mouse_rect.colliderect(self.pos) == False and pygame.mouse.get_pressed()[0] and self.in_motion == False:
            self.selected = False
        if dist > 5 and self.selected:
            self.pos.x += self.vel * math.sin(angle)
            self.pos.y += self.vel * math.cos(angle)
            self.has_walked = True
            self.in_motion = True
        if dist < 5:
            self.in_motion = False
    
    def draw(self):
        self.set_Healthbar()
        Window.blit(self.texture,(self.pos.x,self.pos.y))

class Healthbar:
    def __init__(self,gameobject):
        self.gameobject = gameobject
        self.texture = pygame.image.load(os.path.join("Assets","healthground.png"))
        self.healthtexture = pygame.transform.scale(pygame.image.load(os.path.join("Assets","health.png")),(gameobject.hp,3))
    
    def draw_health(self):
        if self.gameobject.__class__ == Player:
            Window.blit(self.texture,(self.gameobject.pos.x,self.gameobject.pos.y - 6))
            Window.blit(self.healthtexture,(self.gameobject.pos.x + 1,self.gameobject.pos.y - 5))
        else:
            Window.blit(self.texture,(self.gameobject.pos.x - 7,self.gameobject.pos.y - 7))
            Window.blit(self.healthtexture,(self.gameobject.pos.x - 6,self.gameobject.pos.y - 6)) #change healthbar according to enemy.health

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

    def __init__(self):
        self.Background_Image = pygame.transform.scale(pygame.image.load(os.path.join("Assets","snowbackground.png")),(1000,600)).convert()

    def update(self,gameobjectmanager):
        gameobjectmanager.update()
        
    def draw(self,gameobjectmanager):
        global currState
        global escape_count
        global night
        global day_night_timer
        global clock_time
        if escape_count % 2 != 0: # check also if ESC wasnt pressed so for example if options were entered
            currState = PauseMenu() # through pausemenu and back was pressed the pausemenu should still appear
        Window.blit(self.Background_Image, (0,0))
        if round(day_night_timer) == 20 or night: #20 secs day
            Window.fill(Black)
            if night == False:
                clock_time = 0
            night = True
        if night and round(day_night_timer) == 10: #10 secs night
            night = False
            clock_time = 0
        mouse = font.render("Mouse: "+ str(pygame.mouse.get_pos()),1,White)
        Window.blit(mouse,(0,0))
        gameobjectmanager.draw()
        achievement_unlocked()
        

class OptionsMenu():

    def __init__(self):
        self.Slider_Head = pygame.image.load(os.path.join("Assets","sliderheadred.png"))
        self.Slider = pygame.image.load(os.path.join("Assets","sliderred.png"))
        self.slider_selected = False
        self.slider_rect = pygame.Rect(594,92,self.Slider_Head.get_width(),self.Slider_Head.get_height())

    def draw(self):
        Window.fill(Black)
        Window.blit(self.Slider,(Vector2(365,100)))
        back = Button(pygame.Vector2(450,500),"backbutton.png",MainMenu())
        if in_pause:
            back = Button(pygame.Vector2(450,500),"backbutton.png",GameState())
        back.update_button()
        back.draw_button()
        mouse_rect = pygame.Rect(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1],1,1)
        text = font.render("Game Volume",1,White)
        Window.blit(text,(430,50))
        if(mouse_rect.colliderect(pygame.Rect(self.slider_rect.x-5,self.slider_rect.y,self.slider_rect.width,self.slider_rect.height)) and pygame.mouse.get_pressed()[0]):
            self.slider_selected = True
        if self.slider_selected:
            if self.slider_rect.x >= 365 and self.slider_rect.x <= 594:
                self.slider_rect = pygame.Rect(mouse_rect.x,92,self.Slider_Head.get_width(),self.Slider_Head.get_height())
            if mouse_rect.x >= 370 and mouse_rect.x <= 590:
                self.slider_rect = pygame.Rect(mouse_rect.x,92,self.Slider_Head.get_width(),self.Slider_Head.get_height())
            if self.slider_rect.x < 365:
                self.slider_rect.x = 365
            if self.slider_rect.x > 594:
                self.slider_rect.x = 594
        if pygame.mouse.get_pressed()[0] == False:
            self.slider_selected = False
        Window.blit(self.Slider_Head,(self.slider_rect.x,self.slider_rect.y))


class AchievementMenu():

    def draw(self):
        Window.fill(Black)
        Window.blit(pygame.transform.scale(pygame.image.load(os.path.join("Assets","infoground.png")),(900,80)),(50,0))
        Window.blit(pygame.transform.scale(pygame.image.load(os.path.join("Assets","achievementbar.png")),(225,10)),(650,40))
        Window.blit(pygame.transform.scale(pygame.image.load(os.path.join("Assets","achievementfilled.png")),(225*((collected_achievements()/0.04)/100),10)),(650,40))
        Window.blit(font.render(str(collected_achievements()) + " out of 4 " +"Achievements unlocked",1,White),(590,10))
        Window.blit(font.render(str(collected_achievements()/0.04)+ "%",1,White),(885,35))
        Window.blit(font.render("Total play time : " + str(math.floor((achievement_lst[0].condition/60))/100)+" h",1,White),(50,10))
        back = Button(pygame.Vector2(450,550),"backbutton.png",MainMenu())
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
    now = datetime.datetime.now()
    for achievement in achievement_lst:
        if achievement.date == "":
            if achievement.name == "Never Ending Fun" and achievement.condition >= 60:
                achievement.date = now.strftime("%y-%m-%d %H:%M:%S")
            if achievement.name == "Marathon" and achievement.condition >= 1000:
                achievement.date = now.strftime("%y-%m-%d %H:%M:%S")
            if achievement.name == "Oppressor" and achievement.condition == 50:
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
    count = 0
    for achievement in achievement_lst:
        if achievement.date != "":
            count += 1
    return count

"""
AchievementGlobals
"""
curr_pos = Vector2(300,250)
achievement_lst = [AchievementCreator("hourglassLockedD.png","hourglassS.png",Vector2(100,150),0,"",100,"Never Ending Fun","Play for 1 minute."),AchievementCreator("olympiclocked.png","olympic.png",Vector2(100,250),0,"",100,"Marathon","Walk for 1000 meters.")
,AchievementCreator("moonlocked.png","moon.png",Vector2(100,350),0,"",100,"Survivor","Survive 3 nights."),AchievementCreator("skelletheadlocked.png","skelletevil.png",Vector2(100,450),0,"",100,"Oppressor","Kill 50 skelletons.")]

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


class Gameobjectmanager():
    """
    Handles all the methods from the objects in the game.
    """
    def __init__(self):
        self.bulletlist = []
        self.player = Player()
        self.enemylist = []


    def spawn_enemy(self,pos):
        enemy = Enemy(pos,self.enemylist,self.player.get_pos())
        self.enemylist += [enemy]

    def spawn_bullet(self):
        global shoot
        if shoot and len(self.bulletlist) < 5:
            self.bulletlist += [Bullet(self.player.get_pos(),pygame.mouse.get_pos(),self.bulletlist)]
            shoot = False

    def handle_collision(self):
        """
        The enemies have to keep a certain distance between eachother.
        """
        for enemy in range(len(self.enemylist)):
            if enemy + 1 < len(self.enemylist):
                if Vector2.distance_to(self.enemylist[enemy].get_pos(),self.enemylist[enemy+1].get_pos()) < 90:
                    self.enemylist[enemy].pos.x += 1 # <- magical force
                    self.enemylist[enemy+1].pos.x -= 1

    def handle_bullet_enemy_collision(self):
        for bullet in self.bulletlist:
            for enemy in self.enemylist:
                if bullet.pos.colliderect(enemy.pos):
                    enemy.hp -= 10
                    try:
                        self.bulletlist.remove(bullet)
                    except:
                        pass

    def update(self):
        global night
        global day_night_timer
        self.spawn_bullet()
        self.player.movement()
        calc_meters_walked(self.player.get_pos())
        for bullet in self.bulletlist:
            bullet.update()
        for enemy in self.enemylist:
            enemy.update()
        self.handle_collision()
        self.handle_bullet_enemy_collision()
        """
        At day spawns every 6 secs one Wave so in total 4 Waves
        """
        if night == False and len(self.enemylist) < 3 and round(day_night_timer) % 6 == 0:
            self.spawn_enemy(Vector2(970,370))
            self.spawn_enemy(Vector2(970,270))
            self.spawn_enemy(Vector2(970,170))
        
        """
        At Night spawns every 4 secs one Wave so in total 3 Waves
        """
        if night and round(day_night_timer) % 4 == 0 and len(self.enemylist) < 4:
            # spawn left
            self.spawn_enemy(Vector2(170,170))
            # spawn right
            self.spawn_enemy(Vector2(970,370))
            # spawn top
            self.spawn_enemy(Vector2(370,0))
            # spawn bottom
            self.spawn_enemy(Vector2(670,600))

    def draw(self):
        self.player.draw()
        for enemy in self.enemylist:
            enemy.draw()
        for bullet in self.bulletlist:
            bullet.draw()

def game_loop():
    """
    Simple game loop which handles keyboard input and in which state the player currently is.
    """
    clock = pygame.time.Clock()
    gameobjectmanager = Gameobjectmanager()
    global currState
    global escape_count
    global in_pause
    global shoot
    start_time = 0
    load_achievements()
    while True:
        clock.tick(Fps)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
              if event.key == pygame.K_e:
                  shoot = True
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
            save_achievements()
            break
        if currState.__class__ == GameState:
            """
            start_time is total time, clock time is time played (not saved)
            """
            global clock_time
            if start_time == 0:
                start_time = time.time()
            if clock_time == 0:
                clock_time = time.time()
            achievement_lst[0].condition = time.time() - start_time
            global day_night_timer
            day_night_timer = time.time() - clock_time
            currState.update(gameobjectmanager)
            currState.draw(gameobjectmanager)
        else:
            start_time = time.time() - achievement_lst[0].condition
            clock_time = time.time() - day_night_timer
            currState.draw()
        pygame.display.update()
        
    pygame.quit()


def save_achievements():
    """
    Goes through the achievement list and saves all important infos
    in a .txt file separated by ,
    """
    with open("achievementsinfo.txt","w") as file:
        for achievement in achievement_lst:
            file.write("," + str(achievement.condition) + "," + achievement.date + "," + str(achievement.health))
        file.close()


def load_achievements():
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
        pass
        

if __name__ == "__main__":
    game_loop()