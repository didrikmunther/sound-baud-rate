freq_diff = 800
alphabet_square_size = 9
x_freq = 4000
y_freq = x_freq + freq_diff * alphabet_square_size
alphabet = [
    [
        x_freq + freq_diff * x,
        x_freq + freq_diff * y + (freq_diff / 2),
    ]
    for y in range(alphabet_square_size)
    for x in range(alphabet_square_size)
]

send_scaler = 0.14
send_duration = 0.5 * send_scaler
send_pause = 0.09 * send_scaler
pause_freq = x_freq - freq_diff
snip_size = (send_duration + send_pause) / 8
