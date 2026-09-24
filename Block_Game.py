import pygame
import random

# Import pygame.locals for easier access to key coordinates
from pygame.locals import (
    RLEACCEL,       # graphics accelerator constant, used to improve the quality of the game
    K_UP,           # up key
    K_DOWN,         # down key
    K_LEFT,         # left key
    K_RIGHT,        # right key
    K_ESCAPE,       # escape key
    KEYDOWN,        # down key
    QUIT,           # when the window is closed or game ends
    K_SPACE         # space bar (i added this one so that it will be my jump button instead of up arrow)
)

SCREEN_WIDTH = 800      # width of the screen (x = 0 is left side)
SCREEN_HEIGHT = 600     # #height of the screen ( y = 0 is the top, y = 600 is the bottom (i hate this btw))

SCROLL_DELAY = 15000       # 15 second delay before the player is no longer allowed to stand on the bottom and bottom level blocks start disappearing

last_removal_time =  pygame.time.get_ticks()        # putting this here so that it is defined, and we can put it in an if statement later and then modify it
start_time = pygame.time.get_ticks()                # getting the start time
REMOVAL_INTERVAL = 3000                             # three second interval which i want to be the time between instances where the bottom row of blocks get removed

BLOCK_WIDTH = 40        # setting the width i want the falling blocks to be
BLOCK_HEIGHT = 40       # setting the height that i want the falling blocks to be

millisecond_add_enemy = 250     # 250 milliseconds between each time a block spawns (this will increment)
last_spawn_update = pygame.time.get_ticks()         # getting the start time and putting it in last_spawn_update so that i can use it later and change its value
spawn_update_interval = 10000       # 10 seconds, the interval between the number of enemy sprites spawning getting increased

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):                             # these few lines are pretty much the same that was given to use
        super(Player, self).__init__()
        self.original_image = pygame.image.load("../images/game_player.png").convert_alpha()        # just changed the path
        self.player = pygame.transform.scale(self.original_image, (25, 50),)                    #changing the dimensions of the player image so that i like it
        #self.surf.set_colorkey((255, 255, 255), RLEACCEL)               #the white of the png will be disregarded
        self.rect = self.player.get_rect()                               #gets the rectangle for the hit box from the image size
        self.rect.top = SCREEN_HEIGHT-110                                        # where the player character spawns at
        self.rect.left = SCREEN_WIDTH-SCREEN_WIDTH/2            # put the spawn point around the bottom middle

        # defining variables that will help me with player physics/movement
        self.velocity_y = 0             # vel = 0 means no upward or downward movement
        self.gravity = 0.5                  # gravity variable that will get added to the velocity when jumping so that it goes back down toward SCREEN_HEIGHT
        self.jump_strength = -10                # variable to control how many blocks high the character jumps
        self.is_jumping = False          # setting a variable to designate whether the character is jumping or not


    # Move the sprite based on user keypresses
    def update(self, pressed_keys):
        change_in_x = 0                     # creating variable that will have the change in the x and y direction and setting them equal to 0 initially
        change_in_y = 0

        if pressed_keys[K_LEFT]:                # if the left key is pressed
            change_in_x = -5                    # the character will potentially move left 5 spaces depending on if the future conditions also allow that movement
        if pressed_keys[K_RIGHT]:               # if the right key is pressed
            change_in_x = 5                     # the character will potentially move right 5 spaces depending on if the subsequent conditions also allow that movement
        if pressed_keys[K_SPACE] == True and self.is_jumping == False:      # if the space bar is pressed, and the character had previously not been jumping
            self.velocity_y = self.jump_strength        # velocity is at -10, which means 10 units UPWARD
            self.is_jumping = True                     # changing the jumping boolean to true because it will now be jumping


        # handling gravity
        self.velocity_y += self.gravity     # adding the gravity constant to the velocity so that it will dampen with each update
        change_in_y += self.velocity_y      # and adding the velocity to the change in y

        # position before movement
        self.old_rect = self.rect.copy()        # getting a snapshot of the player's position before it is moved at all

        #actually moving the character
        self.rect.move_ip(change_in_x, change_in_y)

        # figuring out collisions with the blocks
        for block in enemies:                           # for each block in the list of ALL of the blocks, even ones still falling through the air
            if self.rect.colliderect(block.rect):           # if the player collides with the block
                if change_in_y < 0 and self.old_rect.top >= block.rect.bottom:      #and if the player is moving upwards and their body was lower than the bottom of the block
                    self.velocity_y = 0                         # change the velocity of the player to zero so they stop that movement
                    self.rect.top = block.rect.bottom           # change the players position to beneath the block
                if change_in_y >0 and self.old_rect.bottom <= block.rect.top:       # if player is moving down and the player's position before moving was above the top of the block (i.e. falling on it)
                    self.velocity_y = 0                             # change the velocity to zero
                    self.rect.bottom = block.rect.top               # change the bottom of the player rectangle to the top position of the block rectangle
                if change_in_x <=0 and self.old_rect.left >= block.rect.right:          # if the player is moving left and the left side of the players previous position is to the right of the block's right side
                    self.change_in_x = 0                                # change the change in x of zero
                    self.rect.left = block.rect.right                   # change the left side of the player to be equal to the right side of the block
                if change_in_x >=0 and self.old_rect.right <= block.rect.left:      # if the player is moving to the right and the player's old position right side was left of the blocks left side
                    self.chang_in_x = 0                                 # change the change in x to zero
                    self.rect.right = block.rect.left                   # move the right of the player equal to the left of the block


        # Keep player on the screen
        if self.rect.left < 0:                      # keeping the character on the screen
            self.rect.left = 0                      # this is taken from the sample code
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        # checking if the player is still allowed to jump on the ground
        current_time = pygame.time.get_ticks()          # getting the current time in the game
        elapsed_time = current_time - start_time        # getting the elapsed time


        # checking the position of the player to set the self.is_jumping
        for block in landed_blocks:                                             # for each block that has landed
            if self.rect.bottom == block.rect.top:                                 # if the bottom of the player is in the same position as the top of the landed block
                self.is_jumping = False                                             # set the jumping variable to False
                self.rect.bottom = block.rect.top                                       # set the player bottom to the top of the block
            elif elapsed_time < SCROLL_DELAY and self.rect.bottom == SCREEN_HEIGHT:       # if the elapsed time is lesser than the scroll delay and the player bottom is equal to screen height
                self.is_jumping  = False                                                # set the jumping boolean to false so that the player is able to jump of the bottom of the screen for the first 15 seconds





