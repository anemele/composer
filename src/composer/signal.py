import numpy as np

from .composer import to_matrix


def envelope(length, n, fs):
    yt = np.arange(length) + 1
    yt = yt / fs
    shape = yt ** (1 / n) / np.exp(2 * yt)
    return shape


def build_signal(matrix, n, fs):
    coefs = np.array(
        [0.6882, 1, 0.9217, 0.2318, 0.0524, 0.1355, 0.1797, 0.09109, 0.0055, 0.1127]
    )
    cf2 = np.arange(10) + 1

    tone = matrix[:, 0]
    rym = matrix[:, 1] * fs
    rym = rym.astype(np.int32)

    signal = np.zeros(np.sum(rym))
    start = 0
    for tn, r in zip(tone, rym):
        end = start + r
        t = np.arange(r) + 1
        t = t / fs
        t = t.reshape(-1, 1)
        a = coefs * np.sin(2 * np.pi * tn * cf2 * t)
        b = envelope(r, n, fs)
        signal[start:end] = np.sum(a.T * b, axis=0)
        start = end

    return signal


def build_melody(matrix, *matrices, fs):
    # 主旋律一般是高音，衰减较快
    signal = build_signal(matrix, 15, fs)
    for matrix in matrices:
        # 伴奏一般是低音，衰减较慢
        signal += build_signal(matrix, 2, fs)
    signal = signal / np.max(np.abs(signal))
    return signal


def read_and_build(*filepath, fs):
    return build_melody(
        *(np.array(to_matrix(fp)) for fp in filepath),
        fs=fs,
    )
