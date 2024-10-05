from alphabet import freq_diff, pause_freq
from dataclasses import dataclass
import numpy as np
from collections import Counter


def relative_difference(x, y):
    if x == y:
        return 0  # If both values are the same, the relative difference is zero
    return abs(x - y) / ((x + y) / 2)


@dataclass
class TopFrequency:
    frequency: float
    amplitude: float

    def __repr__(self):
        return f"{self.frequency:.1f} Hz@{self.amplitude:.1f}"


class AlphabetCoder:
    def __init__(self, size: int):
        self.size = size

        if size >= 64:
            self.letters = [
                x
                for x in "? \0\n\tabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVXYZ0123456789!.,:'"
            ]
        else:
            raise NotImplementedError("Alphabet size must be greater than 64")

    def encode(self, content: str) -> list[int]:
        return [self.letters.index(c) for c in content]

    def _get_letter(self, index: int) -> str:
        try:
            return self.letters[index]
        except IndexError:
            return self.letters[0]

    def decode(self, content: list[int]) -> str:
        return "".join([self._get_letter(c) for c in content])


class Translator:
    def __init__(self, alphabet, required_observations=5):
        self.alphabet = alphabet
        self.required_observations = required_observations

        def add_freq(trie, freq, child):
            if freq in trie:
                trie[freq].update(child)
            else:
                trie[freq] = child

        self.trie = {}
        for i, row in enumerate(alphabet):
            [freq1, freq2] = row
            add_freq(self.trie, freq1, {freq2: i})
            add_freq(self.trie, freq2, {freq1: i})

        self.buffer = []

    def translate(self, frequencies: list[list[TopFrequency]]) -> list[int]:
        decoded = []

        for freqs in frequencies:
            # print("Decoding", freqs)

            l = np.array([f.frequency for f in freqs]) - pause_freq
            # freqs_diff = np.array([f.amplitude for f in freqs])
            if np.any(np.abs(l) < freq_diff / 2):
                if len(self.buffer) > 0:
                    most_common, count = Counter(self.buffer).most_common(1)[0]
                    if count >= self.required_observations:
                        decoded.append(most_common)

                    self.buffer = []

                continue

            node = self.trie
            for freq in freqs:
                index = min(node.keys(), key=lambda x: abs(x - freq.frequency))

                if abs(index - freq.frequency) > 1000:
                    node = -1
                    break

                node = node[index]

            # print("Got node", node)

            # We didn't find a match, append 0, which is always a N/A character
            if not isinstance(node, dict) and node != -1:
                self.buffer.append(node)

        return decoded
