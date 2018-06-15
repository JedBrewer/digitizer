#:kivy 1.10.0

from configparser import ConfigParser
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.config import Config

# disable multitouch
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


class Point(Widget):
    def __init__(self, i, j, display_ratio):
        super().__init__()

        self.x_coord = i
        self.y_coord = j
        self.display_ratio = display_ratio

        self.size_hint = self.display_ratio, self.display_ratio


class Grid(GridLayout):
    def __init__(self, point_coverage, **kwargs):
        super().__init__(**kwargs)

        # The linear scaling of the point representation.
        # Does not effect its actual detection boundary,
        # which is always a square with sides equal to the point spacing
        self._point_coverage = point_coverage

        # Add a Point Widget to each grid location
        for i in range(self.cols):
            for j in range(self.rows):
                point = Point(i, j, self._point_coverage)
                self.add_widget(point)


class RootWidget(FloatLayout):
    def __init__(self):
        super().__init__()

        # read configuration settings
        config = ConfigParser()
        config.read("digitizergui.ini")

        # set grid dimensions
        dims = config['Dimensional Values']
        cols = int(dims['h_res'])
        rows = int(dims['v_res'])
        point_coverage = float(dims['point_coverage'])

        # add point grid
        self.grid = Grid(point_coverage=point_coverage, cols=cols, rows=rows)

        self.add_widget(self.grid)

        del config


class DigitizerGUI(App):
    def build(self):
        # set background color to white
        Window.clearcolor = (1, 1, 1, 1)

        root = RootWidget()
        return root


if __name__ == "__main__":
    MainApp = DigitizerGUI()
    MainApp.run()