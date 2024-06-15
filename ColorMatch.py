

import time
import random
from LightStrip import *
from Button import *
from Displays import *
from Log import *
from StateModel import *

class ColorMatch:
    """ The main class for the color matching game """

    def __init__(self):
        Log.level = INFO

        # Create the neopixel strip
        self._strip = LightStrip("Neopixel", 2, 16)
        self._strip.setBrightness(0.2)

        # Create 4 buttons for the game
        self._redButton = Button(10, 'Red', buttonhandler=self)
        self._blueButton = Button(11, 'Blue', buttonhandler=self)
        self._yellowButton = Button(12, 'Yellow', buttonhandler=self)
        self._whiteButton = Button(13, 'White', buttonhandler=self)

        # Create an LCD Display for score and other info
        self._display = LCDDisplay(sda=0, scl=1, i2cid=0)

        # Create a State Model for the game
        self._model = StateModel(2, self, debug=True) # 2 states: 0-Start, 1-Running

        # Add the buttons to the model
        self._model.addButton(self._redButton)
        self._model.addButton(self._blueButton)
        self._model.addButton(self._yellowButton)
        self._model.addButton(self._whiteButton)

        # Initial values for the game
        self._score = 0
        self._lives = 3

        # Add transitions (only need to start the game)
        self._model.addTransition(0, [BTN1_PRESS, BTN2_PRESS, BTN3_PRESS, BTN4_PRESS], 1)

    def run(self):
        self._model.run()

    def stateDo(self, state):
        # No continuous actions needed in this game
        pass 

    def stateEntered(self, state, event):
        Log.i(f'Entering state {state} on event {EVENTNAMES[event]}')
        if state == 0:
            # Start Screen 
            self._score = 0
            self._lives = 3
            self._strip.off()
            self._display.showText('Color Match', 0, 3) 
            self._display.showText('Press any key', 1, 0)
        elif state == 1:
            # Game Running 
            self.fillBoard()
            self.updateDisplay()

    def stateLeft(self, state, event):
        Log.i(f'Leaving state {state} on event {EVENTNAMES[event]}')
        if state == 1:
            # Game Over 
            self._strip.off()
            self._display.reset()
            self._display.showText('Game Over', 0, 3)
            self._display.showText(f'Score: {self._score}', 1, 3)

    def buttonPressed(self, name):
        Log.i(f'Button pressed: {name}')  

        # Match button name to color
        colorMap = {
            'Red': RED,
            'Blue': BLUE,
            'Yellow': YELLOW,
            'White': WHITE
        }
        color = colorMap.get(name)

        if color:
            self.processMove(color)

    def processMove(self, color):
        """ Main game logic - check for matches, update score/lives """
        match = self.findMatch(color)

        if match:
            self._score += len(match) * 10  
            for i in match:
                self._strip.setPixel(i, BLACK, False) 
            self.fillBoard()
        else:
            self._lives -= 1
            if self._lives == 0: 
                self._model.gotoState(0, NO_EVENT)  # Game Over

        self.updateDisplay()

    def findMatch(self, color):
        """ Find 2 or more consecutive pixels of the given color """
        match = []
        count = 0
        for i in range(self._strip._numleds):
            if self._strip._np[i] == color:
                count += 1
                match.append(i)
            else:
                count = 0
                match = []  
        return match if count >= 2 else None 

    def fillBoard(self):
        """ Fill empty (black) pixels with random colors """
        for i in range(self._strip._numleds):
            if self._strip._np[i] == BLACK:
                self._strip._np[i] = random.choice([WHITE, BLUE, YELLOW, RED])
        self._strip.show()

    def updateDisplay(self):
        """ Display score and lives on the LCD """
        self._display.showText(f'Score: {self._score}', 0, 0)
        self._display.showText(f'Lives: {self._lives}', 1, 0)
