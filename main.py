## Space shooter game
## Below lies the source code that runs everything in the game.


#### DEPENDENCIES ####
import pygame as pg
import asyncio
import random
import time
import math

#######  ASSETS  #######

## SPRITES ##
Sprites = {
    "ship" : "Sprites/DurrrSpaceShip.png",
    "brown_asteroid" : "Sprites/brown_asteroid.png",
    "laser" : "Sprites/red_laser.png",
    "full_heart": "Sprites/red_pixel_heart1.png",
    "empty_heart": "Sprites/empty_pixel_heart1.png",
    "giftbox": "Sprites/Giftbox1.png",
    "bubble_shield": "Sprites/spr_shield.png",
    "Powerups" : {
        "lightning": "Sprites/Lightning_bolt.png",
        "shield": "Sprites/blue_shield.png",
        "health": "Sprites/green_health_pickup.png",
        "doubleshot": "Sprites/Doubleshot.png"
    }
}

## FONTS ##
FONTS = {
    "arcadeclassic": "Fonts/ARCADECLASSIC.TTF",
    "Orbitronbold": "Fonts/Orbitron-Bold.ttf",
    "P2Start": "Fonts/PressStart2P-Regular.ttf"
}

## COLOURS ##
COLOURS = {
    "white": (255, 255, 255),
    "black": (0,0,0),
    "dark_grey": (50,50,50),
    "red": (255, 0, 0),
    "light_red": (100, 0, 0),
    "blue": (0, 0, 255),
    "dark_magenta": (139, 0, 139),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255)
}


## CLASS DEFINITIONS ##
class HealthPoint(pg.sprite.Sprite):
    '''
    Sprite class for health point icon, being either full or empty hp status.
    '''
    def __init__(self, heart_type):
        pg.sprite.Sprite.__init__(self)
        self.status = heart_type
        self.image, self.rect = load_image(Sprites[heart_type], scale=0.15, img_type="")


