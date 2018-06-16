#:kivy 1.10.0
from math import sqrt
from os.path import basename
from re import sub

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget

# disable multitouch
from guiconfig import GUIConfig

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

config_filename = sub(r'.py', r'.ini', basename(__file__))


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


class Circle(Widget):
    rad = 0
    mx = 0
    my = 0

    circle = None

    def __init__(self, thickness, is_bounded, color):
        super().__init__()

        self._thickness = thickness
        self._is_bounded = is_bounded
        self._color = color

    def redraw(self):
        with self.canvas:
            Color(*self._color)

            if not self._is_bounded or \
                    (self.x < self.mx - self.rad and self.right > self.mx + self.rad) and \
                    (self.y < self.my - self.rad and self.top > self.my + self.rad):
                if self.circle:
                    self.canvas.remove(self.circle)

                self.circle = Line(circle=(self.mx, self.my, self.rad), width=self._thickness)


class RootWidget(FloatLayout):
    def __init__(self):
        super().__init__()

        self.default_radius_ratio = 0.2
        self.default_radius = 0

        config = GUIConfig()
        config.read(config_filename)

        # retrieve Grid parameters
        grid_params = config['Grid']
        cols = grid_params.h_res
        rows = grid_params.v_res
        point_coverage = grid_params.point_coverage

        # retrieve Circle parameters
        circle_params = config['Circle']
        thickness = circle_params.line_thick
        is_bounded = circle_params.is_bounded
        color = circle_params.color

        # add point grid
        self.grid = Grid(point_coverage=point_coverage, cols=cols, rows=rows)
        self.circle = Circle(thickness=thickness, is_bounded=is_bounded, color=color)

        self.add_widget(self.grid)
        self.add_widget(self.circle)

        del config

    def on_touch_down(self, touch):
        # default_radius = min(self.grid.width, self.grid.height) * self.default_radius_ratio
        if touch.button == 'left':
            default_radius = min(self.grid.width / self.grid.cols,
                                 self.grid.height / self.grid.rows) * self.default_radius_ratio
            self.circle.mx, self.circle.my = touch.x, touch.y
            self.circle.rad = default_radius
            self.circle.redraw()
            self.circle.opacity = 1

    def on_touch_move(self, touch):
        if touch.button == 'left':
            cx, cy = self.circle.mx, self.circle.my
            self.circle.rad = sqrt((touch.x - cx) ** 2 + (touch.y - cy) ** 2)
            self.circle.redraw()

    def on_touch_up(self, touch):
        self.analyze()

    def analyze(self):
        self.highlight_points()
        self.request_analysis()

    def highlight_points(self):
        pass

    def request_analysis(self):
        pass


class DigitizerGUI(App):
    def build(self):
        # set background color to white
        Window.clearcolor = (1, 1, 1, 1)

        root = RootWidget()
        return root


if __name__ == "__main__":
    MainApp = DigitizerGUI()
    MainApp.run()