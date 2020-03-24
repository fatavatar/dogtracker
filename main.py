from gpiozero import Button
from gpiozero import TonalBuzzer
from gpiozero.tones import Tone
from signal import pause
from time import sleep
from enum import IntEnum
from datetime import datetime
import RPi_I2C_driver

mylcd = RPi_I2C_driver.lcd()

mylcd.lcd_clear()
mylcd.lcd_display_string("Hello World!", 1)
mylcd.lcd_display_string("Hello Me!", 2)
mylcd.lcd_display_string("Hello Dog!", 3)
mylcd.lcd_display_string("Hello Cat!", 4)

button = Button(4)

class Dog():
    def __init__(self, id, name, lastPee, lastPoop, lastFeed):
        self.lastPee = lastPee
        self.lastPoop = lastPoop
        self.lastFeed = lastFeed
        self.id = id
        self.name = name

dogs = { 1: Dog(1, "Millie", None, None, None),
         2: Dog(2, "Hazel", None, None, None)
         }

class State(IntEnum):
    DEFAULT = 1
    DOG_SELECT = 2
    SECRETION = 3
    HUMAN_SELECT_1 = 4
    HUMAN_SELECT_2 = 5
    ACTION_SELECT = 6
    CONFIRM = 7

class Action(IntEnum):
    WALK = 1
    FEED = 2
    ACCIDENT = 3
    EXIT = 4
    NONE = 5

class Secretion(IntEnum):
    PEE = 1
    POOP = 2
    BOTH = 3

humans = {
        1: "Nina",
        2: "Hugo",
        3: "Brody",
        4: "Dad",
        5: "Mom",
        6: "Kiefer"
        }

secretions = {
        1: "Pee",
        2: "Poop",
        3: "Pee and Poop"
        }


human = 0
dog = 0
secretion = 0

class ButtonHandler:
    def __init__(self, id, press_function):
        self.id = id
        self.pressed = False
        self.callback = press_function

    def button_down(self):
        self.pressed = True

    def button_up(self):
        if self.pressed:
            self.pressed = False
            self.callback(self.id)

buzzer = TonalBuzzer(17)

state = State.DEFAULT
action = Action.NONE

def pressCallback(id):
    print("Button " + str(id) + " Pressed")
    advanceState(id)

def advanceState(id):
    global state
    global action
    global dog
    global human
    global secretion

    if state == State.DEFAULT:
        state = State.ACTION_SELECT
        action = Action.NONE
    elif id == Action.EXIT and state != State.HUMAN_SELECT_2:
        state = State.DEFAULT
        action = Action.NONE
    elif state == State.ACTION_SELECT:
        action = id
        print("Action = " + str(action))
        print("action == WALK = " + str(action == Action.WALK))
        state = State.DOG_SELECT
    elif state == State.DOG_SELECT:
        dog = id
        if action == Action.FEED:
            state = State.HUMAN_SELECT_1
        else:
            state = State.SECRETION
    elif state == State.SECRETION:
        secretion = id
        state = State.HUMAN_SELECT_1
    elif state == State.HUMAN_SELECT_1 and id == Action.EXIT:
        state = State.HUMAN_SELECT_2
    elif state == State.HUMAN_SELECT_1:
        state = State.CONFIRM
        human = id
    elif state == State.HUMAN_SELECT_2:
        state = State.CONFIRM
        human = 3 + id
    elif state == State.CONFIRM:
        state = State.DEFAULT

    handleState()

def timeToString(tnow):
    if tnow == None:
        return "Unknown"
    if tnow.date() < datetime.now().date():
        return "Yesterday"
    return tnow.strftime('%H:%M')

def handleState():
    global state
    global action
    global dog
    global human
    global secretion

    if state == State.DOG_SELECT:
        print("Select Dog")
    elif state == State.SECRETION:
        print("SELECT POOP")
    elif state == State.HUMAN_SELECT_1:
        print("Select Human 1")
    elif state == State.HUMAN_SELECT_2:
        print("Select Human 2")
    elif state == State.ACTION_SELECT:
        print("Select Action")
    elif state == State.CONFIRM:
        tnow = datetime.now()
        if action == Action.FEED:
            print(humans[human] + " fed " + dogs[dog].name + " at " + timeToString(tnow))
            dogs[dog].lastFeed = tnow
        if action == Action.WALK:
            print(humans[human] + " took out " + dogs[dog].name + " to " + secretions[secretion] + " at " + timeToString(tnow))
            if secretion == Secretion.POOP or secretion == Secretion.BOTH:
                dogs[dog].lastPoop = tnow
            if secretion == Secretion.PEE or secretion == Secretion.BOTH:
                dogs[dog].lastPee = tnow
        if action == Action.ACCIDENT:
            print(humans[human] + " cleaned up " + dogs[dog].name + "'s " + secretions[secretion] + " at " + timeToString(tnow))
    else:
        print(dogs[1].name + ", last out " + timeToString(dogs[1].lastPee))
        print(dogs[2].name + ", last out " + timeToString(dogs[2].lastPee))
        dog = 0
        human = 0
        action = Action.NONE
        secretion = 0

button4Handler = ButtonHandler(1, pressCallback)
button.when_pressed = button4Handler.button_down
button.when_released = button4Handler.button_up


pause()
