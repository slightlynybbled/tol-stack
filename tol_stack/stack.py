import logging

import matplotlib.pyplot as plt

import tol_stack.distributions as distributions


class Part:
    def __init__(self, name: str,
                 nominal_value: float, upper_tolerance: float, lower_tolerance: float = None,
                 distribution: str = 'norm', size: int = 1000, limits: tuple = None,
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
            if self._limits is not None:
                if self._lower_value is not None:
                    self._logger.warning('When using the normal distribution the "lower_tolerance" parameter is ignored')
                self.values = distributions.norm_screened(
                    loc=self._nominal_value,
                    scale=(self._upper_value - self._nominal_value) / 3,
                    size=self._size,
                    limits=self._limits
                )
            else:
                self.values = distributions.norm(
                    loc=self._nominal_value,
                    scale=(self._upper_value - self._nominal_value) / 3, size=self._size
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
        if self._parts:
            if len(part.values) != len(self._parts[0].values):
                raise ValueError('part sample sizes do not match, cannot perform valid comparison')

        self._parts.append(part)

    def retrieve_parts(self):
        return self._parts.copy()

    def analyze(self):
        for part in self._parts:
            part.refresh()

        if self._path_type in ['circuit', 'max', 'min']:
            finals = []
            for i in range(len(self._parts[0].values)):
                final = 0.0
                for part in self._parts:
                    final += part.values[i]

                finals.append(final)

            self._stackups = finals

        else:
            raise NotImplementedError(f'path type "{self._path_type}" is not currently implemented')

    def show_dist(self, **kwargs):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.hist(self._stackups, **kwargs)
        ax.set_title(f'Stackup Distribution, {self._path_type}')
        ax.grid()

        if self._path_type == 'circuit':
            ax.set_xlabel('sum of gaps between parts')

            interference = [v for v in self._stackups if v < 0]
            if len(interference) > 0:
                interference_percent = 100.0 * len(interference) / len(self._stackups)

                x0, x1 = ax.get_xlim()
                y0, y1 = ax.get_ylim()
                ax.axvspan(x0, 0.0, color='red', zorder=-2, alpha=0.1)
                ax.axvline(x0, color='red', zorder=-1)
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
        nominal_value=1.95,
        upper_tolerance=0.05,
        size=size
    )

    part2 = Part(
        name='part2',
        nominal_value=1.0,
        upper_tolerance=0.1,
        size=size,
        limits=(0.98, 1.02)
    )

    sp = StackPath(path_type='max', max_value=4.0)
    sp.add_part(part0)
    sp.add_part(part1)
    sp.add_part(part2)

    sp.analyze()

    part2.show_dist(density=True, bins=101)

    sp.show_dist(bins=31)
