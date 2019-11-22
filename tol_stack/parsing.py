from pathlib import Path
import yaml

from tol_stack.stack import Part, StackPath


class Parser:
    def __init__(self):
        self._stack = None

    def load_yaml(self, path: Path):
        with path.open(mode='r') as f:
            text = f.read()

        data = yaml.load(text, Loader=yaml.Loader)

        # for the moment, we will only support one stack path
        stack_path = list(data.keys())[0]

        parts = []
        for part in data[stack_path]['parts']:
            part_name = list(part.keys())[0]
            values = {k.strip().replace(' ', '_'): v for k, v in part[part_name].items()}
            parts.append(Part(name=part_name, **values))

        values = {k.strip().replace(' ', '_').lower(): v
                  for k, v in data[stack_path].items()
                  if k.strip().lower() != 'parts'}
        self._stack = StackPath(**values)

        for part in parts:
            self._stack.add_part(part)

    def dump_yaml(self, path: Path):
        """
        Saves stack path and parts into a yaml file.

        :param path: path to file name under which to save the data
        :return:
        """
        raise NotImplementedError

    @property
    def stackup(self):
        return self._stack


if __name__ == '__main__':
    parser = Parser()
    parser.load_yaml(Path('../examples/circuit.yml'))

