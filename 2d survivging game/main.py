import pygame
import time
import math
from gameWindow import ForeGround
from gameWindow import BackGround
from gameWindow import Block
from gameWindow import Gui
from CharacterFile import Character
from inventory import Inventory
from itemIds import Items
from pygame.locals import *
from entity import Entity
import noise
import random
import os

"""
to do list:
make sand edible
"""
"""
notes: 
"""

pg = pygame
pygame.font.init()

#inits

#default values
saveButton = pg.Rect((725,725),(55,55))
textBoxText = ''
activeTextBox = None
inventoryBackGround = pg.image.load("./Images/hud/openInventoryBackground.png").convert_alpha()
entities = []

selectedBox = None

direction = "right"
animationSpeed = 4
playerSpeed = 0.3

jump = False
jumpIterNum = 0
yVelocity = 0

blockBreakNumber = 1
blockBreakSpeed = 15

blockSize = 32
numBlocks = int(800 / blockSize)
worldHeight = 1000
worldLength = 1000

moving = False
movingIter = 1

blockType = Block.Type.BlockType.dirt

characterImage = Character.Image.characterStillRight
croutched = False

myfont = pygame.font.SysFont('Comic Sans MS', 18)

#screen scroll values
scrollSpeed = 0
scrollDirection = 1

#checks for iterations against a modulo operator. used for screens croll
iterNum = 0

characterX = 10
characterY = 10

#defines background image
bgImage = BackGround.bgImage("./Images/background images/cloud.png").convert()

def generateWorld():
    #sets up bottom squares
    for x in range(worldLength):
        for y in range(10,500):
            if not(0.135 <= noise.snoise2(x*0.07,y*0.07,repeaty=999999,repeatx=999999,octaves = 1,persistence=1,lacunarity=10) <= 0.7):
                Block.Grid.placeBlock((x,500 + y),Block.Type.BlockType.stone,True)
                Block.Grid.placeBlockBg((x,500 + y),Block.Type.BlockType.stone,True)
            else:
                Block.Grid.placeBlockBg((x,500 + y),Block.Type.BlockType.stone,True)

    seed = random.randint(0,500)


    for x in range(worldLength):
        frequency = 0.2

        treeTrue = random.randint(0,10)

        y =  int(noise.pnoise1((x+seed)*0.07,repeat=999999999)*5)+495

        if x == 500:
            Character.characterLocation[1] = y-2


        if treeTrue == 5:
            Block.Grid.placeBlockBg((x,y-1),Block.Type.BlockType.log,True)
            Block.Grid.placeBlockBg((x,y-2),Block.Type.BlockType.log,True)
            Block.Grid.placeBlockBg((x,y-3),Block.Type.BlockType.log,True)
            Block.Grid.placeBlockBg((x,y-4),Block.Type.BlockType.log,True)

            #first row of leaves
            Block.Grid.placeBlockBg((x-1,y-5),Block.Type.BlockType.leaves,True)
            Block.Grid.placeBlockBg((x-2,y-5),Block.Type.BlockType.leaves,True)
            Block.Grid.placeBlockBg((x,y-5),Block.Type.BlockType.leaves,True)
            Block.Grid.placeBlockBg((x+1,y-5),Block.Type.BlockType.leaves,True)
            Block.Grid.placeBlockBg((x+2,y-5),Block.Type.BlockType.leaves,True)
            #second row
            Block.Grid.placeBlockBg((x-1,y-6),Block.Type.BlockType.leaves,True)
            Block.Grid.placeBlockBg((x-2,y-6),Block.Type.BlockType.leaves,True)
            Block.Grid.placeBlockBg((x,y-6),Block.Type.BlockType.leaves,True)
            Block.Grid.placeBlockBg((x+1,y-6),Block.Type.BlockType.leaves,True)
            Block.Grid.placeBlockBg((x+2,y-6),Block.Type.BlockType.leaves,True)
            #third row
            Block.Grid.placeBlockBg((x-1,y-7),Block.Type.BlockType.leaves,True)
            Block.Grid.placeBlockBg((x,y-7),Block.Type.BlockType.leaves,True)
            Block.Grid.placeBlockBg((x+1,y-7),Block.Type.BlockType.leaves,True)

            for i in range(random.randint(5,7)):
                pass
                #Block.Grid.placeBlock((x,y-i),Block.Type.BlockType.log,True)

        Block.Grid.placeBlock((x,y),Block.Type.BlockType.grass,True)
        Block.Grid.placeBlock((x,y+1),Block.Type.BlockType.dirt,True)
        Block.Grid.placeBlock((x,y+2),Block.Type.BlockType.dirt,True)
        Block.Grid.placeBlock((x,y+3),Block.Type.BlockType.dirt,True)
        Block.Grid.placeBlock((x,y+4),Block.Type.BlockType.dirt,True)


        for y in range(y,510):
            if not(0 <= noise.snoise2(x*0.07,y*0.07,repeaty=999999,repeatx=999999,octaves = 1,persistence=1) <= 0.6):
                Block.Grid.placeBlock((x,y),Block.Type.BlockType.dirt,True)
            Block.Grid.placeBlockBg((x,y),Block.Type.BlockType.dirt,True)

