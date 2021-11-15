import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from tol_stack.part import Part


class StackPath:
    """
    The stack path analysis class.

    :param max_length: a floating-point number; when present, indicates \
    that the length of the parts is to be stacked and evaluated
    :param min_length: a floating-point number; when present, indicates \
    that the length of the parts is to be stacked and evaluated
    :param max_concentricity: a floating-point number; when present, indicates \
    that the concentricity of the parts is to be stacked and evaluated
    :param loglevel: the logging level that is to be implemented for the class

    """

    def __init__(self,
                 name: str = 'Tolerance Stackup Report',
                 description: str = None,
                 image_path: Path = None,
                 max_length: float = None,
                 min_length: float = None,
                 concentricity: float = None,
                 loglevel=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self.parts = []

        self.max_length = max_length
        self.min_length = min_length
        self.max_concentricity = concentricity

        self.name = name
        self.description = description
        self.image_path = image_path

    @property
    def is_length(self):
        return self.max_length is not None or self.min_length is not None

    @property
    def is_concentricity(self):
        return self.max_concentricity is not None

    def add_part(self, part: Part):
        """
        Adds a part to the stack path.

        :param part: An instance of ``Part``
        :return: None
        """
        if self.parts:
            if self.min_length is not None or self.max_length is not None:
                if len(part.lengths) != len(self.parts[0].lengths):
                    raise ValueError('part sample sizes do not match, '
                                     'cannot perform valid comparison')
            elif self.max_concentricity is not None:
                if len(part.concentricities) != len(
                        self.parts[0].concentricities):
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

    def show_length_dist(self):
        # as this is a length analysis, we are to ensure that
        # all parts have lengths associated with them
        for part in self.parts:
            part.refresh()
            if part.lengths is None:
                raise AttributeError(f'part "{part.name}" does not '
                                     f'have a proper length specification')

        fig, axs = plt.subplots(2, 1)

        axs[0].axvline(0, label='datum', alpha=0.6)

        finals = np.zeros(len(self.parts[0].lengths))
        for i, part in enumerate(self.parts):
            finals += part.lengths
            axs[0].hist(finals, histtype='step', bins=31, label=f'{part.name}')

        # place green/red zones on top plot
        if self.min_length is not None and self.max_length is not None:
            axs[0].axvspan(self.min_length, self.max_length, color='green',
                           zorder=-1, label='target', alpha=0.5)

        axs[0].legend(bbox_to_anchor=(1.04, 1), loc="upper left")
        axs[0].set_title(f'Length Stackup')

        axs[1].hist(finals, histtype='step', bins=31,
                    label='Distribution of final')

        if self.min_length is not None:
            interference = [v for v in finals if v < self.min_length]
            if len(interference) > 0:
                interference_percent = 100.0 * len(interference) / len(finals)

                x0, x1 = axs[1].get_xlim()
                y0, y1 = axs[1].get_ylim()
                axs[1].axvspan(x0, self.min_length, color='red', zorder=-2,
                               alpha=0.1)
                axs[1].axvline(self.min_length, color='red', zorder=-1)
                axs[1].text(x=self.min_length, y=((y1 - y0) * 0.9),
                            s=f'{interference_percent:.02f}% below minimum',
                            color='red', horizontalalignment='right')

        if self.max_length is not None:
            interference = [v for v in finals if v > self.max_length]

            if len(interference) > 0:
                interference_percent = 100.0 * len(interference) / len(finals)

                x0, x1 = axs[1].get_xlim()
                y0, y1 = axs[1].get_ylim()
                axs[1].axvspan(self.max_length, x1, color='red', zorder=-2,
                               alpha=0.1)
                axs[1].axvline(self.max_length, color='red', zorder=-1)
                axs[1].text(x=self.max_length, y=((y1 - y0) * 0.9),
                            s=f'{interference_percent:.02f}% above maximum',
                            color='red', horizontalalignment='left')

        # todo: would be nice to draw arrows on the plot from part to part

        for ax in axs:
            ax.grid()

        fig.tight_layout()
        return fig

    def show_concentricity_dist(self):
        for part in self.parts:
            part.refresh()
            if part.concentricities is None:
                raise AttributeError(f'part "{part.name}" does not '
                                     f'have a proper concentricity specification')

        fig, axs = plt.subplots(len(self.parts) + 1,
                                figsize=(8, (len(self.parts) + 1) * 8),
                                sharex=True, sharey=True)

        thetas = np.zeros(len(self.parts[0].concentricities))
        finals = np.zeros(len(self.parts[0].concentricities)) * np.exp(
            1j * thetas)
        for i, part in enumerate(self.parts):
            finals += part.concentricities
            axs[i].scatter(
                part.concentricities.real,
                part.concentricities.imag,
                label=f'{part.name}',
                s=0.1
            )
            axs[i].set_title(f'Concentricity for {part.name}')

            # place limit circle on part
            axs[i].add_patch(
                plt.Circle((0, 0), self.max_concentricity,
                           fill=False, label='tolerance',
                           color='red', alpha=0.5, zorder=-1)
            )

        # plot final
        axs[-1].set_title('Final Concentricity')
        axs[-1].scatter(finals.real, finals.imag, s=0.1)
        axs[-1].add_patch(
            plt.Circle((0, 0), self.max_concentricity,
                       fill=False, label='tolerance',
                       color='red', alpha=0.5, zorder=-1)
        )

        # calculate how many are outside the circle and report as a percent
        out_of_range = (abs(finals.real) >= self.max_concentricity).sum()
        if out_of_range > 0:
            total = len(finals)
            percent_fail = 100 * out_of_range / total
            axs[-1].text(x=0, y=self.max_concentricity,
                         s=f'{percent_fail:.02f}% outside maximum total concentricity',
                         color='red', horizontalalignment='center', verticalalignment='bottom')

        for ax in axs:
            ax.grid()
            ax.set_aspect(1)

        fig.tight_layout()

        return fig


if __name__ == '__main__':
    size = 100000

    part0 = Part(
        name='part0',
        nominal_length=1.0,
        tolerance=0.01,
        limits=1.02,
        size=size
    )

    part1 = Part(
        name='part1',
        nominal_length=2.0,
        tolerance=0.01,
        limits=2.02,
        size=size
    )

    part2 = Part(
        name='part2',
        nominal_length=-2.98,
        tolerance=0.02,
        size=size
    )

    sp = StackPath(max_length=0.05, min_length=0.00)
    sp.add_part(part0)
    sp.add_part(part1)
    sp.add_part(part2)

    # part0.show_dist(density=True, bins=31)
    # plt.show()

    # part1.show_dist(density=True, bins=31)
    # plt.show()

    # part2.show_dist(density=True, bins=31)
    # plt.show()

    sp.show_length_dist()
    plt.show()
