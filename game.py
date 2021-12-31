import os
import pygame
pygame.init()
import time
pygame.font.init()
import math
from pygame import Vector2
import datetime
from pygame import mixer
Width, Height = 1000,600
Window = pygame.display.set_mode((Width,Height))
pygame.display.set_caption("First PyGame")
White = (255,255,255)
Red = (255,0,0)
Fps = 60
font = pygame.font.Font("upheavtt.ttf",20)
game_over_font = pygame.font.Font("upheavtt.ttf",60)
score_font = pygame.font.Font("upheavtt.ttf",40)
in_pause = False
shoot = False
night = False
escape_count = 0
Black = (0,0,0)
day_night_timer = 0
clock_time = 0
actual_time = 0
background_music = mixer.music.load(os.path.join("Music","day_music.mp3"))
paused = False
day_music_time_played = 0
night_music_time_played = 0
hover_sound = mixer.Sound(os.path.join("Music","menu.wav"))
hit_sound = mixer.Sound(os.path.join("Music","hit.wav"))
shoot_sound = mixer.Sound(os.path.join("Music","shoot.wav"))
gameobjectmanager = None

class Button():

    def __init__(self,pos,string,state):
        self.texture = pygame.image.load(os.path.join("Assets",string))
        self.pos = pygame.Rect(pos.x,pos.y,self.texture.get_width(),self.texture.get_height())
        self.string = string
        self.state = state
        self.played = False

    def update_button(self):
        global currState
        if self.pos.colliderect(pygame.Rect(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1],1,1)):
            global hover_sound
            if self.played == False:
                hover_sound.play()
                self.played = True
            self.texture.set_alpha(75) # hover effect
            if pygame.mouse.get_pressed()[0]:
                if currState.__class__ == GameOver:
                    global escape_count
                    escape_count -= 1
                    global gameobjectmanager
                    gameobjectmanager = Gameobjectmanager() #reset game if game over
                    global background_music
                    global day_music_time_played
                    global night_music_time_played
                    global curr_scores
                    global day_night_timer
                    global night 
                    night = False
                    day_night_timer = 0
                    day_music_time_played = 0
                    night_music_time_played = 0
                    background_music = mixer.music.rewind()
                    curr_scores = [0,0,0,0]
                if self.state != None:
                    currState = eval(self.state)# when button pressed change state
                else:
                    currState = self.state
                if self.string == "resume.png": # count also escape count if resume was pressed
                    escape_count += 1
                if self.string == "menubutton.png":
                    global in_pause
                    in_pause = False
                    escape_count += 1
        else:
            self.texture.set_alpha(300)
            self.played = False
        
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
        """
        Remvoes bullet if its not inside the game screen.
        """
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
        self.healthbar = Healthbar(self)

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
            curr_scores[3] += 1
            self.enemies.remove(self)

    def update(self):
        self.move()
        self.is_dead()

    def draw(self):
        self.healthbar.draw_health()
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
        self.attacked = False
        self.invincibility = 0
        self.healthbar = Healthbar(self)
    
    def get_pos(self):
        return self.pos

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
        if self.attacked == True:
            self.invincibility += 1
        if self.invincibility == 30:
            self.attacked = False
            self.invincibility = 0
        self.healthbar.draw_health()
        Window.blit(self.texture,(self.pos.x,self.pos.y))

class Healthbar:
    def __init__(self,gameobject):
        self.gameobject = gameobject
        self.texture = pygame.image.load(os.path.join("Assets","healthground.png"))
        self.healthtexture = pygame.image.load(os.path.join("Assets","health.png"))
    
    def draw_health(self):
        if self.gameobject.hp > 0:
            if self.gameobject.__class__ == Player:
                Window.blit(self.texture,(self.gameobject.pos.x,self.gameobject.pos.y - 6))
                Window.blit(pygame.transform.scale(self.healthtexture,(self.gameobject.hp,3)),(self.gameobject.pos.x + 1,self.gameobject.pos.y - 5))
            else:
                Window.blit(self.texture,(self.gameobject.pos.x - 7,self.gameobject.pos.y - 7))
                Window.blit(pygame.transform.scale(self.healthtexture,(self.gameobject.hp,3)),(self.gameobject.pos.x - 6,self.gameobject.pos.y - 6)) #change healthbar according to enemy.health

    
