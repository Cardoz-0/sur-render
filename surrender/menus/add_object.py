import sys
import re
from random import randint

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtWidgets import * 

from surrender.shapes import *
from surrender.vector import Vector
  

class AddObject(QWidget):
    def __init__(self, viewport):
        super(AddObject, self).__init__()

        self.viewport = viewport
        self.create_tabs()

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def create_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(BicubicBezierWidget(self.viewport), "Bicubic Bezier")
        self.tabs.addTab(PointWidget(self.viewport), "Point")
        self.tabs.addTab(LineWidget(self.viewport), "Line")
        self.tabs.addTab(PolygonWidget(self.viewport), "Polygon")
        self.tabs.addTab(BezierWidget(self.viewport), "Bezier")
        self.tabs.addTab(BSplineWidget(self.viewport), "B-Spline")
        self.tabs.addTab(RectangleWidget(self.viewport), "Rectangle")
        self.tabs.addTab(CubeWidget(self.viewport), "Cube")

  
class GenericShapeWidget(QWidget):
    def __init__(self, viewport):
        super().__init__()

        self.viewport = viewport
        self.name_line = QLineEdit()
        self.random_button = QPushButton('Generate Random')
        self.apply_button = QPushButton('Apply')
        self.color_button = QPushButton('')
        self.color = (255,0,0)

        self.paint_button(self.color_button, self.color)
        self.color_button.pressed.connect(self.color_callback)
        self.random_button.pressed.connect(self.random_callback)
        self.apply_button.pressed.connect(self.apply_callback)

    def add_shape(self, shape):
        self.viewport.add_shape(shape)

    def color_callback(self):
        c = QColorDialog.getColor()
        self.color = (c.red(), c.green(), c.blue())
        self.paint_button(self.color_button, self.color)

    def paint_button(self, button, color):
        button.setStyleSheet(f'background-color: rgb({color[0]},{color[1]},{color[2]})')

    def random_callback(self):
        pass 
    
    def apply_callback(self):
        pass 


class PointWidget(GenericShapeWidget):
    def __init__(self, viewport): 
        super().__init__(viewport)

        self.x_line = QLineEdit()
        self.y_line = QLineEdit()

        layout = QFormLayout()
        layout.addRow('Name', self.name_line)
        layout.addRow('X', self.x_line)
        layout.addRow('Y', self.y_line)
        layout.addRow('Color', self.color_button)
        layout.addRow(self.random_button)
        layout.addRow(self.apply_button)
        self.setLayout(layout)
    
    def random_callback(self):
        self.color = [randint(0,255) for _ in range(3)]
        self.paint_button(self.color_button, self.color)

        lines = [self.x_line, self.y_line]
        for line in lines:
            n = randint(0, 400)
            line.setText(str(n))

    def apply_callback(self):
        try:
            name = self.name_line.text()
            x = int(self.x_line.text())
            y = int(self.y_line.text())

            pos = Vector(x, y)
            shape = Point(name, pos, self.color)
            self.add_shape(shape)
        except ValueError:
            pass

class LineWidget(GenericShapeWidget):
    def __init__(self, viewport): 
        super().__init__(viewport)

        self.x0_line = QLineEdit()
        self.y0_line = QLineEdit()
        self.x1_line = QLineEdit()
        self.y1_line = QLineEdit()

        layout = QFormLayout()
        layout.addRow('Name', self.name_line)
        layout.addRow('X0', self.x0_line)
        layout.addRow('Y0', self.y0_line)
        layout.addRow('X1', self.x1_line)
        layout.addRow('Y1', self.y1_line)
        layout.addRow('Color', self.color_button)
        layout.addRow(self.random_button)
        layout.addRow(self.apply_button)
        self.setLayout(layout)
    
    def random_callback(self):
        self.color = [randint(0,255) for _ in range(3)]
        self.paint_button(self.color_button, self.color)

        lines = [
            self.x0_line,
            self.y0_line,
            self.x1_line,
            self.y1_line,
        ]

        for line in lines:
            n = randint(0, 400)
            line.setText(str(n))

    def apply_callback(self):
        try:
            name = self.name_line.text()
            x0 = int(self.x0_line.text())
            y0 = int(self.y0_line.text())
            x1 = int(self.x1_line.text())
            y1 = int(self.y1_line.text())

            s = Vector(x0, y0)
            e = Vector(x1, y1)
            shape = Line(name, s, e, self.color)
            self.add_shape(shape)
        except ValueError:
            pass


