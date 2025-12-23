from dataclasses import dataclass
from typing import Iterable, Mapping, Self, Sequence


def build_piano_keyboard(
    A4: float = 440,
) -> tuple[Mapping[str, float], Sequence[str]]:
    """根据十二平均律构建钢琴键盘，A0-C8 加上 0 音共 89 个音。
    （实际钢琴不完全符合十二平均律，这里不予考虑）

    返回：
    一个字典，键是音名，值是音高/频率。
    一个列表，按音名排序。
    """
    tmpl = "C{} D{}b D{} E{}b E{} F{} G{}b G{} A{}b A{} B{}b B{}".split()
    seq = [
        "0",
        "A0",
        "B0b",
        "B0",
        # C1-B7
        *(t.format(num + 1) for num in range(7) for t in tmpl),
        "C8",
    ]

    r2 = 2 ** (1 / 12)
    x = A4 / r2**48  # A0
    val = [0.0]
    for _ in range(len(seq) - 1):
        val.append(x)
        x *= r2

    return dict(zip(seq, val)), seq


Hzd, keys = build_piano_keyboard()


@dataclass
class MatrixItem:
    hz: float  # 音高
    t: float  # 时长

    def __str__(self):
        return f"{self.hz} {self.t}"


@dataclass
class SheetItem:
    tone: str
    rym: float


@dataclass
class MusicSheet:
    root: str  # A0-C8 or ''
    R: float

    # 数字谱只支持自然音阶
    items: Sequence[SheetItem]  # A0-C8 or 0-7

    def check(self) -> bool:
        return NotImplemented

    @classmethod
    def from_text(cls, text: str) -> Self:
        # 用户保证数据合法

        meta, *lines = text.splitlines()

        root, R = meta[1:-1].split(",")
        R = float(R)

        items = []
        for line in lines:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            for item in line.split():
                item = item.lstrip()
                tone, rym = item.rsplit(":", 1)
                rym = float(rym)
                items.extend(SheetItem(t, rym) for t in tone.split(","))

        return cls(root, R, items)

    def num_to_abc(self) -> Self:
        # 数字谱转音名谱

        if self.root == "":
            return self

        root_idx = keys.index(self.root)
        if root_idx < 0:
            raise ValueError(f"根音 {self.root} 不在钢琴键盘中")

        # 自然大调音阶音程
        # yc = [2, 2, 1, 2, 2, 2]
        yc = [0, 2, 4, 5, 7, 9, 11]

        items = []
        for item in self.items:
            t = item.tone
            if t == "0":
                items.append(item)
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
            items.append(SheetItem(keys[seq_idx], item.rym))

        return type(self)("", self.R, items)

    def abc_to_num(self, root: str) -> Self:
        # 音名谱转数字谱

        if self.root != "":
            return self

        return NotImplemented

    def abc_to_matrix(self) -> Iterable[MatrixItem]:
        # 音名谱转矩阵
        for item in self.items:
            line = MatrixItem(Hzd[item.tone], item.rym / self.R)
            yield line


def to_matrix(filepath: str) -> str:
    with open(filepath, encoding="utf-8") as fp:
        text = fp.read()

    matrix = MusicSheet.from_text(text).num_to_abc().abc_to_matrix()
    data = "\n".join(map(str, matrix))

    mfp = f"{filepath}_matrix"
    with open(mfp, "w") as fp:
        fp.write(data)

    return mfp