class GameState():

    def __init__(self):
        self.Background_Image = pygame.transform.scale(pygame.image.load(os.path.join("Assets","snowbackground.png")),(1000,600)).convert()
        self.set_volume()

    def set_volume(self):
        try:
            with open("sliderinfo.txt","r") as file:
                for info in file:
                    comma_split = info.split(",")
                    global background_music
                    global hit_sound
                    global shoot_sound
                    background_music = mixer.music.set_volume((int(comma_split[0])-360)/250)
                    hit_sound.set_volume((int(comma_split[1])-360)/250)
                    shoot_sound.set_volume((int(comma_split[1])-360)/250)
                file.close()
        except:
            pass

    def update(self,gameobjectmanager):
        gameobjectmanager.update()
        
    def draw(self,gameobjectmanager):
        """
        If its day the day music is played before we switch to night music, we
        save the day music pos so if its day again we dont start from begin, same
        for the night. If the pos we get is bigger than the actual length of the mp3
        we set the time_played = 0.
        """
        global currState
        global escape_count
        global night
        global day_night_timer
        global clock_time
        global day_music_time_played
        global night_music_time_played
        if escape_count % 2 != 0: # check also if ESC wasnt pressed so for example if options were entered
            currState = PauseMenu() # through pausemenu and back was pressed the pausemenu should still appear
        Window.blit(self.Background_Image, (0,0))
        if round(day_night_timer) == 20 or night: #20 secs day
            Window.fill(Black)
            if night == False:
                clock_time = 0
                global background_music
                day_music_time_played += mixer.music.get_pos()
                background_music = mixer.music.load(os.path.join("Music","night_music.mp3"))
                try:
                    background_music = mixer.music.play(-1,night_music_time_played/1000)
                except:
                    night_music_time_played = 0
                    background_music = mixer.music.play(-1,night_music_time_played/1000)
            night = True
        if night and round(day_night_timer) == 10: #10 secs night
            night = False
            achievement_lst[2].condition += 1
            curr_scores[2] += 1
            clock_time = 0
            night_music_time_played += mixer.music.get_pos()
            background_music = mixer.music.load(os.path.join("Music","day_music.mp3"))
            try:
                background_music = mixer.music.play(-1,day_music_time_played/1000)
            except:
                day_music_time_played = 0
                background_music = mixer.music.play(-1,day_music_time_played)
        mouse = font.render("Mouse: "+ str(pygame.mouse.get_pos()),1,White)
        Window.blit(mouse,(0,0))
        gameobjectmanager.draw()
        achievement_unlocked()
        

class SliderHandler():
    def __init__(self,pos,pos_slider,title,textpos,percentpos):
        self.Slider_Head = pygame.image.load(os.path.join("Assets","head.png"))
        self.Slider = pygame.image.load(os.path.join("Assets","sliderred.png"))
        self.slider_selected = False
        self.pos = pos
        self.pos_slider = pos_slider
        self.title = title
        self.textpos = textpos
        self.percentpos = percentpos
        self.slider_rect = pygame.Rect(pos.x,pos.y,self.Slider_Head.get_width(),self.Slider_Head.get_height())
     
    def draw(self):
        Window.blit(self.Slider,self.pos_slider)
        mouse_rect = pygame.Rect(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1],1,1)
        text = font.render(self.title,1,White)
        """
        To get percentage from 0 to 100 we have to make x pos 0 so x pos - 360,
        by subtracting start and end we get 100% so 610 - 360 = 250.
        To get percentage we just divide through 250.
        """
        percentage = round(((self.slider_rect.x-360) / 250)*100)
        percent = font.render(str(percentage) + "%",1,White)
        Window.blit(text,self.textpos)
        Window.blit(percent,self.percentpos)
        if(mouse_rect.colliderect(pygame.Rect(self.slider_rect.x,self.slider_rect.y,self.slider_rect.width,self.slider_rect.height)) and pygame.mouse.get_pressed()[0]):
            self.slider_selected = True
        if self.slider_selected:
            """
            Distance check is needed because otherwise you can move slider head
            by clicking it, but we want it only to move when its being dragged.
            If distance > slider head with its being dragged.
            """                                                                              #mid of slider head
            if Vector2.distance_to(Vector2(mouse_rect.x,mouse_rect.y),Vector2(self.slider_rect.x+5,self.slider_rect.y+5)) > 7:
                #some offsets so the slider works more precise
                if mouse_rect.x > self.slider_rect.x:
                    self.slider_rect = pygame.Rect(mouse_rect.x-11,self.slider_rect.y,self.Slider_Head.get_width(),self.Slider_Head.get_height())
                else:
                    self.slider_rect = pygame.Rect(mouse_rect.x,self.slider_rect.y,self.Slider_Head.get_width(),self.Slider_Head.get_height())
            
            """
            Prevents slider head from exiting slider.
            """
            if self.slider_rect.x < 360:
                self.slider_rect.x = 360
            if self.slider_rect.x > 610:
                self.slider_rect.x = 610
            
        if pygame.mouse.get_pressed()[0] == False:
            self.slider_selected = False
        Window.blit(self.Slider_Head,(self.slider_rect.x,self.slider_rect.y))