Inventory.grid[0][0] = Items.Id.defaultPick
Inventory.stackAmount[0][0] = 1
Inventory.grid[0][1] = Items.Id.defaultAxe
Inventory.stackAmount[0][1] = 1
Inventory.grid[0][2] = Items.Id.defaultShovel
Inventory.stackAmount[0][2] = 1

def deleteEnt(index,entites):
	if len(entities) > index:
		if len(entities) > 0:
			entities[index].deleteEntity(index)
		del entities[index]

clock = pygame.time.Clock()

mainMenu = 1
mainGame = 2
loadGameScene= 3
createWorld = 4

scene = mainMenu

while True:
    frame = 0
    #main menu scene
    while scene == mainMenu:
        ev = pg.event.get()
        pg.draw.rect(ForeGround.display,(255,255,255),pg.Rect((0,0),(800,800)))
        loadGameButton = pg.Rect((50,350),(300,100))
        ForeGround.display.blit(Gui.loadGameButton,(50,350))
        if loadGameButton.collidepoint(ForeGround.getMousePos()[0],ForeGround.getMousePos()[1]) and pg.mouse.get_pressed(3) == (True,False,False):
            scene = loadGameScene

        newGameButton = pg.Rect((400,350),(300,100))
        ForeGround.display.blit(Gui.newGameButton,(400,350))
        if newGameButton.collidepoint(ForeGround.getMousePos()[0],ForeGround.getMousePos()[1]) and pg.mouse.get_pressed(3) == (True,False,False):
            scene = createWorld
        pg.display.flip()
    
    #load game screen
    while scene == loadGameScene:
        ev = pg.event.get()
        #clears screen with while background
        pg.draw.rect(ForeGround.display,(255,255,255),pg.Rect((0,0),(800,800)))
        worlds = os.listdir("./saves")
        for i in range(len(worlds)):
            try:
                if str(worlds[i])[-7]+str(worlds[i])[-6]+str(worlds[i])[-5] == "_bg":
                    worlds.pop(i)
                if str(worlds[i])[-4]+str(worlds[i])[-3]+str(worlds[i])[-2]+str(worlds[i])[-1] == "json":
                    worlds.pop(i)
            except:
                pass

        #creates back button
        backButton = pg.Rect((20,30),(50,50))
        ForeGround.display.blit(Gui.backButton,(20,20))
        #places all world select buttons
        for i in range(len(worlds)):
            #defines world button
            worldButton = pg.Rect((200,(395+len(worlds)*15)-i*30),(400,20))
            ForeGround.display.blit(Gui.selectFileButton,(200,(395+len(worlds)*15)-i*30))
            #defines world button text
            fileNameText = myfont.render(str(worlds[i]), False, (0, 0, 0))
            fileNameTextWidth = fileNameText.get_rect().width
            ForeGround.display.blit(fileNameText,(400-(fileNameTextWidth/2),(390+len(worlds)*15)-i*30))
            #checks for mouse input
            for event in ev:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if worldButton.collidepoint(ForeGround.getMousePos()[0],ForeGround.getMousePos()[1]) and pg.mouse.get_pressed(3) == (True,False,False):
                        Block.Grid.loadWorld(str(worlds[i][:-4]))
                        scene = mainGame
                        break
                    elif backButton.collidepoint(ForeGround.getMousePos()[0],ForeGround.getMousePos()[1]) and pg.mouse.get_pressed(3) == (True,False,False):
                        scene = mainMenu
            

        pg.display.flip()
    while scene == createWorld:
        ev = pg.event.get()
        pg.draw.rect(ForeGround.display,(255,255,255),pg.Rect((0,0),(800,800)))
        #creates back button
        backButton = pg.Rect((20,30),(50,50))
        ForeGround.display.blit(Gui.backButton,(20,20))
        #defines all text boxes
        textBoxes = [pg.Rect((350, 375), (100, 50))]
        #creates make worl button
        createWorldButton = pg.Rect((350, 450), (100, 50))
        createWorldButtonText = myfont.render("create world", True, (255, 255, 255))
        pg.draw.rect(ForeGround.display,(180,180,180),createWorldButton)
        ForeGround.display.blit(createWorldButtonText,(350,450))
        #checks through all text boxes to process logic for them
        for i in range(len(textBoxes)):
            boxColor = (180,180,180)
            for event in ev:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if textBoxes[i].collidepoint(ForeGround.getMousePos()[0],ForeGround.getMousePos()[1]) and pg.mouse.get_pressed(3) == (True,False,False):
                            activeTextBox = i

            if activeTextBox == i:
                boxColor = (200,200,200)
            pg.draw.rect(ForeGround.display,boxColor,textBoxes[i])

        #keys key input for text box
        for event in ev:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_BACKSPACE:
                    textBoxText = textBoxText[:-1]
                elif event.key == pygame.K_RETURN:
                    textBoxText = ''
                else:
                    textBoxText += event.unicode
            #mouse input
            if event.type == pygame.MOUSEBUTTONDOWN:
                        if createWorldButton.collidepoint(ForeGround.getMousePos()[0],ForeGround.getMousePos()[1]) and pg.mouse.get_pressed(3) == (True,False,False):
                            generateWorld()
                            Block.openWorld = textBoxText
                            scene = mainGame
                        if backButton.collidepoint(ForeGround.getMousePos()[0],ForeGround.getMousePos()[1]) and pg.mouse.get_pressed(3) == (True,False,False):
                            scene = mainMenu

        textBoxTextSurface = myfont.render(textBoxText, True, (255, 255, 255))
        if activeTextBox != None:
            ForeGround.display.blit(textBoxTextSurface,(textBoxes[activeTextBox]))
        frame += 1
        pg.display.flip()
    #main game loop
    while scene == mainGame:
        #gets pygame events
        ev = pg.event.get()
        keyboardInput = pg.key.get_pressed()
        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
        clock.tick(60)
        #print(int(clock.get_fps()))
        #START

        #checks mouse input
        if pg.mouse.get_pressed(3) == (False,False,True):
            try:
                if Block.Grid.getBlockAtLocation((ForeGround.getMousePos()[0],ForeGround.getMousePos()[1])) == Block.Type.BlockType.air:
                    Inventory.stackAmount[0][Inventory.selectedSlot] -= 1

                    if Inventory.grid[0][Inventory.selectedSlot] != None:
                        Block.Grid.placeBlock((ForeGround.getMousePos()[0],ForeGround.getMousePos()[1]),Inventory.grid[0][Inventory.selectedSlot])
            except:
                pass

        #right click
        if pg.mouse.get_pressed(3) == (True,False,False):
            if Inventory.open == False:
                ySize = 48
                for i in range(9):
                    if math.floor(ForeGround.getMousePos()[0]/48) == i and math.floor(ForeGround.getMousePos()[1]/48) == 0:
                        Inventory.selectedSlot = i
            elif Inventory.open == True:
                ySize = 240

                if saveButton.collidepoint(ForeGround.getMousePos()[0],ForeGround.getMousePos()[1]):
                    for event in ev:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                                Block.Grid.saveWorld(Block.openWorld)
                for y in range(5):
                    for x in range(9):
                        if math.floor(ForeGround.getMousePos()[0]/48) == x and math.floor(ForeGround.getMousePos()[1]/48) == y:

                                    if Inventory.itemOnCursor != Items.Id.empty and Inventory.grid[y][x] != Items.Id.empty:
                                        temporaryItem = Inventory.itemOnCursor
                                        temporaryItemCount = Inventory.itemCountOnCursor

                                        Inventory.itemOnCursor = Inventory.grid[y][x]
                                        Inventory.itemCountOnCursor = Inventory.stackAmount[y][x]

                                        Inventory.grid[y][x] = temporaryItem
                                        Inventory.stackAmount[y][x] = temporaryItemCount

                                    elif Inventory.itemOnCursor == Items.Id.empty:
                                        Inventory.itemOnCursor = Inventory.grid[y][x]
                                        Inventory.itemCountOnCursor = Inventory.stackAmount[y][x]

                                        Inventory.grid[y][x] = Items.Id.empty
                                        Inventory.stackAmount[y][x] = 0

                                    elif Inventory.itemOnCursor != Items.Id.empty:
                                        Inventory.grid[y][x] = Inventory.itemOnCursor
                                        Inventory.stackAmount[y][x] = Inventory.itemCountOnCursor

                                        Inventory.itemOnCursor = Items.Id.empty
                                        Inventory.itemCountOnCursor = 0

            if Inventory.selectedSlot != None and (ForeGround.getMousePos()[0] > 432 or ForeGround.getMousePos()[1] > ySize) and 1 <= Inventory.grid[0][Inventory.selectedSlot] <= 50:
                if Inventory.stackAmount[0][Inventory.selectedSlot] <= 0:
                    Inventory.grid[0][Inventory.selectedSlot] = Items.Id.empty
                    Inventory.stackAmount[0][Inventory.selectedSlot] = 0

            if 224 < ForeGround.getMousePos()[0] < 576 and 352 < ForeGround.getMousePos()[1] < 736:
                if Block.Grid.blockBreakingPos != Block.Grid.blockBreakingPosLast:
                    blockBreakNumber = 1

                Block.Grid.SetBlockBreakCoord((ForeGround.getMousePos()[0]+Character.characterDrawLocation[0], (ForeGround.getMousePos()[1]+Character.characterDrawLocation[1])-600))

                blockBreakSpeed = Block.Type.determineBreakingSpeed()
                if Block.Grid.getBlockAtLocation2(Block.Grid.blockBreakingPos) == Block.Type.BlockType.air:
                        blockBreakNumber = 1

                if iterNum%blockBreakSpeed == 0:
                    blockBreakNumber += 1
                if blockBreakNumber%6 == 0:
                    Inventory.addItem(Block.Grid.getBlockAtLocation2(Block.Grid.blockBreakingPos))
                    Block.Grid.breakBlock((ForeGround.getMousePos()[0],ForeGround.getMousePos()[1]),1)
                    blockBreakNumber = 1
        else:
                blockBreakNumber = 1

        if pg.mouse.get_pressed(3) == (False,True,False) and Inventory.selectedSlot != None and Block.Grid.getBlockAtLocation((ForeGround.getMousePos()[0],ForeGround.getMousePos()[1])) != Block.Type.BlockType.air:
            Inventory.grid[0][Inventory.selectedSlot] = Block.Grid.getBlockAtLocation((ForeGround.getMousePos()[0],ForeGround.getMousePos()[1]))
        

        """
        visual screen logic(background, screen scrolling ect.)
        """

        #draws background image
        BackGround.BlitToSurface(ForeGround.display,bgImage,scrollSpeed-4)

        #logic for setting the x value of the background to make it scroll 
        if scrollDirection == 0 and iterNum%50 == 0:
            scrollSpeed += 1
        elif scrollDirection == 1 and iterNum%50 == 0:
            scrollSpeed -= 1

        if scrollSpeed <= -4:
            scrollDirection = 0
        if scrollSpeed >= 4:
            scrollDirection = 1




        """
        block placement and properties logic
        """
        #grid matrix logic at top

        
        #block rendering logic is to be placed at the bottom

        Block.Renderer.drawBlocksOnScreen()
            
        Block.Renderer.drawBreakingOverlay(blockBreakNumber)
                    
        """
        player logic
        """
        if Character.characterLocation[1]%1 != 0 and yVelocity == 0:
            Character.characterLocation[1] = math.floor(Character.characterLocation[1])

        yVelocity += 0.2

        if yVelocity > 1:
            yVelocity = 1

            #zeroes out velocity if the player is on the ground
        if Character.Pos.newCollisionCheck()[4] == 1 or Character.Pos.newCollisionCheck()[5] == 1:
            yVelocity = 0

        #keyboard input

        for event in ev:
            if event.type == pg.KEYDOWN:
                if keyboardInput[pg.K_TAB]:
                    Inventory.open = not Inventory.open
                if keyboardInput[pg.K_SPACE]:
                    if Character.Pos.newCollisionCheck()[4] == 1 and Character.Pos.newCollisionCheck()[5] == 1:
                        yVelocity -= 0.5
                if keyboardInput[K_e]:
                    if Inventory.craftingTableOpen == True:
                        Inventory.craftingTableOpen = False
                    elif Block.Grid.getBlockAtLocation((ForeGround.getMousePos()[0],ForeGround.getMousePos()[1])) == Block.Type.BlockType.craftingTable:
                        if Inventory.craftingTableOpen == False:
                            Inventory.craftingTableOpen = True
                            Inventory.activeCraftingTableCoords = [Character.characterLocation[0],Character.characterLocation[1]]
        if keyboardInput[pg.K_z]:
                Block.Grid.saveWorld(Block.openWorld)
                    

        if Character.Pos.newCollisionCheck()[6] == 1:
            if yVelocity < 0:
                yVelocity = 0
        Character.Input.inputKey(keyboardInput,iterNum,entities)

        Character.Pos.update()
        #draw character at the end AFTER(DO NOT FORGOR💀) setting game logic for position
        Character.Render.drawStillX(ForeGround.display,Character.characterImage)

        Character.characterLocation[1] += yVelocity

        """
        hud/inventory code
        """
        #cragting table stuff
        if Inventory.craftingTableOpen == True:
            ForeGround.display.blit(Inventory.Render.craftingTableInterface,(500,500))
        if (Character.characterLocation[0]-Inventory.activeCraftingTableCoords[0]) > 5 or (Character.characterLocation[0]-Inventory.activeCraftingTableCoords[0]) <-5 or (Character.characterLocation[1]-Inventory.activeCraftingTableCoords[1]) > 5 or (Character.characterLocation[1]-Inventory.activeCraftingTableCoords[1]) <-5:
            Inventory.craftingTableOpen = False


        if Inventory.selectedSlot != None and Inventory.stackAmount[0][Inventory.selectedSlot] <= 0:
            Inventory.grid[0][Inventory.selectedSlot] = Items.Id.empty
            Inventory.stackAmount[0][Inventory.selectedSlot] = 0

        #hud rendering code
        if Inventory.open == True:
            ForeGround.display.blit(Gui.saveButton,(725,725))
            ForeGround.display.blit(inventoryBackGround,(0,0))
            for y in range(1,5):
                for x in range(9):
                        Inventory.Render.renderBox(((x*48),(y*48)),Inventory.grid[y][x])
                        ForeGround.display.blit(myfont.render(str(Inventory.stackAmount[y][x]), False, (150, 150, 150)),(x*48+30,y*48+24))

        for i in range(9):
            if i == Inventory.selectedSlot:
                Inventory.Render.renderBox(((i*48),1),Inventory.grid[0][i],True)
                ForeGround.display.blit(myfont.render(str(Inventory.stackAmount[0][i]), False, (150, 150, 150)),(i*48+30,25))
            else:
                Inventory.Render.renderBox(((i*48),1),Inventory.grid[0][i])
                ForeGround.display.blit(myfont.render(str(Inventory.stackAmount[0][i]), False, (150, 150, 150)),(i*48+30,25))

        

        """
        entity logic
        """
        for i in range(len(entities)):
            try:
                ForeGround.display.blit(Items.iconList[entities[i].id],(entities[i].drawCoordinates))
                entities[i].update()
                entities[i].gravityUpdate()

                if Character.characterBoundingBox.colliderect(entities[i].boundingBox):
                    Inventory.addItem(entities[i].id)
                    deleteEnt(i,entities)
            except:
                pass

        for event in ev:
            if event.type == pg.KEYDOWN:
                if keyboardInput[pg.K_q]:
                    Inventory.dropItem(Inventory.selectedSlot,entities)



        """
        any ending functions such as iteration numbers or updates of that kind or misc renderings
        """

        #draws cursor with block where player cursor is
        ForeGround.display.blit(ForeGround.cursorIcon,(ForeGround.getMousePos()[0]-12,ForeGround.getMousePos()[1]-9))
        ForeGround.display.blit(Items.iconList[Inventory.itemOnCursor],(ForeGround.getMousePos()[0]-12,ForeGround.getMousePos()[1]-9))

        #number of times the while loop has run
        iterNum +=1

        #END
        #end of main loop. all code goes in between
        pg.display.flip()

