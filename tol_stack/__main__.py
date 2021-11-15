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
@click.option('file', '-f', multiple=True,
              help='specify for each yml file against which to run a '
                   'report to implement')
def main(file):
    print(
        f'Tolerance Stack Analyzer, v{__version__}\n'
        f'Jason R. Jones\n'
        '----------------------------------'
    )

    paths = [Path(f) for f in file]
    if not paths:
        _logger.warning(f'no files found')
        return

    for path in paths:
        if not path.exists():
            _logger.critical(f'file not found at "{path}"')
            return

    print(f'{len(paths)} files found for processing...')

    sleep(0.01)  # minor sleep to preserve console output order
    for path in tqdm(paths):
        parser = Parser()
        parser.load_yaml(path)
        stack = parser.stack
        StackupReport(stackpath=stack)

    sleep(0.01)  # minor sleep to preserve console output order

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
