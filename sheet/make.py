"""自动生成音乐文件：wav 和 flac"""

from pathlib import Path
from subprocess import run

this_path = Path(__file__).parent
music_path = this_path / "music"
if not music_path.exists():
    music_path.mkdir()
    music_path.joinpath(".gitignore").write_text("*")

# NOTE: 4536251 是低音，带数字后缀的是“高音”
# 需要修改衰减系数，单独生成。
# 4536251_full 4536251 4536251_1 4536251_2 4536251_3
manifest = """
4536251
月半小夜曲 melody1 melody2
穿越时空的思念
回梦游仙
御剑江湖
浮光
"""


def make_wav_and_flac(*src: Path, dst: Path):
    wav = dst.with_suffix(".wav")
    if not wav.exists():
        cmd = ["composer", *src, "--save", wav]
        run(cmd)
    flac = dst.with_suffix(".flac")
    if not flac.exists():
        cmd = ["ffmpeg", "-i", wav, flac]
        run(cmd)


for line in manifest.strip().splitlines():
    name, *items = line.strip().split()
    mf = music_path / name

    if items:
        make_wav_and_flac(*(this_path / item for item in items), dst=mf)
    else:
        make_wav_and_flac(this_path / name, dst=mf)
