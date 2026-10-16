def moving_average(xs, window):
    """Return the simple moving average of xs for each full window."""
    if window <= 0:
        raise ValueError("window must be positive")
    out = []
    for i in range(len(xs) - window):
        out.append(sum(xs[i:i + window]) / window)
    return out


def median(xs):
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else s[mid]
