try:
    import PyQt5
    from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QAbstractButton, QPushButton, QLabel
    from PyQt5.QtGui import QPixmap, QPainter, QCursor
except:
    input('Error importing PyQt5 components. (press enter to close)')
    exit()

import os

from coreLogic import (_input, _output, _andGate, _orGate, _xorGate,
                   _nandGate, _norGate, _xnorGate, _notGate)

# PICK UP AT "mousePlaceObject"

class mainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        print('starting...')
        self.initData()
        self.initUI()
        #self.loadProgram('projects/test/test.lgc')
                
    def initData(self):
        self.settings = {}
        self.settingsFilePath = os.environ['LOCALAPPDATA'] + '\\Logic\\settings.cfg'
        print('Retrieving settings from {}'.format(self.settingsFilePath))
        with open(self.settingsFilePath, 'r') as settingsFile:
            settingsRaw = settingsFile.read().splitlines()
        for i in range(len(settingsRaw)):
            currentSetting = settingsRaw[i].split(': ')
            self.settings.update({currentSetting[0]: currentSetting[1]})
        print('Retrieved settings:\n{}'.format(self.settings))
        self.objects = []
        self.updateCycles = 5
        self.projectDir = self.settings['projectDir']
        self.gridSize = 10
        self.gridOffset = (0, 0)
        self.windowPosOffset = (0, -36)
        docPos = (0, 0)
        self.objectToPlace = ''
        self.placeLocation = ()
        self.objectTypes = {'in': gInput, 'out': gOutput, 'and': gAndGate, 'or': gOrGate, 'xor': gXorGate,
                            'nand': gNandGate, 'nor': gNorGate, 'xnor': gXnorGate, 'not': gNotGate}

    def initUI(self):
        self.setGeometry(200, 500, 800, 500)
        self.objectButtons()
        self.canvas = QPushButton(self)
        self.canvas.setText('')
        self.canvas.setGeometry(60, 10, 740, 450)
        self.canvas.clicked.connect(self.mousePlaceObject)

        self.updateButton = QPushButton(self)
        self.updateButton.setText('Update')
        self.updateButton.setGeometry(730, 470, 60, 20)
        self.updateButton.clicked.connect(self.update)
        
        self.loadBtn = QPushButton(self)
        self.loadBtn.setText('Load')
        self.loadBtn.setGeometry(680, 470, 40, 20)
        self.loadBtn.clicked.connect(self.openProgram)

    def objectButtons(self):
        ctr = 0
        self.newInButton = QPushButton(self)
        self.newInButton.setText('input')
        self.newInButton.setGeometry(10, 10 + (ctr * 30), 40, 20)
        self.newInButton.clicked.connect(self.newInput)

        ctr += 1
        self.newOutButton = QPushButton(self)
        self.newOutButton.setText('output')
        self.newOutButton.setGeometry(10, 10 + (ctr * 30), 40, 20)
        self.newOutButton.clicked.connect(self.newOutput)

        ctr += 1
        self.newAndButton = QPushButton(self)
        self.newAndButton.setText('and')
        self.newAndButton.setGeometry(10, 10 + (ctr * 30), 40, 20)
        self.newAndButton.clicked.connect(self.newAndGate)

        ctr += 1
        self.newOrButton = QPushButton(self)
        self.newOrButton.setText('or')
        self.newOrButton.setGeometry(10, 10 + (ctr * 30), 40, 20)
        self.newOrButton.clicked.connect(self.newOrGate)
        
        ctr += 1
        self.newXorButton = QPushButton(self)
        self.newXorButton.setText('xor')
        self.newXorButton.setGeometry(10, 10 + (ctr * 30), 40, 20)
        self.newXorButton.clicked.connect(self.newXorGate)
        
        ctr += 1
        self.newNandButton = QPushButton(self)
        self.newNandButton.setText('nand')
        self.newNandButton.setGeometry(10, 10 + (ctr * 30), 40, 20)
        self.newNandButton.clicked.connect(self.newNandGate)
        
        ctr += 1
        self.newNorButton = QPushButton(self)
        self.newNorButton.setText('nor')
        self.newNorButton.setGeometry(10, 10 + (ctr * 30), 40, 20)
        self.newNorButton.clicked.connect(self.newNorGate)
        
        ctr += 1
        self.newXnorButton = QPushButton(self)
        self.newXnorButton.setText('xnor')
        self.newXnorButton.setGeometry(10, 10 + (ctr * 30), 40, 20)
        self.newXnorButton.clicked.connect(self.newXnorGate)
        
        ctr += 1
        self.newNotButton = QPushButton(self)
        self.newNotButton.setText('not')
        self.newNotButton.setGeometry(10, 10 + (ctr * 30), 40, 20)
        self.newNotButton.clicked.connect(self.newNotGate)
        
    #in, out, and, or, xor, nand, nor, xnor, not
    def newInput(self):
        print('new input')
        self.objectToPlace = 'in'

    def newOutput(self):
        print('new output')
        self.objectToPlace = 'out'

    def newAndGate(self):
        print("new andGate")
        self.objectToPlace = 'and'

    def newOrGate(self):
        print("new orGate")
        self.objectToPlace = 'or'

    def newXorGate(self):
        print("new xorGate")
        self.objectToPlace = 'xor'

    def newNandGate(self):
        print("new nandGate")
        self.objectToPlace = 'nand'

    def newNorGate(self):
        print("new norGate")
        self.objectToPlace = 'nor'

    def newXnorGate(self):
        print("new xnorGate")
        self.objectToPlace = 'xnor'

    def newNotGate(self):
        print("new notGate")
        self.objectToPlace = 'not'

    def windowToCanvas(self, x, y):     #Convert coordinates relative to the window to canvas coordinates.
        canvasPos = self.canvas.pos()
        X = int(((x - canvasPos.x()) + self.gridOffset[0]) / self.gridSize)
        Y = int(((y - canvasPos.y()) + self.gridOffset[1]) / self.gridSize)
        return (X, Y)

    def canvasToWindow(self, x, y):     #Convert canvas coordinates to coordinates relative to the window
        canvasPos = self.canvas.pos()
        X = canvasPos.x() + (x * self.gridSize) + self.gridOffset[0]
        Y = canvasPos.y() + (y * self.gridSize) + self.gridOffset[1]
        return (X, Y)       #(0, 0)canvas is the canvas's upper left corner.

    def canvasPlaceObject(self, x, y):
        if self.objectToPlace in self.objectTypes.keys():
            #print('placing object from canvas {}'.format(self.objectToPlace))
            newObject = self.objectTypes[self.objectToPlace](self)
            pos = (x, y)
            print(pos)
            pos = self.canvasToWindow(*pos)
            print(pos, end = '\n\n')
            newObject.move(pos[0], pos[1])
            newObject.show()
            self.objects.append(newObject)

    def mousePlaceObject(self):
        if self.objectToPlace in self.objectTypes.keys():
            #print('placing object from mouse {}'.format(self.objectToPlace))
            canvasPos = self.canvas.pos()
            windowPos = self.pos()
            mousePos = QCursor.pos()
            placePos = ((mousePos.x() - windowPos.x()) + self.windowPosOffset[0], (mousePos.y() - windowPos.y()) + self.windowPosOffset[1])
            print(placePos)
            self.canvasPlaceObject(*self.windowToCanvas(*placePos))

            #Test object to place
            #self.testLabel = QLabel(self)
            #self.testLabel.move(placePos[0], placePos[1])
            #self.testLabel.setText('it works if you see this')
            #self.testLabel.show()

    def update(self):
        for i in range(self.updateCycles):
            for o in self.objects:
                print(o)
                o.update()

    def testGates(self):
        andGate = _andGate()
        orGate = _orGate()
        in1 = gInput(self)
        in2 = gInput(self)
        out1 = gOutput(self)
        out2 = gOutput(self)

        andGate._in[0].connect(in1._out)
        andGate._in[1].connect(in2._out)
        out1._in.connect(andGate._out)
        
        orGate._in[0].connect(in1._out)
        orGate._in[1].connect(in2._out)
        out2._in.connect(orGate._out)

        andGate.update()    #0, 0
        orGate.update()
        out1.update()
        out2.update()

        in2.toggle()
        andGate.update()    #0, 1
        orGate.update()
        out1.update()
        out2.update()

        in1.toggle()        #1, 0
        in2.toggle()
        andGate.update()
        orGate.update()
        out1.update()
        out2.update()

        in2.toggle()        #1, 1
        andGate.update()
        orGate.update()
        out1.update()
        out2.update()

    def testObjects(self):
        in1 = gInput(self)
        in2 = gInput(self)
        and1 = gAndGate(self)
        or1 = gOrGate(self)
        out1 = gOutput(self)
        out2 = gOutput(self)

        loc = self.gridByCoord(0, 0)
        in1.move(loc[0], loc[1])
        loc = self.gridByCoord(0, 2)
        in2.move(loc[0], loc[1])
        loc = self.gridByCoord(3, 0)
        and1.move(loc[0], loc[1])
        loc = self.gridByCoord(3, 6)
        or1.move(loc[0], loc[1])
        loc = self.gridByCoord(9, 2)
        out1.move(loc[0], loc[1])
        loc = self.gridByCoord(9, 8)
        out2.move(loc[0], loc[1])

        and1._in[0].connect(in1._out)
        and1._in[1].connect(in2._out)
        or1._in[0].connect(in1._out)
        or1._in[1].connect(in2._out)
        out1._in[0].connect(and1._out)
        out2._in[0].connect(or1._out)

        self.objects.append(in1)
        self.objects.append(in2)
        self.objects.append(and1)
        self.objects.append(or1)
        self.objects.append(out1)
        self.objects.append(out2)

    def openProgram(self):
        print('findProgram called')
        fileName = QFileDialog.getOpenFileName(self, 'Open logic program', self.projectDir)[0]
        if fileName == '':
            print('No file selected, canceling')
            return
        self.loadProgram(fileName)

    def loadProgram(self, programPath):
        commands = []
        with open(programPath, 'r') as programFile:
            loop = True
            while loop:
                data = programFile.readline()
                if data:
                    commands.append(data)
                else:
                    print('Finished reading program file.')
                    loop = False
        self.outputNames = {}
        self.objects = []
        for c in commands:              #run through the list of commands and create the items
            data = c.split()
            newItemType = data[0].lower()
            comment = False
            if newItemType == 'in':
                coordsAt = 2
                outputLoc = 1
            elif newItemType == 'out':
                coordsAt = 2
                outputLoc = -1
            elif newItemType in ['and', 'or', 'xor', 'nand', 'nor', 'xnor', 'not']:
                coordsAt = 4
                outputLoc = 3
            else:
                coordsAt = 0
                outputLoc = -1
                comment = True

            loc = int(data[coordsAt]), int(data[coordsAt + 1])
            self.canvasPlaceObject(loc[0], loc[1])
            if outputLoc != -1:
                self.outputNames.update({data[outputLoc]: self.objects[len(self.objects) -1 ]._out})

        print('\n\n\n')
        print(self.outputNames)
        ctr = -1
        for c in commands:              #run through the list of commands and connect the items
            data = c.split()
            newItemType = data[0].lower()
            if newItemType == 'in':
                inputs = []
                ctr += 1
            elif newItemType in ['out', 'not']:
                inputs = [0]
                ctr += 1
            elif newItemType in ['and', 'or', 'xor', 'nand', 'nor', 'xnor']:
                inputs = [0, 1]
                ctr += 1
            else:
                inputs = []
            print(newItemType)
            print(ctr)
            print(inputs)
            for i in inputs:                  
                self.objects[ctr]._in[i].connect(self.outputNames[data[i + 1]])
                
