from typing import Tuple
import numpy as np
from scipy.stats import skewnorm

_max_iterations = 100


def norm(loc: float, scale: float, size: int) -> np.ndarray:
    """
    Returns a random sampling from the normal distribution.

    :param loc: the nominal value
    :param scale: the range of common values
    :param size: the number of samples within the common values
    :return: a numpy array of values
    """
    return np.random.normal(loc=loc, scale=scale, size=size)


def norm_screened(loc: float, scale: float,
                  limits: Tuple[float, float], size: int) \
        -> np.ndarray:
    """
    Returns a random sampling from the normal distribution
    which has been screened.  This is a common distribution when
    a go/no-go fixture is in use.

    :param loc: the nominal value
    :param scale: the range of common values
    :param limits: a tuple of floats containing the low \
    and high screening limits
    :param size: the number of samples within the common values
    :return: a numpy array of values
    """
    values = np.random.normal(loc=loc, scale=scale, size=size)

    if limits is not None:
        if len(limits) != 2:
            raise ValueError('"limits" must be a tuple of exactly two '
                             'floating-point values')
        low_limit, high_limit = limits

        # removes values not in range
        values = values[(values >= low_limit) & (values <= high_limit)]
        count = 0
        while len(values) < size:
            values = np.append(values, np.random.normal(loc=loc,
                                                        scale=scale,
                                                        size=size))
            values = values[(values >= low_limit) & (values <= high_limit)]
            count += 1
            if count > _max_iterations:
                raise ValueError('number of iterations exceeds the max '
                                 'allowable... are the limits set '
                                 'appropriately?')

        values = values[:size]

    return values


def norm_notched(loc: float, scale: float,
                 limits: Tuple[float, float], size: int) -> np.ndarray:
    """
    Returns a random sampling from the normal distribution
    which has been screened in order to remove the nominal values.  This is a
    common distribution when parts are being sorted and the leftover parts
    are used.

    :param loc: the nominal value
    :param scale: the range of common values
    :param limits: a tuple of floats containing the low \
    and high screening limits
    :param size: the number of samples within the common values
    :return: a numpy array of values
    """

    values = np.random.normal(loc=loc, scale=scale, size=size)

    if limits is not None:
        if len(limits) != 2:
            raise ValueError('"limits" must be a tuple of exactly two '
                             'floating-point values')
        low_limit, high_limit = limits

        # removes values not in range
        values = values[(values <= low_limit) | (values >= high_limit)]

        count = 0
        while len(values) < size:
            values = np.append(values, np.random.normal(loc=loc, scale=scale, size=size))
            values = values[(values <= low_limit) | (values >= high_limit)]

            count += 1
            if count > _max_iterations:
                raise ValueError('number of iterations exceeds the max '
                                 'allowable... are the limits set '
                                 'appropriately?')

        values = values[:size]

    return values


def norm_lt(loc: float, scale: float, limit: float, size: int) -> np.ndarray:
    """
    Returns a random sampling from the normal distribution
    which has been screened in order to remove values above the limit.

    :param loc: the nominal value
    :param scale: the range of common values
    :param limit: a floats containing the upper screening limit
    :param size: the number of samples within the common values
    :return: a numpy array of values
    """
    values = np.random.normal(loc=loc, scale=scale,
                              size=size)

    # removes values not in range
    values = values[values <= limit]

    count = 0
    while len(values) < size:
        values = np.append(values, np.random.normal(loc=loc,
                                                    scale=scale,
                                                    size=size))
        values = values[(values <= limit)]

        count += 1
        if count > _max_iterations:
            raise ValueError('number of iterations exceeds the max '
                             'allowable... is the limit set appropriately?')

    values = values[:size]

    return values


def norm_gt(loc: float, scale: float, limit: float, size: int) -> np.ndarray:
    """
    Returns a random sampling from the normal distribution
    which has been screened in order to remove values below the limit.

    :param loc: the nominal value
    :param scale: the range of common values
    :param limit: a floats containing the lower screening limit
    :param size: the number of samples within the common values
    :return: a numpy array of values
    """
    values = np.random.normal(loc=loc, scale=scale, size=size)

    # removes values not in range
    values = values[values >= limit]

    count = 0
    while len(values) < size:
        values = np.append(values, np.random.normal(loc=loc,
                                                    scale=scale,
                                                    size=size))
        values = values[(values >= limit)]

        count += 1
        if count > _max_iterations:
            raise ValueError('number of iterations exceeds '
                             'the max allowable... '
                             'is the limit set appropriately?')

    values = values[:size]

    return values


def skew_normal(skewiness: float, loc: float,
                scale: float, size: int) -> np.ndarray:
    """
    Returns a random sampling from skewnormal distribution.

    :param skewiness: "0" skewiness, represents no skew; a negative skewiness \
    will create a left skew while a positive skewiness will create a \
    right skew; as skewiness increases, so does the skew of the distribution
    :param loc: the nominal value
    :param scale: the range of common values
    :param size: the number of samples within the common values
    :return: a numpy array of values
    """
    values = skewnorm.rvs(skewiness, loc=loc, scale=scale, size=size)\
        .astype(np.float64)
    return values


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()

    ax.hist(skew_normal(skewiness=-5, loc=1, scale=0.01, size=10000), bins=51)
    plt.show()
