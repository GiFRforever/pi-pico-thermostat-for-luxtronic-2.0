from math import floor, ceil


def time_generator():
    for h in range(0, 24):
        for m in range(0, 60, 5):
            yield f"{h:02d}:{m:02d}"


def horizontal(data, width, character="█") -> str:
    """
    Return a horizontal graph from a list of integers.

    Either labelled or unlabeled, a specific width can be given.

        data   - list of integers to graph
                 list of tuples of label integer to graph
        width  - width of the largest bar (int)
    """
    parts = [character * i for i in range(0, width)]

    if isinstance(data, list):
        # Check if list of tuples (with label) or just numbers
        if isinstance(data[0], tuple):
            labels = [k for k, v in data]
            nums = [v for k, v in data]
        else:
            labels = None
            nums = data

    fraction = max(nums) / float(len(parts) - 1)

    if labels:
        # First pad labels
        max_length = len(max(labels, key=len))
        labels = [x + " " * (max_length - len(x)) for x in labels]

        # Create Lines and output
        out = ""
        for index, value in enumerate(nums):
            out = out + labels[index]
            out = out + " " + parts[int(round(value / fraction))]
            out = out + "\n"
        return out

    return "".join(parts[int(round(x / fraction))] + "\n" for x in nums)


def makegraph(path: str, col: int, data: list[str] | None = None) -> str:  # type: ignore
    if data is None:
        with open(path, "r") as f:
            f.readline()
            data: list[str] = f.readlines()

    tps = time_generator()
    parsed_data = []
    temp = []
    i = 0
    for _ in range(24):
        for _, tp in zip(range(12), tps):
            if tp not in data[i]:
                continue
            temp.append(float(data[i].split(";")[1]))
            i += 1

        if temp:
            parsed_data.append(sum(temp) / len(temp))
        else:
            parsed_data.append(None)
        temp = []

    del data
    del temp

    for i, p in enumerate(parsed_data):
        if p is not None:
            continue

        for j in range(i, 0, -1):
            if parsed_data[j] is not None:
                prev = float(parsed_data[j])
                prev_i = j
                break
        else:
            prev = None

        for j in range(i, len(parsed_data)):
            if parsed_data[j] is not None:
                next_ = float(parsed_data[j])
                next_i = j
                break
        else:
            next_ = None

        if prev is not None and next_ is not None:
            parsed_data[i] = (prev * (i - prev_i) + next_ * (next_i - i)) / (next_i - prev_i)  # type: ignore linear interpolation
        elif prev is not None:
            parsed_data[i] = prev
        elif next_ is not None:
            parsed_data[i] = next_
        else:
            parsed_data[i] = 21

    minimum: int = floor(min(parsed_data))
    maximum: int = ceil(max(parsed_data))

    normalized_data = [
        (f"{h:>02}:00 {p:.2f} °C", int((p - minimum) / (maximum - minimum) * col))
        for h, p in enumerate(parsed_data)
    ]
    del parsed_data

    out = ""

    #     out += f" Čas  |{minimum:>02} °C {' ' * (col - 15)} {maximum:>02} °C|\n"
    #     out = (
    #         f"      {('. '.join([str(int(x)) for x in path.split('/')[-1].split('-')[::-1]])):^{len(out) - 7}}\n"
    #         + out
    #     )
    out += horizontal(normalized_data, col)
    return out