class OptionsMenu():

    def __init__(self):
        self.back = Button(Vector2(450,500),"backbutton.png","MainMenu()")
        if in_pause:
            self.back = Button(Vector2(450,500),"backbutton.png","GameState()")
        self.game_volume = SliderHandler(Vector2(610,97),Vector2(365,100),"Game Volume",Vector2(430,50),Vector2(630,90))
        self.effect_volume = SliderHandler(Vector2(610,197),Vector2(365,200),"Effect Volume",Vector2(430,150),Vector2(630,190))
        self.ui_volume = SliderHandler(Vector2(610,297),Vector2(365,300),"UI Volume",Vector2(430,250),Vector2(630,290))
        self.load_slider_pos()

    def save_slider_pos(self):
        with open("sliderinfo.txt","w") as file:
            file.write(str(self.game_volume.slider_rect.x) + "," + str(self.effect_volume.slider_rect.x) + "," + str(self.ui_volume.slider_rect.x))
            global hover_sound
            hover_sound.set_volume((self.ui_volume.slider_rect.x-360)/250)
            file.close()

    def load_slider_pos(self):
        try:
            with open("sliderinfo.txt","r") as file:
                for info in file:
                    comma_split = info.split(",")
                    self.game_volume.slider_rect.x = int(comma_split[0])
                    self.effect_volume.slider_rect.x = int(comma_split[1])
                    self.ui_volume.slider_rect.x = int(comma_split[2])
                file.close()
        except:
            pass

    def draw(self):
        global paused
        Window.fill(Black)
        if in_pause:
            paused = False # we set paused to false because otherwise it would play the music
                           # for a half second because we switch to GameState and not to PauseMenu
        self.back.update_button()
        self.back.draw_button()
        self.game_volume.draw()
        self.effect_volume.draw()
        self.ui_volume.draw()
        self.save_slider_pos()

class AchievementMenu():
    def __init__(self):
        self.back = Button(Vector2(450,550),"backbutton.png","MainMenu()")

    def draw(self):
        Window.fill(Black)
        Window.blit(pygame.transform.scale(pygame.image.load(os.path.join("Assets","infoground.png")),(900,80)),(50,0))
        Window.blit(pygame.transform.scale(pygame.image.load(os.path.join("Assets","achievementbar.png")),(225,10)),(650,40))
        Window.blit(pygame.transform.scale(pygame.image.load(os.path.join("Assets","achievementfilled.png")),(225*((collected_achievements()/0.04)/100),10)),(650,40))
        Window.blit(font.render(str(collected_achievements()) + " out of 4 " +"Achievements unlocked",1,White),(590,10))
        Window.blit(font.render(str(collected_achievements()/0.04)+ "%",1,White),(885,35))
        Window.blit(font.render("Total play time : " + str(math.floor((achievement_lst[0].condition/60))/100)+" h",1,White),(50,10))
        self.back.update_button()
        self.back.draw_button()
        for achievement in achievement_lst:
            achievement.draw()