# Define the enemy object by extending pygame.sprite.Sprite
# The surface you draw on the screen is now an attribute of 'enemy'
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.original = pygame.image.load("../images/game_block_new.png").convert_alpha()       # change the path of the block image
        self.block_sprite = pygame.transform.scale(self.original, (BLOCK_WIDTH ,BLOCK_HEIGHT))      # change the dimensions of the block how i want
        self.rect = self.block_sprite.get_rect(                             # gets the rectangle for the hit box from the image size
            center=(                                                        # it takes the argument center, which sets the starting position of the enemies
                random.randint(0, SCREEN_WIDTH),                    # x = random int between 820 and 900
                random.randint(-100, -10),                           # y = somme number 0 to 600
            )
        )

        # Use the time to increase difficulty over time
        current_time = pygame.time.get_ticks()              #getting the current time
        elapsed_time = current_time - start_time            # getting the elapsed time
        seconds = elapsed_time // 1000                      # getting the amount of seconds that have passed
        slow = 2 + seconds//10                         # everytime 10 seconds have passed, the slow gets incremented by 2
        fast = 5 + seconds// 7                      # everytime 7 seconds have passed, the fast gets incremented 5
        self.speed = random.randint(slow, fast)      # setting speed to a random into between the slop variables and fast variable



    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self):        # update for the enemy is simpler


        # seeing what the block will look like if moved down at the speed
        next_rect = self.rect.move(0, self.speed)

        # concerning landing on blocks
        for block in landed_blocks:                         # for each block that has landed
            if next_rect.colliderect(block.rect):               # if the next position of the block rectangle is going to collide with a landed block
                # Land on top only if falling from above
                if self.rect.bottom <= block.rect.top:          # if the block bottom is higher than the landed block top
                    self.rect.bottom = block.rect.top           # then the falling block bottom is set equal to the landed block top
                    landed_blocks.add(self)                     # and added the falling block (now landed) to the landed_blocks group
                    self.speed = 0                          # set the speed of the now landed block to zero
                    return                                 #break the method

        # moving the block down
        self.rect.move_ip(0, self.speed)                    #now actually moving the block down


        # making the blocks stop at the bottom
        if self.rect.bottom >= SCREEN_HEIGHT:           #if the bottom of the block is lower or equal to the screen height
            self.rect.bottom = SCREEN_HEIGHT            # then set the bottom of the block equal to the screen height
            landed_blocks.add(self)                     # and add the block to the landed_blocks group
            self.speed = 0                              # and get the block to stop moving
            return                                      # break the method



