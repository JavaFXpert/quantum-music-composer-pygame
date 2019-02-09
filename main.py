import sys, pygame, pygame.midi
from pygame.locals import *

import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit import BasicAer
from qiskit.tools.visualization import plot_state_qsphere

num_qubits = 4
state_vector_len = num_qubits**2
cur_mel_midi_vals = [0, 0, 0, 0]

screen_size = width, height = 1200, 768
white = 255, 255, 255
black = 0, 0, 0

screen = pygame.display.set_mode(screen_size)


def createTransitionCircuit(midi_vals):
    # Create a Quantum Register with 1 qubit (wire).
    qr = QuantumRegister(4)

    # Create a Classical Register with 1 bit (double wire).
    # cr = ClassicalRegister(4)

    # Create a Quantum Circuit from the quantum and classical registers
    # qc = QuantumCircuit(qr, cr)
    qc = QuantumCircuit(qr)

    # Place X rotation gate on each wire
    qc.rx(midi_vals[0] * (np.pi / 64), qr[0])
    qc.rx(midi_vals[1] * (np.pi / 64), qr[1])
    qc.rx(midi_vals[2] * (np.pi / 64), qr[2])
    qc.rx(midi_vals[3] * (np.pi / 64), qr[3])

    # qc.barrier(qr)

    # Measure the qubit into the classical register
    # qc.measure(qr, cr)

    return qc


def update_circuit(dial_num, midi_val):
    if dial_num <= 4:
        cur_mel_midi_vals[dial_num -1] = midi_val
        print("cur_mel_midi_vals: ", cur_mel_midi_vals)
        mel_circ = createTransitionCircuit(cur_mel_midi_vals)

        mel_circ_drawing = mel_circ.draw(output='mpl')
        mel_circ_drawing.savefig("images/mel_circ.png")
        mel_circ_img = pygame.image.load("images/mel_circ.png")
        mel_circ_img_rect = mel_circ_img.get_rect()
        mel_circ_img_rect.topleft = (0, 0)

        screen.fill(white)
        screen.blit(mel_circ_img, mel_circ_img_rect)
        pygame.display.flip()
        return mel_circ


def display_statevector(circ):
    backend_sv_sim = BasicAer.get_backend('statevector_simulator')

    # Execute the circuit on the state vector simulator
    job_sim = execute(circ, backend_sv_sim)

    # Grab the results from the job.
    result_sim = job_sim.result()

    # Obtain the state vector for the quantum circuit
    # quantum_state = result_sim.get_statevector(circ, decimals=3)
    # qsphere_drawing = plot_state_qsphere(quantum_state)
    #
    # qsphere_drawing.savefig("images/mel_qsphere.png")
    # mel_qsphere_img = pygame.image.load("images/mel_qsphere.png")
    #
    # mel_qsphere_img_rect = mel_qsphere_img.get_rect()
    # mel_qsphere_img_rect.topleft = (600, 0)
    #
    # # screen.fill(white)
    # screen.blit(mel_qsphere_img, mel_qsphere_img_rect)
    # pygame.display.flip()

def display_unitary(circ):
    backend_unit_sim = BasicAer.get_backend('unitary_simulator')

    # Execute the circuit on the state vector simulator
    job_sim = execute(circ, backend_unit_sim)

    # Grab the results from the job.
    result_sim = job_sim.result()

    # Obtain the unitary for the quantum circuit
    unitary = result_sim.get_unitary(circ, decimals=3)
    # unitary = result_sim.get_unitary(circ)
    print("Circuit unitary:\n", unitary)

    block_size = 20
    x_offset = 400
    y_offset = 20
    for y in range(state_vector_len):
        for x in range(state_vector_len):
            rect = pygame.Rect(x * block_size + x_offset,
                               y * block_size + y_offset,
                               block_size, block_size)
            pygame.draw.rect(screen, black, rect, 1)

    # qsphere_drawing = plot_state_qsphere(quantum_state)
    #
    # qsphere_drawing.savefig("images/mel_qsphere.png")
    # mel_qsphere_img = pygame.image.load("images/mel_qsphere.png")
    #
    # mel_qsphere_img_rect = mel_qsphere_img.get_rect()
    # mel_qsphere_img_rect.topleft = (600, 0)
    #
    # # screen.fill(white)
    # screen.blit(mel_qsphere_img, mel_qsphere_img_rect)
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
                if midi_ev.status == 176 and index == len(midi_evs) - 1:
                    melody_circ = update_circuit(midi_ev.data1, midi_ev.data2)
                    display_statevector(melody_circ)
                    display_unitary(melody_circ)

    del i
    pygame.midi.quit()


pygame.init()

input_main()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