class PauseMenu():
    def __init__(self):
        self.resume = Button(Vector2(450,220),"resume.png","GameState()")
        self.options = Button(Vector2(450,300),"options.png","OptionsMenu()")
        self.menu = Button(Vector2(450,380),"menubutton.png","MainMenu()")

    def draw(self):
        Window.blit(pygame.image.load(os.path.join("Assets","pause.png")),(350,50))
        lst = [self.resume,self.options,self.menu]
        for button in lst:
            button.update_button()
            button.draw_button()  


class StatsMenu():
    def __init__(self):
        self.back = Button(Vector2(450,560),"backbutton.png","MainMenu()")
        self.stats = []
        self.load_statistics()
    
    def load_statistics(self):
        try:
            with open("statistics_sorted.txt","r") as file:
                for listobj in file:
                    comma_split = listobj.split(":")
                    for lists in comma_split:
                        self.stats += [eval(lists)]
        except:
            pass
            
    def draw(self):
        Window.fill(Black)
        self.back.update_button()
        self.back.draw_button()
        offset = 30
        Window.blit(font.render("Time survived     Meters walked      Nights survived      Skellets killed      Total score",1,White),(30,offset))
        for info in range(len(self.stats)):
            offset += 50 #29
            Window.blit(font.render(self.stats[info][0],1,White),(30,offset))
            Window.blit(font.render(self.stats[info][1],1,White),(215,offset))
            Window.blit(font.render(self.stats[info][2],1,White),(412,offset))
            Window.blit(font.render(self.stats[info][3],1,White),(626,offset))
            Window.blit(font.render(self.stats[info][4],1,White),(843,offset))
        offset = 50

class GameOver():
    """
    After the game is lost we savedthe collected score.
    """
    def __init__(self):
        self.main_menu = Button(pygame.Vector2(455,480),"menubutton.png","MainMenu()")
        self.score = round(curr_scores[2]*(curr_scores[0]*(curr_scores[1] + curr_scores[3])))
        if self.score == 0:
            self.score = round(curr_scores[0]*(curr_scores[1] + curr_scores[3]))
        self.save_statistics()
        self.sort_statistics() 
        
    def save_statistics(self):
        with open("statistics.txt","a") as file:
            file.write(str(round(curr_scores[0])) + "," + str(round(curr_scores[1])) + "," + str(curr_scores[2]) + "," + str(curr_scores[3]) + "," + str(self.score) +"\n")
            file.close()

    def sort_statistics(self):
        """
        So first we go through the unsorted .txt and collect the lists in collect_stats.
        To sort the actual lists in collect_stats we first sort the scores.
        After we sorted the scores descending, we first check if the sorted list is bigger than 10
        if yes we cut it to 10, so we just get the top 10 scores.
        After that we can simply go through the sorted score list and the unsorted collect_stats containing the list with the stats.
        Because the scores are already sorted, we simple check if the iterating score argument equals the score in the unsorted list at index [4],
        if yes we add it to sorted_collect_stats hereby we can simple sort the lists by their scores descending.
        After this we write the newly gathered sorted lists into a new .txt and load it everytime we go into the StatsMenu.
        """
        collect_stats = []
        scores = []
        sorted_collect_stats = []
        num_without_newline = ""
        with open("statistics.txt","r") as file:
            for stat in file:
                comma_split = stat.split(",")
                for number in comma_split[4]:
                    if number != "\n":
                        num_without_newline += number
                comma_split[4] = num_without_newline
                scores += [num_without_newline]
                num_without_newline = ""
                collect_stats += [comma_split]
            for num in range(len(scores)):
                for num2 in range(len(scores)):
                    if int(scores[num]) > int(scores[num2]):
                        scores[num],scores[num2] = scores[num2],scores[num]
            if len(scores) > 10:
                scores = scores[:10]
            for score in scores:
                for stat in range(len(collect_stats)):
                    """
                    We only add 1 score for every loop. We check first for the identical score then also if the attribtues correlating to the score
                    are not in the sorted list, if no we can savely add this score to the list. It can happen that in top 10 are same scores with same attributes.
                    So lets say one score with 178 is already added with its attributes to sorted list. The second score with 178 would not land
                    in the first if but in the second if. This would be true because score already in sorted and attributes,result is saved in a temp.
                    If it meets another score with 178 with same attributes it overwrites the temp and if then no score with 178 and diff attributes is found it
                    just gets added to the sorted list.
                    """
                    if score == collect_stats[stat][4] and collect_stats[stat] not in sorted_collect_stats:
                        sorted_collect_stats += [collect_stats[stat]]
                        temp = 0
                        break # add only 1 score per loop
                    if score == collect_stats[stat][4] and collect_stats[stat] in sorted_collect_stats:
                        temp = collect_stats[stat]
                if temp != 0:
                    sorted_collect_stats += [temp]
            file.close()
            with open("statistics_sorted.txt","w") as file:
                for sorted in sorted_collect_stats:
                    if sorted == sorted_collect_stats[-1]:
                        file.write(str(sorted))
                    else:
                        file.write(str(sorted) + ":")
                file.close()


    def draw(self):
        Window.fill(Black)
        Window.blit(game_over_font.render("GAME OVER",1,White),(350,100))
        Window.blit(font.render("Time survived: " + str(round(curr_scores[0])) + " secs",1,White),(350,250))
        Window.blit(font.render("Meters walked: " + str(round(curr_scores[1])) + " m",1,White),(350,300))
        Window.blit(font.render("Nights survived: " + str(curr_scores[2]),1,White),(350,350))
        Window.blit(font.render("Skellets killed: " + str(curr_scores[3]),1,White),(350,400))
        Window.blit(score_font.render("Score: " + str(self.score),1,White),(420,170))
        self.main_menu.update_button()
        self.main_menu.draw_button()

