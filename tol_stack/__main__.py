import logging
from pathlib import Path
from time import sleep

import click
from tqdm import tqdm

from tol_stack.parsing import Parser
from tol_stack.report import StackupReport
from tol_stack.version import __version__

_logger = logging.getLogger(__name__)


@click.command()
@click.option('path', '-p',
              help='specify for each yml file against which to run a '
                   'report to implement')
@click.option('output', '-o', default='output.png', help='output file (i.e. "out.png")')
def main(path, output):
    _logger.info(
        '----------------------------------\n'
        f'Tolerance Stack Analyzer, v{__version__}\n'
        f'Jason R. Jones\n'
        '----------------------------------'
    )

    if not path:
        _logger.warning(f'no files found')
        return

    path = Path(path)
    if not path.exists():
        _logger.critical(f'file not found at "{path}"')
        return

    parser = Parser()
    parser.load_yaml(path)
    stack = parser.stack

    fig = stack.show_dist()
    _logger.info(f'saving output to {output}')
    fig.savefig(output)

    _logger.info('exiting...')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    main()
