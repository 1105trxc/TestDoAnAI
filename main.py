import pygame
import random

pygame.init()

class MessageBox:
    def __init__(self, message, ship_image=None, duration=2000):
        self.font = pygame.font.SysFont('Stencil', 30)
        self.message = self.font.render(message, True, (255, 255, 255))
        self.bg_color = (50, 50, 50, 200)  # Màu nền xám với độ trong suốt
        self.border_color = (255, 0, 0)  # Viền đỏ
        self.duration = duration  # Thời gian hiển thị (ms)
        self.start_time = pygame.time.get_ticks()
        
        # Xử lý hình ảnh tàu nếu có
        self.ship_image = ship_image
        
        # Tính toán kích thước ô thông báo
        self.padding = 20
        self.text_width = self.message.get_width()
        self.text_height = self.message.get_height()
        
        if self.ship_image:
            self.image_width = self.ship_image.get_width()
            self.image_height = self.ship_image.get_height()
            # Chiều rộng là giá trị lớn nhất giữa văn bản và hình ảnh
            self.width = max(self.text_width, self.image_width) + self.padding * 2
            # Chiều cao là tổng chiều cao của văn bản và hình ảnh, cộng thêm khoảng trống giữa chúng
            self.height = self.text_height + self.image_height + self.padding * 3  # Thêm padding giữa văn bản và hình
        else:
            self.width = self.text_width + self.padding * 2
            self.height = self.text_height + self.padding * 2
        
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (SCREENWIDTH // 2, SCREENHEIGHT // 2)

    def draw(self, window):
        # Kiểm tra nếu vẫn còn trong thời gian hiển thị
        if pygame.time.get_ticks() - self.start_time < self.duration:
            # Vẽ nền với độ trong suốt
            surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            surface.fill(self.bg_color)
            window.blit(surface, self.rect)
            
            # Vẽ viền
            pygame.draw.rect(window, self.border_color, self.rect, 2)
            
            # Vẽ thông điệp ở phía trên
            message_rect = self.message.get_rect()
            message_rect.center = (self.rect.centerx, self.rect.top + self.padding + self.text_height // 2)
            window.blit(self.message, message_rect)
            
            # Vẽ hình ảnh tàu phía dưới văn bản nếu có
            if self.ship_image:
                image_rect = self.ship_image.get_rect()
                image_rect.center = (self.rect.centerx, message_rect.bottom + self.padding + self.image_height // 2)
                window.blit(self.ship_image, image_rect)
            
            return True
        return False

class Ship:
    def __init__(self, name, img, pos, size, numGuns=0, gunPath=None, gunsize=None, gunCoordsOffset=None):
        self.name = name
        self.pos = pos
        self.vImage = loadImage(img, size)
        self.vImageWidth = self.vImage.get_width()
        self.vImageHeight = self.vImage.get_height()
        self.vImageRect = self.vImage.get_rect()
        self.vImageRect.topleft = pos
        self.hImage = pygame.transform.rotate(self.vImage, -90)
        self.hImageWidth = self.hImage.get_width()
        self.hImageHeight = self.hImage.get_height()
        self.hImageRect = self.hImage.get_rect()
        self.hImageRect.topleft = pos
        self.image = self.vImage
        self.rect = self.vImageRect
        self.rotation = False
        self.active = False
        self.is_sunk = False
        self.gunslist = []
        if numGuns > 0:
            self.gunCoordsOffset = gunCoordsOffset
            for num in range(numGuns):
                self.gunslist.append(
                    Guns(gunPath,
                         self.rect.center,
                         (size[0] * gunsize[0],
                          size[1] * gunsize[1]),
                         self.gunCoordsOffset[num])
                )

    def selectShipAndMove(self):
        self.rect.center = pygame.mouse.get_pos()
        self.hImageRect.center = self.vImageRect.center = self.rect.center

    def rotateShip(self, doRotation=False):
        if self.active or doRotation == True:
            if self.rotation == False:
                self.rotation = True
            else:
                self.rotation = False
            self.switchImageAndRect()

    def switchImageAndRect(self):
        if self.rotation == True:
            self.image = self.hImage
            self.rect = self.hImageRect
        else:
            self.image = self.vImage
            self.rect = self.vImageRect
        self.hImageRect.center = self.vImageRect.center = self.rect.center

    def checkForCollisions(self, shiplist):
        slist = shiplist.copy()
        slist.remove(self)
        for item in slist:
            if self.rect.colliderect(item.rect):
                return True
        return False

    def checkForRotateCollisions(self, shiplist):
        slist = shiplist.copy()
        slist.remove(self)
        for ship in slist:
            if self.rotation == True:
                if self.vImageRect.colliderect(ship.rect):
                    return True
            else:
                if self.hImageRect.colliderect(ship.rect):
                    return True
        return False

    def returnToDefaultPosition(self):
        if self.rotation == True:
            self.rotateShip(True)
        self.rect.topleft = self.pos
        self.hImageRect.center = self.vImageRect.center = self.rect.center

    def snapToGridEdge(self, gridCoords):
        if self.rect.topleft != self.pos:
            if self.rect.left > gridCoords[0][-1][0] + 50 or \
               self.rect.right < gridCoords[0][0][0] or \
               self.rect.top > gridCoords[-1][0][1] + 50 or \
               self.rect.bottom < gridCoords[0][0][1]:
                self.returnToDefaultPosition()
            elif self.rect.right > gridCoords[0][-1][0]+50:
                self.rect.right = gridCoords[0][-1][0] + 50
            elif self.rect.left < gridCoords[0][0][0]:
                self.rect.left = gridCoords[0][0][0]
            elif self.rect.top < gridCoords[0][0][1]:
                self.rect.top = gridCoords[0][0][1]
            elif self.rect.bottom > gridCoords[-1][0][1] + 50:
                self.rect.bottom = gridCoords[-1][0][1] + 50
            self.vImageRect.center = self.hImageRect.center = self.rect.center

    def snapToGrid(self, gridCoords):
        for rowX in gridCoords:
            for cell in rowX:
                if self.rect.left >= cell[0] and self.rect.left < cell[0] + CELLSIZE \
                   and self.rect.top >= cell[1] and self.rect.top < cell[1] + CELLSIZE:
                    if self.rotation == False:
                        self.rect.topleft = (cell[0] + (CELLSIZE - self.image.get_width())//2, cell[1])
                    else:
                        self.rect.topleft = (cell[0], cell[1] + (CELLSIZE - self.image.get_height())//2)
        self.hImageRect.center = self.vImageRect.center = self.rect.center

    def draw(self, window, is_computer_grid=False):
        if not is_computer_grid or (is_computer_grid and self.is_sunk):
            window.blit(self.image, self.rect)
            for guns in self.gunslist:
                guns.draw(window, self)

class Guns:
    def __init__(self, imgPath, pos, size, offset):
        self.orig_image = loadImage(imgPath, size, True)
        self.image = self.orig_image
        self.offset = offset
        self.rect = self.image.get_rect(center=pos)

    def update(self, ship):
        self.rotateGuns(ship)
        if ship.rotation == False:
            self.rect.center = (ship.rect.centerx, ship.rect.centery + (ship.image.get_height()//2 * self.offset))
        else:
            self.rect.center = (ship.rect.centerx + (ship.image.get_width()//2 * -self.offset), ship.rect.centery)

    def _update_image(self, angle):
        self.image = pygame.transform.rotate(self.orig_image, -angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def rotateGuns(self, ship):
        direction = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(self.rect.center)
        radius, angle = direction.as_polar()
        if not ship.rotation:
            if self.rect.centery <= ship.vImageRect.centery and angle <= 0:
                self._update_image(angle)
            if self.rect.centery >= ship.vImageRect.centery and angle > 0:
                self._update_image(angle)
        else:
            if self.rect.centerx <= ship.hImageRect.centerx and (angle <= -90 or angle >= 90):
                self._update_image(angle)
            if self.rect.centerx >= ship.hImageRect.centerx and (angle >= -90 and angle <= 90):
                self._update_image(angle)

    def draw(self, window, ship):
        self.update(ship)
        window.blit(self.image, self.rect)

class Button:
    def __init__(self, image, size, pos, msg):
        self.name = msg
        self.image = image
        self.imageLarger = pygame.transform.scale(self.image, (size[0] + 10, size[1] + 10))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.active = False
        self.msg = self.addText(msg)
        self.msgRect = self.msg.get_rect(center=self.rect.center)

    def addText(self, msg):
        font = pygame.font.SysFont('Stencil', 22)
        message = font.render(msg, 1, (255,255,255))
        return message

    def focusOnButton(self, window):
        if self.active:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                window.blit(self.imageLarger, (self.rect[0] - 5, self.rect[1] - 5, self.rect[2], self.rect[3]))
            else:
                window.blit(self.image, self.rect)

    def actionOnPress(self):
        if self.active:
            if self.name == 'Randomize':
                self.randomizeShipPositions(pFleet, pGameGrid)
                self.randomizeShipPositions(cFleet, cGameGrid)
            elif self.name == 'Reset':
                self.resetShips(pFleet)
            elif self.name == 'Deploy':
                self.deploymentPhase()
            elif self.name == 'Quit':
                pass
            elif self.name == 'Redeploy':
                self.restartTheGame()

    def randomizeShipPositions(self, shiplist, gameGrid):
        if DEPLOYMENT == True:
            randomizeShipPositions(shiplist, gameGrid)

    def resetShips(self, shiplist):
        if DEPLOYMENT == True:
            for ship in shiplist:
                ship.returnToDefaultPosition()
                ship.is_sunk = False

    def deploymentPhase(self):
        pass

    def restartTheGame(self):
        TOKENS.clear()
        self.resetShips(pFleet)
        self.randomizeShipPositions(cFleet, cGameGrid)
        for ship in cFleet:
            ship.is_sunk = False
        updateGameLogic(cGameGrid, cFleet, cGameLogic)
        updateGameLogic(pGameGrid, pFleet, pGameLogic)

    def updateButtons(self, gameStatus):
        if self.name == 'Deploy' and gameStatus == False:
            self.name = 'Redeploy'
        elif self.name == 'Redeploy' and gameStatus == True:
            self.name = 'Deploy'
        if self.name == 'Reset' and gameStatus == False:
            self.name = 'Radar Scan'
        elif self.name == 'Radar Scan' and gameStatus == True:
            self.name = 'Reset'
        if self.name == 'Randomize' and gameStatus == False:
            self.name = 'Quit'
        elif self.name == 'Quit' and gameStatus == True:
            self.name = 'Randomize'
        self.msg = self.addText(self.name)
        self.msgRect = self.msg.get_rect(center=self.rect.center)

    def draw(self, window):
        self.updateButtons(DEPLOYMENT)
        self.focusOnButton(window)
        window.blit(self.msg, self.msgRect)

class Player:
    def __init__(self):
        self.turn = True

    def makeAttack(self, grid, logicgrid, enemy_fleet, window):
        posX, posY = pygame.mouse.get_pos()
        if posX >= grid[0][0][0] and posX <= grid[0][-1][0] + 50 and posY >= grid[0][0][1] and posY <= grid[-1][0][1] + 50:
            for i, rowX in enumerate(grid):
                for j, colX in enumerate(rowX):
                    if posX >= colX[0] and posX < colX[0] + 50 and posY >= colX[1] and posY <= colX[1] + 50:
                        if logicgrid[i][j] != ' ':
                            if logicgrid[i][j] == 'O':
                                TOKENS.append(Tokens(REDTOKEN, grid[i][j], 'Hit', None, None, None))
                                logicgrid[i][j] = 'T'
                                SHOTSOUND.play()
                                HITSOUND.play()
                                self.turn = False
                                checkAndNotifyDestroyedShip(grid, logicgrid, enemy_fleet, window)
                        else:
                            logicgrid[i][j] = 'X'
                            SHOTSOUND.play()
                            MISSSOUND.play()
                            TOKENS.append(Tokens(GREENTOKEN, grid[i][j], 'Miss', None, None, None))
                            self.turn = False

class EasyComputer:
    def __init__(self):
        self.turn = False
        self.status = self.computerStatus('Thinking')
        self.name = 'Easy Computer'

    def computerStatus(self, msg):
        image = pygame.font.SysFont('Stencil', 22)
        message = image.render(msg, 1, (0, 0, 0))
        return message

    def makeAttack(self, gamelogic, grid, enemy_fleet, window):
        COMPTURNTIMER = pygame.time.get_ticks()
        if COMPTURNTIMER - TURNTIMER >= 3000:
            validChoice = False
            while not validChoice:
                rowX = random.randint(0, 9)
                colX = random.randint(0, 9)
                if gamelogic[rowX][colX] == ' ' or gamelogic[rowX][colX] == 'O':
                    validChoice = True
            if gamelogic[rowX][colX] == 'O':
                TOKENS.append(Tokens(REDTOKEN, grid[rowX][colX], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None))
                gamelogic[rowX][colX] = 'T'
                SHOTSOUND.play()
                HITSOUND.play()
                checkAndNotifyDestroyedShip(grid, gamelogic, enemy_fleet, window)
                self.turn = False
            else:
                gamelogic[rowX][colX] = 'X'
                TOKENS.append(Tokens(BLUETOKEN, grid[rowX][colX], 'Miss', None, None, None))
                SHOTSOUND.play()
                MISSSOUND.play()
                self.turn = False
        return self.turn

    def draw(self, window):
        if self.turn:
            window.blit(self.status, (cGameGrid[0][0][0] - CELLSIZE, cGameGrid[-1][-1][1] + CELLSIZE))

class HardComputer(EasyComputer):
    def __init__(self):
        super().__init__()
        self.moves = []

    def makeAttack(self, gamelogic, grid, enemy_fleet, window):
        if len(self.moves) == 0:
            COMPTURNTIMER = pygame.time.get_ticks()
            if COMPTURNTIMER - TURNTIMER >= 3000:
                validChoice = False
                while not validChoice:
                    rowX = random.randint(0, 9)
                    rowY = random.randint(0, 9)
                    if gamelogic[rowX][rowY] == ' ' or gamelogic[rowX][rowY] == 'O':
                        validChoice = True
                if gamelogic[rowX][rowY] == 'O':
                    TOKENS.append(Tokens(REDTOKEN, grid[rowX][rowY], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None))
                    gamelogic[rowX][rowY] = 'T'
                    SHOTSOUND.play()
                    HITSOUND.play()
                    self.generateMoves((rowX, rowY), gamelogic)
                    checkAndNotifyDestroyedShip(grid, gamelogic, enemy_fleet, window)
                    self.turn = False
                else:
                    gamelogic[rowX][rowY] = 'X'
                    TOKENS.append(Tokens(BLUETOKEN, grid[rowX][rowY], 'Miss', None, None, None))
                    SHOTSOUND.play()
                    MISSSOUND.play()
                    self.turn = False
        elif len(self.moves) > 0:
            COMPTURNTIMER = pygame.time.get_ticks()
            if COMPTURNTIMER - TURNTIMER >= 2000:
                rowX, rowY = self.moves[0]
                TOKENS.append(Tokens(REDTOKEN, grid[rowX][rowY], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None))
                gamelogic[rowX][rowY] = 'T'
                SHOTSOUND.play()
                HITSOUND.play()
                checkAndNotifyDestroyedShip(grid, gamelogic, enemy_fleet, window)
                self.moves.remove((rowX, rowY))
                self.turn = False
        return self.turn

    def generateMoves(self, coords, grid, lstDir=None):
        x, y = coords
        nx, ny = 0, 0
        for direction in ['North', 'South', 'East', 'West']:
            if direction == 'North' and lstDir != 'North':
                nx = x - 1
                ny = y
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'South')
            if direction == 'South' and lstDir != 'South':
                nx = x + 1
                ny = y
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'North')
            if direction == 'East' and lstDir != 'East':
                nx = x
                ny = y + 1
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'West')
            if direction == 'West' and lstDir != 'West':
                nx = x
                ny = y - 1
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'East')
        return

class Tokens:
    def __init__(self, image, pos, action, imageList=None, explosionList=None, soundFile=None):
        self.image = image
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        self.imageList = imageList
        self.explosionList = explosionList
        self.action = action
        self.soundFile = soundFile
        self.timer = pygame.time.get_ticks()
        self.imageIndex = 0
        self.explosionIndex = 0
        self.explosion = False

    def animate_Explosion(self):
        self.explosionIndex += 1
        if self.explosionIndex < len(self.explosionList):
            return self.explosionList[self.explosionIndex]
        else:
            return self.animate_fire()

    def animate_fire(self):
        if pygame.time.get_ticks() - self.timer >= 100:
            self.timer = pygame.time.get_ticks()
            self.imageIndex += 1
        if self.imageIndex < len(self.imageList):
            return self.imageList[self.imageIndex]
        else:
            self.imageIndex = 0
            return self.imageList[self.imageIndex]

    def draw(self, window):
        if not self.imageList:
            window.blit(self.image, self.rect)
        else:
            self.image = self.animate_Explosion()
            self.rect = self.image.get_rect(topleft=self.pos)
            self.rect[1] = self.pos[1] - 10
            window.blit(self.image, self.rect)

MESSAGE_BOXES = []

def checkAndNotifyDestroyedShip(grid, logicGrid, shiplist, window):
    destroyed_ships = []
    
    for ship in shiplist:
        ship_sunk = True
        ship_cells = []
        for i, row in enumerate(grid):
            for j, col in enumerate(row):
                if pygame.rect.Rect(col[0], col[1], CELLSIZE, CELLSIZE).colliderect(ship.rect):
                    ship_cells.append((i, j))
                    if logicGrid[i][j] != 'T':
                        ship_sunk = False
        
        if ship_sunk and ship_cells and not ship.is_sunk:
            ship.is_sunk = True
            destroyed_ships.append(ship)
            # Sử dụng hình ảnh ngang của tàu (hImage) nếu tàu đang nằm ngang, nếu không thì dùng vImage
            ship_image = ship.hImage if ship.rotation else ship.vImage
            MESSAGE_BOXES.append(MessageBox(f"{ship.name} destroyed!", ship_image))
    
    return destroyed_ships

def createGameGrid(rows, cols, cellsize, pos):
    startX = pos[0]
    startY = pos[1]
    coordGrid = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append((startX, startY))
            startX += cellsize
        coordGrid.append(rowX)
        startX = pos[0]
        startY += cellsize
    return coordGrid

def createGameLogic(rows, cols):
    gamelogic = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append(' ')
        gamelogic.append(rowX)
    return gamelogic

def updateGameLogic(coordGrid, shiplist, gamelogic):
    for i, rowX in enumerate(coordGrid):
        for j, colX in enumerate(rowX):
            if gamelogic[i][j] == 'T' or gamelogic[i][j] == 'X':
                continue
            else:
                gamelogic[i][j] = ' '
                for ship in shiplist:
                    if pygame.rect.Rect(colX[0], colX[1], CELLSIZE, CELLSIZE).colliderect(ship.rect):
                        gamelogic[i][j] = 'O'

def showGridOnScreen(window, cellsize, playerGrid, computerGrid):
    gamegrids = [playerGrid, computerGrid]
    for grid in gamegrids:
        for row in grid:
            for col in row:
                pygame.draw.rect(window, (255, 255, 255), (col[0], col[1], cellsize, cellsize), 1)

def printGameLogic():
    print('Player Grid'.center(50, '#'))
    for _ in pGameLogic:
        print(_)
    print('Computer Grid'.center(50, '#'))
    for _ in cGameLogic:
        print(_)

def loadImage(path, size, rotate=False):
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, size)
    if rotate == True:
        img = pygame.transform.rotate(img, -90)
    return img

def loadAnimationImages(path, aniNum, size):
    imageList = []
    for num in range(aniNum):
        if num < 10:
            imageList.append(loadImage(f'{path}00{num}.png', size))
        elif num < 100:
            imageList.append(loadImage(f'{path}0{num}.png', size))
        else:
            imageList.append(loadImage(f'{path}{num}.png', size))
    return imageList

def loadSpriteSheetImages(spriteSheet, rows, cols, newSize, size):
    image = pygame.Surface((128, 128))
    image.blit(spriteSheet, (0, 0), (rows * size[0], cols * size[1], size[0], size[1]))
    image = pygame.transform.scale(image, (newSize[0], newSize[1]))
    image.set_colorkey((0, 0, 0))
    return image

def createFleet():
    fleet = []
    for name in FLEET.keys():
        fleet.append(
            Ship(name,
                 FLEET[name][1],
                 FLEET[name][2],
                 FLEET[name][3],
                 FLEET[name][4],
                 FLEET[name][5],
                 FLEET[name][6],
                 FLEET[name][7])
        )
    return fleet

def sortFleet(ship, shiplist):
    shiplist.remove(ship)
    shiplist.append(ship)

def randomizeShipPositions(shiplist, gamegrid):
    placedShips = []
    for i, ship in enumerate(shiplist):
        validPosition = False
        while validPosition == False:
            ship.returnToDefaultPosition()
            rotateShip = random.choice([True, False])
            if rotateShip == True:
                yAxis = random.randint(0, 9)
                xAxis = random.randint(0, 9 - (ship.hImage.get_width()//50))
                ship.rotateShip(True)
                ship.rect.topleft = gamegrid[yAxis][xAxis]
            else:
                yAxis = random.randint(0, 9 - (ship.vImage.get_height()//50))
                xAxis = random.randint(0, 9)
                ship.rect.topleft = gamegrid[yAxis][xAxis]
            if len(placedShips) > 0:
                for item in placedShips:
                    if ship.rect.colliderect(item.rect):
                        validPosition = False
                        break
                    else:
                        validPosition = True
            else:
                validPosition = True
        placedShips.append(ship)

def deploymentPhase(deployment):
    if deployment == True:
        return False
    else:
        return True

def takeTurns(p1, p2):
    if p1.turn == True:
        p2.turn = False
    else:
        p2.turn = True
        if not p2.makeAttack(pGameLogic, pGameGrid, pFleet, GAMESCREEN):
            p1.turn = True

def checkForWinners(grid):
    validGame = True
    for row in grid:
        if 'O' in row:
            validGame = False
    return validGame

def shipLabelMaker(msg):
    textMessage = pygame.font.SysFont('Stencil', 22)
    textMessage = textMessage.render(msg, 1, (0, 17, 167))
    textMessage = pygame.transform.rotate(textMessage, 90)
    return textMessage

def displayShipNames(window):
    shipLabels = []
    for ship in ['carrier', 'battleship', 'destroyer', 'submarine', 'patrol boat']:
        shipLabels.append(shipLabelMaker(ship))
    startPos = 25
    for item in shipLabels:
        window.blit(item, (startPos, 600))
        startPos += 75

def mainMenuScreen(window):
    window.fill((0, 0, 0))
    window.blit(MAINMENUIMAGE, (0, 0))
    for button in BUTTONS:
        if button.name in ['Easy Computer', 'Hard Computer']:
            button.active = True
            button.draw(window)
        else:
            button.active = False

def deploymentScreen(window):
    window.fill((0, 0, 0))
    window.blit(BACKGROUND, (0, 0))
    window.blit(PGAMEGRIDIMG, (0, 0))
    window.blit(CGAMEGRIDIMG, (cGameGrid[0][0][0] - 50, cGameGrid[0][0][1] - 50))
    window.blit(RADARGRID, (cGameGrid[0][0][0], cGameGrid[0][-1][1]))

    for ship in pFleet:
        ship.draw(window)
        ship.snapToGridEdge(pGameGrid)
        ship.snapToGrid(pGameGrid)

    for ship in cFleet:
        ship.draw(window, is_computer_grid=True)
        ship.snapToGridEdge(cGameGrid)
        ship.snapToGrid(cGameGrid)

    displayShipNames(window)

    for button in BUTTONS:
        if button.name in ['Randomize', 'Reset', 'Deploy', 'Quit', 'Redeploy']:
            button.active = True
            button.draw(window)
        else:
            button.active = False

    computer.draw(window)

    for token in TOKENS:
        token.draw(window)

    updateGameLogic(pGameGrid, pFleet, pGameLogic)
    updateGameLogic(cGameGrid, cFleet, cGameLogic)

def endScreen(window):
    window.fill((0, 0, 0))
    window.blit(ENDSCREENIMAGE, (0, 0))
    for button in BUTTONS:
        if button.name in ['Easy Computer', 'Hard Computer', 'Quit']:
            button.active = True
            button.draw(window)
        else:
            button.active = False

def updateGameScreen(window, GAMESTATE):
    if GAMESTATE == 'Main Menu':
        mainMenuScreen(window)
    elif GAMESTATE == 'Deployment':
        deploymentScreen(window)
    elif GAMESTATE == 'Game Over':
        endScreen(window)
        player1Wins = checkForWinners(cGameLogic)
        computerWins = checkForWinners(pGameLogic)
        if player1Wins:
            MESSAGE_BOXES.append(MessageBox("You Win!", duration=5000))
        elif computerWins:
            MESSAGE_BOXES.append(MessageBox("You Lose!", duration=5000))

    i = 0
    while i < len(MESSAGE_BOXES):
        if not MESSAGE_BOXES[i].draw(window):
            MESSAGE_BOXES.pop(i)
        else:
            i += 1

    pygame.display.update()

# Game Settings and Variables
SCREENWIDTH = 1260
SCREENHEIGHT = 990
ROWS = 10
COLS = 10
CELLSIZE = 50
DEPLOYMENT = True
TURNTIMER = pygame.time.get_ticks()
GAMESTATE = 'Main Menu'

GAMESCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Battle Ship')

FLEET = {
    'carrier': ['carrier', 'assets/images/ships/carrier/carrier.png', (50, 600), (45, 245),
                0, '', None, None],
    'battleship': ['battleship', 'assets/images/ships/battleship/battleship.png', (125, 600), (40, 195),
                   4, 'assets/images/ships/battleship/battleshipgun.png', (0.4, 0.125), [-0.525, -0.34, 0.67, 0.49]],
    'destroyer': ['destroyer', 'assets/images/ships/destroyer/destroyer.png', (200, 600), (30, 145),
                  2, 'assets/images/ships/destroyer/destroyergun.png', (0.5, 0.15), [-0.52, 0.71]],
    'submarine': ['submarine', 'assets/images/ships/submarine/submarine.png', (275, 600), (30, 145),
                  1, 'assets/images/ships/submarine/submarinegun.png', (0.25, 0.125), [-0.45]],
    'patrol boat': ['patrol boat', 'assets/images/ships/patrol boat/patrol boat.png', (350, 600), (20, 95),
                    0, '', None, None]
}
STAGE = ['Main Menu', 'Deployment', 'Game Over']

pGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (50, 50))
pGameLogic = createGameLogic(ROWS, COLS)
pFleet = createFleet()

cGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (SCREENWIDTH - (ROWS * CELLSIZE), 50))
cGameLogic = createGameLogic(ROWS, COLS)
cFleet = createFleet()
randomizeShipPositions(cFleet, cGameGrid)

for ship in cFleet:
    ship.is_sunk = False

printGameLogic()

MAINMENUIMAGE = loadImage('assets/images/background/Battleship.jpg', (SCREENWIDTH // 3 * 2, SCREENHEIGHT))
ENDSCREENIMAGE = loadImage('assets/images/background/Carrier.jpg', (SCREENWIDTH, SCREENHEIGHT))
BACKGROUND = loadImage('assets/images/background/gamebg.png', (SCREENWIDTH, SCREENHEIGHT))
PGAMEGRIDIMG = loadImage('assets/images/grids/player_grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))
CGAMEGRIDIMG = loadImage('assets/images/grids/comp_grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))
BUTTONIMAGE = loadImage('assets/images/buttons/button.png', (150, 50))
BUTTONIMAGE1 = loadImage('assets/images/buttons/button.png', (250, 100))
BUTTONS = [
    Button(BUTTONIMAGE, (150, 50), (25, 900), 'Randomize'),
    Button(BUTTONIMAGE, (150, 50), (200, 900), 'Reset'),
    Button(BUTTONIMAGE, (150, 50), (375, 900), 'Deploy'),
    Button(BUTTONIMAGE1, (250, 100), (900, SCREENHEIGHT // 2 - 150), 'Easy Computer'),
    Button(BUTTONIMAGE1, (250, 100), (900, SCREENHEIGHT // 2 + 150), 'Hard Computer')
]
REDTOKEN = loadImage('assets/images/tokens/redtoken.png', (CELLSIZE, CELLSIZE))
GREENTOKEN = loadImage('assets/images/tokens/greentoken.png', (CELLSIZE, CELLSIZE))
BLUETOKEN = loadImage('assets/images/tokens/bluetoken.png', (CELLSIZE, CELLSIZE))
FIRETOKENIMAGELIST = loadAnimationImages('assets/images/tokens/fireloop/fire1_ ', 13, (CELLSIZE, CELLSIZE))
EXPLOSIONSPRITESHEET = pygame.image.load('assets/images/tokens/explosion/explosion.png').convert_alpha()
EXPLOSIONIMAGELIST = []
for row in range(8):
    for col in range(8):
        EXPLOSIONIMAGELIST.append(loadSpriteSheetImages(EXPLOSIONSPRITESHEET, col, row, (CELLSIZE, CELLSIZE), (128, 128)))
TOKENS = []
RADARGRID = loadImage('assets/images/grids/grid_faint.png', ((ROWS) * CELLSIZE, (COLS) * CELLSIZE))
HITSOUND = pygame.mixer.Sound('assets/sounds/explosion.wav')
HITSOUND.set_volume(0.05)
SHOTSOUND = pygame.mixer.Sound('assets/sounds/gunshot.wav')
SHOTSOUND.set_volume(0.05)
MISSSOUND = pygame.mixer.Sound('assets/sounds/splash.wav')
MISSSOUND.set_volume(0.05)

player1 = Player()
computer = EasyComputer()

RUNGAME = True
while RUNGAME:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNGAME = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if DEPLOYMENT == True:
                    for ship in pFleet:
                        if ship.rect.collidepoint(pygame.mouse.get_pos()):
                            ship.active = True
                            sortFleet(ship, pFleet)
                else:
                    if player1.turn == True:
                        player1.makeAttack(cGameGrid, cGameLogic, cFleet, GAMESCREEN)
                        if player1.turn == False:
                            TURNTIMER = pygame.time.get_ticks()
                for button in BUTTONS:
                    if button.rect.collidepoint(pygame.mouse.get_pos()):
                        if button.name == 'Deploy' and button.active == True:
                            status = deploymentPhase(DEPLOYMENT)
                            DEPLOYMENT = status
                        elif button.name == 'Redeploy' and button.active == True:
                            status = deploymentPhase(DEPLOYMENT)
                            DEPLOYMENT = status
                        elif button.name == 'Quit' and button.active == True:
                            RUNGAME = False
                        elif (button.name == 'Easy Computer' or button.name == 'Hard Computer') and button.active == True:
                            if button.name == 'Easy Computer':
                                computer = EasyComputer()
                            elif button.name == 'Hard Computer':
                                computer = HardComputer()
                            if GAMESTATE == 'Game Over':
                                TOKENS.clear()
                                for ship in pFleet:
                                    ship.returnToDefaultPosition()
                                randomizeShipPositions(cFleet, cGameGrid)
                                pGameLogic = createGameLogic(ROWS, COLS)
                                updateGameLogic(pGameGrid, pFleet, pGameLogic)
                                cGameLogic = createGameLogic(ROWS, COLS)
                                updateGameLogic(cGameGrid, cFleet, cGameLogic)
                                for ship in cFleet:
                                    ship.is_sunk = False
                                status = deploymentPhase(DEPLOYMENT)
                                DEPLOYMENT = status
                            GAMESTATE = STAGE[1]
                        button.actionOnPress()
            elif event.button == 2:
                printGameLogic()
            elif event.button == 3:
                if DEPLOYMENT == True:
                    for ship in pFleet:
                        if ship.rect.collidepoint(pygame.mouse.get_pos()) and not ship.checkForRotateCollisions(pFleet):
                            ship.rotateShip(True)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and DEPLOYMENT == True:
                for ship in pFleet:
                    if ship.active and not ship.checkForCollisions(pFleet):
                        ship.active = False

    if DEPLOYMENT == True:
        for ship in pFleet:
            if ship.active:
                ship.selectShipAndMove()

    updateGameScreen(GAMESCREEN, GAMESTATE)
    if GAMESTATE == 'Deployment' and DEPLOYMENT != True:
        player1Wins = checkForWinners(cGameLogic)
        computerWins = checkForWinners(pGameLogic)
        if player1Wins == True or computerWins == True:
            GAMESTATE = STAGE[2]
        takeTurns(player1, computer)
        if computer.turn:
            computer.makeAttack(pGameLogic, pGameGrid, pFleet, GAMESCREEN)

pygame.quit()