# creating a function to draw the time on the screen (instead of the score)
def draw_time():
    current_time = pygame.time.get_ticks()          # getting the current time
    elapsed_time = current_time - start_time        # getting the elapsed time
    seconds = elapsed_time // 1000                  # converting the elapsed time to seconds

    time_surface = SCORE_FONT.render(f"Time: {seconds}", True, (255, 255, 255))     # creates a surface that is the text, antialias means the edges are smooth if True, color is white
    screen.blit(time_surface, dest = (10, 10))     # upper left corner (10,10)      # putting the time surface on the screen near the top left

# initiating pygame
pygame.init()

# setting a variable for the font of the score text
SCORE_FONT = pygame.font.Font(None, 36)

# making the screen with the set dimensions
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# msking id numbers for spawning enemy event
ADDENEMY = pygame.USEREVENT + 1                 # every 250 milliseconds it creates a user event, number it plus one, and add an enemy
pygame.time.set_timer(ADDENEMY, millisecond_add_enemy)

# initiating the player class
player = Player()

# loading the image for the background in imgBg
imgBg = pygame.image.load("../images/game_background.png").convert()

# making a group for the enemies (all blocks)
enemies = pygame.sprite.Group()

# making a group for the landed blocks
landed_blocks = pygame.sprite.Group()

# making a group for all sprites (all blocks and the character)
all_sprites = pygame.sprite.Group()
all_sprites.add(player)     # adding the player's character
all_sprites.add(enemies)    # adding all blocks

# variable to run the while loop while it is true
running = True

# will help control the frame rate later
clock = pygame.time.Clock()

# getting the start time again
start_time = pygame.time.get_ticks()

