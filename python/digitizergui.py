#:kivy 1.10.0
from math import sqrt
from os.path import basename
from re import sub

from kivy.app import App
from kivy.config import Config as KivyConfig
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget

from guiconfig import GUIConfig

config_filename = sub(r'.py', r'.ini', basename(__file__))

# disable multitouch
KivyConfig.set('input', 'mouse', 'mouse,multitouch_on_demand')


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

        self._refarray = [None] * (self.cols * self.rows)

        index = 0
        # Add a Point Widget to each grid location
        for i in range(self.cols):
            for j in range(self.rows):
                point = Point(i, j, self._point_coverage)
                self.add_widget(point)
                self._refarray[index] = point
                index += 1

    def __getitem__(self, col, row):
        """
        Retrieve Point at col, row.
        Note: row order is reversed to align with coordinate system.
        :param col: the column number (from left to right) of the desired Point
        :param row: the row number (from bottom to top) of the desired Point
        :return: the Point at the given coordinate
        """
        return self._refarray[col + (self.rows - row - 1) * self.cols]


class Circle(Widget):
    rad = 0
    mx = 0
    my = 0

    circle = None

    def __init__(self, thickness, start_radius_factor, is_bounded, color):
        super().__init__()

        self._start_radius_factor = start_radius_factor
        self._thickness = thickness
        self._is_bounded = is_bounded
        self._color = color

    def redraw(self):
        with self.canvas:
            Color(*self._color)

            if not self._is_bounded or self.is_in_bounds():
                if self.circle:
                    self.canvas.remove(self.circle)

                self.circle = Line(circle=(self.mx, self.my, self.rad), width=self._thickness)

    def is_in_bounds(self):
        """
        Checks to if the circle is within the bounds of the canvas.
        :return: True if the circle is contained on the canvas, False otherwise.
        """
        return (self.x < self.mx - self.rad and self.right > self.mx + self.rad) and \
               (self.y < self.my - self.rad and self.top > self.my + self.rad)

    def on_touch_down(self, touch):
        self.mx, self.my = touch.pos
        self.rad = min(self.width / self.parent.grid.cols, self.height / self.parent.grid.rows) * self._start_radius_factor
        self.redraw()

    def on_touch_move(self, touch):
        self.rad = sqrt((touch.x - self.mx) ** 2 + (touch.y - self.my) ** 2)
        self.redraw()

    def collide_point(self, point):
        """
        Check if a Point intersects with the circles circumference.

        :Parameters:
            `point`: Point
                a Point object

        :Returns:
            A bool. True if the point intersects, False otherwise.
        """
        #TODO: Complete Circle.collide_point


class RootWidget(FloatLayout):
    def __init__(self):
        super().__init__()

        self.default_radius_ratio = 0.5

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
        start_radius_factor = circle_params.start_radius_factor

        # add point grid
        self.grid = Grid(point_coverage=point_coverage, cols=cols, rows=rows)
        self.circle = Circle(thickness=thickness, start_radius_factor=start_radius_factor, is_bounded=is_bounded, color=color)

        self.add_widget(self.grid)
        self.add_widget(self.circle)

        del config

    def on_touch_down(self, touch):
        if touch.button == 'left':
            self.circle.on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.button == 'left':
            self.circle.on_touch_move(touch)

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