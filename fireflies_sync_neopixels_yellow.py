#
# Fireflies
from microbit import button_a, button_b, sleep, running_time, pin0
import random
import radio
import neopixel

FF_CNT = 25

BLINK_INTERVAL = 5000
BLINK_ON_TIME = 200
BLINK_FADE_STEP = 50

MAX_BRIGHT = 9

TIMER_NUDGE = 0.02
RESTART_COUNT = 60
RADIO_NOTIFY_COUNT = 5

BLINK_ON_MAX = (BLINK_ON_TIME + MAX_BRIGHT * BLINK_FADE_STEP)

# Radio "protocol"
RP_HELLO   = 0
RP_RANDOM  = 1
RP_BLINK   = 2
RP_ALLON   = 3

FF_TS         = 0
FF_BLINK_TMR  = 1
FF_LIGHT_TMR  = 2

gFireflies = [[0, 0, 0] for f in range(FF_CNT)]
gBrightness = bytearray(25)
gImage = neopixel.NeoPixel(pin0, FF_CNT)
gCycleCount = 0

def ffRandomize():
    global gImage
    global gFireflies
    global gBrightness
    global gCycleCount
    gCycleCount = 0
    for k in range(FF_CNT):
        ff = gFireflies[k]
        ff[FF_BLINK_TMR]  = random.randint(0, BLINK_INTERVAL)
        ff[FF_LIGHT_TMR]  = BLINK_ON_MAX
        gBrightness[k] = 0
        gImage[k] = (0, 0, 0)

def ffNudge(k):
    global gFireflies
    ff = gFireflies[k]
    if ff[FF_BLINK_TMR] > 0:
        timeToGo = BLINK_INTERVAL - ff[FF_BLINK_TMR]
        if timeToGo < 0:
            timeToGo = 0
        ff[FF_BLINK_TMR] -= int(timeToGo * TIMER_NUDGE)
        if ff[FF_BLINK_TMR] < 0:
            ff[FF_BLINK_TMR] = 0

def ffFlashed(f):
    ffNudge((f - 5) % FF_CNT)
    ffNudge((f - 1) % FF_CNT)
    ffNudge((f + 5) % FF_CNT)
    ffNudge((f + 1) % FF_CNT)

def ffShowFF():
    for f in range(FF_CNT):
        gImage[f] = (gBrightness[f] * 3, gBrightness[f] * 3, 0)
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
        
    for f in range(FF_CNT):
        gImage[f] = clr
    gImage.show()
   
def ffSend(cmd, param = 0):
    radio.send_bytes(bytearray([cmd, param]))

for f in range(FF_CNT):
    gFireflies[f][FF_TS] = running_time()
ffRandomize()

f = 0
pushUpdate = False
counter = 0
increment = 4
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
    counter = (counter + 1) % FF_CNT
    if counter == 0:
        notifyCount = 0
        
    if gCycleCount >= RESTART_COUNT:
        ffRandomize()
        ffSend(RP_RANDOM)
        ffShowMsg(RP_RANDOM)
        sleep(250)
        ffShowFF()
        
    if increment == 0:
        f = random.randint(0, FF_CNT - 1)
    else:
        f = (f + increment) % FF_CNT
        
    ff = gFireflies[f]
    
    update = False

    elapsedTime = running_time() - ff[FF_TS]
    if elapsedTime < 0:
        elapsedTime = 0
    ff[FF_TS] = running_time()

    ff[FF_BLINK_TMR] -= elapsedTime
    
    if ff[FF_BLINK_TMR] <= 0:
        while ff[FF_BLINK_TMR] <= 0:
            ff[FF_BLINK_TMR] += BLINK_INTERVAL
        
        if gBrightness[f] == 0:
            ff[FF_LIGHT_TMR] = 0
            gBrightness[f] = MAX_BRIGHT
            update = True

        ffFlashed(f)
        
        if notifyCount < RADIO_NOTIFY_COUNT:
            ffSend(RP_BLINK, f)
            notifyCount += 1
            
        if f == 0:
            gCycleCount += 1

    if ff[FF_LIGHT_TMR] < BLINK_ON_MAX:
        ff[FF_LIGHT_TMR] += elapsedTime
        tmr = ff[FF_LIGHT_TMR]
        br = 0
        if tmr <= 0 or tmr >= BLINK_ON_MAX:
            br = 0
        elif tmr < BLINK_ON_TIME:
            br = MAX_BRIGHT
        else:
            br = MAX_BRIGHT - int((tmr - BLINK_ON_TIME) / BLINK_FADE_STEP)
        if br < 0:
            br = 0
        elif br > MAX_BRIGHT:
            br = MAX_BRIGHT
        if gBrightness[f] != br:
            gBrightness[f] = br
            update = True

    if update:
        gImage[f] = (gBrightness[f]*3, gBrightness[f]*3, 0)
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
    
    if button_b.was_pressed():
        ffRandomize()
        
    msg = radio.receive_bytes()
    if msg != None and len(msg) >= 2:
        cmd = msg[0]
        if (cmd == RP_RANDOM):
            ffRandomize()
            ffShowMsg(RP_RANDOM)
            sleep(1000)
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
