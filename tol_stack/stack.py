import logging
from pathlib import Path
from typing import List

from engineering_notation import EngNumber
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from tol_stack.part import Part


class StackPath:
    """
    The stack path analysis class.

    :param name: the name of the stack path
    :param description: a brief description of the stack path intent
    :param image_paths: a single path or a list of paths to \
    different images that clarify the stack path.
    :param max_length: a floating-point number; when present, indicates \
    that the length of the parts is to be stacked and evaluated
    :param min_length: a floating-point number; when present, indicates \
    that the length of the parts is to be stacked and evaluated
    :param concentricity: a floating-point number; when present, indicates \
    that the concentricity of the parts is to be stacked and evaluated
    :param loglevel: the logging level that is to be implemented for the class
    """

    def __init__(self,
                 name: str = 'Tolerance Stackup Report',
                 description: str = None,
                 image_paths: (str, List[str], Path, List[Path]) = None,
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

        # convert any strings to paths, convert to a list of paths
        if image_paths is not None:
            if isinstance(image_paths, list):
                image_paths = [Path(ip) if isinstance(ip, str) else ip for ip in image_paths]
            else:
                if isinstance(image_paths, str):
                    image_paths = [Path(image_paths)]
                else:
                    image_paths = [image_paths]

            if image_paths is not None:
                if isinstance(image_paths, list):
                    self.images = [Image.open(ip) for ip in image_paths]
                else:
                    raise ValueError('image_paths must be of type `Path` or `List[Path]`')
        else:
            self.images = None

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

        fig, axs = plt.subplots(3, 1, figsize=(6, 9), dpi=300)

        axs[0].axvline(0, label='datum', alpha=0.6)
        if self.min_length is not None and self.max_length is not None:
            axs[0].axvspan(self.min_length, self.max_length, color='green',
                           zorder=-1, label='target', alpha=0.3)

        num_of_parts = len(self.parts)

        # determine rough plot length to size the arrow heads
        head_width = new_width = 0
        for part in self.parts:
            new_width += part.nominal_length
            if new_width > head_width:
                head_width = new_width
        head_width *= 0.05

        # draw arrows
        last_part_x = 0
        for i in range(num_of_parts):
            part = self.parts[i]
            axs[0].arrow(y=i, dy=0, x=last_part_x, dx=part.nominal_length,
                         width=head_width / 3,
                         length_includes_head=True, head_width=head_width)

            last_part_x = last_part_x + part.nominal_length
        axs[0].set_yticks(range(len(self.parts)))
        axs[0].set_yticklabels([part.name for part in self.parts])
        axs[0].invert_yaxis()
        axs[0].set_title('Stackup Flow Chart')
        axs[0].legend(bbox_to_anchor=(1.04, 1), loc="upper left")

        # draw datum, then distributions of added errors.
        axs[1].axvline(0, label='datum', alpha=0.6)
        finals = np.zeros(len(self.parts[0].lengths))
        for i in range(num_of_parts):
            part = self.parts[i]
            finals += part.lengths
            axs[1].hist(finals, histtype='step', bins=31, label=f'{part.name}')

        # place green/red zones on length stackup
        if self.min_length is not None and self.max_length is not None:
            axs[1].axvspan(self.min_length, self.max_length, color='green',
                           zorder=-1, label='target', alpha=0.3)

        axs[1].legend(bbox_to_anchor=(1.04, 1), loc="upper left")
        axs[1].set_title(f'Distribution by Length')

        axs[2].hist(finals, histtype='step', bins=31,
                    label='Distribution of final')
        axs[2].set_title(f'Final Stackup, {EngNumber(len(finals))} Samples')

        if self.min_length is not None:
            interference = [v for v in finals if v < self.min_length]
            if len(interference) > 0:
                interference_percent = 100.0 * len(interference) / len(finals)

                x0, x1 = axs[2].get_xlim()
                y0, y1 = axs[2].get_ylim()
                axs[2].axvspan(x0, self.min_length, color='red', zorder=-2,
                               alpha=0.1)
                axs[2].axvline(self.min_length, color='red', zorder=-1)
                axs[2].text(x=self.min_length, y=((y1 - y0) * 0.9),
                            s=f'{interference_percent:.02f}% below minimum',
                            color='red', horizontalalignment='right')

        if self.max_length is not None:
            interference = [v for v in finals if v > self.max_length]

            if len(interference) > 0:
                interference_percent = 100.0 * len(interference) / len(finals)

                x0, x1 = axs[2].get_xlim()
                y0, y1 = axs[2].get_ylim()
                axs[2].axvspan(self.max_length, x1, color='red', zorder=-2,
                               alpha=0.1)
                axs[2].axvline(self.max_length, color='red', zorder=-1)
                axs[2].text(x=self.max_length, y=((y1 - y0) * 0.9),
                            s=f'{interference_percent:.02f}% above maximum',
                            color='red', horizontalalignment='left')

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