class MainMenu():
    def __init__(self):
        self.start = Button(Vector2(450,150),"christmasbutton.png","GameState()")
        self.options = Button(Vector2(450,200),"options.png","OptionsMenu()")
        self.achievement = Button(Vector2(450,250),"achievements.png","AchievementMenu()")
        self.stats = Button(Vector2(450,300),"stats.png","StatsMenu()")
        self.exit = Button(Vector2(450,350),"exit.png",None)

    def draw(self):
        buttons = [self.start,self.options,self.achievement,self.stats,self.exit]
        Window.fill(Black)
        for button in buttons:
            button.update_button()
            button.draw_button()

currState = MainMenu()

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
        """
        Draw achievement with colour when its unlocked, without colour when its locked.
        """
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
        curr_scores[1] += (distance.x + distance.y) / 100

def achievement_unlocked():
    """
    Checks the conditions on which a achievement can be unlocked. We
    dont check anymore, if the date is set. If date is set the achievement
    is unlocked.
    """
    now = datetime.datetime.now()
    for achievement in achievement_lst:
        if achievement.date == "":
            if achievement.name == "Never Ending Fun" and achievement.condition >= 60:
                achievement.date = now.strftime("%y-%m-%d %H:%M:%S")
            if achievement.name == "Marathon" and achievement.condition >= 1000:
                achievement.date = now.strftime("%y-%m-%d %H:%M:%S")
            if achievement.name == "Survivor" and achievement.condition == 3:
                achievement.date = now.strftime("%y-%m-%d %H:%M:%S")
            if achievement.name == "Oppressor" and achievement.condition == 50:
                achievement.date = now.strftime("%y-%m-%d %H:%M:%S")
        else:
            if achievement.health > 0:
                achievement_unlocked_draw(achievement)

def achievement_unlocked_draw(achievement):
    """
    At the point where the achievement is unlocked it gets drawn onto the game screen,
    while its health is above 0.
    """ 
    offset = (450,380)
    if achievement.name == "Never Ending Fun":
        offset = (420,380)
    Window.blit(font.render("Achievement",1,White),(440,450))
    Window.blit(font.render(achievement.name,1,White),offset)
    Window.blit(pygame.transform.scale(pygame.image.load(os.path.join("Assets",achievement.string)),(50,50)),(475,400))
    achievement.health -= 1

def collected_achievements():
    """
    Returns the amount of achievements that are already unlocked.
    """
    count = 0
    for achievement in achievement_lst:
        if achievement.date != "":
            count += 1
    return count