# Object definitions:
class gInput(QPushButton):
    xSize = 20
    ySize = 20
    def __init__(self, parent):
        self.parent = parent
        QPushButton.__init__(self, self.parent)
        self.clicked.connect(self.toggle)
        self.value = False
        self._out = _output()
        self.setText(str(int(self.value)))

    def toggle(self):
        self.value = not self.value
        self._out.set(self.value)
        self.setText(str(int(self.value)))

    def move(self, xPos, yPos):
        self.xPos = xPos
        self.yPos = yPos
        self.setGeometry(self.xPos, self.yPos, self.xSize, self.ySize)

    def update(self):
        pass

class gOutput(QLabel):
    xSize = 20
    ySize = 20
    styleSheet = """background-color: rgb(225, 225, 225);\n
        border: 1px solid rgb(173, 173, 173);\n
        text-align: center;"""

    def __init__(self, parent):
        self.parent = parent
        QLabel.__init__(self, self.parent)
        self.value = False
        self._in = [_input()]
        self.setText(str(int(self.value)))
        self.setStyleSheet(self.styleSheet)

    def connect(self, target):
        self._in.connect(target)

    def move(self, xPos, yPos):
        self.xPos = xPos
        self.yPos = yPos
        self.setGeometry(self.xPos + 1, self.yPos + 1, self.xSize - 2, self.ySize - 2)

    def update(self):
        self.value = self._in[0].fetch()
        self.setText(str(int(self.value)))
        print('update for {} with value {}'.format(self, self.value))

