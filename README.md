# MicroBit Fireflies

This project uses one or more micro:bit boards to simulate fireflies, either using the on-board LEDs ("display") or WS2811 (NeoPixel) RGB LEDs. It was inspired by the [Micro:Bit firefly demo](http://microbit-micropython.readthedocs.io/en/latest/tutorials/radio.html#fireflies) and [Nicky Case's Firefly simulation](http://ncase.me/fireflies/)

I was intrigued by the idea of creating up to one hundred synchronized fireflies, but realized that if each firefly required one micro:bit that this would be too costly. I realized that since the micro:bit can control WS2811 LEDs that with one micro:bit I could simulate multiply fireflies. If I could get one board to simulate 25 fireflies, then I would only need four boards.

The first step was to create a program that would use the 5x5 LED display on the micro:bit board. Each LED would act as an independent firefly.

## Basic Operation
Each firefly has its own timer. When the timer counts down to zero, the firefly flashes and notifies its neighbors that it flashed. When a firefly is notified that its neighbor flashed, it adjusts it timer by a very small percentage. Those rules are sufficient to get 25 random fireflies to flash in sync. To get multiple boards to synchronize, some of the fireflies will also broadcast a radio message that says "I blinked". The program will check the radio for a message. If it sees an "I blinked" message it notifies some of the fireflies on the board. After about five minutes, a board will randomize the timers for its fireflies and send a "randomize" message to the other boards, which restarts the self-synchronization behavior again.
I have found that the boards do not perfectly synchronize all of the fireflies. There is always some slight variation. I imagine, but do not know for certain, that this is due to the speed of the python environment.

When a board starts up it will broadcom a "hello" message. When a board receives a "hello" message it will show a small diamond on the display for a moment.

## Buttons
* **Randomize locally**: Press button-B to randomize the fireflies on the local board
* **Randomize all**: Press button-A to randomize the fireflies on the local board and the remote boards
* **All On**: Press button-A and hold for one second to perform an "all on" test for the local board and the remote boards (Note that this actually shows a large square image)

## Configuration
### Firefly count
```python
FF_CNT = 25
```
`FF_CNT` sets the number of fireflies. 
### Blink timing
```python
BLINK_INTERVAL = 5000
```
The blink timing is in milliseconds. The current version blinks a each firefly every five seconds.
### Light timing
```python
BLINK_ON_TIME = 200
BLINK_FADE_STEP = 50
MAX_BRIGHT = 9
```
When a firefly flashes it immediately goes to a maximum brightness (`MAX_BRIGHT`) for the `BLINK_ON_TIME` and then fades by one each `BLINK_FADE_STEP` milliseconds. `9` is the maximum brightness of the LEDs on the micro:bit.
### Synchronization speed
```python
TIMER_NUDGE = 0.02
```
When a firefly is notified that its neighbor blinked, it will adjust its timer by `TIMER_NUDGE`. The smaller the number the longs it takes the fireflies to synchronize.
### Restart time
```python
RESTART_COUNT = 60 # About 5 minutes
```
The program counts the number of times the firefly 0 flashes. When it hits `RESTART_COUNT` it will randomize the timing of the fireflies.
### Restart time
```python
RADIO_NOTIFY_COUNT = 5
```
Only some of the fireflies send a radio message when they blink. This is controlled with `RADIO_NOTIFY_COUNT`
## Notes

### Memory
The biggest challenge with these boards is that they run out of memory very easily. I typically heavily comment my code. This quickly caused the files to fail to be transfered to the boards. Without warning. And without explanation. The `uflash` application I was using simply exited. Only after reviewing the `uflash` source did I see the `assert` line that insures that the filesize is 8K or less.
If the application fits on the board, it might still fail to be compiled by the Micropython environment.
I also had problems with the amount of data I needed to store the information for the fireflies.

## Files
### fireflies_sync_display.py
The `fireflies_sync_display.py` version shows the fireflies on the 5x5 LED display on the micro:bit

### fireflies_sync_neopixels.py
(Not available yet.)
