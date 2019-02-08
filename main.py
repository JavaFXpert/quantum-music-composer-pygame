import sys, pygame, pygame.midi
from pygame.locals import *

import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute

cur_mel_midi_vals = [0, 0, 0, 0]

screen_size = width, height = 1024, 768
white = 127, 127, 127

screen = pygame.display.set_mode(screen_size)


def createTransitionCircuit(midi_vals):
    # Create a Quantum Register with 1 qubit (wire).
    qr = QuantumRegister(4)

    # Create a Classical Register with 1 bit (double wire).
    cr = ClassicalRegister(4)

    # Create a Quantum Circuit from the quantum and classical registers
    qc = QuantumCircuit(qr, cr)

    # Place X rotation gate on each wire
    qc.rx(midi_vals[0] * (np.pi / 64), qr[0])
    qc.rx(midi_vals[1] * (np.pi / 64), qr[1])
    qc.rx(midi_vals[2] * (np.pi / 64), qr[2])
    qc.rx(midi_vals[3] * (np.pi / 64), qr[3])

    qc.barrier(qr)

    # Measure the qubit into the classical register
    qc.measure(qr, cr)

    return qc


def update_circuit(dial_num, midi_val):
    if dial_num <= 4:
        cur_mel_midi_vals[dial_num -1] = midi_val
        print("cur_mel_midi_vals: ", cur_mel_midi_vals)
        mel_circ = createTransitionCircuit(cur_mel_midi_vals)
        mel_circ_drawing = mel_circ.draw(output='mpl')

        # TODO: Ascertain whether these two steps may be skipped
        mel_circ_drawing.savefig("images/mel_circ.png")
        mel_circ_img = pygame.image.load("images/mel_circ.png")

        mel_circ_img_rect = mel_circ_img.get_rect()

        screen.fill(white)
        screen.blit(mel_circ_img, mel_circ_img_rect)
        pygame.display.flip()


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


def input_main(device_id=None):
    # pygame.init()
    pygame.fastevent.init()
    event_get = pygame.fastevent.get
    event_post = pygame.fastevent.post

    pygame.midi.init()

    print_midi_device_info()

    if device_id is None:
        input_id = pygame.midi.get_default_input_id()
    else:
        input_id = device_id

    print("using input_id :%s:" % input_id)
    i = pygame.midi.Input(input_id)

    update_circuit(1, 0)

    going = True
    while going:
        events = event_get()
        for e in events:
            if e.type in [QUIT]:
                going = False
            if e.type in [KEYDOWN]:
                going = False
            if e.type in [pygame.midi.MIDIIN]:
                print(e)

        if i.poll():
            midi_events = i.read(10)
            # convert them into pygame events.
            midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

            for index, midi_ev in enumerate(midi_evs):
                # event_post(midi_ev)
                # print("midi_ev", midi_ev)

                if midi_ev.status == 176 and index == len(midi_evs) - 1:
                    update_circuit(midi_ev.data1, midi_ev.data2)

    del i
    pygame.midi.quit()


pygame.init()

# size = width, height = 320, 240
# speed = [2, 2]
# black = 0, 0, 0
#
# screen = pygame.display.set_mode(size)
#
# ball = pygame.image.load("images/intro_ball.gif")
# ballrect = ball.get_rect()

input_main()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    # ballrect = ballrect.move(speed)
    # if ballrect.left < 0 or ballrect.right > width:
    #     speed[0] = -speed[0]
    # if ballrect.top < 0 or ballrect.bottom > height:
    #     speed[1] = -speed[1]
    #
    # screen.fill(black)
    # screen.blit(ball, ballrect)
    # pygame.display.flip()