"""
AchievementGlobals
"""
curr_pos = Vector2(300,250)
curr_scores = [0,0,0,0]
achievement_lst = [AchievementCreator("hourglassLockedD.png","hourglassS.png",Vector2(100,150),0,"",100,"Never Ending Fun","Play for 1 minute."),AchievementCreator("olympiclocked.png","olympic.png",Vector2(100,250),0,"",100,"Marathon","Walk for 1000 meters.")
,AchievementCreator("moon50locked.png","moon50.png",Vector2(100,350),0,"",100,"Survivor","Survive 3 nights."),AchievementCreator("skelletheadlocked.png","skelletevil.png",Vector2(100,450),0,"",100,"Oppressor","Kill 50 skelletons.")]

class Gameobjectmanager():
    """
    Handles all the methods from the objects in the game.
    """
    def __init__(self):
        self.bulletlist = []
        self.playerlist = [Player()]
        self.enemylist = []


    def spawn_enemy(self,pos):
        for player in self.playerlist:
            enemy = Enemy(pos,self.enemylist,player.get_pos())
            self.enemylist += [enemy]

    def spawn_bullet(self):
        global shoot
        if shoot and len(self.bulletlist) < 5:
            shoot_sound.play()
            for player in self.playerlist:
                self.bulletlist += [Bullet(player.get_pos(),pygame.mouse.get_pos(),self.bulletlist)]
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
        """
        Delete bullets when rectangle of enemy and bullet intersects
        """
        for bullet in self.bulletlist:
            for enemy in self.enemylist:
                if bullet.pos.colliderect(enemy.pos):
                    hit_sound.play()
                    enemy.hp -= 10
                    try:
                        self.bulletlist.remove(bullet)
                    except:
                        pass

    def handle_enemy_player_collision(self):
        global currState
        for enemy in self.enemylist:
            for player in self.playerlist:
                if enemy.pos.colliderect(player.pos):
                    if player.attacked == False:
                        player.hp -= 5
                        player.attacked = True
                    if player.hp <= 0:
                        self.playerlist.remove(player)
                        currState = GameOver()

    def update(self):
        global night
        global day_night_timer
        self.spawn_bullet()
        for player in self.playerlist:
            player.movement()
            calc_meters_walked(player.get_pos())
        for bullet in self.bulletlist:
            bullet.update()
        for enemy in self.enemylist:
            enemy.update()
        self.handle_collision()
        self.handle_bullet_enemy_collision()
        self.handle_enemy_player_collision()
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
        for player in self.playerlist:
            player.draw()
        for enemy in self.enemylist:
            enemy.draw()
        for bullet in self.bulletlist:
            bullet.draw()

def set_ui_sound():
    try:
        with open("sliderinfo.txt","r") as file:
            for info in file:
                comma_split = info.split(",")            
                hover_sound.set_volume((int(comma_split[2])-360)/250)
                print("lul")
                file.close()
    except:
        pass

def game_loop():
    """
    Simple game loop which handles keyboard input and in which state the player currently is.
    """
    clock = pygame.time.Clock()
    global gameobjectmanager
    gameobjectmanager = Gameobjectmanager()
    global currState
    global escape_count
    global in_pause
    global shoot
    global background_music
    start_time = 0
    load_achievements()
    set_ui_sound()
    playes = False
    global paused
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
            start_time is total time played (saved), clock time is time played (not saved)
            """
            global clock_time
            global actual_time
            global day_night_timer
            if start_time == 0:
                start_time = time.time()
            if clock_time == 0:
                clock_time = time.time()
            if actual_time == 0:
                actual_time = time.time()

            achievement_lst[0].condition = time.time() - start_time
            day_night_timer = time.time() - clock_time
            curr_scores[0] = time.time() - actual_time

            currState.update(gameobjectmanager)
            if currState.__class__ != GameOver:
                currState.draw(gameobjectmanager)

            if playes == False:
                background_music = mixer.music.play(-1)
                playes = True
            if paused: 
                background_music = mixer.music.unpause()
        else:
            start_time = time.time() - achievement_lst[0].condition
            clock_time = time.time() - day_night_timer
            actual_time = time.time() - curr_scores[0]

            if playes:
                background_music = mixer.music.pause()
                paused = True
            
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