class PolygonWidget(GenericShapeWidget):
    def __init__(self, viewport): 
        super().__init__(viewport)

        self.points_line = QLineEdit()
        self.fill_box = QCheckBox()

        self.type_buttons = [
            QRadioButton('Open'),
            QRadioButton('Closed'),
            QRadioButton('Filled'),
        ]
        self.type_buttons[0].setChecked(True)
        self.type_group = QButtonGroup()

        for i, b in enumerate(self.type_buttons):
            self.type_group.addButton(b, i)

        layout = QFormLayout()
        layout.addRow('Name', self.name_line)
        layout.addRow('Your Points', self.points_line)
        layout.addRow('Color', self.color_button)
        layout.addRow('', self.type_buttons[0])
        layout.addRow('', self.type_buttons[1])
        layout.addRow('', self.type_buttons[2])
        layout.addRow(self.random_button)
        layout.addRow(self.apply_button)
        self.setLayout(layout)

    def random_callback(self):
        self.color = [randint(0,255) for _ in range(3)]
        self.paint_button(self.color_button, self.color)

        n_points = randint(3, 8)
        points = [(randint(0,400), randint(0,400)) for i in range(n_points)]
        text =  ''.join(f'{i}, ' for i in points)
        self.points_line.setText(text)
    
    def apply_callback(self):
        try:
            get_digits = lambda x: tuple(int(i) for i in re.findall(r'-?\d+', x))
            between_brackets = re.findall(r'\((.*?)\)', self.points_line.text())
            
            name = self.name_line.text()
            digits = [get_digits(i) for i in between_brackets]

            types = [
                Polygon.OPEN,
                Polygon.CLOSED,
                Polygon.FILLED
            ]
            style = types[self.type_group.checkedId()]

            vectors = [Vector(p[0], p[1]) for p in digits]
            shape = Polygon(name, vectors, self.color, style)

            if vectors:
               self.add_shape(shape)
               
        except ValueError:
            pass


class RectangleWidget(GenericShapeWidget):
    def __init__(self, viewport): 
        super().__init__(viewport)

        self.x0_line = QLineEdit()
        self.y0_line = QLineEdit()
        self.x1_line = QLineEdit()
        self.y1_line = QLineEdit()
        self.fill_box = QCheckBox()

        layout = QFormLayout()
        layout.addRow('Name', self.name_line)
        layout.addRow('X0', self.x0_line)
        layout.addRow('Y0', self.y0_line)
        layout.addRow('X1', self.x1_line)
        layout.addRow('Y1', self.y1_line)
        layout.addRow('Color', self.color_button)
        layout.addRow('Fill color', self.fill_box)
        layout.addRow(self.random_button)
        layout.addRow(self.apply_button)
        self.setLayout(layout)

    def random_callback(self):
        self.color = [randint(0,255) for _ in range(3)]
        self.paint_button(self.color_button, self.color)

        lines = [
            self.x0_line,
            self.y0_line,
            self.x1_line,
            self.y1_line,
        ]

        for line in lines:
            n = randint(0, 400)
            line.setText(str(n))

    def apply_callback(self):
        try:
            name = self.name_line.text()
            x0 = int(self.x0_line.text())
            y0 = int(self.y0_line.text())
            x1 = int(self.x1_line.text())
            y1 = int(self.y1_line.text())
            fill = bool(self.fill_box.checkState())
            style = Polygon.FILLED if fill else Polygon.CLOSED

            s = Vector(x0, y0)
            e = Vector(x1, y1)
            shape = Rectangle(name, s, e, self.color, style)
            self.add_shape(shape)
        except ValueError:
            pass


class BezierWidget(GenericShapeWidget):
    def __init__(self, viewport): 
        super().__init__(viewport)

        self.points_line = QLineEdit()

        layout = QFormLayout()
        layout.addRow('Name', self.name_line)
        layout.addRow('Your Points', self.points_line)
        layout.addRow('Color', self.color_button)
        layout.addRow(self.random_button)
        layout.addRow(self.apply_button)
        self.setLayout(layout)

    def random_callback(self):
        self.color = [randint(0,255) for _ in range(3)]
        self.paint_button(self.color_button, self.color)

        n_points = randint(1, 5) * 3 + 1
        points = [(randint(0,400), randint(0,400)) for i in range(n_points)]
        text =  ''.join(f'{i}, ' for i in points)
        self.points_line.setText(text)
    
    def apply_callback(self):
        try:
            get_digits = lambda x: tuple(int(i) for i in re.findall(r'-?\d+', x))
            between_brackets = re.findall(r'\((.*?)\)', self.points_line.text())
            
            name = self.name_line.text()
            digits = [get_digits(i) for i in between_brackets]

            vectors = [Vector(p[0], p[1]) for p in digits]
            shape = Bezier(name, vectors, self.color)

            if vectors:
               self.add_shape(shape)
               
        except ValueError:
            pass


