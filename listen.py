import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal
from scipy.signal import find_peaks
from pydub import AudioSegment
from alphabet import (
    x_freq,
    alphabet,
    freq_diff,
    pause_freq,
    alphabet_square_size,
    snip_size,
)
from dataclasses import dataclass
import itertools

from decoder import AlphabetCoder, TopFrequency, Translator


# Import the .wav audio
f = "out.wav"
# s = sampling (int)
# a = audio signal (numpy array)
s, a = wavfile.read(f)
# number of samples
na = a.shape[0]
# audio time duration
la = na / s

sound = AudioSegment.from_wav(f)
sound = sound.set_channels(1)
fm = f[:-4] + "_mono.wav"
sound.export(fm, format="wav")

s, a = wavfile.read(fm)
print("Sampling Rate:", s)
print("Audio Shape:", np.shape(a))

top_frequencies = []

f_max = x_freq + freq_diff * alphabet_square_size * 2 + 50
f_min = int(pause_freq / 2 - 50)

print(la, snip_size, la / snip_size)

for i in range(0, int(la / snip_size)):
    audio = a[i * int(s * snip_size) : (i + 1) * int(s * snip_size)]
    na = len(audio)
    a_k = np.fft.fft(audio)[0 : int(na / 2)] / na
    a_k[1:] = 2 * a_k[1:]
    Pxx = np.abs(a_k)
    f = s * np.arange((na / 2)) / na
    i_max = np.argmin(np.abs(f - f_max))
    i_min = np.argmin(np.abs(f - f_min))
    f = f[i_min:i_max]
    Pxx = Pxx[i_min:i_max]
    peaks, _ = find_peaks(Pxx)
    peak_heights = Pxx[peaks]

    top_two = np.argsort(peak_heights)[-2:]
    frequencies = [
        TopFrequency(float(f[peaks[index]] * 2), float(Pxx[peaks[index]]))
        for index in top_two
    ]
    # print(frequencies)

    top_frequencies.append(frequencies)

result = AlphabetCoder(alphabet_square_size**2).decode(
    Translator(alphabet).translate(top_frequencies)
)

print(result)
