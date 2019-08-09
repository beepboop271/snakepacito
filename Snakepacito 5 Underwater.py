#########################################
# File Name: Kevin Qiao - Snake Game.py
# Description: ICS2OG Snake Assignment
# Author: Kevin Qiao
# Date: 2018-11-17
#########################################
import random
import pygame
import time

pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()

# --------------------------------------- #
# constants and variables                 #
# --------------------------------------- #
# display and game grid #################
width = 800
height = 600
display = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Snakepacito 5: Underwater (Deluxe Edition) (Collector's Edition) (NEW UPDATES)")
pygame.display.set_icon(pygame.image.load("assets/images/icon.png").convert_alpha())

GRID_SIZE = 20  # Each grid is n by n pixels
gridWidth = width/GRID_SIZE
gridHeight = height/GRID_SIZE

window = "Title"

# surfaces and images ###################

# Full resolution surfaces that are not touched by scaling, so if the game window is scaled to a small
# size then back to a large one quality doesn't deteriorate
TITLE_BACKGROUND_MASTER = pygame.image.load("assets/images/title.png").convert()
GAME_BACKGROUND_MASTER = pygame.image.load("assets/images/underwater2160.png").convert()
TITLE_TEXT_MASTER = pygame.image.load("assets/images/title text.png").convert_alpha()
WARNING_SEGMENT_MASTER = pygame.image.load("assets/images/warning.png").convert_alpha()
LORE_BACKGROUND_MASTER = pygame.image.load("assets/images/lore.png").convert()

# The actual surfaces that are drawn and scaled
titleBackground = TITLE_BACKGROUND_MASTER.copy()
gameBackground = GAME_BACKGROUND_MASTER.copy()
titleText = TITLE_TEXT_MASTER.copy()
warningSegment = pygame.transform.scale(WARNING_SEGMENT_MASTER, (GRID_SIZE, int(float(GRID_SIZE)/WARNING_SEGMENT_MASTER.get_width()*WARNING_SEGMENT_MASTER.get_height())))
leftWarningSegment = pygame.transform.rotate(warningSegment, 90)
rightWarningSegment = pygame.transform.rotate(warningSegment, -90)
loreBackground = LORE_BACKGROUND_MASTER.copy()

# semi-transparent overlay surface
GRAY_OVERLAY = pygame.Surface((100, 100), pygame.SRCALPHA)
GRAY_OVERLAY.fill((150, 150, 150, 100))

# surfaces that never get scaled
COIN = pygame.transform.scale(pygame.image.load("assets/images/coin.png").convert_alpha(), (GRID_SIZE, GRID_SIZE))
OBSTACLE_TEXTURES = [pygame.image.load("assets/images/concrete1600.png").convert(), pygame.image.load("assets/images/rocks1024.png").convert(), pygame.image.load("assets/images/sharp rocks1024.png").convert()]
WARNING_SIGN = pygame.image.load("assets/images/warning sign.png").convert_alpha()

# solid colour overlay surfaces
SCORE_BACKGROUND = pygame.transform.scale(GRAY_OVERLAY, (100, 40))
TIME_BACKGROUND = pygame.transform.scale(GRAY_OVERLAY, (170, 50))
TITLE_INFO_OVERLAY = pygame.transform.scale(GRAY_OVERLAY, (400, 310))
pauseOverlay = pygame.transform.scale(GRAY_OVERLAY, (width, height))

# sounds and music ######################
deathSound = pygame.mixer.Sound("assets/sounds/oof.wav")
coinSound = pygame.mixer.Sound("assets/sounds/coin.wav")
coinSound.set_volume(0.6)
music = pygame.mixer.music.load("assets/sounds/toto-africa noteblock loop.ogg")
pygame.mixer.music.set_volume(0.3)

# fonts #################################
COMIC_SANS_30 = pygame.font.SysFont("Comic Sans MS", 30)    # Body text
COMIC_SANS_20 = pygame.font.SysFont("Comic Sans MS", 20)      #
IMPACT_70 = pygame.font.SysFont("Impact", 70)                # Titles
COURIER_NEW_30 = pygame.font.SysFont("Courier New", 30)       # Monospace font for time and score

# colours ###############################
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# score #################################
score = 0

# difficulty ############################
difficulty = 1
DIFFICULTIES = ["Easy", "Normal", "Hard", "Very Hard", "Probably Impossible"]

# time and speed ########################

# constants and variables in a list of length of length 5 in this section
# are to keep different rates and starting speeds for different difficulties

# required increase in score to increase speeds
SPEED_INTERVAL = 2
# amounts to increase speed
FPS_SPEED_RATE = [1, 1, 2, 3, 4]
OBSTACLE_SPEED_RATE = [0.05, 0.05, 0.07, 0.09, 0.1]
OBSTACLE_MAX_INTERVALS = [1.5, 1, 0.6, 0.6, 0.2]        # don't let the obstacle interval get lower than this

# snake and obstacle starting speeds
frame = 0
fps = [20, 20, 20, 30, 35]                  # snake and obstacle speed
obstacleInterval = [1.5, 1.5, 1, 1, 0.7]    # time between each new obstacle generation

# timer and timing
CLOCK = pygame.time.Clock()
periodStart = time.time()
INITIAL_TIME = 30
timeElapsed = 0
periodElapsed = 0

# create an event every COIN_DELAY ms on the event queue with the id GENERATE_COIN
# this custom event is handled in the event processing to generate a new coin
COIN_DELAY = 3000
GENERATE_COIN = pygame.USEREVENT
pygame.time.set_timer(GENERATE_COIN, COIN_DELAY)

# starting elements #####################

# make the first coin
coinX = [random.randint(1, gridWidth-1)]
coinY = [random.randint(1, gridHeight-1)]

# make the snake
HEAD = 0                                # for reading array indices
START_LENGTH = 4
SPEED = 1
dx = 0
dy = -SPEED                             # initially the snake moves upwards
segX = []
segY = []
segColours = []
GRADIENT_INTERVAL = 5                    # every n segments, blend to a new colour
for i in range(START_LENGTH):           # add coordinates for the head and 3 segments
    segX.append(gridWidth/2)
    segY.append(gridHeight + i)
for i in range(START_LENGTH/GRADIENT_INTERVAL+2):  # add starting colours for the gradients
    segColours.append((random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))

# create the obstacles list
obstacles = []
# constants to make reading obstacle handling code easier to read
SURFACE = 0                 # the surface (image) that holds the obstacle
X = 1                       # x position
Y = 2                       # y position
WARNING_STATUS = 3          # whether or not to draw a precise warning, vague warning, or no warning
WIDTH = 4                   # width of the obstacle
HEIGHT = 5                  # height of the obstacle
SCALE = 6                   # size of each obstacle node, in pixels
COLLISION_RECTANGLES = 7    # list of rectangles to check for collision
DIRECTION = 8               # direction of the obstacle, as [dx, dy]
DX = 0
DY = 1

# --------------------------------------- #
# functions                               #
# --------------------------------------- #

# "utility" functions ###################
# Functions not really specific to any game and just do some general task

def drawCenteredText(x, y, font, text, border, padding=0):
    # Draws text centered at x,y
    TEXT_WIDTH, TEXT_HEIGHT = 0, 1
    textSize = font.size(text)
    if border:
        pygame.draw.rect(display, BLACK, (x-textSize[TEXT_WIDTH]/2-padding, y-textSize[TEXT_HEIGHT]/2-padding, 2*padding+textSize[TEXT_WIDTH], 2*padding+textSize[TEXT_HEIGHT]))
    display.blit(font.render(text, 1, WHITE), (x-textSize[TEXT_WIDTH]/2, y-textSize[TEXT_HEIGHT]/2))

def drawCenteredSurface(x, y, surface):
    # Draw a surface (can be an image) centered at x,y
    SURFACE_WIDTH, SURFACE_HEIGHT = 0, 1
    surfaceSize = surface.get_size()
    display.blit(surface, (x-surfaceSize[SURFACE_WIDTH]/2, y-surfaceSize[SURFACE_HEIGHT]/2))

def rgbSlerp(rgb1, rgb2, offset):
    # Spherical Linear intERPolation between two RGB colours (two points in a cube)
    # i.e. calculate colours in between rgb1 and rgb2 to produce a gradient
    rgb1 = pygame.math.Vector3(rgb1)  # An rgb colour is just a 3d vector and can be treated as such
    rgb2 = pygame.math.Vector3(rgb2)
    newRgb = rgb1.slerp(rgb2, offset)  # Slerp-ing produces better looking transformations compared to lerp-ing
    return max(0, min(newRgb.x, 255)), max(0, min(newRgb.y, 255)), max(0, min(newRgb.z, 255))  # Clamp values to 0-255 (Slerp-ing sometimes produces >255 results)

def matteTexture(mask, image):
    # Returns a random section of "image" with only the pixels present in "mask", i.e. "image" with the shape of "mask"
    # Mask must be solid white
    minX = -image.get_width()+mask.get_width()
    minY = -image.get_height()+mask.get_height()
    # Multiply each pixel of "image" with the corresponding pixel of "mask", since "mask" is either white or black, values are essentially multiplied by 0 or 1,
    # eliminating all pixels from "image" that don't belong.
    mask.blit(image, (random.randint(minX, 0), random.randint(minY, 0)), None, pygame.BLEND_MULT)
    return mask

def scaleImage(image, w, h):
    # Scale images to the correct resolution while maintaining 1:1 ratio
    if w > h:
        newImage = pygame.transform.smoothscale(image, (w, w))
    else:
        newImage = pygame.transform.smoothscale(image, (h, h))
    return newImage

def splitParagraph(maxLineWidth, paragraph):
    # Split a very long string into lines of at most maxLineWidth characters,
    # searching for a space " " to end the line
    i = -1
    lines = []
    nextLine = ""
    while len(paragraph) >= maxLineWidth:
        nextLine = paragraph[:maxLineWidth]
        if nextLine[i] == " ":
            lines.append(nextLine[:i])
            paragraph = paragraph[(maxLineWidth+i+1):]
            i = -1
        else:
            i = i-1
    lines.append(paragraph)
    return lines

# element drawing functions #############
# functions that draw an element on a screen (not the whole window)

def drawMenu():
    # Draw the menu information text
    menuTop = min(titleText.get_height()/6, 175)

    drawCenteredText(width/2, menuTop+20, COMIC_SANS_20, "Difficulty:", False)
    drawCenteredText(width/2, menuTop+55, COMIC_SANS_20, DIFFICULTIES[difficulty], True, 5)
    drawCenteredText(width/2, menuTop+90, COMIC_SANS_20, "Use L+R arrow keys to change", False)

    drawCenteredText(width/2, menuTop+130, COMIC_SANS_20, "Resolution can be adjusted like a normal", False)
    drawCenteredText(width/2, menuTop+155, COMIC_SANS_20, "window (drag corners, maximize, etc)", False)

    drawCenteredText(width/2, menuTop+205, COMIC_SANS_20, "Press L for lore, ESC to pause/unpause,", False)
    drawCenteredText(width/2, menuTop+230, COMIC_SANS_20, "and WASD to move the snake", False)

def drawParagraph(lines, top, lineSpacing, font):
    # Draw a paragraph using a list of lines
    for i in range(len(lines)):
        drawCenteredText(width/2, top+lineSpacing*i, font, lines[i], False)

def drawObstacles():
    # Draw obstacles and obstacle warnings
    for obstacle in obstacles:
        display.blit(obstacle[SURFACE], (obstacle[X]*GRID_SIZE, obstacle[Y]*GRID_SIZE))
        if obstacle[WARNING_STATUS] == 2:  # precise (red) warnings
            # convert obstacle x and y into screen coordinates, then clamp them to being on the screen
            warningX = max(0, min(obstacle[X]*GRID_SIZE, width))
            warningY = max(0, min(obstacle[Y]*GRID_SIZE, height))
            # draw the appropriate warning for the direction (e.g. don't draw a left facing warning if its going down)
            if obstacle[DIRECTION] == [0, 1]:
                for i in range(obstacle[WIDTH]*obstacle[SCALE]/GRID_SIZE):
                    # The warningSegment image is an image with the width of one grid unit, so draw it for each grid unit the obstacle takes
                    display.blit(warningSegment, (warningX+(i*GRID_SIZE), warningY))
            elif obstacle[DIRECTION] == [-1, 0]:
                for i in range(obstacle[HEIGHT]*obstacle[SCALE]/GRID_SIZE):
                    display.blit(rightWarningSegment, (warningX-rightWarningSegment.get_width(), warningY+(i*GRID_SIZE)))
            elif obstacle[DIRECTION] == [1, 0]:
                for i in range(obstacle[HEIGHT]*obstacle[SCALE]/GRID_SIZE):
                    display.blit(leftWarningSegment, (warningX, warningY+(i*GRID_SIZE)))
        elif obstacle[WARNING_STATUS] == 1:  # vague (yellow) warnings
            # get the middle x and y position to draw the warning
            warningX = obstacle[X]*GRID_SIZE+(obstacle[WIDTH]*obstacle[SCALE])/2
            warningY = obstacle[Y]*GRID_SIZE+(obstacle[HEIGHT]*obstacle[SCALE])/2
            warningOffset = WARNING_SIGN.get_width()/2
            display.blit(WARNING_SIGN, (max(0, min(warningX-warningOffset, width-2*warningOffset)), max(0, min(warningY-warningOffset, height-2*warningOffset))))
            drawCenteredSurface(max(16, min(warningX, width-16)), max(16, min(warningY, height-16)), WARNING_SIGN)

# window drawing functions ##############
# functions that an entire window

def redrawTitle():
    menuTop = min(titleText.get_height()/6, 175)

    drawCenteredSurface(width/2, height/2, titleBackground)
    drawCenteredSurface(width/2, titleText.get_height()/14, titleText)
    drawCenteredSurface(width/2, menuTop+TITLE_INFO_OVERLAY.get_height()/2, TITLE_INFO_OVERLAY)

    drawMenu()
    drawCenteredText(width/2, menuTop+280, COMIC_SANS_20, "Press ENTER to play (read lore first)", False)

def redrawGame():
    CIRCLE_OFFSET = GRID_SIZE/2
    drawCenteredSurface(width/2, height/2, gameBackground)

    # Draw the apples
    for i in range(len(coinX)):
        drawCenteredSurface(coinX[i]*GRID_SIZE+CIRCLE_OFFSET, coinY[i]*GRID_SIZE+CIRCLE_OFFSET, COIN)

    # Draw the snake segments
    currentGradients = 1
    for i in range(len(segX)):
        # Switch gradient colours every n segments, n = GRADIENT_INTERVAL
        if i % (GRADIENT_INTERVAL*currentGradients) == 0 and i != 0:
            currentGradients = currentGradients+1
        # Interpolate between each different colour by getting an offset (0-1) that determines how much of each colour to blend
        gradientOffset = 1-((i % GRADIENT_INTERVAL)*(1.0/GRADIENT_INTERVAL))
        # Draw a black circle as an ourline, then fill the segment and pick the appropriate colour in the gradient of the two random colours
        pygame.draw.circle(display, BLACK, (segX[i]*GRID_SIZE+CIRCLE_OFFSET, segY[i]*GRID_SIZE+CIRCLE_OFFSET), CIRCLE_OFFSET+1)
        if i == 0:
            # get the rectangle containing the head to use for obstacle collision detection
            headRect = pygame.draw.circle(display, segColours[currentGradients-1], (segX[i]*GRID_SIZE+CIRCLE_OFFSET, segY[i]*GRID_SIZE+CIRCLE_OFFSET), CIRCLE_OFFSET)
        else:
            pygame.draw.circle(display, (rgbSlerp(segColours[currentGradients], segColours[currentGradients-1], gradientOffset)), (segX[i]*GRID_SIZE+CIRCLE_OFFSET, segY[i]*GRID_SIZE+CIRCLE_OFFSET), CIRCLE_OFFSET)

    drawObstacles()

    drawCenteredSurface(width/2, 25, TIME_BACKGROUND)
    drawCenteredSurface(width/2, 70, SCORE_BACKGROUND)
    drawCenteredText(width/2, 25, COURIER_NEW_30, str(INITIAL_TIME-timeElapsed-periodElapsed)[:6], False)
    drawCenteredText(width/2, 70, COURIER_NEW_30, str(score), False)

    return headRect

def redrawPause():
    drawCenteredSurface(width/2, height/2, pauseOverlay)
    drawCenteredText(width/2, 50, IMPACT_70, "PAUSED", False)
    drawMenu()

def redrawLore():
    top = 10
    lineSpacing = 25
    paragraph1 = splitParagraph(width/10, "After a saddening loss in the Despongcito (in space) battle, the Despaclan retreated to a nearby planet, Htrae. Known for its vast oceans and warm waters, Htrae was a perfect habitat for the Despacito spiders. Adventuring around the planet, our Despaheros stumbled across a magnifient shipwreck from ages before. Setting up a camp nearby, the Despaclan planned to thoroughly explore this derelict construction. However, soon after, the evil primes ambushed the Despaclan, attempting to once again eliminate the Despacito spiders.")
    paragraph2 = splitParagraph(width/10, "Our Despaheros, not willing to be defeated again, used the familiar environment of the oceans against the primes, who had malicious snake bots to not only attack the Despacito spiders, but also steal treasure from the shipwreck. In an amazing feat of strength, Nivek Hpesoj started to throw concrete blocks at the primes' bots, but unfortunately, he wasn't very accurate, made worse by the fact that the prime bots were only weak in the head...")
    paragraph3 = splitParagraph(width/10, "(You are an evil prime bot- collect as many coins as you can and don't let the concrete blocks hit your head!)")
    paragraph4 = splitParagraph(width/10, "PRESS ENTER TO PLAY")

    drawCenteredSurface(width/2, height/2, loreBackground)
    drawParagraph(paragraph1, top, lineSpacing, COMIC_SANS_20)
    drawParagraph(paragraph2, top+lineSpacing*(len(paragraph1)+0.2), lineSpacing, COMIC_SANS_20)
    drawParagraph(paragraph3, top+lineSpacing*(len(paragraph1)+len(paragraph2)+0.4), lineSpacing, COMIC_SANS_20)
    drawParagraph(paragraph4, top+lineSpacing*(len(paragraph1)+len(paragraph2)+len(paragraph3)+1), lineSpacing, COMIC_SANS_20)

def redrawEndScreen():
    drawCenteredSurface(width/2, height/2, loreBackground)
    drawCenteredText(width/2, 80, IMPACT_70, "Score: "+str(score), False)
    drawCenteredText(width/2, 170, IMPACT_70, "Time Left: "+str(max(0, INITIAL_TIME-periodElapsed-timeElapsed))[:5], False)

    drawCenteredText(width/2, 300, COMIC_SANS_30, "ENTER to play again", False)
    drawCenteredText(width/2, 350, COMIC_SANS_30, DIFFICULTIES[difficulty], True, 5)

    drawCenteredText(width/2, 400, COMIC_SANS_30, "Close the window to exit, or press ESC", False)

# game specific utility functions #######
# functions that do something fairly specific for this game

def generateNodeList(numNodes):
    # Generates a list of connected nodes
    X, Y = 0, 1
    index = 1
    nodesX = [numNodes]
    nodesY = [numNodes]
    newNode = []
    # Generate the nodes by picking a random direction to move off in from the last node,
    # and discarding the result and trying again if the new node is already in the structure
    while len(nodesX) <= numNodes:
        nodeDirection = random.randint(1, 4)
        if nodeDirection == 1:
            newNode = (nodesX[index-1], nodesY[index-1]-1)
        elif nodeDirection == 2:
            newNode = (nodesX[index-1]+1, nodesY[index-1])
        elif nodeDirection == 3:
            newNode = (nodesX[index-1], nodesY[index-1]+1)
        elif nodeDirection == 4:
            newNode = (nodesX[index-1]-1, nodesY[index-1])

        isUnique = True
        for i in range(len(nodesX)):
            if newNode[X] == nodesX[i] and newNode[Y] == nodesY[i]:
                isUnique = False
        if isUnique:
            nodesX.append(newNode[X])
            nodesY.append(newNode[Y])
            index = index+1

    # Shift all values in the node list so that the minimum values of X and Y are 0
    shiftX = -min(nodesX)
    shiftY = -min(nodesY)
    for i in range(len(nodesX)):
        nodesX[i] = nodesX[i]+shiftX
        nodesY[i] = nodesY[i]+shiftY

    return nodesX, nodesY

def drawNodeList(nodesX, nodesY, squareSize):
    # Draw a list of nodes as squares on a surface
    rectList = []
    surface = pygame.Surface(((max(nodesX)+1)*squareSize, (max(nodesY)+1)*squareSize), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    for i in range(len(nodesX)):
        rectList.append(pygame.draw.rect(surface, WHITE, (nodesX[i]*squareSize, nodesY[i]*squareSize, squareSize, squareSize)))
    surface = matteTexture(surface, OBSTACLE_TEXTURES[random.randint(0, len(OBSTACLE_TEXTURES)-1)])

    return surface, rectList

def generateObstacle(squareSize):
    # Returns a surface of an obstacle that consists of adjacent identical squares (like tetris),
    # as well as other attributes needed to process the obstacle
    X, Y = 0, 1
    numNodes = random.choice([1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6])  # Weighted random number generation

    nodesX, nodesY = generateNodeList(numNodes)
    obstacleSurface, collideRectList = drawNodeList(nodesX, nodesY, squareSize)
    obstacleHeight = max(nodesY)+1  # Add one because 0 is still a node in the obstacle
    obstacleWidth = max(nodesX)+1

    # choose directions and which kind of warning to show based on the difficulty
    if difficulty == 1:
        direction = [0, 1]
        warningPrecision = 2
    elif difficulty == 2:
        direction = random.choice(([-1, 0], [0, 1], [0, 1], [0, 1], [1, 0]))  # more likely to choose top to bottom
        warningPrecision = 2
    elif difficulty > 2:
        direction = random.choice(([-1, 0], [0, 1], [1, 0], [0, -1]))
        warningPrecision = 1

    # choose starting coords based on direction
    if direction[X] == 0:
        startX = random.randint(0, gridWidth-(obstacleWidth*(squareSize/GRID_SIZE)))
        if direction[Y] == 1:
            startY = -gridHeight-obstacleHeight
        else:
            startY = 2*gridHeight+obstacleHeight
    else:
        startY = random.randint(0, gridHeight-(obstacleHeight*(squareSize/GRID_SIZE)))
        if direction[X] == -1:
            startX = 2*gridWidth+obstacleWidth
        else:
            startX = -gridWidth-obstacleWidth

    return [obstacleSurface, startX, startY, warningPrecision, obstacleWidth, obstacleHeight, squareSize, collideRectList, direction]

def headIsOutsideGame(headX, headY, gameWidth, gameHeight):
    # Returns if the head is outside the playable area and in which dimension
    if (headX >= gameWidth or headX < 0) and (headY >= gameHeight or headY < 0):
        info = (True, 2)
    elif headX >= gameWidth or headX < 0:
        info = (True, 0)
    elif headY >= gameHeight or headY < 0:
        info = (True, 1)
    else:
        info = (False, -1)
    return info

def pushSnakeIntoGame(direction, segX, segY):
    # If resizing the game made the snake leave the playable area, move it back into the game
    X, Y = 0, 1
    if direction == 0:
        posDelta = [segX[HEAD]-gridWidth, 0]
    elif direction == 1:
        posDelta = [0, segY[HEAD]-gridHeight]
    elif direction == 2:
        posDelta = [segX[HEAD]-gridWidth, segY[HEAD]-gridHeight]
    else:
        return segX, segY
    for i in range(len(segX)):
        segX[i] = segX[i]-posDelta[X]-2
        segY[i] = segY[i]-posDelta[Y]-2
    return segX, segY

# --------------------------------------- #
# main program                            #
# --------------------------------------- #

# scale images to the right resolution while maintaining proportions
titleBackground = scaleImage(TITLE_BACKGROUND_MASTER, width, height)
titleText = scaleImage(TITLE_TEXT_MASTER, min(width, 1200), min(height, 1200))
gameBackground = scaleImage(GAME_BACKGROUND_MASTER, width, height)
loreBackground = scaleImage(LORE_BACKGROUND_MASTER, width, height)

obstacleTimer = time.time()

pygame.mixer.music.play(-1)

# main loop
running = True
while running:
    # timing
    CLOCK.tick(fps[difficulty])
    frame = (frame+1) % fps[difficulty]

    # event queue processing
    difficultyChanged = False
    for event in pygame.event.get():
        if window == "Game":
            if event.type == GENERATE_COIN:
                coinX.append(random.randint(0, gridWidth-1))
                coinY.append(random.randint(0, gridHeight-1))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    window = "Pause"
                    timeElapsed = timeElapsed + periodElapsed
                    periodElapsed = 0
        elif window == "Title" or window == "Pause" or window == "End":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    difficulty = max(0, difficulty-1)
                    difficultyChanged = True
                elif event.key == pygame.K_RIGHT:
                    difficulty = min(len(DIFFICULTIES)-1, difficulty+1)
                    difficultyChanged = True
                elif event.key == pygame.K_l:
                    window = "Lore"
                elif event.key == pygame.K_ESCAPE:
                    if window == "Pause":
                        window = "Game"
                        periodStart = time.time()
                    elif window == "End":
                        running = False
        if event.type == pygame.VIDEORESIZE:
            width = max(600, event.w)
            height = max(550, event.h)
            gridWidth = width/GRID_SIZE
            gridHeight = height/GRID_SIZE
            # rescale surfaces
            display = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            titleBackground = scaleImage(TITLE_BACKGROUND_MASTER, width, height)
            titleText = scaleImage(TITLE_TEXT_MASTER, min(width, 1200), min(height, 1200))
            loreBackground = scaleImage(LORE_BACKGROUND_MASTER, width, height)
            gameBackground = scaleImage(GAME_BACKGROUND_MASTER, width, height)
            pauseOverlay = pygame.transform.scale(GRAY_OVERLAY, (width, height))
            # "push" the snake back into the game area if resizing the window made it leave the playable area
            headInfo = headIsOutsideGame(segX[HEAD], segY[HEAD], gridWidth, gridHeight)
            if headInfo[0]:
                segX, segY = pushSnakeIntoGame(headInfo[1], segX, segY)
        elif event.type == pygame.QUIT:  # if the exit button on the window has been clicked
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if window == "End":
                    # reset game
                    score = 0
                    frame = 0
                    fps = [20, 20, 20, 30, 35]
                    timeElapsed = 0
                    periodElapsed = 0
                    obstacleInterval = [1.5, 1.5, 1, 1, 0.7]
                    obstacles = []
                    coinX = [random.randint(1, gridWidth-1)]
                    coinY = [random.randint(1, gridHeight-1)]
                    dx = 0
                    dy = -SPEED
                    segX = []
                    segY = []
                    segColours = []
                    for i in range(START_LENGTH):
                        segX.append(gridWidth/2)
                        segY.append(gridHeight + i)
                    for i in range(START_LENGTH/GRADIENT_INTERVAL+2):
                        segColours.append((random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
                window = "Game"
                periodStart = time.time()
    if difficultyChanged:
        # change the speeds to be appropriate for the given difficulty if the difficulty was changed in the middle
        # of the game (e.g. if 10 coins were obtained in easy mode, then the user switched to hard, the speed would
        # adjust accordingly)
        fps[difficulty] = fps[difficulty]+(score/SPEED_INTERVAL*FPS_SPEED_RATE[difficulty])
        obstacleInterval[difficulty] = max(OBSTACLE_MAX_INTERVALS[difficulty], obstacleInterval[difficulty]-(score/SPEED_INTERVAL*OBSTACLE_SPEED_RATE[difficulty]))

    # processing and drawing
    keys = pygame.key.get_pressed()
    if window == "Title":
        redrawTitle()
    elif window == "Game":
        headRect = redrawGame()
        # generate the obstacles
        if time.time()-obstacleTimer > obstacleInterval[difficulty] and difficulty > 0:
            obstacleTimer = time.time()
            obstacles.append(generateObstacle(random.randint(1, 3)*GRID_SIZE))
            for i in range(len(obstacles[-1][COLLISION_RECTANGLES])):
                # align the rectangles of the obstacle from obstacle coordinates to screen coordinates
                obstacles[-1][COLLISION_RECTANGLES][i].move_ip(obstacles[-1][X]*GRID_SIZE, obstacles[-1][Y]*GRID_SIZE)
        for i in range(len(obstacles)-1, -1, -1):
            # check for collision with the head
            if headRect.collidelist(obstacles[i][COLLISION_RECTANGLES]) > -1:
                window = "End"
                deathSound.play()
            # move the obstacles and their collision rectanges
            obstacles[i][X] = obstacles[i][X]+obstacles[i][DIRECTION][DX]
            obstacles[i][Y] = obstacles[i][Y]+obstacles[i][DIRECTION][DY]
            for j in range(len(obstacles[i][COLLISION_RECTANGLES])):
                obstacles[i][COLLISION_RECTANGLES][j].move_ip(obstacles[i][DIRECTION][DX]*GRID_SIZE, obstacles[i][DIRECTION][DY]*GRID_SIZE)
            # check if the obstacles should be drawing warnings or if they should be removed
            if obstacles[i][DIRECTION][DY] == 0:  # moving horizontally (dy = 0)
                if obstacles[i][X] > 0 and obstacles[i][X] < gridWidth:
                    obstacles[i][WARNING_STATUS] = 0  # Don't draw the warning at the top
                elif obstacles[i][DIRECTION][DX] == 1:  # moving right
                    if obstacles[i][X] > gridWidth:
                        obstacles.pop(i)
                else:
                    if obstacles[i][X] < -obstacles[i][WIDTH]*obstacles[i][SCALE]/GRID_SIZE:  # moving left is special since the coords are for the top-left corner, so take that into account
                        obstacles.pop(i)
            else:  # moving vertically
                if obstacles[i][Y] > 0 and obstacles[i][Y] < gridHeight:
                    obstacles[i][WARNING_STATUS] = 0  # Don't draw the warning at the top
                elif obstacles[i][DIRECTION][DY] == 1:  # moving down
                    if obstacles[i][Y] > gridHeight:
                        obstacles.pop(i)
                else:
                    if obstacles[i][Y] < -obstacles[i][HEIGHT]*obstacles[i][SCALE]/GRID_SIZE:  # moving up is also special
                        obstacles.pop(i)
        # move the segments
        lastIndex = len(segX)-1
        for i in range(lastIndex, 0, -1):
            segX[i] = segX[i-1]
            segY[i] = segY[i-1]
        # move the head
        segX[HEAD] = segX[HEAD] + dx
        segY[HEAD] = segY[HEAD] + dy

        # timer
        periodElapsed = time.time()-periodStart
        if INITIAL_TIME-periodElapsed-timeElapsed < 0:
            window = "End"
            deathSound.play()

        # keyboard input
        if keys[pygame.K_a] and dx != SPEED:
            dx = -SPEED
            dy = 0
        elif keys[pygame.K_d] and dx != -SPEED:
            dx = SPEED
            dy = 0
        elif keys[pygame.K_w] and dy != SPEED:
            dx = 0
            dy = -SPEED
        elif keys[pygame.K_s] and dy != -SPEED:
            dx = 0
            dy = SPEED

        # check coin collision
        for i in range(len(coinX)-1, -1, -1):
            if segX[HEAD] == coinX[i] and segY[HEAD] == coinY[i]:
                coinX.pop(i)
                coinY.pop(i)
                segX.append(segX[-1])
                segY.append(segY[-1])
                score = score+1
                coinSound.play()
                if score % SPEED_INTERVAL == 0:
                    fps[difficulty] = fps[difficulty]+FPS_SPEED_RATE[difficulty]
                    obstacleInterval[difficulty] = max(OBSTACLE_MAX_INTERVALS[difficulty], obstacleInterval[difficulty]-OBSTACLE_SPEED_RATE[difficulty])
        # spawn coin if there are none on screen
        if len(coinX) == 0:
            coinX.append(random.randint(0, gridWidth-1))
            coinY.append(random.randint(0, gridHeight-1))

        # add more colours if the snake is getting too long (for the colour gradient)
        while len(segX) / ((len(segColours)-1)*GRADIENT_INTERVAL) == 1:
            segColours.append((random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))

        # check if snake has left game area
        if headIsOutsideGame(segX[HEAD], segY[HEAD], gridWidth, gridHeight)[0]:
            window = "End"
            deathSound.play()
        # check if snake touches itself
        for i in range(1, len(segX)):
            if segX[HEAD] == segX[i] and segY[HEAD] == segY[i]:
                window = "End"
                deathSound.play()
    elif window == "Pause":
        redrawGame()  # draw the game so that it'll appear behind the pause overlay
        redrawPause()
    elif window == "Lore":
        redrawLore()
    elif window == "End":
        redrawEndScreen()

    pygame.display.update()
# --------------------------------------- #
pygame.quit()