class BSplineWidget(GenericShapeWidget):
    def __init__(self, viewport): 
        super().__init__(viewport)

        self.points_line = QLineEdit()

        layout = QFormLayout()
        layout.addRow('Name', self.name_line)
        layout.addRow('Your Points', self.points_line)
        layout.addRow('Color', self.color_button)
        layout.addRow(self.random_button)
        layout.addRow(self.apply_button)
        self.setLayout(layout)

    def random_callback(self):
        self.color = [randint(0,255) for _ in range(3)]
        self.paint_button(self.color_button, self.color)

        n_points = randint(4, 10)
        points = [(randint(0,400), randint(0,400)) for i in range(n_points)]
        text =  ''.join(f'{i}, ' for i in points)
        self.points_line.setText(text)
    
    def apply_callback(self):
        try:
            get_digits = lambda x: tuple(int(i) for i in re.findall(r'-?\d+', x))
            between_brackets = re.findall(r'\((.*?)\)', self.points_line.text())
            
            name = self.name_line.text()
            digits = [get_digits(i) for i in between_brackets]

            vectors = [Vector(p[0], p[1]) for p in digits]
            shape = BSpline(name, vectors, self.color)

            if vectors:
               self.add_shape(shape)
               
        except ValueError:
            pass


class CubeWidget(GenericShapeWidget):
    def __init__(self, viewport):
        super().__init__(viewport)
        self.x_line = QLineEdit()
        self.y_line = QLineEdit()
        self.z_line = QLineEdit()
        self.s_line = QLineEdit()
        
        layout = QFormLayout()
        layout.addRow('Name', self.name_line)
        layout.addRow('X', self.x_line)
        layout.addRow('Y', self.y_line)
        layout.addRow('Z', self.z_line)
        layout.addRow('L', self.s_line)
        layout.addRow('Color', self.color_button)
        layout.addRow(self.random_button)
        layout.addRow(self.apply_button)
        self.setLayout(layout)

    def random_callback(self):
        self.color = [randint(0,255) for _ in range(3)]
        self.paint_button(self.color_button, self.color)

        lines = [
            self.x_line,
            self.y_line,
            self.z_line,
        ]

        for line in lines:
            n = randint(0, 400)
            line.setText(str(n))

        n = randint(100, 400)
        self.s_line.setText(str(n))

    def apply_callback(self):
        try:
            name = self.name_line.text()
            x = int(self.x_line.text())
            y = int(self.y_line.text())
            z = int(self.z_line.text())
            s = int(self.s_line.text())
            shape = Cube(name, Vector(x,y,z), s, self.color)
            self.add_shape(shape)
        except ValueError:
            pass

            y0 = int(self.y0_line.text())
            x1 = int(self.x1_line.text())
            y1 = int(self.y1_line.text())
            fill = bool(self.fill_box.checkState())
            style = Polygon.FILLED if fill else Polygon.CLOSED

            s = Vector(x0, y0)
            e = Vector(x1, y1)
            shape = Rectangle(name, s, e, self.color, style)
            self.add_shape(shape)
        except ValueError:
            pass


class BicubicBezierWidget(GenericShapeWidget):
    def __init__(self, viewport): 
        super().__init__(viewport)

        self.points_line = QLineEdit()

        layout = QFormLayout()
        layout.addRow('Name', self.name_line)
        layout.addRow('Your Points', self.points_line)
        layout.addRow('Color', self.color_button)
        layout.addRow(self.random_button)
        layout.addRow(self.apply_button)
        self.setLayout(layout)

    def random_callback(self):
        self.color = [randint(0,255) for _ in range(3)]
        self.paint_button(self.color_button, self.color)

        width = randint(1,5)
        height = randint(1,5)

        text = ''
        for i in range(width):
            points = []
            for j in range(height):
                x = randint(0,400)
                y = randint(0,400)
                z = randint(0,400)
                points.append((x,y,z))
            text += ', '.join(f'({x}, {y}, {z})' for x,y,z in points)
            text += '; '
        self.points_line.setText(text)
    
    def apply_callback(self):
        segments = [
            [Vector(0,   0, 0), Vector(100, 0,   0), Vector(200, 0,   0), Vector(300, 0,   0)],
            [Vector(0, 100, 0), Vector(100, 100, 0), Vector(200, 100, 0), Vector(300, 100, 0)],
            [Vector(0, 200, 0), Vector(100, 200, 0), Vector(200, 200, 0), Vector(300, 200, 0)],
            [Vector(0, 300, 0), Vector(100, 300, 0), Vector(200, 300, 0), Vector(300, 300, 0)],
        ]

        name = self.name_line.text()
        shape = BicubicBezier(name, segments, (255,0,0))
        self.add_shape(shape)