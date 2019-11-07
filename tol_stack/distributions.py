import numpy as np

_max_iterations = 100


def norm(loc, scale, size=1):
    return np.random.normal(loc=loc, scale=scale, size=size)


def norm_screened(loc, scale, limits: tuple, size=1):
    values = np.random.normal(loc=loc, scale=scale, size=size)

    if limits is not None:
        low_limit, high_limit = limits

        # removes values not in range
        values = values[(values >= low_limit) & (values <= high_limit)]
        count = 0
        while len(values) < size:
            values = np.append(values, np.random.normal(loc=loc, scale=scale, size=size))
            values = values[(values >= low_limit) & (values <= high_limit)]
            count += 1
            if count > _max_iterations:
                raise ValueError('number of iterations exceeds the max allowable... are the limits set appropriately?')

        values = values[:size]

    return values


def norm_notched(loc, scale, limits: tuple, size=1):
    values = np.random.normal(loc=loc, scale=scale, size=size)

    if limits is not None:
        low_limit, high_limit = limits

        # removes values not in range
        values = values[(values <= low_limit) | (values >= high_limit)]

        count = 0
        while len(values) < size:
            values = np.append(values, np.random.normal(loc=loc, scale=scale, size=size))
            values = values[(values <= low_limit) | (values >= high_limit)]

            count += 1
            if count > _max_iterations:
                raise ValueError('number of iterations exceeds the max allowable... are the limits set appropriately?')

        values = values[:size]

    return values


def norm_lt(loc, scale, limit, size=1):
    values = np.random.normal(loc=loc, scale=scale, size=size)

    # removes values not in range
    values = values[values <= limit]

    count = 0
    while len(values) < size:
        values = np.append(values, np.random.normal(loc=loc, scale=scale, size=size))
        values = values[(values <= limit)]

        count += 1
        if count > _max_iterations:
            raise ValueError('number of iterations exceeds the max allowable... is the limit set appropriately?')

    values = values[:size]

    return values


def norm_gt(loc, scale, limit, size=1):
    values = np.random.normal(loc=loc, scale=scale, size=size)

    # removes values not in range
    values = values[values >= limit]

    count = 0
    while len(values) < size:
        values = np.append(values, np.random.normal(loc=loc, scale=scale, size=size))
        values = values[(values >= limit)]

        count += 1
        if count > _max_iterations:
            raise ValueError('number of iterations exceeds the max allowable... is the limit set appropriately?')

    values = values[:size]

    return values
