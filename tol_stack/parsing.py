from pathlib import Path
import yaml

from tol_stack.stack import Part, StackPath


class Parser:
    def __init__(self):
        self._stack = None

    @property
    def stack(self):
        return self._stack

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

    def dump_yaml(self, path: Path):
        """
        Saves stack path and parts into a yaml file.

        :param path: path to file name under which to save the data
        :return:
        """
        data = {}

        if self._stack.max_length is not None:
            data['max value'] = self._stack.max_length
        if self._stack.min_length is not None:
            data['min value'] = self._stack.min_length

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


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    parser = Parser()
    parser.load_yaml(Path('examples/max_length.yml'))
    # parser.load_yaml(Path('../examples/concentricity.yml'))
    parser.dump_yaml(Path('examples/dump.yml'))

    parser.stack.show_length_dist()
    # parser.stack.show_concentricity_dist()

    # plt.show()
    # parser.stack.report()

