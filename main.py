# -*- coding: utf-8 -*-
# Made by Cary

import multiprocessing
import pygame
import sys
import math
import random
from pygame.locals import *

pygame.init()  # Initialize

'''
def move_spirit(en_list, en_tag, new_pos):
    while True:
        for en_index in range(len(en_list) - 1, -1, -1):
            if en_list[en_index].tag == en_tag:
                en_list[en_index].pos = new_pos
        pygame.display.update()
'''


def circular_detect(radius, detected_pos=(0, 0), origin=(0, 0)):
    if (((detected_pos[0] - origin[0]) ** 2) + ((detected_pos[1] - origin[1]) ** 2)) < (radius ** 2):
        return True
    else:
        return False


def get_slope(st_x, st_y, en_x, en_y):
    return (en_y - st_y) / (en_x - st_x)


def is_crashed(crasher_sx, crasher_sy, crasher_ex, crasher_ey, obj_sx, obj_sy, obj_ex, obj_ey):
    # Rectangular collision detect if crasher crashed obj
    if crasher_sx <= obj_ex and crasher_ex >= obj_sx:
        if crasher_ey >= obj_sy and crasher_sy <= obj_ey:
            return True
    return False


def countdown(count, step, stop):
    if count - step >= stop:
        count -= step
    else:
        count = 0
    return count


class FlyingObject:
    def __init__(self, image, weight, height, hp, x_speed, y_speed, tag, pos=None, contact_dmg=100, shield=100,
                 damaged_by=None, team=None):
        # pos: left top of spirits
        if pos is None:  # Initialize object position
            pos = [0, 0]
        self.image = pygame.image.load(image)
        self.weight = weight
        self.height = height
        self.pos = pos  # pos = [x, y] -> pos[0]: x, pos[1]: y
        self.hp = hp
        self.shield = shield
        self.x_speed = x_speed
        self.y_speed = y_speed
        '''
        self.x_speed and self.y_speed determine the motion of the plane on x or y-axis
        x_speed = 0: stay still    y_speed = 0: stay still
        x_speed > 0: move right    y_speed > 0: move down
        x_speed < 0: move left     y_speed < 0: move up
        '''
        self.tag = tag  # It tells the game what type of entity it is
        self.contact_dmg = contact_dmg  # Damage when collided
        self.gp_remain = 0  # Remaining invulnerable time
        self.damaged_by = damaged_by
        self.team = team

    def explode(self, explode_radius, damage, check_entity_list, friend=None, friend_team=None):
        for explosion_index in range(len(check_entity_list) - 1, - 1, - 1):
            if circular_detect(explode_radius, (
                    check_entity_list[explosion_index].pos[0] + math.floor(check_entity_list[explosion_index].weight / 2),
                    check_entity_list[explosion_index].pos[1] + math.floor(check_entity_list[explosion_index].height / 2)),
                               (self.pos[0] + math.floor(self.weight / 2),
                                self.pos[1] + math.floor(self.height / 2))):  # Get center
                # Prevent harming friends
                if check_entity_list[explosion_index].tag != friend:
                    check_entity_list[explosion_index].shield -= damage
                elif check_entity_list[explosion_index].team != friend_team:
                    check_entity_list[explosion_index].shield -= damage
                if bool(friend) and bool(friend_team):  # AND detect, preventing arguments conflicts
                    raise TypeError("One of the arguments \"friend\" and \"friend_team\" has to be None, yet both were given")


class Plane(FlyingObject):
    def fire(self, firing_x, firing_y, bullet_x_speed, bullet_y_speed, entity_check_list=None, bullet_team=None):
        # Initializing unfilled arguments
        if entity_check_list is None:
            entity_check_list = []
        if bullet_team is None:
            bullet_team = self.team
        # Initializing speed for bullet
        if self.y_speed < 0:
            bullet_y_speed += self.y_speed * 0.75
        if self.x_speed != 0:
            bullet_x_speed += self.x_speed * 0.25
        bullet = Bullet(image='bullet.png', weight=5, height=16+abs(bullet_y_speed), hp=1, shield=0, y_speed=bullet_y_speed,
                        x_speed=bullet_x_speed, tag="bullet", pos=[firing_x, firing_y], team=bullet_team)
        entity_check_list.append(bullet)