class gGate(QAbstractButton):
    xSize = 50
    ySize = 50
    def __init__(self, parent, imagePath):
        self.parent = parent
        self.imagePath = imagePath
        QAbstractButton.__init__(self, self.parent)
        self.move(70, 20)
        self.pixMap = QPixmap(imagePath)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixMap)

    def sizeHint(self):
        return self.pixMap.size()

    def move(self, xPos, yPos):
        self.xPos = xPos
        self.yPos = yPos
        self.setGeometry(self.xPos, self.yPos, self.xSize, self.ySize)

class gAndGate(_andGate, gGate):
    def __init__(self, parent):
        self.parent = parent
        self.imagePath = 'images/gates/andRaw.png'
        gGate.__init__(self, self.parent, self.imagePath)
        _andGate.__init__(self)

class gOrGate(_orGate, gGate):
    def __init__(self, parent):
        self.parent = parent
        self.imagePath = 'images/gates/orRaw.png'
        gGate.__init__(self, self.parent, self.imagePath)
        _andGate.__init__(self)

class gXorGate(_xorGate, gGate):
    def __init__(self, parent):
        self.parent = parent
        self.imagePath = 'images/gates/xorRaw.png'
        gGate.__init__(self, self.parent, self.imagePath)
        _andGate.__init__(self)

class gNandGate(_nandGate, gGate):
    def __init__(self, parent):
        self.parent = parent
        self.imagePath = 'images/gates/nandRaw.png'
        gGate.__init__(self, self.parent, self.imagePath)
        _andGate.__init__(self)

class gNorGate(_norGate, gGate):
    def __init__(self, parent):
        self.parent = parent
        self.imagePath = 'images/gates/norRaw.png'
        gGate.__init__(self, self.parent, self.imagePath)
        _andGate.__init__(self)

class gXnorGate(_xnorGate, gGate):
    def __init__(self, parent):
        self.parent = parent
        self.imagePath = 'images/gates/xnorRaw.png'
        gGate.__init__(self, self.parent, self.imagePath)
        _andGate.__init__(self)

class gNotGate(_notGate, gGate):
    def __init__(self, parent):
        self.parent = parent
        self.imagePath = 'images/gates/notRaw.png'
        gGate.__init__(self, self.parent, self.imagePath)
        _notGate.__init__(self)