#:kivy 1.10.0
from math import sqrt
from os.path import basename
from re import sub
from enum import Enum

from kivy.app import App
from kivy.config import Config as KivyConfig
from kivy.core.window import Window
from kivy.graphics import Color, Line, Ellipse
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget

from guiconfig import GUIConfig

config_filename = sub(r'.py', r'.ini', basename(__file__))

# disable multitouch
KivyConfig.set('input', 'mouse', 'mouse,multitouch_on_demand')


class Side(Enum):
    TOP = 0,
    RIGHT = 1,
    BOTTOM = 2,
    LEFT = 3


class Point(Widget):
    def __init__(self, i, j, display_ratio, initial_color):
        super().__init__()

        self.x_coord = i
        self.y_coord = j
        self.display_ratio = display_ratio
        self.is_highlighted = False

        self.size_hint = self.display_ratio, self.display_ratio

        for instruction in self.canvas.get_group(None):
            if type(instruction) == Color:
                self._color = instruction
                break

        self._color.rgb = initial_color

    def highlight(self):
        self.is_highlighted = True
        self._color.rgb = self.parent.colors[1]


class Grid(GridLayout):
    def __init__(self, colors, point_coverage, **kwargs):
        super().__init__(**kwargs)

        # The linear scaling of the point representation.
        # Does not effect its actual detection boundary,
        # which is always a square with sides equal to the point spacing
        self._point_coverage = point_coverage
        self.colors = colors

        self._refarray = [None] * (self.cols * self.rows)

        index = 0
        # Add a Point Widget to each grid location
        for i in range(self.cols):
            for j in range(self.rows):
                point = Point(i, j, self._point_coverage, self.colors[0])
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
    cx = 0
    cy = 0

    circle = None
    colorref = None

    def __init__(self, thickness, start_radius_factor, is_bounded, color):
        super().__init__()

        self._start_radius_factor = start_radius_factor
        self._thickness = thickness
        self._is_bounded = is_bounded
        self._color = color

    def redraw(self):
        with self.canvas:
            if not self.colorref:
                self.colorref = Color(*self._color)

            if not self._is_bounded or self.is_in_bounds():
                if self.circle:
                    self.canvas.remove(self.circle)

                self.circle = Line(circle=(self.cx, self.cy, self.rad), width=self._thickness)

    def is_in_bounds(self):
        """
        Checks if the circle is within the bounds of the canvas.
        :return: True if the circle is contained on the canvas, False otherwise.
        """
        return (self.x < self.cx - self.rad and self.right > self.cx + self.rad) and \
               (self.y < self.cy - self.rad and self.top > self.cy + self.rad)

    def on_touch_down(self, touch):
        self.cx, self.cy = touch.pos
        self.rad = min(self.width / self.parent.grid.cols, self.height / self.parent.grid.rows) * self._start_radius_factor
        self.redraw()

    def on_touch_move(self, touch):
        self.rad = sqrt((touch.x - self.cx) ** 2 + (touch.y - self.cy) ** 2)
        self.redraw()

    def collide_point(self, point):
        """
        Check if a Point intersects with the circles circumference.

        :Parameters:
            `point`: Point
                a Point object

        :Returns:
            If the point intersects, a 4-tuple of the intersection of the arc with
                the 4 sides (left, right, bottom, top),
                False otherwise.
        """
        # If the point is outside the circle's bounding box, return False
        if (point.x > self.cx + self.rad) or (point.x + point.height < self.cx - self.rad) or \
                (point.y < self.cy - self.rad) or (point.y + point.height > self.cy + self.rad):
            return False

        left = point.x
        right = point.x + point.point.width
        bottom = point.y
        top = point.y + point.point.height

        rel_arc_top = sqrt(self.rad**2 - (top - self.cx)**2)
        rel_arc_right = sqrt(self.rad**2 - (right - self.cx)**2)
        rel_arc_bottom = sqrt(self.rad**2 - (bottom - self.cy)**2)
        rel_arc_left = sqrt(self.rad**2 - (left - self.cx)**2)

        top_intersection = right_intersection = bottom_intersection = left_intersection = True

        if ((left > self.cx + rel_arc_top) or (right < self.cx - rel_arc_top) or
                (left > self.cx - rel_arc_top and right < self.cx + rel_arc_top)):
            top_intersection = False

        if ((bottom > self.cy + rel_arc_right) or (top < self.cy - rel_arc_right) or
                (bottom > self.cy - rel_arc_right and top < self.cy + rel_arc_right)):
            right_intersection = False

        if ((left > self.cx + rel_arc_bottom) or (right < self.cx - rel_arc_bottom) or
                (left > self.cx - rel_arc_bottom and right < self.cx + rel_arc_bottom)):
            bottom_intersection = False

        if ((bottom > self.cy + rel_arc_left) or (top < self.cy - rel_arc_left) or
                (bottom > self.cy - rel_arc_left and top < self.cy + rel_arc_left)):
            left_intersection = False

        if top_intersection or right_intersection or bottom_intersection or left_intersection:
            return top_intersection, right_intersection, bottom_intersection, left_intersection

        return False


class RootWidget(FloatLayout):
    def __init__(self):
        super().__init__()

        self.default_radius_ratio = 0.5

        config = GUIConfig()
        config.read(config_filename)

        # retrieve Grid parameters
        grid_params = config['Grid']

        # retrieve Circle parameters
        circle_params = config['Circle']

        # add point grid
        self.grid = Grid(colors=grid_params.colors, point_coverage=grid_params.point_coverage, cols=grid_params.h_res, rows=grid_params.v_res)
        self.circle = Circle(thickness=circle_params.line_thick, start_radius_factor=circle_params.is_bounded,
                             is_bounded=circle_params.is_bounded, color=circle_params.color)

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
        self._highlight_points()
        self.request_analysis()

    def _highlight_points(self):
        for point in self._trace_circumference:
            point.highlight()

    def _trace_circumference(self):
        pass

    def _find_next_point(self, point, side):
        pass

    def _get_top_point(self):
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