class Bullet(FlyingObject):
    def track(self, obj_x, obj_y):
        pass


def main():
    # Basic settings
    winW = 600
    winH = 800
    screen = pygame.display.set_mode((winW, winH))  # Set screen size
    fps = 60  # 80 frames per second
    fps_clock = pygame.time.Clock()
    game_status = "in_game"  # All status: in_game; paused; died

    # edge of camera                        Positions:
    left_edge = ((0, 0), (0, 799))  # (top, bottom)
    right_edge = ((599, 0), (599, 799))  # (top, bottom)
    up_edge = ((0, 0), (599, 0))  # (left, right)
    down_edge = ((0, 799), (599, 799))  # (left, right)

    # Text fonts & colors setup
    general_font = pygame.font.Font("freesansbold.ttf", 18)
    general_text_color = (0, 0, 0)
    # Score tracking
    score = 0
    highest_score_file = open("highest_score.txt", "r")  # Opening score file
    highest_score = highest_score_file.read()
    highest_score_file.close()

    # Global images, background text etc
    game_over_img = pygame.image.load("Dead_text.png")

    # spirits
    my_plane = Plane(image='my_plane.png', weight=32, height=64, hp=1, shield=300, x_speed=1, y_speed=1, tag="my_plane",
                     pos=[300, 600], team="player")
    spawn_enemy_rate = 20  # 1 out of 50 per every frame

    # CDs
    max_fire_cd = 20
    max_evade_cd = 40
    current_fire_cd = 0
    current_evade_cd = 0

    # Initialize entities
    entity_list = [my_plane]

    # Keys setting
    mouse_x = 0
    mouse_y = 0
    move_up = False
    move_down = False
    move_left = False
    move_right = False
    evade_direction = [0, 0]  # int: [dash left, dash right], determine evade distance
    key_holding = [0, 0]  # [left/right, up/down] Controls the accelerating speed of the plane
    space = False
    # Main loop
    while True:
        if game_status == "in_game":  # In game
            # Basic settings
            entity_list_len = len(entity_list)
            mouse_clicked = False
            screen.fill((255, 255, 255))
            if current_fire_cd > 0:
                current_fire_cd -= 1
            if current_evade_cd > 0:
                current_evade_cd -= 1
            for gp in range(entity_list_len - 1, -1, -1):
                if entity_list[gp].gp_remain > 0:
                    entity_list[gp].gp_remain -= 1

            #  Texts initializing
            text = general_font.render("Score: {0}".format(score), True, general_text_color)
            text_rect = text.get_rect()
            text_rect.center = (535, 30)
            highest_score_text = general_font.render("Highest Score: {0}".format(highest_score), True, general_text_color)
            high_score_rect = highest_score_text.get_rect()
            high_score_rect.center = (500, 60)

            # Detecting spirits crashing
            for player_team_i in range(entity_list_len - 1, -1, -1):
                if entity_list[player_team_i].team == "player":
                    for enm_i in range(entity_list_len - 1, -1, -1):
                        if entity_list[enm_i].team == "enemy":
                            if is_crashed(crasher_sx=entity_list[player_team_i].pos[0],
                                          crasher_sy=entity_list[player_team_i].pos[1],
                                          crasher_ex=entity_list[player_team_i].pos[0] + entity_list[player_team_i].weight,
                                          crasher_ey=entity_list[player_team_i].pos[1] + entity_list[player_team_i].height,

                                          obj_sx=entity_list[enm_i].pos[0], obj_sy=entity_list[enm_i].pos[1],
                                          obj_ex=entity_list[enm_i].pos[0] + entity_list[enm_i].weight,
                                          obj_ey=entity_list[enm_i].pos[1] + entity_list[enm_i].height):
                                # Dealing damages and pending deletion
                                if not entity_list[player_team_i].gp_remain:
                                    entity_list[player_team_i].shield -= entity_list[enm_i].contact_dmg
                                    entity_list[player_team_i].damaged_by = entity_list[enm_i]
                                    entity_list[enm_i].shield -= entity_list[player_team_i].contact_dmg
                                    entity_list[enm_i].damaged_by = entity_list[player_team_i]

            # Dealing hp damages to spirits with negative shields
            for health in range(entity_list_len - 1, -1, -1):
                if entity_list[health].shield < 0:
                    entity_list[health].hp += entity_list[health].shield

            # Spawn entities
            do_spawn_enemy = (random.randint(1, spawn_enemy_rate) == 1)
            if do_spawn_enemy:
                enemy_pos = [random.randint(0, right_edge[0][0] - 24), -20]
                enemy_speed = random.randint(2, 10)
                new_enemy = Plane(image='enemy_plane.png', weight=24, height=24, hp=1, shield=0, x_speed=0,
                                  y_speed=enemy_speed,
                                  tag="weak_enemy", pos=enemy_pos, team="enemy")
                entity_list.append(new_enemy)

            # Key detection
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEMOTION:
                    mouse_x, mouse_y = event.pos
                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_clicked = True
                if event.type == pygame.KEYDOWN:  # Hold keys
                    if event.key == K_w:
                        move_up = True
                        move_down = False
                        key_holding[1] = 1
                    elif event.key == K_s:
                        move_down = True
                        move_up = False
                        key_holding[1] = 1
                    if not evade_direction[0] and not evade_direction[1]:
                        if event.key == K_d:
                            move_right = True
                            move_left = False
                            key_holding[0] = 1
                        elif event.key == K_a:
                            move_left = True
                            move_right = False
                            key_holding[0] = 1
                        if event.key == K_SPACE:
                            space = True
                elif event.type == pygame.KEYUP:  # Release keys
                    if event.key == K_w:
                        move_up = False
                        key_holding[1] = 0
                    elif event.key == K_s:
                        move_down = False
                        key_holding[1] = 0
                    if not evade_direction[0] and not evade_direction[1]:
                        if event.key == K_d:
                            move_right = False
                            key_holding[0] = 0
                        elif event.key == K_a:
                            move_left = False
                            key_holding[0] = 0
                    if event.key == K_SPACE:
                        space = False
                    # Arrow keys: evasion=gp
                    if event.key == K_LEFT:
                        evade_direction[0] = 8
                        evade_direction[1] = 0
                        my_plane.gp_remain = 7
                    elif event.key == K_RIGHT:
                        evade_direction[0] = 0
                        evade_direction[1] = 8
                        my_plane.gp_remain = 7

            # Accelerating the plane
            if key_holding[0] and my_plane.x_speed < 5 and move_right:
                my_plane.x_speed += 0.25
            if key_holding[0] and my_plane.x_speed > -5 and move_left:
                my_plane.x_speed -= 0.25
            if key_holding[1] and my_plane.y_speed > -5 and move_up:
                my_plane.y_speed -= 0.75
            if key_holding[1] and my_plane.y_speed < 5 and move_down:
                my_plane.y_speed += 0.75

            # Setting the x and y axis motions of the plane
            if move_up:
                key_holding[1] = 1
                if my_plane.y_speed > 0:
                    my_plane.y_speed = -my_plane.y_speed
            elif move_down:
                key_holding[1] = 1
                if my_plane.y_speed < 0:
                    my_plane.y_speed = -my_plane.y_speed
            else:
                my_plane.y_speed = 0

            if move_right:
                key_holding[0] = 1
                if my_plane.x_speed < 0:
                    my_plane.x_speed = -my_plane.x_speed
            elif move_left:
                key_holding[0] = 1
                if my_plane.x_speed > 0:
                    my_plane.x_speed = -my_plane.x_speed
            else:
                my_plane.x_speed = 0

            # Plane evasion movements
            if evade_direction[0]:
                evade_direction[0] -= 1
                my_plane.pos[0] -= 10 + 3 * evade_direction[0]
            elif evade_direction[1]:
                evade_direction[1] -= 1
                my_plane.pos[0] += 10 + 3 * evade_direction[1]

            # Plane fire
            if space and current_fire_cd < 1:
                my_plane.fire(firing_x=my_plane.pos[0] + math.floor(my_plane.weight / 2) - 7,
                              firing_y=my_plane.pos[1] + math.floor(my_plane.height / 2) - 24, bullet_x_speed=0,
                              bullet_y_speed=-10, entity_check_list=entity_list)
                my_plane.fire(firing_x=my_plane.pos[0] + math.floor(my_plane.weight / 2) + 2,
                              firing_y=my_plane.pos[1] + math.floor(my_plane.height / 2) - 24, bullet_x_speed=0,
                              bullet_y_speed=-10, entity_check_list=entity_list)
                current_fire_cd = max_fire_cd

            # Spirits movements
            for ent_i in range(entity_list_len - 1, -1, -1):
                entity_list[ent_i].pos[0] += entity_list[ent_i].x_speed
                entity_list[ent_i].pos[1] += entity_list[ent_i].y_speed

            # Preventing plane from moving away the screen
            if my_plane.pos[0] < left_edge[0][0]:
                my_plane.pos[0] = 0
                my_plane.x_speed = 0
            if my_plane.pos[1] < up_edge[0][1]:
                my_plane.pos[1] = 0
                my_plane.y_speed = 0
            if (my_plane.pos[0] + my_plane.weight - 1) > right_edge[0][0]:
                my_plane.pos[0] = right_edge[0][0] - 31
                my_plane.x_speed = 0
            if (my_plane.pos[1] + my_plane.height - 1) > down_edge[0][1]:
                my_plane.pos[1] = down_edge[0][1] - 63
                my_plane.y_speed = 0

            # Displaying entities on the screen
            for i in range(entity_list_len - 1, -1, -1):
                screen.blit(entity_list[i].image, entity_list[i].pos)
            # Displaying texts
            screen.blit(text, text_rect)
            screen.blit(highest_score_text, high_score_rect)

            # Deleting spirits too far away from the camera
            for entity in range(entity_list_len - 1, -1, -1):
                if entity_list[entity].tag != "my_plane":
                    if not is_crashed(crasher_sx=entity_list[entity].pos[0], crasher_sy=entity_list[entity].pos[1],
                                      crasher_ex=entity_list[entity].pos[0] + entity_list[entity].weight,
                                      crasher_ey=entity_list[entity].pos[1] + entity_list[entity].height,

                                      obj_sx=left_edge[0][0], obj_sy=left_edge[0][1],
                                      obj_ex=right_edge[1][0], obj_ey=right_edge[1][1]):
                        entity_list[entity].hp = 0

            # Killing entities with hp less than 1
            for kill in range(entity_list_len - 1, -1, -1):
                if entity_list[kill].hp < 1:
                    if entity_list[kill].tag == "bullet":
                        entity_list[kill].explode(explode_radius=20, damage=20, check_entity_list=entity_list, friend_team="player")
                    if entity_list[kill].tag == "weak_enemy":
                        entity_list[kill].explode(explode_radius=40, damage=20, check_entity_list=entity_list)
                        if entity_list[kill].damaged_by:
                            if entity_list[kill].damaged_by.team == "player" and entity_list[kill].damaged_by.tag != "my_plane":
                                score += 1
                    if entity_list[kill].tag == "my_plane":
                        game_status = "died"
                    del entity_list[kill]

            pygame.display.update()
            fps_clock.tick(fps)
        if game_status == "died":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_RETURN:
                        main()

            screen.blit(game_over_img, (0, 0))
            pygame.display.update()


if __name__ == '__main__':
    main()
