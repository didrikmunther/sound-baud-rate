import sys
import time
from matplotlib import pyplot as plt
from pvrecorder import PvRecorder
import numpy as np
from scipy.signal import find_peaks

# Assuming the necessary imports from your algorithm
from alphabet import (
    x_freq,
    alphabet,
    freq_diff,
    pause_freq,
    alphabet_square_size,
)
from decoder import AlphabetCoder, TopFrequency, Translator

# for index, device in enumerate(PvRecorder.get_available_devices()):
#     print(f"[{index}] {device}")

f_max = x_freq + freq_diff * alphabet_square_size * 2 + 50
f_min = int(pause_freq / 2 - 50)


# Function to process a single chunk of audio and run through the algorithm
def process_audio_chunk(audio_chunk, sampling_rate):
    na = len(audio_chunk)
    top_frequencies = []

    snip_size = 0.025

    for i in range(0, int(na / sampling_rate / snip_size * 4)):
        audio = audio_chunk[
            i
            * int(sampling_rate * snip_size) : (i + 1)
            * int(sampling_rate * snip_size)
        ]
        na = len(audio)

        if na <= 0:
            break

        a_k = np.fft.fft(audio)[0 : int(na / 2)] / na
        a_k[1:] = 2 * a_k[1:]  # Double non-DC components
        Pxx = np.abs(a_k)
        f = sampling_rate * np.arange(na / 2) / na
        i_max = np.argmin(np.abs(f - f_max))
        i_min = np.argmin(np.abs(f - f_min))
        f = f[i_min:i_max]
        Pxx = Pxx[i_min:i_max]

        peaks, _ = find_peaks(Pxx)
        peak_heights = Pxx[peaks]

        # Get the top two peak frequencies
        top_two = np.argsort(peak_heights)[-3:]
        frequencies = [
            TopFrequency(float(f[peaks[index]] * 2), float(Pxx[peaks[index]]))
            for index in top_two
        ]

        top_frequencies.append(frequencies)

    return top_frequencies


def listen_until_timeout(duration: float):
    start_time = time.time()

    coder = AlphabetCoder(alphabet_square_size**2)
    translator = Translator(alphabet)
    result_full = ""

    recorder = PvRecorder(device_index=-1, frame_length=512)
    sampling_rate = recorder.sample_rate

    try:
        recorder.start()

        coder = AlphabetCoder(alphabet_square_size**2)
        translator = Translator(alphabet)

        while True:
            if time.time() - start_time > duration:
                return

            a = np.array(recorder.read())

            frequencies = process_audio_chunk(a, sampling_rate)
            translated = translator.translate(frequencies)
            last = translated[-1] if len(translated) > 0 else None
            if last == 0:
                translated = translated[:-1]
            result = coder.decode(translated)
            result_full += result

            # print(result)

            if result != "":
                yield result

            if last == 0:
                return

    except KeyboardInterrupt:
        recorder.stop()
    finally:
        recorder.delete()


def listen_until_stop(line=None, fig=None):
    coder = AlphabetCoder(alphabet_square_size**2)
    translator = Translator(alphabet)
    result_full = ""

    recorder = PvRecorder(device_index=-1, frame_length=512)
    sampling_rate = recorder.sample_rate

    try:
        recorder.start()

        coder = AlphabetCoder(alphabet_square_size**2)
        translator = Translator(alphabet)

        while True:
            a = np.array(recorder.read())

            na = len(a)
            a_k = np.fft.fft(a)[0 : int(na / 2)] / na  # FFT function from numpy
            a_k[1:] = 2 * a_k[1:]  # single-sided spectrum only
            Pxx = np.abs(a_k)  # remove imaginary part
            f = sampling_rate * np.arange((na / 2)) / na  # frequency vector

            if line is not None and fig is not None:
                line.set_xdata(f)
                line.set_ydata(Pxx / np.linalg.norm(Pxx))
                fig.canvas.draw()
                fig.canvas.flush_events()

            frequencies = process_audio_chunk(a, sampling_rate)
            translated = translator.translate(frequencies)
            last = translated[-1] if len(translated) > 0 else None
            if last == 0:
                translated = translated[:-1]
            result = coder.decode(translated)
            result_full += result

            yield result

            if last == 0:
                return

    except KeyboardInterrupt:
        recorder.stop()
    finally:
        recorder.delete()


def main():
    plt.ion()
    fig, ax = plt.subplots()
    ax.grid()
    ax.legend()
    ax.set_ylabel("Amplitude")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    (line1,) = ax.plot([], [], "b-", label="Audio Signal")
    ax.plot(
        [20, 20000], [0.1, 0.1], "r-", alpha=0.7, linewidth=10, label="Audible (Humans)"
    )

    for x in listen_until_stop(line1, fig):
        sys.stdout.write(x)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