##################################### Main game loop ##################################
# Main loop, this is all from the sample code
while running:
    # for loop through the event queue
    for event in pygame.event.get():
        # Check for KEYDOWN event
        if event.type == KEYDOWN:
            # If the Esc key is pressed, then exit the main loop
            if event.key == K_ESCAPE:
                running = False
        # Check for QUIT event. If QUIT, then set running to false.
        elif event.type == QUIT:
            running = False
        # Add a new enemy?
        elif event.type == ADDENEMY:
            # Create the new enemy and add it to sprite groups
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

    # Get the set of keys pressed and check for user input
    pressed_keys = pygame.key.get_pressed()
    #update player
    player.update(pressed_keys)

    # Update enemy position
    enemies.update()

    # deleting any blocks that go beneath the bottom of the screen
    # this shouldn't happen but just putting it here to make sure
    for enemy in list(enemies):         # for each block in all blocks group
        if enemy.rect.top > SCREEN_HEIGHT:      # if the block is copletely beneath the screen
            enemies.remove(enemy)               # remove the block from the enemies group
            all_sprites.remove(enemy)           # remove the block from the all sprite group
            enemy.kill()                    # killing the enemy

    # deleting any blocks that have landed and are above the screen's view
    for block in list(landed_blocks):          # for all blocks in the landed blocks group
        if block.rect.bottom <= 0:           # if the bottom of the rectangle is above the screen
            landed_blocks.remove(block)         # remove the block from the landed_blocks group
            all_sprites.remove(block)           # remove the block from the all sprites group

    # getting the current time and the elapsed time
    current_time = pygame.time.get_ticks()
    elapsed = current_time - start_time

    # removing the bottom row of blocks. this happens for the first time after 15 seconds, and then after that once every three seconds (this amount decreases though)
    if elapsed > SCROLL_DELAY and current_time - last_removal_time > REMOVAL_INTERVAL:      # if the elapsed time is greater than the scroll delay and enought time has based since the last removal of bottom blocks
        for block in landed_blocks:                     # for each landed block
            if block.rect.bottom == SCREEN_HEIGHT:          # if the bottom of the block is at the bottom of the screen
                landed_blocks.remove(block)                 # remove the block from all groups and kill it
                all_sprites.remove(block)
                enemies.remove(block)
                block.kill()
        for blocks in landed_blocks:                    # for every other landed block
            blocks.rect.move_ip(0, 40)              # we move them downwards, and the amount we move it down is the height of a block
        REMOVAL_INTERVAL-= 100                          # decreasing the removal interval each time this happens
        if REMOVAL_INTERVAL <= 1200:                # making sure the removal interval doesn't get to fast
            REMOVAL_INTERVAL = 1200

        last_removal_time = current_time            # getting the current time so we know when blocks were last removed

    # getting the time again
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - start_time

    # handling if the player looses
    if elapsed_time > SCROLL_DELAY and player.rect.bottom >= SCREEN_HEIGHT:     # if the elapsed time is greater than 15 seconds and the bottom of the player is at the bottom of the screen
        print("You lost!")
        running = False     # stop the while loop

    # spawning new blocks
    if current_time - last_spawn_update >= spawn_update_interval:       # if enough time between te spawn interval has passed
        millisecond_add_enemy = max(170, millisecond_add_enemy - 25)     # Decrease interval (not below 100ms)
        pygame.time.set_timer(ADDENEMY, millisecond_add_enemy)          # get the timer to add enemy
        last_spawn_update = current_time                            # update the last spawn time

    # Fill the screen color
    screen.fill((23,183,232))           # not sure if this line is still needed but leaving it here

    # to use an image as the background instead of solid color
    screen.blit(imgBg, dest=(0, 0))  # upper corner at (0,0)

    # Draw all sprites
    for entity in all_sprites:
        if isinstance(entity, Player):                  # if the sprite is the player
            screen.blit(entity.player, entity.rect)     # putting the player on the screen
        elif isinstance(entity, Enemy):                 # if the sprite is a block
            screen.blit(entity.block_sprite, entity.rect)   # putting the block on the screen

    # calling the function to put the time on the screen
    draw_time()

    # Update the display
    pygame.display.flip()

    # Ensure program maintains a rate of 30 frames per second
    clock.tick(60)

################################ Out of the Game loop now ################################

# getting the final time so we can show the user how long they lasted
final_time = (pygame.time.get_ticks() - start_time) // 1000

# Create message surfaces
end_font = pygame.font.Font(None, 48)                       # making the font for the end game message
end_text = end_font.render("Game Over", True, (255, 0, 0))      # creating the game over text, making it red
time_text = SCORE_FONT.render(f"Time Survived: {final_time} seconds", True, (255, 255, 255))        # creating the final time message, white
instruction_text = SCORE_FONT.render("Press ESC to quit", True, (255, 255, 255))                # telling the user to press esc to stop running the program, white

# creating the rectangle for the texts
end_text_rect = end_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))      # putting the around the center of the screen
time_text_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
instruction_text_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

# Wait for user to quit or press ESC
paused = True
while paused:
    for event in pygame.event.get():
        if event.type == QUIT:
            paused = False
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            paused = False

    screen.fill((0, 0, 0))  # black background
    screen.blit(end_text, end_text_rect)        # drawing the game over message on the screen
    screen.blit(time_text, time_text_rect)          # putting the time text on the screen
    screen.blit(instruction_text, instruction_text_rect)        # putting the quit instructions on the screen
    pygame.display.flip()                           # updating the window with all of this stuff
    clock.tick(30)          # setting the frame rate to 30
