"""输入乐谱文件，构造音乐信号。

默认直接播放，也可以保存到 wav 文件。"""

from os.path import exists

from .composer import to_matrix
from .signal import read_and_build


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "file", type=str, nargs="+", help="旋律文件路径（主旋律放在第一）"
    )
    parser.add_argument("--fs", type=int, default=48000, help="采样率，默认 48000")
    parser.add_argument("--save", help="保存到文件，不播放")

    args = parser.parse_args()
    file = args.file
    fs = args.fs
    is_save = args.save

    matrix_file = []
    for f in file:
        if f.endswith("_matrix"):
            matrix_file.append(f)
        elif exists(fm := f"{f}_matrix"):
            matrix_file.append(fm)
        else:
            matrix_file.append(to_matrix(f))

    melody = read_and_build(*matrix_file, fs=fs)

    if is_save is not None:
        from scipy.io.wavfile import write

        write(is_save, fs, melody)
    else:
        import sounddevice as sd

        sd.play(melody, fs)
        # sd.wait()
        input("按回车结束")
        sd.stop()
