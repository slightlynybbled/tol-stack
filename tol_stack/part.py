import logging
import matplotlib.pyplot as plt
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
    :param cte: coefficient of thermal expansion in (length / deg C) where length is the same unit \
    as is specified for the `nominal_value` and `tolerance`
    """
    def __init__(self, name: str,
                 nominal_value: float, tolerance: float,
                 distribution: str = 'norm', size: int = 10000,
                 limits: (tuple, float) = None,
                 material: str = None,
                 cte: str = None,
                 comment: str = None,
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
        self.material = material
        self.cte = cte
        self.comment = comment

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
        fig, axs = plt.subplots(2)

        # show a "zoomed out" view with the datum and the dimension
        axs[0].hist(self.values, **kwargs)
        axs[0].set_xlim(0)
        axs[0].set_title(f'Part distribution, {self.name}')

        axs[1].hist(self.values, **kwargs)

        for ax in axs:
            ax.grid()


if __name__ == '__main__':
    p1 = Part(name='p1', nominal_value=1.0, tolerance=0.01, size=100000)
    p1.show_dist(bins=51)
    plt.show()
