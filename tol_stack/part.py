import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import tol_stack.distributions as distributions


class Part:
    """
    Represents a part, complete with tolerances as defined
    by the distributions.

    :param name: a string representing the part
    :param nominal_length: the nominal value of the dimension
    :param distribution: the distribution of the dimension
    :param size: the number of samples to generate
    :param nominal_length: the nominal value of the dimension
    :param tolerance: the tolerance of the part
    :param concentricity: specifies concentricity as defined by GD&T; not \
    currently implemented
    :param runout: specifies runout as defined by GD&T; \
    not currently implemented
    :param limits: the limits of the distribution; if there are two limits on the distribution, then \
    there are two lengths to be passed as a tuple; else, if the distribution is expecting a single value, \
    then this value will be a float
    :param material: essentially, a comment at this point, but we may
    wish to make this into a placeholder which allows a lookup of
    common CTE lengths
    :param cte: coefficient of thermal expansion in (length / deg C) \
    where length is the same unit \
    as is specified for the `nominal_length` and `tolerance`
    :param comment: any comment about the part that the user wishes to add
    :param skewiness: "0" skewiness, represents no skew; a negative skewiness \
    will create a left skew while a positive skewiness will create a \
    right skew; as skewiness increases, so does the skew of the distribution
    :param image_path: the Path to an image, such as a PNG, which shows
    the dimension(s)
    """
    def __init__(self, name: str,
                 distribution: str = 'norm',
                 size: int = 10000,
                 nominal_length: float = None,
                 tolerance: float = None,
                 concentricity: float = None,
                 runout: float = None,
                 limits: (tuple, float) = None,
                 material: str = None,
                 cte: str = None,
                 comment: str = None,
                 skewiness: float = None,
                 image_path: Path = None,
                 loglevel=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        valid_distributions = self.retrieve_distributions()
        if distribution.lower() not in valid_distributions:
            raise ValueError(f'unexpected distribution "{distribution}"; '
                             f'distribution must be in "{valid_distributions}"')

        if 'skew' in distribution and skewiness is None:
            raise ValueError('the "skewiness" must be specified when '
                             'a skewed distribution is specified')

        self.name = name
        self.distribution = distribution.lower()
        self.nominal_length = nominal_length
        self.tolerance = abs(tolerance) if tolerance else tolerance
        self.concentricity = concentricity  # todo: implement concentricity
        self.runout = runout  # todo: implement runout
        self.material = material
        self.cte = cte
        self.comment = comment

        self._limits = limits
        self._size = size
        self._skewiness = skewiness
        self._image_path = image_path

        self.lengths = None
        self.concentricities = None

        self.refresh()

    def __repr__(self):
        return f'<Part "{self.name}" dist="{self.distribution}" ' \
               f'nom={self.nominal_length:.03f} \u00b1{self.tolerance:.03f}>'

    def to_dict(self):
        return {
            'name': self.name,
            'distribution': self.distribution,
            'nominal value': self.nominal_length,
            'tolerance': self.tolerance
        }

    @staticmethod
    def retrieve_distributions():
        return ['norm', 'norm-screened', 'norm-notched',
                'norm-lt', 'norm-gt', 'skew-normal']

    def refresh(self, size: int = None):
        """
        Re-calculates the distribution.

        :param size: Allows external software to override the size
        :return: None
        """
        if size is not None:
            self._size = size

        if self.nominal_length is not None:
            if self.distribution == 'norm':
                self.lengths = distributions.norm(
                    loc=self.nominal_length,
                    scale=self.tolerance / 3,
                    size=self._size
                )
            elif self.distribution == 'norm-screened':
                self.lengths = distributions.norm_screened(
                    loc=self.nominal_length,
                    scale=self.tolerance / 3,
                    size=self._size,
                    limits=self._limits
                )
            elif self.distribution == 'norm-notched':
                self.lengths = distributions.norm_notched(
                    loc=self.nominal_length,
                    scale=self.tolerance / 3,
                    size=self._size,
                    limits=self._limits
                )
            elif self.distribution == 'norm-lt':
                if isinstance(self._limits, tuple):
                    limit, *_ = self._limits
                else:
                    limit = self._limits

                self.lengths = distributions.norm_lt(
                    loc=self.nominal_length,
                    scale=self.tolerance / 3,
                    size=self._size,
                    limit=limit
                )
            elif self.distribution == 'norm-gt':
                if isinstance(self._limits, tuple):
                    limit, *_ = self._limits
                else:
                    limit = self._limits

                self.lengths = distributions.norm_gt(
                    loc=self.nominal_length,
                    scale=self.tolerance / 3,
                    size=self._size,
                    limit=limit
                )

            elif self.distribution == 'skew-normal':
                self.lengths = distributions.skew_normal(
                    loc=self.nominal_length,
                    scale=self.tolerance / 3,
                    size=self._size,
                    skewiness=self._skewiness
                )

            else:
                raise ValueError(f'distribution "{self.distribution}" '
                                 f'appears to be invalid')

        if self.concentricity is not None:
            if self.distribution == 'norm':
                r = distributions.norm(
                    loc=0,
                    scale=self.concentricity / 3,
                    size=self._size
                )
                theta = np.random.uniform(0.0, 2*np.pi, size=self._size)
                self.concentricities = r * np.exp(1j*theta)

            else:
                raise ValueError('currently, only the "norm" distribution '
                                 'is implemented for concentricity '
                                 'calculations')

        if self.runout is not None:
            raise ValueError('runout not currently implemented')

    def show_length_dist(self, **kwargs):
        """
        Shows the distribution for the part on a matplotlib plot.

        :param kwargs: All keyword arguments must be valid for matplotlib.pyplot.hist
        :return: Figure
        """
        if self.lengths is None:
            raise AttributeError('this part has no length attributes')

        fig, axs = plt.subplots(2)

        # show a "zoomed out" view with the datum and the dimension
        axs[0].hist(self.lengths, **kwargs)
        axs[0].set_xlim(0)
        axs[0].set_title(f'Part distribution, {self.name}')

        axs[1].hist(self.lengths, **kwargs)

        for ax in axs:
            ax.grid()

        return fig

    def show_concentricity_dist(self, **kwargs):
        if self.concentricities is None:
            raise AttributeError('this part has no concentricity attributes')

        # semi-smart adjustment of alpha
        fig, ax = plt.subplots()

        alpha = 1000 / len(self.concentricities)
        alpha = alpha if alpha < 1.0 else 1.0
        alpha = alpha if alpha > 0.1 else 0.1

        ax.scatter(
            self.concentricities.real,
            self.concentricities.imag,
            label='samples',
            s=1.0,
            alpha=alpha
        )
        ax.add_patch(
            plt.Circle((0, 0), self.concentricity,
                       fill=False, label='tolerance',
                       color='red', alpha=0.5, zorder=-1)
        )
        ax.set_aspect(1)
        ax.set_title('Concentricity Samples')

        ax.grid()
        ax.legend()

        return fig


if __name__ == '__main__':
    p1 = Part(name='p1',
              concentricity=0.02,
              size=2000)
    #p1.show_length_dist(bins=51)
    p1.show_concentricity_dist()

    plt.show()
