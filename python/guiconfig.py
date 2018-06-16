from configparser import ConfigParser
from re import findall


class GUIConfig(ConfigParser):
    # Grid parameters
    cols = 0
    rows = 0
    point_coverage = 0.0

    # Circle parameters
    thickness = 1
    is_bounded = True
    color = (0, 0, 1)

    def read(self, filename):
        super().read(filename)

        self.config_filename = filename

        grid_params = self.get_section('Grid')

        grid_params.h_res = self.int('Grid', 'h_res')
        grid_params.v_res = self.int('Grid', 'v_res')
        grid_params.point_coverage = self.float('Grid', 'point_coverage')
        grid_params.colors = [self.tuple('Grid', 'color_off', 3), self.tuple('Grid', 'color_on', 3)]

        circle_params = self.get_section('Circle')

        circle_params.line_thick = self.int('Circle', 'line_thick')
        circle_params.is_bounded = self.bool('Circle', 'is_bounded')
        circle_params.color = self.tuple('Circle', 'color', 3)
        circle_params.start_radius_factor = self.float('Circle', 'start_radius_factor')

    def get_section(self, label):
        try:
            return self[label]
        except KeyError:
            raise KeyError('Section "' + label + '" not found in configuration file "' + self.config_filename + '"')

    def get_val(self, section, label):
        try:
            return self[section][label]
        except KeyError:
            raise KeyError('Value "' + label + '" not found in section "' + section + '" configuration file "' + self.config_filename + '"')

    def int(self, section, label):
        val = self.get_val(section, label)
        try:
            return int(val)
        except ValueError:
            raise ValueError('Value "' + label + '" in section "' + section + '" must be an integer. Instead, got: "' + val + '"')

    def float(self, section, label):
        val = self.get_val(section, label)
        try:
            return float(val)
        except ValueError:
            raise ValueError('Value "' + label + '" in section "' + section + '" must be a float. Instead, got: "' + val + '"')

    def bool(self, section, label):
        val = self.get_val(section, label)
        if val == "True" or val == "False":
            return val == "True"
        raise ValueError('Value "' + label + '" in section "' + section + '" must be True or False. Instead, got: "' + val + '"')

    def tuple(self, section, label, size):
        val = self.get_val(section, label)
        valtup = tuple(map(float, findall('[0-9.]+', val)))
        if len(valtup) == size:
            return valtup
        raise ValueError('Value "' + label + '" in section "' + section + '" must be a ' + str(size) + '-tuple. Instead, got: "' + val + '"')