import sys, pygame, pygame.midi
from pygame.midi import time
from pygame.locals import *

import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit import BasicAer
from qiskit.tools.visualization import plot_state_qsphere
from qiskit.tools.visualization import plot_histogram

num_qubits = 4
state_vector_len = num_qubits**2
cur_mel_midi_vals = [0, 0, 0, 0]

screen_size = width, height = 1400, 900
white = 255, 255, 255
black = 0, 0, 0

screen = pygame.display.set_mode(screen_size)
screen.fill(white)


def createTransitionCircuit(midi_vals):
    # Create a Quantum Register with 4 qubit (wire).
    qr = QuantumRegister(4, 'q_reg')

    # Create a Classical Register with 1 bit (double wire).
    # cr = ClassicalRegister(4, 'c_reg')

    # Create a Quantum Circuit from the quantum and classical registers
    # qc = QuantumCircuit(qr, cr)
    qc = QuantumCircuit(qr)

    # Place X rotation gate on each wire
    qc.rx(midi_vals[0] * (np.pi / 64), qr[0])
    qc.rx(midi_vals[1] * (np.pi / 64), qr[1])
    qc.rx(midi_vals[2] * (np.pi / 64), qr[2])
    qc.rx(midi_vals[3] * (np.pi / 64), qr[3])

    # qc.cu3(midi_vals[0] * (np.pi / 64),
    #        midi_vals[1] * (np.pi / 64),
    #        midi_vals[2] * (np.pi / 64), qr[0], qr[1])
    # qc.barrier(qr)

    # Measure the qubit into the classical register
    # qc.measure(qr, cr)

    return qc


def update_circuit(dial_num, midi_val):
    if dial_num <= 4:
        cur_mel_midi_vals[num_qubits - dial_num] = midi_val
        # print("cur_mel_midi_vals: ", cur_mel_midi_vals)
        mel_circ = createTransitionCircuit(cur_mel_midi_vals)

        # mel_circ_drawing = mel_circ.draw(output='mpl')
        # mel_circ_drawing.savefig("images/mel_circ.png")
        # mel_circ_img = pygame.image.load("images/mel_circ.png")
        # mel_circ_img_rect = mel_circ_img.get_rect()
        # mel_circ_img_rect.topleft = (0, 0)
        #
        # screen.fill(white)
        # screen.blit(mel_circ_img, mel_circ_img_rect)
        # pygame.display.flip()
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
    # print("Circuit unitary:\n", unitary)

    screen.fill(white)

    block_size = 20
    x_offset = 600
    y_offset = 100
    for y in range(state_vector_len):
        for x in range(state_vector_len):
            rect = pygame.Rect(x * block_size + x_offset,
                               y * block_size + y_offset,
                               abs(unitary[y][x]) * block_size,
                               abs(unitary[y][x]) * block_size)
            # rect = pygame.Rect(x * block_size + x_offset,
            #                    y * block_size + y_offset,
            #                    block_size, block_size)
            if abs(unitary[y][x]) > 0:
                pygame.draw.rect(screen, black, rect, 1)

    # qsphere_drawing = plot_state_qsphere(quantum_state)
    #
    # qsphere_drawing.savefig("images/mel_qsphere.png")
    # mel_qsphere_img = pygame.image.load("images/mel_qsphere.png")
    #
    # mel_qsphere_img_rect = mel_qsphere_img.get_rect()
    # mel_qsphere_img_rect.topleft = (600, 0)
    #
    # screen.fill(white)
    # screen.blit(mel_qsphere_img, mel_qsphere_img_rect)
    pygame.display.flip()


def measure_circuit(circ, initial_bit_str):
    # Use the BasicAer qasm_simulator backend
    from qiskit import BasicAer
    backend_sim = BasicAer.get_backend('qasm_simulator')

    # Initialize each wire
    init_qr = QuantumRegister(4, 'q_reg')

    # TODO: Ascertain if necessary to create classical registers for the circuit merge
    # init_cr = ClassicalRegister(4, 'c_reg')

    # init_circ = QuantumCircuit(init_qr, init_cr)
    init_circ = QuantumCircuit(init_qr)

    for bit_idx in range(0, num_qubits):
        if int(initial_bit_str[bit_idx]) == 1:
            init_circ.x(init_qr[num_qubits - bit_idx - 1])
        else:
            init_circ.iden(init_qr[num_qubits - bit_idx - 1])

    init_circ.barrier(init_qr)

    # Create a Quantum Register with 4 qubits
    qr = QuantumRegister(4, 'q_reg')

    # Create a Classical Register with 4 bits
    cr = ClassicalRegister(4, 'c_reg')

    # Create the measurement portion of a quantum circuit
    meas_circ = QuantumCircuit(qr, cr)

    # Create a barrier that separates the gates from the measurements
    meas_circ.barrier(qr)

    # Measure the qubits into the classical registers
    meas_circ.measure(qr, cr)

    # Add the measument circuit to the original circuit
    complete_circuit = init_circ + circ + meas_circ

    mel_circ_drawing = (init_circ + circ).draw(output='mpl')
    mel_circ_drawing.savefig("images/mel_circ.png")
    mel_circ_img = pygame.image.load("images/mel_circ.png")
    mel_circ_img_rect = mel_circ_img.get_rect()
    mel_circ_img_rect.topleft = (0, 0)
    screen.blit(mel_circ_img, mel_circ_img_rect)
    pygame.display.flip()

    # Execute the circuit on the qasm simulator, running it 1000 times.
    job_sim = execute(complete_circuit, backend_sim, shots=1)

    # Grab the results from the job.
    result_sim = job_sim.result()

    # Print the counts, which are contained in a Python dictionary
    counts = result_sim.get_counts(complete_circuit)
    print(counts)
    basis_state_str = list(counts.keys())[0]
    # print ("basis_state_str: ", basis_state_str)
    return basis_state_str


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

    device_id = 0
    if device_id is None:
        input_id = pygame.midi.get_default_input_id()
    else:
        input_id = device_id

    input_id = 1
    print("using input_id :%s:" % input_id)
    i = pygame.midi.Input(input_id)

    # sending midi to the output
    output_id = pygame.midi.get_default_output_id()
    print("using output_id :%s:" % output_id)
    midi_output = pygame.midi.Output(output_id)
    midi_output.set_instrument(0)

    # end of sending midi to output

    bit_str_meas = '0000'
    melody_circ = update_circuit(1, 0)

    beg_time = time()
    recent_note_time = beg_time
    going = True
    while going:
        if time() > recent_note_time:
            bit_str_meas = measure_circuit(melody_circ, bit_str_meas)
            int_meas = int(bit_str_meas, 2)
            recent_note_time += 1000
            # midi_output.write([[[0x90, 62, 127], recent_note_time],
            #                    [[0x90, 62, 0], recent_note_time + 2000]])
            midi_output.write([[[0x90, 60 + int_meas, 127], recent_note_time],
                               [[0x90, 60 + int_meas, 0], recent_note_time + 2000]])
            melody_circ = createTransitionCircuit(cur_mel_midi_vals)

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