class HealthSystem:
    '''
    Class containing information and current state of Player's current Health points.
    '''
    def __init__(self, hp):
        # Total health attributes
        self.current_hp = hp
        self.max_hp = hp
        self.hp_bars = []

        self.is_taking_damage = False # controls whether to call blinking animation or not
        self.can_take_dmg = True
        self.timer = 0
        self.BLINK_TIMER = 200
        
        # Bar attributes
        self.bar_width = 22
        self.bar_height = 15
        self.starting_left = 10
        self.padding = 1
        self.pos_y = 50

        # Heart types for use
        self.Full_heart = HealthPoint("full_heart")
        self.Empty_heart = HealthPoint("empty_heart")

        self.intialise()
    
    def intialise(self):
        self.hp_bars = [] #clear prev hearts

        # Initialise hp to full hp bars
        for i in range(self.max_hp):
            pos_x = (i * (self.bar_width + self.padding)) + self.starting_left
            self.hp_bars.append([])
            self.hp_bars[i].append(self.Full_heart)
            self.hp_bars[i].append((pos_x, self.pos_y))

    def display_hp(self, Screen: pg.Surface):
        for i in range(self.max_hp):
            hp_icon = self.hp_bars[i][0]
            coords = self.hp_bars[i][1]
            Screen.blit(hp_icon.image, coords)

    def take_damage(self):
        if (not self.can_take_dmg): # shield activated
            return False
        
        if (self.is_taking_damage and self.current_hp > 0):
            self.hp_bars[self.current_hp][0] = self.Empty_heart
            self.timer = 0
        
        ## sets conditions in place for blinking animation
        if (not self.is_taking_damage):
            self.is_taking_damage = True
            self.timer = 0
        if (self.current_hp > 0):
            self.current_hp -= 1

        if self.current_hp <= 0:
            return True  # Game over
        else:
            return False  # Continue game
    
    def regain_health(self):
        if (self.is_taking_damage == True):
            self.is_taking_damage = False
        if (self.current_hp < self.max_hp):
            self.current_hp += 1
            self.hp_bars[self.current_hp-1][0] = self.Full_heart

    def reset(self):
        self.current_hp = self.max_hp
        self.is_taking_damage = False
        self.timer = 0
        self.intialise()

    def call_animation(self):
        BLINK_TIMER = 200
        NUM_OF_BLINKS = 8
        TOTAL_ANIMATION_TIME = BLINK_TIMER * NUM_OF_BLINKS

        if (self.timer > TOTAL_ANIMATION_TIME): # break out of animation and set to empty heart
            self.hp_bars[self.current_hp][0] = self.Empty_heart
            self.is_taking_damage = False
            self.timer = 0

        # Draw hearts again, changing last one between full and empty.
        is_visible = (self.timer // BLINK_TIMER) % 2

        if (is_visible):
            self.hp_bars[self.current_hp][0] = self.Full_heart
        else:
            self.hp_bars[self.current_hp][0] = self.Empty_heart

    def update(self, Screen, dt):
        self.timer += dt
        if (self.is_taking_damage):
            self.call_animation()
        self.display_hp(Screen)


class Powerup(pg.sprite.Sprite):
    def __init__(self, coords, power_type: str):
        pg.sprite.Sprite.__init__(self)
        if (power_type == "lightning"):
            scale = 0.045
        elif (power_type == "health"):
            scale = 0.20
        elif (power_type == "doubleshot"):
            scale = 0.125
        else:
            scale = 0.45
        self.image, self.rect = load_image(Sprites["Powerups"][power_type], scale, img_type="")
        self.rect.left = coords[0]
        self.rect.top = coords[1]
        self.power_type = power_type
        self.elapsed_time = 0


class PowerupsOnScreen:
    def __init__(self):
        self.powerups = []
        self.hold_time = 500 # ms
        self.fade_time = 1000 # ms

    def add(self, coords, power_type):
        new_powerup = Powerup(coords, power_type)
        self.powerups.append(new_powerup)
    
    def remove(self, old_powerup: Powerup):
        self.powerups.remove(old_powerup)

    def call_animation(self, dt: int):
        total_time = self.hold_time + self.fade_time

        # iterate over list of powerups on screen and animate them.
        for power in self.powerups:
            power.elapsed_time += dt # adjust their elapsed time
            alpha = 255 # initialise

            # make it float upwards:
            if ((power.elapsed_time // 35) % 2 == 0):
                power.rect.y -= 1

            if power.elapsed_time < total_time:
                if power.elapsed_time < self.hold_time:  # Hold
                    alpha = 255
                elif power.elapsed_time < total_time:  # Fade out
                    alpha = int(255 - (255 * (power.elapsed_time / total_time)))

                power.image.set_alpha(alpha)
            
    def display(self, Screen: pg.Surface):
        total_time = self.fade_time + self.hold_time
        for power in self.powerups[:]:
            if power.elapsed_time > total_time:
                self.remove(power) #filter for currently animating ones only
            else:
                Screen.blit(power.image, power.rect)

    def update(self, Screen, dt):
        self.call_animation(dt)
        self.display(Screen)


class MysteryBox(pg.sprite.Sprite):
    '''
    Sprite class for the game's powerup.
    '''
    def __init__(self, coords):
        pg.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(Sprites["giftbox"], scale=0.045, img_type="")
        self.rect.left = coords[0]
        self.rect.top = coords[1]


class MysteryBoxes:
    '''
    Class containing information for instances of MysteryBox classes on Screen.
    '''
    def __init__(self):
        self.boxes = []
        self.speed = 2
        self.amount = 0
        self.spawn_chance = 0.1
        self.powerup_types = ["lightning", "shield", "health", "doubleshot"]
        self.weights = [0.3, 0.2, 0.2, 0.3] # chance of obtaining
    
    def display(self, Screen: pg.Surface):
        for box in self.boxes:
            Screen.blit(box.image, box.rect)
        
    def remove(self, box: MysteryBox):
        self.amount -= 1
        self.boxes.remove(box)
    
    def add(self, box: MysteryBox):
        self.amount += 1
        self.boxes.append(box)
    
    def update(self, Player, Powerups: PowerupsOnScreen, Screen: pg.Surface, Health: HealthSystem):
        for box in self.boxes[:]:
            box.rect.y += self.speed
            bottom_of_screen = Screen.get_height()

            if (box.rect.colliderect(Player.rect)):
                coords = (box.rect.x, box.rect.y)
                
                chosen_powerup_type = random.choices(self.powerup_types, self.weights, k=1)[0]
                Powerups.add(coords, chosen_powerup_type) # spawn powerup icon
                if (chosen_powerup_type == "health"):
                    Health.regain_health()
                else:
                    Player.add_powerup(Health, chosen_powerup_type)
                self.remove(box)
            if (box.rect.y > bottom_of_screen):
                self.remove(box)
        
        self.display(Screen)
    
    def reset(self):
        self.amount = 0
        self.boxes = []


class Asteroid(pg.sprite.Sprite):
    '''
    Asteroid sprite class as game objects
    '''
    def __init__(self, coord):
        pg.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(Sprites["brown_asteroid"], scale=0.30, img_type="Asteroid")
        self.rect.left, self.rect.top = coord, -40
        speed = random.randint(2, 3)
        self.speed = speed

class AsteroidsOnScreen:
    '''
    Parent class housing all information on all
        instances of Asteroid classes on Screen.
    '''
    def __init__(self, Screen: pg.Surface):
        self.SCREEN_WIDTH = Screen.get_width()
        self.ASTEROID_WIDTH = 45
        self.asteroids = {}
        for i in range(0, self.SCREEN_WIDTH + 1, self.ASTEROID_WIDTH):
            self.asteroids[i] = [] # create buckets for asteroids at different x coords

        self.asteroid_speed = 2 # move speed
    
    def add(self, coord):
        ## Insert new asteroid
        if (self.asteroids[coord] == []):
            asteroid = Asteroid(coord)
            self.asteroids[coord].append(asteroid)
        ## Check if spawning too close to last one
        else:
            closest_asteroid = self.asteroids[coord][-1]
            distance_threshold = 50
            spawn_y_coord = -40
            distance = abs(closest_asteroid.rect.y - spawn_y_coord)

            if (distance >= distance_threshold):
                asteroid = Asteroid(coord)
                self.asteroids[coord].append(asteroid)
    
    def display(self, Screen: pg.Surface):
        for asteroid_list in self.asteroids.values():
            for asteroid in asteroid_list:
                Screen.blit(asteroid.image, asteroid.rect)
    
    def reset(self):
        self.asteroids = {}
        for i in range(0, self.SCREEN_WIDTH + 1, self.ASTEROID_WIDTH):
            self.asteroids[i] = [] # create buckets for asteroids at different x coords


class Laser(pg.sprite.Sprite):
    '''
    Laser class for player's shot lasers
    '''
    def __init__(self, coords):
        pg.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(Sprites["laser"], scale=0.5, img_type="laser")
        self.rect.center = coords


class LasersOnScreen:
    '''
    Parent class housing all data relevant to Laser class instances
        on Screen and in game.
    '''
    def __init__(self):
        self.lasers = []
        self.laser_speed = 5

    def add(self, coords, mode):
        if mode == 1:
            new_laser = Laser(coords)
            self.lasers.append(new_laser)
        elif mode == 2:
            coords_x, coords_y = coords[0] - 10, coords[1]
            new_coords = (coords_x, coords_y)
            new_laser = Laser(new_coords)
            self.lasers.append(new_laser)

            coords_x, coords_y = coords[0] + 10, coords[1]
            new_coords = (coords_x, coords_y)
            new_laser = Laser(new_coords)
            self.lasers.append(new_laser)
    
    def display(self, Screen: pg.Surface):
        for laser in self.lasers:
            Screen.blit(laser.image, laser.rect)
        
    def update(self, Screen: pg.Surface, Asteroids: AsteroidsOnScreen, Giftboxes: MysteryBoxes, score):
        new_lasers = []
        for laser in self.lasers:
            laser.rect.y -= self.laser_speed # shoot forward
            if (laser.rect.y <= 0):
                continue

            ## Check only asteroids in same vertical plane
            collision = False
            ASTEROID_WIDTH = Asteroids.ASTEROID_WIDTH

            laser_ctr = laser.rect.center[0]
            x_coord = (laser_ctr // ASTEROID_WIDTH) * ASTEROID_WIDTH
            for asteroid in Asteroids.asteroids[x_coord]:
                if (laser.rect.colliderect(asteroid.rect)):
                    Asteroids.asteroids[x_coord].remove(asteroid)
                    collision = True
                    score += 1

                    # try spawning a powerup
                    powerup_coords = (asteroid.rect.x, asteroid.rect.y - 2)
                    Giftboxes = spawn_giftboxes(Giftboxes, powerup_coords, score)
                    break
            x_coord = ((laser_ctr // ASTEROID_WIDTH) + 1) * ASTEROID_WIDTH
            if (x_coord > Screen.get_width()):
                continue
            for asteroid in Asteroids.asteroids[x_coord]:
                if (laser.rect.colliderect(asteroid.rect)):
                    Asteroids.asteroids[x_coord].remove(asteroid)
                    collision = True
                    score += 1

                    # try spawning a power up
                    powerup_coords = (asteroid.rect.x, asteroid.rect.y - 2)
                    Giftboxes = spawn_giftboxes(Giftboxes, powerup_coords, score)
                    break
            
            if not collision:
                new_lasers.append(laser)
        self.lasers = new_lasers
        self.display(Screen)
        return score

    def reset(self):
        self.laser_speed = 5
        self.lasers = []


class Ship(pg.sprite.Sprite):
    '''
    Spaceship sprite class for player shooter
    '''
    def __init__(self):
        pg.sprite.Sprite.__init__(self) #call pg sprite init
        self.image, self.rect = load_image(Sprites["ship"], scale=0.5, img_type="Ship")
        self.rect.center = (360, 580)
        self.powers = {}
        self.shot_cooldown = 150
        self.last_shot = 0
        self.move_speed = 6
        self.doubleshot_on = False
    
    def shoot(self):
        if (self.last_shot >= self.shot_cooldown):
            self.last_shot = 0 # reset cooldown
            if (self.doubleshot_on):
                mode = 2
            else:
                mode = 1

            ## Laser constants
            ship_dims = self.rect.center
            laser_x = ship_dims[0] + 3 # offset to align centre
            laser_y = ship_dims[1] - self.rect.height

            coords = (laser_x, laser_y)
            return coords, mode
        else:
            return None, 1
    
    def add_powerup(self, Health: HealthSystem, power_type: str):
        if (power_type == "lightning"):
            time_limit = 7.5 * 1000 # 7.5 seconds
            self.move_speed = 8
            self.shot_cooldown = 100
        elif (power_type == "doubleshot"):
            self.doubleshot_on = True
            time_limit = 5 * 1000 # 5 seconds
        else:
            Health.can_take_dmg = False
            time_limit = 5 * 1000 # 5 seconds for shield
        
        if (power_type in self.powers ):
            self.powers[power_type] += 3 * 1000 # 3 seconds boost
        else:
            self.powers[power_type] = time_limit # update list of player's powerups
    
    def draw_shield(self, screen: pg.Surface, Health: HealthSystem):
        screen.blit(self.image, self.rect)

        if not Health.can_take_dmg:
            shield_surface = pg.Surface(
                (self.rect.width + 20, self.rect.height + 20),
                pg.SRCALPHA
            )
            pg.draw.ellipse(
                shield_surface,
                (0, 150, 255, 50),                # RGBA with alpha
                shield_surface.get_rect(),
                0
            )
            screen.blit(shield_surface, (self.rect.x - 10, self.rect.y - 10))
    
    def update(self, Screen, Health: HealthSystem, dt: int):
        for power in self.powers:
            if (self.powers[power] > 0):
                self.powers[power] -= dt # updates time accordingly

        ## Disables powerups once time up
        if ("lightning" in self.powers and self.powers["lightning"] <= 0):
            self.move_speed = 6
            self.shot_cooldown = 150
        if ("shield" in self.powers and self.powers["shield"] <= 0):
            Health.can_take_dmg = True
        if ("doubleshot" in self.powers and self.powers["doubleshot"] <= 0):
            self.doubleshot_on = False
        
        self.draw_shield(Screen, Health)
    

        
class Broken_Asteroid(pg.sprite.Sprite):
    '''
    Asteroid sprite class as game objects
    '''
    def __init__(self, bounds):
        pg.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(Sprites["broken_asteroid"], scale=0.10, img_type=None)
        self.rect = bounds
        

########### GAME FUNCTIONS #############

def reset_game(Spaceship, Asteroids, Lasers, Score, Health, Giftboxes):
    '''
    Resets the current game by cleaning all game objects
        and resetting score.
    '''
    Spaceship.rect.center = (360, 580)
    Asteroids.reset()
    Lasers.reset()
    Score = 0
    Health.reset()
    Giftboxes.reset()
    return Spaceship, Asteroids, Lasers, Score, Health, Giftboxes


def trim_surface(image: pg.Surface) -> pg.Surface:
    '''
    Masks and cuts out background pixels to form a tight bound
        rectangle around visible bounds in the image asset.
    '''
    mask = pg.mask.from_surface(image)
    if mask.count() == 0:
        return image
    tight = mask.get_bounding_rects()[0]  # visble bounds
    return image.subsurface(tight).copy()


def load_image(name: str, scale: float, img_type: str):
    '''
    Loads in a .png image object, scales it by scale, and makes adjustments 
        to the image object or its rectangle according to img_type.
    '''
    if (name == ""):
        print("Unable to read image: Invalid path.")
        return None

    image = pg.image.load(name)

    if (img_type == "laser"):
        image = pg.transform.rotate(image, 90)

    ## scale image to suit screen
    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)

    image = image.convert_alpha()
    image = trim_surface(image)

    mask = pg.mask.from_surface(image)
    tight_rect = mask.get_bounding_rects()[0]

    if (img_type == "Asteroid"):
        tight_rect.width = 45
    
    if (img_type == "Ship"):
        tight_rect.width = tight_rect.width * 0.9
        tight_rect.height = tight_rect.height * 0.9

    return image, tight_rect


def spawn_asteroids(Asteroids: AsteroidsOnScreen, Screen: pg.Surface, spawn_threshold: int) -> None:
    '''
    Creates new asteroid object instances randomly across the screen,
      and ensures valid spacing between instances
    '''
    if random.random() < spawn_threshold:
        asteroid_width = Asteroids.ASTEROID_WIDTH
        screen_width = Screen.get_width()
        coord = random.randrange(0, screen_width, asteroid_width)

        Asteroids.add(coord) # add to container of asteroids on screen
        

def update_and_draw_stars(screen: pg.Surface, stars: list[list[int]]) -> None:
    '''
    Simulates movement of each star in stars, then projects them onto screen.
    '''
    for star in stars:
        star[1] += star[2]   # move down by speed
        if star[1] > screen.get_height():  # wrap to top of screen
            star[0] = random.randint(0, screen.get_width())
            star[1] = 0
            star[2] = random.randint(1, 2)

        pg.draw.circle(screen, COLOURS["white"], center=(star[0], star[1]), radius=1)


def spawn_stars(screen_width: int, screen_height: int, number: int):
    '''
    Returns a list of length number, which contains stars, each with a
        position and a speed at which they travel.
    '''
    stars = []
    for i in range(number):
        star = []
        star.append(random.randint(0, screen_width))
        star.append(random.randint(0, screen_height))
        star.append(random.randint(0, 2))
        stars.append(star)
    return stars


def game_over(Screen: pg.Surface, GameEndFont, RestartFont, elapsed_time, fade_in_time, hold_time):
    '''
    Defines the game over game state and its animation on the Screen, using the fonts GameEndFont,
        and RestartFont.
    '''
    game_over_text = GameEndFont.render(f"GAME OVER", False, COLOURS["red"])
    total_time = fade_in_time + hold_time

    if elapsed_time < total_time:
        if elapsed_time < fade_in_time:  # Fade in
            alpha = int(255 * (elapsed_time / fade_in_time))
        elif elapsed_time < fade_in_time + hold_time:  # Hold
            alpha = 255

        temp_surface = game_over_text.copy()
        temp_surface.set_alpha(alpha)

        dest_x = Screen.get_width() / 2
        dest_y = Screen.get_height() / 2
        rect = temp_surface.get_rect(center=(dest_x, dest_y))

        Screen.blit(temp_surface, rect)

        if (elapsed_time > fade_in_time):
            ## Prompt user to restart game
            display_font = RestartFont.render("Click Anywhere To Restart", False, COLOURS["yellow"])
            ScreenMiddle = (Screen.get_width()// 2, Screen.get_height()// 2)

            x_offset = display_font.get_width() // 2
            y_offset = display_font.get_height()
            coords = ((ScreenMiddle[0] - x_offset), (ScreenMiddle[1] + y_offset * 2))
            Screen.blit(display_font, coords)
        return True
    else:
        return False


def spawn_giftboxes(Giftboxes: MysteryBoxes, coords, score):
    '''
    Randomly decides if to spawn a powerup at coords where a laser
        has destroyed an asteroid, determined by spawn_threshold.
    '''
    # Limit spawning to 3 onscreen at a time
    spawn_threshold = Giftboxes.spawn_chance
    max_powerups = score // 75
    if (random.random() < spawn_threshold and Giftboxes.amount <= max_powerups):
        new_powerup = MysteryBox(coords)
        Giftboxes.add(new_powerup)
    return Giftboxes
    

############   MAIN FUNCTION  ###########
async def main():
    pg.init()

    ## GAME CONSTANTS ##
    SCREEN_WIDTH = 720
    SCREEN_HEIGHT = 640
    GAME_STARTING_HEALTH = 6
    BASE_SPAWN_RATE = 0.01
    GROW_SPEED = 0.001

    ## GAME VARIABLES ##
    score = 0
    stars = spawn_stars(SCREEN_WIDTH, SCREEN_HEIGHT, number=150)
    
    ## GAME STATES AND TIMINGS (MS)
    game_start_menu = True
    fade_in_time = 2000
    hold_time    = 100000
    elapsed_game_end = 0
    is_game_ending = False
    just_entered_game_end = False
    is_game_reset = False

    ## GAME CLASSES & SETTINGS ##
    Screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("SPACE DEFENDER")
    Asteroids = AsteroidsOnScreen(Screen)
    Lasers = LasersOnScreen()
    Clock = pg.time.Clock()
    Spaceship = Ship()
    Health_pts = HealthSystem(GAME_STARTING_HEALTH)
    Giftboxes = MysteryBoxes()
    Powerups = PowerupsOnScreen()
    TitleFont = pg.font.Font(FONTS["arcadeclassic"], 80)
    ClickToStartFont = pg.font.Font(FONTS["P2Start"], 18)
    Score_Font = pg.font.Font(FONTS["Orbitronbold"], 22)
    Game_end_Font = pg.font.Font(FONTS["arcadeclassic"], 48)
    RestartFont = pg.font.Font(FONTS["P2Start"], 15)

    ## Create and display background 
    background = pg.surface.Surface(size=Screen.get_size())
    background = background.convert()
    background.fill(color=COLOURS["black"])

    running = True
    
    while (running):
        dt = Clock.tick(60) # limit frame rate
        Spaceship.last_shot += dt
        elapsed_game_end += dt

        Screen.blit(background, (0, 0))

        update_and_draw_stars(Screen, stars) # draw stars in background


        ## User input handling
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN and game_start_menu:
                game_start_menu = False
        
        ## Spawn player's lasers
        mouseclicks = pg.mouse.get_pressed()
        if mouseclicks[0]:
            if (is_game_ending and just_entered_game_end): # reset timer
                elapsed_game_end = 0
                just_entered_game_end = False
            elif (is_game_ending and elapsed_game_end > fade_in_time): # condition to restart game on user input
                is_game_ending = False
                is_game_reset = True
            else: # mouseclicks otherwise spawn lasers
                coords, mode = Spaceship.shoot()
                if (coords != None):
                    Lasers.add(coords, mode)
        

        ## Draw Start menu
        if (game_start_menu):
            GameTitle = TitleFont.render("SPACE DEFENDER", False, COLOURS["dark_magenta"])
            pos_x = (Screen.get_width() // 2) - (GameTitle.get_width()//2)
            pos_y = (Screen.get_height() // 3)
            Screen.blit(GameTitle, (pos_x, pos_y))

            StartFont = ClickToStartFont.render("Click Enter to Start", False, COLOURS["cyan"])
            pos_x = (Screen.get_width() // 2) - (StartFont.get_width()//2)
            pos_y = (Screen.get_height() // 2) + (StartFont.get_height() * 2)
            Screen.blit(StartFont, (pos_x, pos_y))

            pg.display.flip()
            await asyncio.sleep(0)
            continue

        if (is_game_ending and not Health_pts.is_taking_damage):
            if (just_entered_game_end):
                elapsed_game_end = 0
                just_entered_game_end = False
            is_game_ending = game_over(Screen, Game_end_Font, RestartFont, elapsed_game_end, fade_in_time, hold_time)

            if (not is_game_ending):
                is_game_reset = True
            pg.display.flip()
            await asyncio.sleep(0)
            
            continue
            

        # game-end condition
        if (is_game_reset):
            Spaceship, Asteroids, Lasers, score, Health_pts, Giftboxes = \
            reset_game(Spaceship, Asteroids, Lasers, score, Health_pts, Giftboxes)
            is_game_reset = False


        ## Move player across screen
        keys = pg.key.get_pressed()
        if keys[pg.K_a] and Spaceship.rect.left > 0:
            Spaceship.rect.left -= Spaceship.move_speed
        if keys[pg.K_d] and Spaceship.rect.right < Screen.get_width():
            Spaceship.rect.right += Spaceship.move_speed
        if keys[pg.K_s] and Spaceship.rect.bottom < Screen.get_height():
            Spaceship.rect.bottom += Spaceship.move_speed
        if keys[pg.K_w] and Spaceship.rect.top > 0:
            Spaceship.rect.bottom -= Spaceship.move_speed


        ## Spawn asteroids randomly
        if (score < 50):
            score_buffer = math.sqrt(score)
        else:
            score_buffer = math.sqrt(score) + (score // 2)
        asteroid_spawn_rate = BASE_SPAWN_RATE + (score_buffer * GROW_SPEED)
        spawn_asteroids(Asteroids, Screen, asteroid_spawn_rate)

        ## Move asteroids
        collision_found = False
        for i in Asteroids.asteroids:
            asteroid_list = Asteroids.asteroids[i][:]
            for asteroid in asteroid_list:
                asteroid.rect.y += asteroid.speed # move downwards
                additional_bounds = 30 # extra distance till base dmg taken

                # Remove ones offscreen
                if asteroid.rect.top > Screen.get_height() + additional_bounds:
                    is_game_ending = Health_pts.take_damage()
                    if (is_game_ending):
                        # elapsed_game_end = 0
                        just_entered_game_end = True
                    Asteroids.asteroids[i].remove(asteroid)

                ## Asteroid-player collision
                if (Spaceship.rect.colliderect(asteroid)):
                    is_game_ending = Health_pts.take_damage()
                    if (is_game_ending):
                        # elapsed_game_end = 0
                        just_entered_game_end = True
                    Asteroids.asteroids[i].remove(asteroid)
                    collision_found = True
                    break
            if collision_found:
                break

        ## Draw asteroids and ship on screen
        Screen.blit(Spaceship.image, Spaceship.rect)
        Asteroids.display(Screen)

        ## Update all sprites
        score = Lasers.update(Screen, Asteroids, Giftboxes, score)
        Giftboxes.update(Spaceship, Powerups, Screen, Health_pts)
        Powerups.update(Screen, dt)
        Health_pts.update(Screen, dt)
        Spaceship.update(Screen, Health_pts, dt)
        score_text = Score_Font.render(f"Score: {score}", False, COLOURS["blue"])
        Screen.blit(score_text, (10, 10))

        pg.display.flip()
        await asyncio.sleep(0)
    pg.quit()


if __name__ == "__main__":
    asyncio.run(main())