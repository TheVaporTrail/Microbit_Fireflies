# MicroBit Fireflies

This project uses one or more micro:bit boards to simulate fireflies, either using the on-board LEDs or WS2811 RGB LEDs (NeoPixels). It was inspired by the [Micro:Bit firefly demo](http://microbit-micropython.readthedocs.io/en/latest/tutorials/radio.html#fireflies) and [Nicky Case's Firefly simulation](http://ncase.me/fireflies/)

I was intrigued by the idea of creating large numbers of synchronized fireflies. Using one micro:bit per firefly would be both too expensive and too impractical (e.g., to reprogram). Instead each micro:bit simulates multiple (25) fireflies, and multiple micro:bit boards communicate via radio so that all of the fireflies become synchronized.
The basic application uses the on-board LEDs, where each LED represents one firefly. The NeoPixel versions of the application uses the neopixel library to drive external LEDs.

## Available versions
* **fireflies_sync_display.py**: Uses on-board LEDs
* **fireflies_sync_neopixels_yellow.py**: Uses WS2812 LEDs, always yellow
* **fireflies_sync_neopixels_random.py**: Uses WS2812 LEDs, with random colors
* **fireflies_sync_neopixels_converge.py**: Uses WS2812 LEDs, which start as random colors but eventually converge to a single random color

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

### fireflies_sync_neopixels_yellow.py
`fireflies_sync_neopixels_yellow.py` uses the `neopixel` library to show the fireflies on WS2812 (NeoPixel) LEDs. All code (and imports) used to show the fireflies on the 5x5 LED display is removed. The fireflies are all yellow. To allow the micro:bit board to flash up to 25 LEDs simultaneously that are directly connected to the board, the brightness of the LEDs is limited to roughly 10% of the maximum possible brightness (27 vs 255). Note this [warning](http://microbit-micropython.readthedocs.io/en/latest/neopixel.html): "Do not use the 3v connector on the Microbit to power any more than 8 Neopixels at a time. If you wish to use more than 8 Neopixels, you must use a separate 3v-5v power supply for the Neopixel power pin." I have interpreted this to mean 8 WS2812 LEDs at full brightness (a brightness of 255 in each R, G, and B channel). And that by limiting the brightness of the LEDs I can support more than 8. I have not yet seen an issue with driving 25 WS2812 LEDs from on micro:bit at the lower brightness.
#### Message colors
The application will show special colors to indicate when certain messages are received by other micro:bit boards running the firefly appplication. The colors are shown on all LEDs and only shown for a moment.
* **Hello**: Dim blue when the board receives a "hello" message. 
* **Random**: Dim green when the board receives a "random" message. 
* **All On** Dim white when the board receives a "all on" message
Note that different WS2812 LEDs use different channel (RGB vs GRB) sequences. This will result in different message colors (green will be red and vice versa).

### fireflies_sync_neopixels_random.py
`fireflies_sync_neopixels_random.py` selects a random color for each firefly and always blinks the firefly in that color until the next randomize call.

### fireflies_sync_neopixels_converge.py
`fireflies_sync_neopixels_converge.py` selects a random color for each firefly and selects a common random color. As the fireflies flash the color of each firefly converges on the common color. When fireflies are randomized again a new common random color is selected. Note that the common random color is not communicated to other boards.
