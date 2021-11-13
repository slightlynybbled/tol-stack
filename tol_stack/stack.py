import logging

import matplotlib.pyplot as plt
from matplotlib.figure import figaspect
import numpy as np

from tol_stack.part import Part


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
                raise ValueError('part sample sizes do not match, '
                                 'cannot perform valid comparison')

        self.parts.append(part)

    def retrieve_parts(self, safe=True):
        """
        Retrieves a safe copy of the parts to work with.

        :param safe: if False, will return a list of the \
        part instances; if True, \
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
        fig, axs = plt.subplots(2, 1)

        axs[0].axvline(0, label='datum', alpha=0.6)

        finals = np.zeros(len(self.parts[0].values))
        for i, part in enumerate(self.parts):
            part.refresh()
            finals += part.values
            axs[0].hist(finals, histtype='step', bins=31, label=f'{part.name}')

        # place green/red zones on top plot
        if self.min_value is not None and self.max_value is not None:
            axs[0].axvspan(self.min_value, self.max_value, color='green', zorder=-1, label='target', alpha=0.5)

        # plt.legend(bbox_to_anchor=(0, 1), loc='upper left', ncol=1)
        axs[0].legend(bbox_to_anchor=(1.04, 1), loc="upper left")
        axs[0].set_title(f'Stackup')
        axs[0].grid()

        axs[1].hist(finals, histtype='step', bins=31,
                    label='Distribution of final')

        if self.min_value is not None:
            interference = [v for v in self._stackups if v < self.min_value]
            if len(interference) > 0:
                interference_percent = 100.0 * len(interference) / len(
                    self._stackups)

                x0, x1 = axs[1].get_xlim()
                y0, y1 = axs[1].get_ylim()
                axs[1].axvspan(x0, self.min_value, color='red', zorder=-2,
                               alpha=0.1)
                axs[1].axvline(self.min_value, color='red', zorder=-1)
                axs[1].text(x=self.min_value, y=((y1 - y0) * 0.9),
                            s=f'{interference_percent:.02f}% below minimum',
                            color='red', horizontalalignment='right')

        if self.max_value is not None:
            interference = [v for v in self._stackups if v > self.max_value]

            if len(interference) > 0:
                interference_percent = 100.0 * len(interference) / len(
                    self._stackups)

                x0, x1 = axs[1].get_xlim()
                y0, y1 = axs[1].get_ylim()
                axs[1].axvspan(self.max_value, x1, color='red', zorder=-2,
                               alpha=0.1)
                axs[1].axvline(self.max_value, color='red', zorder=-1)
                axs[1].text(x=self.max_value, y=((y1 - y0) * 0.9),
                            s=f'{interference_percent:.02f}% above maximum',
                            color='red', horizontalalignment='left')

        fig.tight_layout()
        return fig

    def show_dist2(self, **kwargs):
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
            ax.set_xlabel('distribution of total length')

            interference = [v for v in self._stackups if v > self.max_value]

            if len(interference) > 0:
                interference_percent = 100.0 * len(interference) / len(
                    self._stackups)

                x0, x1 = ax.get_xlim()
                y0, y1 = ax.get_ylim()
                ax.axvspan(self.max_value, x1, color='red', zorder=-2,
                           alpha=0.1)
                ax.axvline(self.max_value, color='red', zorder=-1)
                ax.text(x=self.max_value, y=((y1 - y0) * 0.9),
                        s=f'{interference_percent:.02f}% above maximum',
                        color='red', horizontalalignment='left')

        if self.min_value is not None:
            ax.set_xlabel('distribution of total length')

            interference = [v for v in self._stackups if v < self.min_value]

            if len(interference) > 0:
                interference_percent = 100.0 * len(interference) / len(
                    self._stackups)

                x0, x1 = ax.get_xlim()
                y0, y1 = ax.get_ylim()
                ax.axvspan(x0, self.min_value, color='red', zorder=-2,
                           alpha=0.1)
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

    # part0.show_dist(density=True, bins=31)
    # plt.show()

    # part1.show_dist(density=True, bins=31)
    # plt.show()

    # part2.show_dist(density=True, bins=31)
    # plt.show()

    sp.show_dist()
    plt.show()
