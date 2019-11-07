import logging

import matplotlib.pyplot as plt
import numpy as np

import tol_stack.distributions as distributions


class Part:
    def __init__(self, name: str,
                 nominal_value: float, upper_tolerance: float, lower_tolerance: float = None,
                 distribution: str = 'norm', size: int = 1000, limits: (tuple, float) = None,
                 loglevel=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self.name = name
        self._distribution = distribution
        self._nominal_value = nominal_value
        self._upper_value = self._nominal_value + upper_tolerance
        try:
            self._lower_value = self._nominal_value - lower_tolerance
        except TypeError:
            self._lower_value = None

        self._limits = limits
        self._size = size

        self.values = None

        self.refresh()

    def refresh(self):
        """
        Re-calculates the distribution

        :return: None
        """
        if self._distribution == 'norm':
            self.values = distributions.norm(
                loc=self._nominal_value,
                scale=(self._upper_value - self._nominal_value) / 3, size=self._size
            )
        elif self._distribution == 'norm-screened':
            self.values = distributions.norm_screened(
                loc=self._nominal_value,
                scale=(self._upper_value - self._nominal_value) / 3,
                size=self._size,
                limits=self._limits
            )
        elif self._distribution == 'norm-notched':
            self.values = distributions.norm_notched(
                loc=self._nominal_value,
                scale=(self._upper_value - self._nominal_value) / 3,
                size=self._size,
                limits=self._limits
            )
        elif self._distribution == 'norm-lt':
            if isinstance(self._limits, tuple):
                limit, *_ = self._limits
            else:
                limit = self._limits

            self.values = distributions.norm_lt(
                loc=self._nominal_value,
                scale=(self._upper_value - self._nominal_value) / 3,
                size=self._size,
                limit=limit
            )
        elif self._distribution == 'norm-gt':
            if isinstance(self._limits, tuple):
                limit, *_ = self._limits
            else:
                limit = self._limits

            self.values = distributions.norm_gt(
                loc=self._nominal_value,
                scale=(self._upper_value - self._nominal_value) / 3,
                size=self._size,
                limit=limit
            )

        else:
            raise ValueError(f'distribution "{self._distribution}" appears to be invalid')

    def show_dist(self, **kwargs):
        """
        Shows the distribution for the part on a matplotlib plot.

        :param kwargs: All keyword arguments must be valid for matplotlib.pyplot.hist
        :return: None
        """
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.hist(self.values, **kwargs)
        ax.set_title(f'Part distribution, {self.name}')

        plt.show()

        return None


class StackPath:
    def __init__(self, path_type: str = 'circuit',
                 max_value: float = None, min_value: float = None,
                 loglevel=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        valid_path_types = [
            'circuit', 'max', 'min', 'radial'
        ]
        if path_type not in valid_path_types:
            raise ValueError(f'"path_type" must be in f{valid_path_types}')
        if path_type not in ['circuit', 'max', 'min']:
            raise NotImplementedError('the specified path type is on the roadmap, but not currently supported')

        self._path_type = path_type
        self._parts = []
        self._stackups = []

        self._max_value = max_value
        self._min_value = min_value

    def add_part(self, part: Part):
        """
        Adds a part to the stack path.

        :param part: An instance of ``Part``
        :return: None
        """
        if self._parts:
            if len(part.values) != len(self._parts[0].values):
                raise ValueError('part sample sizes do not match, cannot perform valid comparison')

        self._parts.append(part)

    def retrieve_parts(self, safe=True):
        """
        Retrieves a safe copy of the parts to work with.

        :param safe: if False, will return a list of the part instances; if True, \
        will return a copied list of the instances
        :return:
        """
        if safe:
            return self._parts.copy()

        return self._parts

    def analyze(self):
        """
        Refreshes the parts and ddds up all of the distributions of the parts.

        :return: None
        """
        for part in self._parts:
            part.refresh()

        finals = np.zeros(len(self._parts[0].values))
        for part in self._parts:
            finals += part.values

        self._stackups = finals

    def show_dist(self, **kwargs):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.hist(self._stackups, **kwargs)
        ax.set_title(f'Stackup Distribution, {self._path_type}')
        ax.grid()

        if self._path_type == 'circuit':
            ax.set_xlabel('sum of gaps between parts')

            interference = [v for v in self._stackups if v > 0]
            if len(interference) > 0:
                interference_percent = 100.0 * len(interference) / len(self._stackups)

                x0, x1 = ax.get_xlim()
                y0, y1 = ax.get_ylim()
                ax.axvspan(0.0, x1, color='red', zorder=-2, alpha=0.1)
                ax.axvline(0.0, color='red', zorder=-1)
                ax.text(x=x0*0.9, y=((y1-y0) * 0.9), s=f'interference on {interference_percent:.02f}%', color='red')

        elif self._path_type == 'max':
            ax.set_xlabel('distribution of total height')

            interference = [v for v in self._stackups if v > self._max_value]

            if len(interference) > 0:
                interference_percent = 100.0 * len(interference) / len(self._stackups)

                x0, x1 = ax.get_xlim()
                y0, y1 = ax.get_ylim()
                ax.axvspan(self._max_value, x1, color='red', zorder=-2, alpha=0.1)
                ax.axvline(self._max_value, color='red', zorder=-1)
                ax.text(x=x1, y=((y1 - y0) * 0.9), s=f'{interference_percent:.02f}% exceed maximum height', color='red', horizontalalignment='right')

        elif self._path_type == 'min':
            ax.set_xlabel('distribution of total height')

            interference = [v for v in self._stackups if v < self._min_value]

            if len(interference) > 0:
                interference_percent = 100.0 * len(interference) / len(self._stackups)

                x0, x1 = ax.get_xlim()
                y0, y1 = ax.get_ylim()
                ax.axvspan(x0, self._min_value, color='red', zorder=-2, alpha=0.1)
                ax.axvline(self._min_value, color='red', zorder=-1)
                ax.text(x=x0, y=((y1 - y0) * 0.9), s=f'{interference_percent:.02f}% exceed maximum height', color='red')

        plt.show()

        return None


if __name__ == '__main__':
    size = 100000
    part0 = Part(
        name='part0',
        nominal_value=1.0,
        upper_tolerance=0.03,
        size=size
    )

    part1 = Part(
        name='part1',
        nominal_value=2.0,
        upper_tolerance=0.05,
        size=size
    )

    part2 = Part(
        name='part2',
        nominal_value=-3.05,
        upper_tolerance=0.05,
        size=size
    )

    sp = StackPath()
    sp.add_part(part0)
    sp.add_part(part1)
    sp.add_part(part2)

    sp.analyze()

    part0.show_dist(density=True, bins=101)
    part1.show_dist(density=True, bins=101)
    part2.show_dist(density=True, bins=101)

    sp.show_dist(bins=31)
