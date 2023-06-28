# -*- coding: utf-8 -*-

import pygame, random, sys, time
from pygame.locals import *


def is_crashed(des_sx, des_sy, des_ex, des_ey, type_sx, type_sy, type_ex, type_ey):  # Crash detect
    if des_sx <= type_ex and des_ex >= type_sx:
        if des_ey >= type_sy and des_sy <= type_ey:
            return True
    return False


def main():
    # Regular values
    pygame.init()
    fps = 60
    fpsClock = pygame.time.Clock()
    win_height = 800
    win_weight = 600
    disp = pygame.display.set_mode((win_weight, win_height))
    background = pygame.image.load("background.png")
    disp.blit(background, (0, 0))

    # Scores' variables and constants
    scores = 0
    scoreFont = pygame.font.Font("freesansbold.ttf", 18)

    highest_score_file = open("highest_score.txt", "r")
    highest_score = highest_score_file.read()
    highest_score_file.close()
    highest_score_Font = pygame.font.Font("freesansbold.ttf", 18)

    skills_font = pygame.font.Font("freesansbold.ttf", 15)  # Skills texts' font

    # Game Over's variables and constants
    isDead = False
    dead_text = pygame.image.load("Dead_text.png")

    # Game Pause's variables and constants
    isPause = False
    pauseFont = pygame.font.Font("freesansbold.ttf", 50)
    try_again_Font = pygame.font.Font("freesansbold.ttf", 24)
    textColor = (0, 0, 0)   # Major texts' color

    # Entities' display data
    bullets = {
        "bullet_photo": pygame.image.load("bullets.png"),
        "bulletX": 100,
        "bulletY": 100

    }
    enemy_data = {
        "enemy_photo": pygame.image.load("enemy_plane.png"),
        "ene_x": 0,
        "ene_y": 5
    }

    # Skills' display data
    skill_1 = {
        "number": 0,
        "photo": [pygame.image.load("skill_1.png"), pygame.image.load("click_skill_1.png")],
        "photo_x": 510,
        "photo_y": 233,
        "delay_to_fire": 5
    }

    skill_2 = {
        "number": 0,
        "photo": [pygame.image.load("skill_2.png"), pygame.image.load("click_skill_2.png")],
        "photo_x": 510,
        "photo_y": 290
    }

    skill_1_entity = {
        "x": 0,
        "y": -1,
        "spawn_probability": [[0, 800], 10],        #
        "skill_1_photo": pygame.image.load("skill_1_entity.png")
    }

    skill_2_entity = {
        "x": 0,
        "y": -1,
        "spawn_probability": [[0, 800], 10],
        "skill_2_photo": pygame.image.load("skill_2_entity.png")
    }

    skill_1_index = 0
    skill_2_index = 0

    skill_1_using = False
    skill_1_cd = 0
    skill_1_cdX = skill_1["photo_x"]
    skill_1_cdY = skill_1["photo_y"]
    skill_1_lifetime = 0
    skill_1_delay = 0

    skill_cd_height = 48
    skill_cd_weight = 1

    skill_2_using = False
    skill_2_cd = 0
    skill_2_cdX = skill_2["photo_x"]
    skill_2_cdY = skill_2["photo_y"]

    shield_photos = [pygame.image.load("empty_shield.png"), pygame.image.load("one_shield.png"),
                     pygame.image.load("two_shields.png"), pygame.image.load("full_shield.png")]
    shield_num = 3
    reward = 100

    plane_photo = pygame.image.load("my_plane.png")
    plane_mid_pos = (0, 0)
    planex, planey = 299, 399

    mouseX = 0
    mouseY = 0
    mouseClicked = False
    fire_delay = 0
    emytime = 0
    skill_1_time = 0
    skill_2_time = 0

    moveD = False
    moveU = False
    moveL = False
    moveR = False
    planeSpeed = 6

    bullets_list = []
    fire = False
    emy_list = []
    skills_list = []
    friend_plane_list = []
    friend_plane_photo = pygame.image.load("plane_2.png")
    friend_plane_speed = 3

    # edge of camera
    left_edge = ((0, 0), (0, 799))
    right_edge = ((599, 0), (599, 799))
    up_edge = ((0, 0), (599, 0))
    down_edge = ((0, 799), (599, 799))

    while True:
        if not (isDead and isPause):
            # print("skill_2 cd:{0}\nskill_2 using:{1}".format(skill_2_cd, skill_2_using))
            mouseClicked = False
            if scores > int(highest_score):
                highest_score = scores
                highest_score_file = open("highest_score.txt", "w")
                highest_score_file.write(str(highest_score))
                highest_score_file.close()

            # print("emy_list:{0},bullet_list:{1}".format(emy_list, bullets_list))
            score_text = scoreFont.render("Score:{0}".format(scores), True, textColor)
            score_rect = score_text.get_rect()
            score_rect.center = (535, 30)

            highest_score_text = highest_score_Font.render("Highest Score:{0}".format(highest_score), True, textColor)
            highest_score_rect = highest_score_text.get_rect()
            highest_score_rect.center = (500, 60)

            skill_1_text = skills_font.render("{0}".format(skill_1["number"]), True, textColor)
            skill_1_rect = skill_1_text.get_rect()
            skill_1_rect.center = (skill_1["photo_x"] + 50, skill_1["photo_y"] + 45)

            skill_2_text = skills_font.render("{0}".format(skill_2["number"]), True, textColor)
            skill_2_rect = skill_2_text.get_rect()
            skill_2_rect.center = (skill_2["photo_x"] + 50, skill_2["photo_y"] + 45)

            emytime = random.randint(0, 30)
            skill_1_time = random.randint(skill_1_entity["spawn_probability"][0][0],
                                          skill_1_entity["spawn_probability"][0][1])
            skill_2_time = random.randint(skill_2_entity["spawn_probability"][0][0],
                                          skill_2_entity["spawn_probability"][0][1])
            # print("skill_1:{0}\nskill_2:{1}".format(skill_1_time, skill_2_time))
            # print("time:%s" % time)

            if fire_delay < 20:
                fire_delay += 1
            if skill_1_delay < skill_1["delay_to_fire"]:
                skill_1_delay += 1
            if skill_1_cd > 0:
                if skill_1_cd % 4 == 0:
                    skill_cd_weight = skill_1_cd / 4
                skill_1_cd -= 12
            if skill_1_using and skill_1_lifetime > 0:
                skill_1_lifetime -= 1
                if skill_1_lifetime == 0:
                    skill_1_cd = 196
                    skill_1_using = False
            if skill_2_using and skill_2_cd == 0:
                if len(emy_list) > 5:
                    for summon in range(len(emy_list) - 1, -1, -1):
                        friend_plane_list.append([friend_plane_photo, emy_list[summon][1], 840])
                    skill_2_using = False
                    skill_2_cd = 392
                else:
                    for summon in range(len(emy_list) - 1, -1, -1):
                        friend_plane_list

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEMOTION:
                    mouseX, mouseY = event.pos
                if event.type == pygame.MOUSEBUTTONUP:
                    mouseClicked = True
                if event.type == pygame.KEYUP:
                    if event.key == K_w:
                        moveU = False
                    if event.key == K_s:
                        moveD = False
                    if event.key == K_a:
                        moveL = False
                    if event.key == K_d:
                        moveR = False
                    if event.key == K_SPACE:
                        fire = False
                    if event.key == K_ESCAPE:
                        isPause = True
                elif event.type == KEYDOWN:
                    if event.key == K_w:
                        moveU = True
                        moveD = False
                    elif event.key == K_s:
                        moveU = False
                        moveD = True
                    if event.key == K_a:
                        moveL = True
                        moveR = False
                    elif event.key == K_d:
                        moveL = False
                        moveR = True
                    if event.key == K_SPACE:
                        fire = True

            if moveU:
                planey -= planeSpeed
            if moveD:
                planey += planeSpeed
            if moveL:
                planex -= planeSpeed
            if moveR:
                planex += planeSpeed
            if fire:
                if skill_1_using and skill_1_lifetime > 0 and skill_1_delay == skill_1["delay_to_fire"]:
                    bullets["bulletX"] = plane_mid_pos[0] - 8
                    bullets["bulletY"] = plane_mid_pos[1]
                    newbullt = [None, None, None]
                    # print(mouseX, mouseY)
                    newbullt[0], newbullt[1], newbullt[2] = bullets["bullet_photo"], bullets["bulletX"], bullets[
                        "bulletY"]
                    bullets_list.append(newbullt)
                    skill_1_delay = 0
                if fire_delay >= 20:
                    bullets["bulletX"] = plane_mid_pos[0] - 8
                    bullets["bulletY"] = plane_mid_pos[1]
                    newbullt = [None, None, None]
                    # print(mouseX, mouseY)
                    newbullt[0], newbullt[1], newbullt[2] = bullets["bullet_photo"], bullets["bulletX"], bullets[
                        "bulletY"]
                    bullets_list.append(newbullt)
                    # print("new bullet:{0}".format(bullets_list))
                    fire_delay = 0

            if planex < left_edge[0][0]:
                planex = 0
            if planey < up_edge[0][1]:
                planey = 0
            if (planex + 31) > right_edge[0][0]:
                planex = right_edge[0][0] - 31
            if (planey + 61) > down_edge[0][1]:
                planey = down_edge[0][1] - 63

            if emytime == 16:
                enemy_data["ene_x"] = random.randint(0, right_edge[0][0] - 15)
                enemy_data["ene_y"] = -8
                newemy = [None, None, None]
                newemy[0], newemy[1], newemy[2] = enemy_data["enemy_photo"], enemy_data["ene_x"], enemy_data["ene_y"]
                emy_list.append(newemy)

            if skill_1_time == skill_1_entity["spawn_probability"][1]:
                skill_1_entity["x"] = random.randint(0, right_edge[0][0] - 48)
                skill_1_entity["y"] = -8
                new_skill_1 = [skill_1_entity["skill_1_photo"], skill_1_entity["x"], skill_1_entity["y"], "skill_1"]
                skills_list.append(new_skill_1)

            if skill_2_time == skill_2_entity["spawn_probability"][1]:
                skill_2_entity["x"] = random.randint(0, right_edge[0][0] - 48)
                skill_2_entity["y"] = -8
                new_skill_2 = [skill_2_entity["skill_2_photo"], skill_2_entity["x"], skill_2_entity["y"], "skill_2"]
                skills_list.append(new_skill_2)
            # print("skill_1_photo:{0}\nskill_2_photo:{1}".format(skill_1_entity["skill_1_photo"], skill_2_entity["skill_2_photo"]))

            if scores == reward:
                shield_num = 3
                reward *= 2.5

            if len(emy_list) > 0:
                for emy_des in range(len(emy_list) - 1, -1, -1):
                    for z in range(len(bullets_list) - 1, -1, -1):
                        try:
                            # print("\temy_list[{0}]:{1},bullets[{2}]:{3}".format(emy_des, emy_list[emy_des], z, bullets_list[z]))
                            # print("emy_list < bullets, bullets:%s, emy:%s" % (len(bullets_list), len(emy_list)))
                            if is_crashed(emy_list[emy_des][1], emy_list[emy_des][2], emy_list[emy_des][1] + 23,
                                          emy_list[emy_des][2] + 23, bullets_list[z][1], bullets_list[z][2],
                                          bullets_list[z][1] + 17, bullets_list[z][2] + 15):
                                del bullets_list[z], emy_list[emy_des]
                                scores += 1
                        except IndexError:
                            # print("index error")
                            # print("emy_des={0},z={1},len_emy={2},len_bullets={3}".format(emy_des, z, len(emy_list), len(bullets_list)))
                            pass
            """ if len(emy_list) < len(bullets_list):
                for z in range(len(bullets_list) - 1, -1, -1):
                    for emy_des in range(len(emy_list) - 1, -1, -1):
                        print("bullets > emy_list, bullets:%s, emy:%s" % (len(bullets_list), len(emy_list)))
                        if is_crashed(emy_list[emy_des][1], emy_list[emy_des][2], emy_list[emy_des][1] + 23, emy_list[emy_des][2] + 23, bullet s_list[z][1], bullets_list[z][2], bullets_list[z][1] + 4, bullets_list[z][2] + 15):
                            del bullets_list[z], emy_list[emy_des]
            """

            if is_crashed(skill_1["photo_x"], skill_1["photo_y"], skill_1["photo_x"] + 47, skill_1["photo_y"] + 47,
                          mouseX, mouseY, mouseX, mouseY):
                skill_1_index = 1
                skill_2_index = 0
                if mouseClicked and skill_1["number"] > 0 and skill_1_cd < 1 and not skill_1_using:
                    skill_1_using = True
                    skill_1_lifetime = 180
                    skill_1["number"] -= 1
            elif is_crashed(skill_2["photo_x"], skill_2["photo_y"], skill_2["photo_x"] + 47, skill_2["photo_y"] + 47,
                            mouseX, mouseY, mouseX, mouseX):
                skill_1_index = 0
                skill_2_index = 1
                if mouseClicked and skill_2["number"] > 0 and skill_2_cd < 1:
                    skill_2["number"] -= 1
                    skill_2_using = True
            else:
                skill_1_index = 0
                skill_2_index = 0

            disp.blit(background, (0, 0))

            for e in range(len(emy_list) - 1, -1, -1):
                if is_crashed(planex, planey, planex + 31, planey + 63, emy_list[e][1], emy_list[e][2],
                              emy_list[e][1] + 23, emy_list[e][2] + 23):
                    if shield_num == 0:
                        isDead = True
                    else:
                        shield_num -= 1
                        del emy_list[e]

            for s in range(len(skills_list) - 1, -1, -1):
                if is_crashed(planex, planey, planex + 31, planey + 63, skills_list[s][1], skills_list[s][2],
                              skills_list[s][1] + 47, skills_list[s][2] + 47):
                    if skills_list[s][3] == "skill_1" and skill_1["number"] < 5:
                        skill_1["number"] += 1
                        del skills_list[s]
                    elif skills_list[s][3] == "skill_2" and skill_2["number"] < 5:
                        skill_2["number"] += 1
                        del skills_list[s]

            if len(friend_plane_list):
                for att in range(len(friend_plane_list) - 1, -1, -1):
                    disp.blit(friend_plane_list[att][0], (friend_plane_list[att][1], friend_plane_list[att][2]))
                for atty in range(len(friend_plane_list) - 1, -1, -1):
                    friend_plane_list[atty][2] -= friend_plane_speed
                for delete in range(len(friend_plane_list) - 1, -1, -1):
                    if friend_plane_list[delete][2] <= 0:
                        del friend_plane_list[delete]

            for i in range(len(bullets_list) - 1, -1, -1):
                disp.blit(bullets_list[i][0], (bullets_list[i][1], bullets_list[i][2]))
            for x in range(len(bullets_list) - 1, -1, -1):
                bullets_list[x][2] -= 20
                # print(bullets_list)
            for y in range(len(bullets_list) - 1, -1, -1):
                if bullets_list[y][2] <= 0:
                    del bullets_list[y]

            for emy_i in range(len(emy_list) - 1, -1, -1):
                disp.blit(enemy_data["enemy_photo"], (emy_list[emy_i][1], emy_list[emy_i][2]))
            for emy_down in range(len(emy_list) - 1, -1, -1):
                emy_list[emy_down][2] += 10
            for emy_del in range(len(emy_list) - 1, -1, -1):
                if emy_list[emy_del][2] >= 800:
                    del emy_list[emy_del]

            for skills in range(len(skills_list) - 1, -1, -1):
                disp.blit(skills_list[skills][0], (skills_list[skills][1], skills_list[skills][2]))
            for skills_down in range(len(skills_list) - 1, -1, -1):
                skills_list[skills_down][2] += 1022
            for skills_del in range(len(skills_list) - 1, -1, -1):
                if skills_list[skills_del][2] >= 800:
                    del skills_list[skills_del]

            disp.blit(plane_photo, (planex, planey))
            disp.blit(score_text, score_rect)
            disp.blit(highest_score_text, highest_score_rect)
            disp.blit(shield_photos[shield_num], (0, 5))
            disp.blit(skill_1["photo"][skill_1_index], (skill_1["photo_x"], skill_1["photo_y"]))
            disp.blit(skill_1_text, skill_1_rect)
            if skill_cd_weight > 1:
                pygame.draw.rect(disp, (128, 128, 128), (skill_1_cdX, skill_1_cdY, skill_cd_weight, skill_cd_height))
            plane_mid_pos = (planex + 15, planey + 31)
            disp.blit(skill_2["photo"][skill_2_index], (skill_2["photo_x"], skill_2["photo_y"]))
            disp.blit(skill_2_text, skill_2_rect)

            pygame.display.update()
            fpsClock.tick(fps)

        if isDead:
            while True:
                try_again_text = try_again_Font.render("Press Enter to Rebirth", True, textColor)
                try_again_rect = try_again_text.get_rect()
                try_again_rect.center = (win_weight / 2, win_height / 2 + 50)

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
                disp.blit(try_again_text, try_again_rect)
                disp.blit(dead_text, (0, 0))
                pygame.display.update()

        if isPause:
            quit_button_image_index = 0
            back_button_image_index = 0

            while isPause:
                mouseClicked = False

                pauseText = pauseFont.render("Pause", True, textColor)
                pauseRect = pauseText.get_rect()
                pauseRect.center = (win_weight / 2, 60)

                quit_button_image = [pygame.image.load("quit_button.png"), pygame.image.load("quit_button2.png")]
                back_button_image = [pygame.image.load("back_button.png"), pygame.image.load("back_button2.png")]

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYUP:
                        if event.key == K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                    if event.type == pygame.MOUSEMOTION:
                        mouseX, mouseY = event.pos
                    if event.type == pygame.MOUSEBUTTONUP:
                        mouseClicked = True

                if is_crashed(236, 372, 364, 436, mouseX, mouseY, mouseX, mouseY):
                    back_button_image_index = 1
                    quit_button_image_index = 0
                    if mouseClicked:
                        isPause = False
                elif is_crashed(236, 464, 364, 528, mouseX, mouseY, mouseX, mouseY):
                    back_button_image_index = 0
                    quit_button_image_index = 1
                    if mouseClicked:
                        pygame.quit()
                        sys.exit()
                else:
                    back_button_image_index, quit_button_image_index = 0, 0

                disp.blit(pauseText, pauseRect)
                disp.blit(quit_button_image[quit_button_image_index], (236, 464))
                disp.blit(back_button_image[back_button_image_index], (236, 372))
                pygame.display.update()


# 1sc2dv
# %localappdata%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang


if __name__ == "__main__":
    main()
