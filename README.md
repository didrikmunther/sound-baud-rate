# Sound baud rate thingy

This is a simple program that uses sound to transmit data between two computers.

## How it works

Three frequencies are generated, and are mapped to an alphabet. The receiver uses FFT on the sound to determine the frequencies, and then maps them back to the alphabet.