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

        parts = []
        for part in data['parts']:
            part_name = list(part.keys())[0]
            values = {k.strip().replace(' ', '_'): v for k, v in part[part_name].items()}
            parts.append(Part(name=part_name, **values))

        values = {k.strip().replace(' ', '_').lower(): v
                  for k, v in data.items()
                  if k.strip().lower() != 'parts'}
        self._stack = StackPath(**values)

        for part in parts:
            self._stack.add_part(part)

        self._stack.analyze()

    def dump_yaml(self, path: Path):
        """
        Saves stack path and parts into a yaml file.

        :param path: path to file name under which to save the data
        :return:
        """
        data = {}

        if self._stack.max_value is not None:
            data['max value'] = self._stack.max_value
        if self._stack.min_value is not None:
            data['min value'] = self._stack.min_value

        parts = [part.to_dict() for part in self._stack.parts]
        data['parts'] = []
        for part in parts:
            part_data = {
                'distribution': part.get('distribution'),
                'nominal value': part.get('nominal value'),
                'tolerance': part.get('tolerance')
            }
            data['parts'].append({part.get('name'): part_data})

        with path.open('w') as f:
            f.write(yaml.dump(data, sort_keys=False))

    @property
    def stackup(self):
        return self._stack


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    parser = Parser()
    parser.load_yaml(Path('../examples/circuit.yml'))
    parser.dump_yaml(Path('../examples/dump.yml'))

    parser.stackup.show_dist()

    plt.show()

