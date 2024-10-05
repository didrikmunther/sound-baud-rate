import numpy as np


freq_diff = 1200
alphabet_square_size = 9
x_freq = 3000
y_freq = x_freq + freq_diff * alphabet_square_size
pause_freq = x_freq - freq_diff

alphabet_dimensions = [9, 9, 10]
alphabet = [
    [
        x_freq + freq_diff * x,
        x_freq + freq_diff * y + (freq_diff / 3),
        x_freq + freq_diff * z + (freq_diff / 3 * 2),
    ]
    for y in range(alphabet_dimensions[0])
    for x in range(alphabet_dimensions[1])
    for z in range(alphabet_dimensions[2])
]

print("Alphabet len:", len(alphabet))
print("Alphabet min/max", np.min(alphabet), np.max(alphabet))
