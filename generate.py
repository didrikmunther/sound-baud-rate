import time
import pyaudio
from alphabet import (
    alphabet,
    alphabet_square_size,
    send_duration,
    send_pause,
    pause_freq,
)
from decoder import AlphabetCoder
from tqdm import tqdm

"""
https://soledadpenades.com/2009/10/29
       /fastest-way-to-generate-wav-files-in-python-using-the-wave-module/
"""
import math
import random, struct
import wave

SAMPLE_FREQ = 44100


def generator(func, *args):
    def wrapper(i):
        return func(i, *args)

    return wrapper


def noise(_i, amplitude):
    return random.randint(-32767 * amplitude, 32767 * amplitude)


def sine_wave(i, frequency, amplitude):
    return int(32767.0 * amplitude * math.sin(frequency * math.pi * float(i) / 44100.0))


def square_wave(i, frequency, amplitude):
    v = math.sin(frequency * math.pi * float(i) / 44100.0)
    if v > 0:
        return int(32767.0 * amplitude)
    else:
        return int(-32767.0 * amplitude)


def message_generator(content: int):
    generators = [generator(sine_wave, freq, 1.0) for freq in alphabet[content]]

    for i in range(0, int(send_duration * SAMPLE_FREQ)):
        yield int(sum([g(i) for g in generators]) / len(generators))

    pause_generator = generator(sine_wave, pause_freq, 1.0)
    for i in range(0, int(send_pause * SAMPLE_FREQ)):
        yield pause_generator(i)


def get_audio_data(message_text: str) -> bytes:
    message = AlphabetCoder(alphabet_square_size**2).encode(message_text)
    message_generators = [message_generator(content) for content in message]

    values = []
    for generator in tqdm(message_generators):
        for value in generator:
            packed_value = struct.pack("h", value)
            values.append(packed_value)
            values.append(packed_value)

    value_str = b"".join(values)

    return value_str


def play_message(message_text: str):
    channels = 2
    sample_width = 2  # 16-bit audio
    rate = 44100  # Sample rate (Hz)
    p = pyaudio.PyAudio()
    chunk_size = 1024
    stream = p.open(
        format=p.get_format_from_width(sample_width),
        channels=channels,
        rate=rate,
        output=True,
    )

    value_str = get_audio_data(message_text + "\n\n\n")

    try:
        data_len = len(value_str)
        for i in range(0, data_len, chunk_size):
            chunk = value_str[i : i + chunk_size]
            stream.write(chunk)
            time.sleep(0.001)  # Short sleep to allow KeyboardInterrupt
    except KeyboardInterrupt:
        return
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


def main():
    message_text = f"""
    is simply dummy text of the printing and typesetting industry.
    Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
    when an unknown printer took a galley of type and scrambled it to make a type specimen book.
    """

    noise_output = wave.open("out.wav", "w")
    noise_output.setparams((2, 2, 44100, 0, "NONE", "not compressed"))

    value_str = get_audio_data(message_text + "\n\n\n")
    noise_output.writeframes(value_str)

    noise_output.close()


if __name__ == "__main__":
    main()
