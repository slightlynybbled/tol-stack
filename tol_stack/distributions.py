import numpy as np


def norm(loc, scale, size=1):
    return np.random.normal(loc=loc, scale=scale, size=size)


def norm_screened(loc, scale, size=1, limits: tuple = None):
    values = np.random.normal(loc=loc, scale=scale, size=size)

    if limits is not None:
        low_limit, high_limit = limits

        # removes values not in range
        values = values[(values >= low_limit) & (values <= high_limit)]

        while len(values) < size:
            values = np.append(values, np.random.normal(loc=loc, scale=scale, size=size))
            values = values[(values >= low_limit) & (values <= high_limit)]
        values = values[:size]

    return values
