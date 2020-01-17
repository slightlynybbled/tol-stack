import logging

import matplotlib.pyplot as plt
import numpy as np

import tol_stack.distributions as distributions


class Part:
    """
    Represents a part, complete with tolerances as defined by the distributions.

    :param name: a string representing the part
    :param nominal_value: the nominal value of the dimension
    :param tolerance: the tolerance of the part
    :param distribution: the distribution of the dimension
    :param size: the number of samples to generate
    :param limits: the limits of the distribution; if there are two limits on the distribution, then \
    there are two values to be passed as a tuple; else, if the distribution is expecting a single value, \
    then this value will be a float
    """
    def __init__(self, name: str,
                 nominal_value: float, tolerance: float,
                 distribution: str = 'norm', size: int = 1000, limits: (tuple, float) = None,
                 loglevel=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        valid_distributions = self.retrieve_distributions()
        if distribution.lower() not in valid_distributions:
            raise ValueError(f'unexpected distribution "{distribution}"; '
                             f'distribution must be in "{valid_distributions}"')

        self.name = name
        self.distribution = distribution.lower()
        self.nominal_value = nominal_value
        self.tolerance = abs(tolerance)

        self._limits = limits
        self._size = size

        self.values = None

        self.refresh()

    def __repr__(self):
        return f'<Part "{self.name}" dist="{self.distribution}" ' \
               f'nom={self.nominal_value:.03f} \u00b1{self.tolerance:.03f}>'

    def to_dict(self):
        return {
            'name': self.name,
            'distribution': self.distribution,
            'nominal value': self.nominal_value,
            'tolerance': self.tolerance
        }

    @staticmethod
    def retrieve_distributions():
        return ['norm', 'norm-screened', 'norm-notched', 'norm-lt', 'norm-gt']

    def refresh(self, size: int = None):
        """
        Re-calculates the distribution.

        :param size: Allows external software to override the size
        :return: None
        """
        if size is not None:
            self._size = size

        if self.distribution == 'norm':
            self.values = distributions.norm(
                loc=self.nominal_value,
                scale=self.tolerance / 3, size=self._size
            )
        elif self.distribution == 'norm-screened':
            self.values = distributions.norm_screened(
                loc=self.nominal_value,
                scale=self.tolerance / 3,
                size=self._size,
                limits=self._limits
            )
        elif self.distribution == 'norm-notched':
            self.values = distributions.norm_notched(
                loc=self.nominal_value,
                scale=self.tolerance / 3,
                size=self._size,
                limits=self._limits
            )
        elif self.distribution == 'norm-lt':
            if isinstance(self._limits, tuple):
                limit, *_ = self._limits
            else:
                limit = self._limits

            self.values = distributions.norm_lt(
                loc=self.nominal_value,
                scale=self.tolerance / 3,
                size=self._size,
                limit=limit
            )
        elif self.distribution == 'norm-gt':
            if isinstance(self._limits, tuple):
                limit, *_ = self._limits
            else:
                limit = self._limits

            self.values = distributions.norm_gt(
                loc=self.nominal_value,
                scale=self.tolerance / 3,
                size=self._size,
                limit=limit
            )

        else:
            raise ValueError(f'distribution "{self.distribution}" appears to be invalid')

    def show_dist(self, **kwargs):
        """
        Shows the distribution for the part on a matplotlib plot.

        :param kwargs: All keyword arguments must be valid for matplotlib.pyplot.hist
        :return: Figure
        """
        fig, ax = plt.subplots()

        ax = fig.add_subplot(1, 1, 1)
        ax.hist(self.values, **kwargs)
        ax.set_title(f'Part distribution, {self.name}')


class StackPath:
    """
    The stack path analysis class.

    :param max_value: a floating-point number
    :param min_value: a floating-point number
    :param loglevel: the logging level that is to be implemented for the class

    """
    def __init__(self, max_value: float = None, min_value: float = None,
                 loglevel=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self.parts = []
        self._stackups = []

        self.max_value = max_value
        self.min_value = min_value

    def add_part(self, part: Part):
        """
        Adds a part to the stack path.

        :param part: An instance of ``Part``
        :return: None
        """
        if self.parts:
            if len(part.values) != len(self.parts[0].values):
                raise ValueError('part sample sizes do not match, cannot perform valid comparison')

        self.parts.append(part)

    def retrieve_parts(self, safe=True):
        """
        Retrieves a safe copy of the parts to work with.

        :param safe: if False, will return a list of the part instances; if True, \
        will return a copied list of the instances
        :return: a list of ``Parts``
        """
        if safe:
            return self.parts.copy()

        return self.parts

    def analyze(self):
        """
        Refreshes the parts and ddds up all of the distributions of the parts.

        :return: None
        """
        for part in self.parts:
            part.refresh()

        finals = np.zeros(len(self.parts[0].values))
        for part in self.parts:
            finals += part.values

        self._stackups = finals

    def show_dist(self, **kwargs):
        """
        Shows the distribution for the part on a matplotlib plot.

        :param kwargs: All keyword arguments must be valid for matplotlib.pyplot.hist
        :return: Figure
        """
        fig, ax = plt.subplots()

        ax.hist(self._stackups, bins=31, **kwargs)
        ax.set_title(f'Stackup Distribution')
        ax.grid()

        if self.max_value is not None:
            ax.set_xlabel('distribution of total height')

            interference = [v for v in self._stackups if v > self.max_value]

            if len(interference) > 0:
                interference_percent = 100.0 * len(interference) / len(self._stackups)

                x0, x1 = ax.get_xlim()
                y0, y1 = ax.get_ylim()
                ax.axvspan(self.max_value, x1, color='red', zorder=-2, alpha=0.1)
                ax.axvline(self.max_value, color='red', zorder=-1)
                ax.text(x=self.max_value, y=((y1 - y0) * 0.9),
                        s=f'{interference_percent:.02f}% above maximum',
                        color='red', horizontalalignment='left')

        if self.min_value is not None:
            ax.set_xlabel('distribution of total height')

            interference = [v for v in self._stackups if v < self.min_value]

            if len(interference) > 0:
                interference_percent = 100.0 * len(interference) / len(self._stackups)

                x0, x1 = ax.get_xlim()
                y0, y1 = ax.get_ylim()
                ax.axvspan(x0, self.min_value, color='red', zorder=-2, alpha=0.1)
                ax.axvline(self.min_value, color='red', zorder=-1)
                ax.text(x=self.min_value, y=((y1 - y0) * 0.9),
                        s=f'{interference_percent:.02f}% below minimum',
                        color='red', horizontalalignment='right')


if __name__ == '__main__':
    size = 100000

    part0 = Part(
        name='part0',
        nominal_value=1.0,
        tolerance=0.01,
        limits=1.02,
        size=size
    )

    part1 = Part(
        name='part1',
        nominal_value=2.0,
        tolerance=0.01,
        limits=2.02,
        size=size
    )

    part2 = Part(
        name='part2',
        nominal_value=-2.98,
        tolerance=0.02,
        size=size
    )

    sp = StackPath(max_value=0.05, min_value=0.00)
    sp.add_part(part0)
    sp.add_part(part1)
    sp.add_part(part2)

    sp.analyze()

    #part0.show_dist(density=True, bins=31)
    #plt.show()

    #part1.show_dist(density=True, bins=31)
    #plt.show()

    #part2.show_dist(density=True, bins=31)
    #plt.show()

    sp.show_dist(bins=31)
    plt.show()
