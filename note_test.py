import pygame.midi
from pygame.midi import time

def print_midi_device_info():
    for i in range(pygame.midi.get_count()):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r

        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"

        print("%2i: interface :%s:, name :%s:, opened :%s:  %s" %
              (i, interf, name, opened, in_out))

pygame.midi.init()
print_midi_device_info()
player = pygame.midi.Output(2, 1, 1000)
player.set_instrument(3)

# player.note_on(64, 127)
# player.note_on(68, 127)
# pygame.time.wait(1000)
# player.note_on(64, 0)
# player.note_on(68, 0)
#
# player.note_on(41, 127)
# pygame.time.wait(1000)
# player.note_on(41, 0)
#
# player.note_on(42, 127)
# pygame.time.wait(1000)
# player.note_on(42, 0)

# nowA = pygame.pypm.Time()
nowA = time()
print("nowA: " + str(nowA))
player.write([[[0x90,62,127],nowA],[[0x90,66,127],nowA + 1000]])
# pygame.time.wait(2000)

nowA = time()
print("nowA: " + str(nowA))
player.write([[[0x90,68,127],nowA + 2000],[[0x90,70,127],nowA + 3000]])
pygame.time.wait(5000)

del player
pygame.midi.quit()