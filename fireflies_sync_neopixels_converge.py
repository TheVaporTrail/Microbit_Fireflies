# Fireflies
from microbit import button_a, sleep, running_time, pin0
import random
import radio
import neopixel

_FF_CNT = 25

BLINK_INTERVAL = 5000
BLINK_ON_TIME = 200
BLINK_FADE_STEP = 50

MAX_BRIGHT = 9
_MAX_COLOR = 120

TIMER_NUDGE = 0.02
RESTART_COUNT = 60
RADIO_NOTIFY_COUNT = 5

BLINK_ON_MAX = (BLINK_ON_TIME + MAX_BRIGHT * BLINK_FADE_STEP)

RP_HELLO   = 0
RP_RANDOM  = 1
RP_BLINK   = 2
RP_ALLON   = 3

#_TS = 0
_TMR = 1
_LED = 2

gFF = [[0, 0, 0] for f in range(_FF_CNT)]
gData = bytearray(_FF_CNT*2)
gImage = neopixel.NeoPixel(pin0, _FF_CNT)
gCycleCount = 0
gClr = 0


def ffRandomize():
    global gImage, gFF, gData, gCycleCount, gClr
    gCycleCount = 0
    gClr = random.randint(0, _MAX_COLOR)
    for k in range(_FF_CNT):
        gFF[k][_TMR]  = random.randint(0, BLINK_INTERVAL)
        gFF[k][_LED]  = BLINK_ON_MAX
        gData[k] = 0
        gData[_FF_CNT + k] = random.randint(0, _MAX_COLOR)
        gImage[k] = (0, 0, 0)

def ffFlashed(f):
    global gFF, gClr, gData
    for k in [(f - 2) % _FF_CNT, (f - 1) % _FF_CNT, (f + 1) % _FF_CNT, (f + 2) % _FF_CNT]:
        if gFF[k][_TMR] > 0 and gFF[k][_TMR] < BLINK_INTERVAL:
            gFF[k][_TMR] -= int((BLINK_INTERVAL - gFF[k][_TMR]) * TIMER_NUDGE) 
            if gFF[k][_TMR] < 0:
                gFF[k][_TMR] = 0

def ffShowFF():
    for f in range(_FF_CNT):
        gImage[f] = (gData[f] * 3, gData[f] * 3, 0)
    gImage.show()

def ffShowMsg(m):
    if m == RP_HELLO:
        clr = (0, 0, 12)
    elif m == RP_RANDOM:   
        clr = (8, 0, 0)
    elif m == RP_ALLON:
        clr = (8, 8, 8)
    else:
        clr = (0, 0, 0)
        
    for f in range(_FF_CNT):
        gImage[f] = clr
    gImage.show()
   
def ffSend(cmd, param = 0):
    radio.send_bytes(bytearray([cmd, param]))

for f in range(_FF_CNT):
    gFF[f][0] = running_time()
ffRandomize()

f = 0
pushUpdate = False
counter = 0
notifyCount = 0

radio.on()
radio.config(address = 0x46466c79)  # FFly
radio.config(length = 3)
radio.config(queue = 8)

ffSend(RP_HELLO)
ffShowMsg(RP_HELLO)
sleep(250)
ffShowFF()

while True:
    counter = (counter + 1) % _FF_CNT
    if counter == 0:
        notifyCount = 0
        
    if gCycleCount >= RESTART_COUNT:
        ffRandomize()
        ffSend(RP_RANDOM)
        ffShowMsg(RP_RANDOM)
        sleep(250)
        ffShowFF()
        
    f = (f + 1) % _FF_CNT
    
    update = False

    elapsedTime = running_time() - gFF[f][0]
    if elapsedTime < 0:
        elapsedTime = 0
    gFF[f][0] = running_time()

    gFF[f][_TMR] -= elapsedTime
    
    if gFF[f][_TMR] <= 0:
        while gFF[f][_TMR] <= 0:
            gFF[f][_TMR] += BLINK_INTERVAL
        
        if gData[f] == 0:
            gFF[f][_LED] = 0
            gData[f] = MAX_BRIGHT
            update = True

        ffFlashed(f)
        
        d = gClr - gData[_FF_CNT + f]
        if d > -30 and d < 0:
            d = -30
        elif d < 30 and d > 0:
            d = 30
        gData[_FF_CNT + f] = (gData[_FF_CNT + f] + d//30) % _MAX_COLOR
        
        if notifyCount < RADIO_NOTIFY_COUNT:
            ffSend(RP_BLINK, f)
            notifyCount += 1
            
        if f == 0:
            gCycleCount += 1

    if gFF[f][_LED] < BLINK_ON_MAX:
        gFF[f][_LED] += elapsedTime
        tmr = gFF[f][_LED]
        if tmr <= 0 or tmr >= BLINK_ON_MAX:
            br = 0
        elif tmr < BLINK_ON_TIME:
            br = MAX_BRIGHT
        else:
            br = MAX_BRIGHT - (tmr - BLINK_ON_TIME) // BLINK_FADE_STEP
        if br < 0:
            br = 0
        elif br > MAX_BRIGHT:
            br = MAX_BRIGHT
        if gData[f] != br:
            gData[f] = br
            update = True

    if update:
        br = gData[f]
        c  = gData[_FF_CNT + f]
        if c < 40:
            r = 40 - c
            g = 0
            b = c
        elif c < 80:
            r = 0
            g = c - 40
            b = 80 - c
        else:
            r = c - 80
            g = 120 - c
            b = 0
        gImage[f] = (br*3*r//40, br*3*g//40, br*3*b//40)
        pushUpdate = True
    
    if pushUpdate and counter == 0:
        gImage.show()
        pushUpdate = False

    if button_a.was_pressed():
        ffRandomize()
        ffSend(RP_RANDOM)
        i = 10
        while (i > 0) and button_a.is_pressed():
            i -= 1
            sleep(100)
        if button_a.is_pressed():
            ffSend(RP_ALLON)
            ffShowMsg(RP_ALLON)
            sleep(1000)
            ffShowFF()
    
    msg = radio.receive_bytes()
    if msg != None and len(msg) >= 2:
        cmd = msg[0]
        if (cmd == RP_RANDOM):
            ffRandomize()
            ffShowMsg(RP_RANDOM)
            sleep(250)
            ffShowFF()
        elif (cmd == RP_ALLON):
            ffShowMsg(RP_ALLON)
            sleep(1000)
            ffShowFF()
        elif (cmd == RP_BLINK):
            param = msg[1]
            ffFlashed(param)
        elif (cmd == RP_HELLO):
            ffShowMsg(RP_HELLO)
            sleep(250)
            ffShowFF()
