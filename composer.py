from typing import Sequence


def build_piano_keyboard():
    """构建钢琴键盘。
    A0-C8 共 88 个音。

    返回一个字典，键是音名，值是绝对频率。
    另外返回一个列表，按音名排序。
    """
    A4 = 440
    r2 = 2 ** (1 / 12)

    tmpl = "C_ D_b D_ E_b E_ F_ G_b G_ A_b A_ B_b B_".split()
    seq = [
        "0",
        "A0",
        "B0b",
        "B0",
        # C1-B6
        *[ab.replace("_", str(num)) for num in range(1, 7) for ab in tmpl],
        "C8",
    ]
    # 音高
    val = [0.0]
    x = A4 / r2**48  # A0
    for _ in range(len(seq) - 1):
        val.append(x)
        x *= r2

    return dict(zip(seq, val)), seq


# 赫兹字典与音名列表
Hzd, keys = build_piano_keyboard()


type Pair = tuple[str, float]


def read_melody(fn: str) -> tuple[Pair, Sequence[Pair]]:
    with open(fn, "r", encoding="utf-8") as fp:
        meta = fp.readline().strip()
        lines = fp.readlines()

    root, R = meta[1:-1].split(",")
    R = float(R)

    melody = []
    for line in lines:
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        for item in line.split():
            item = item.lstrip()
            tone, rym = item.rsplit(":", 1)
            rym = float(rym)
            for t in tone.split(","):
                melody.append((t, rym))

    return (root, R), melody


# 自然大调音阶音程
# yc = [2, 2, 1, 2, 2, 2]
yc = [0, 2, 4, 5, 7, 9, 11]


def convert_num_sheet_to_keys(root: str, melody: Sequence[Pair]) -> Sequence[Pair]:
    root_idx = keys.index(root)
    if root_idx < 0:
        raise ValueError(f"根音 {root} 不在钢琴键盘中")

    ret = []
    for t, r in melody:
        if t == "0":
            ret.append((t, r))
            continue
        idx = int(t[0]) - 1  # 0-6
        seq_idx = root_idx + yc[idx]
        if len(t) > 1:
            for sign in t[1:]:
                if sign == "_":
                    seq_idx -= 12
                elif sign == "^":
                    seq_idx += 12
                else:
                    raise ValueError()
        ret.append((keys[seq_idx], r))

    return ret


def convert_keys_to_matrix(melody: Sequence[Pair], R: float) -> str:
    tmp = []
    for t, r in melody:
        t = Hzd[t]
        r = float(r) / R
        tmp.append(f"{t} {r}")
    return "\n".join(tmp)


def convert_and_save(fn):
    (root, R), melody = read_melody(fn)
    if root != "":
        melody = convert_num_sheet_to_keys(root, melody)

    data = convert_keys_to_matrix(melody, R)
    with open(f"{fn}_matrix", "w") as fp:
        fp.write(data)


def cvt_between_da_and_xiao(melody: Sequence[Pair]) -> Sequence[Pair]:
    """唱名谱大小调转换"""
    tmp = [f"{num + 1}{mark}" for mark in "__,_,,^,^^".split(",") for num in range(7)]
    mapping = dict(zip(tmp[2:], tmp[:-2]))  # 大调转小调
    mapping = dict(zip(tmp[2:], tmp[:-2]))  # 小调转大调

    ret = []
    for t, r in melody:
        if t == "0":
            ret.append((t, r))
            continue
        t = mapping[t]
        ret.append((t, r))

    return ret


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("melody", type=str, help="旋律文件路径")

    args = parser.parse_args()
    melody = args.melody
    convert_and_save(melody)


if __name__ == "__main__":
    main()
