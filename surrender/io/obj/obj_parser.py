from dataclasses import dataclass
import re
from surrender.io.obj import *
from surrender.shapes import *
from surrender.vector import Vector

line_regex = re.compile(r'[fgplov]((\s*)|(\s[\d|\s|\w|.]*))')


@dataclass 
class Token:
    type : str
    args : str


class OBJParser:
    @classmethod
    def encode_shapes(cls, shapes):
        string = '# File generated by SurRender Developer Version \n\n'
        index = 1
        for shape in shapes:
            descriptor = cls._get_descriptor(shape)
            string += descriptor.encode_shape(shape, index)
            num_points = len(shape.points())
            index += num_points
        return string
    
    @classmethod
    def parse_string(cls, string):
        tokens = list(cls._create_tokens(string))
        vertices = cls._read_vertices(tokens)

        name = ''
        is_grouping = False
        current_group = []

        for token in tokens:
            if token.type == 'v':
                continue

            elif token.type == 'g':
                if is_grouping and current_group:
                    pass
                name = token.args
                is_grouping = True
                current_group = []

            elif token.type == 'end':
                if is_grouping and current_group:
                    pass
                name = ''
                is_grouping = False
                current_group = []
            
            elif token.type == 'f':
                yield PolygonDescriptor.parse_string(name, token.args, vertices)
                name = '' 
    
    @classmethod
    def _get_descriptor(cls, shape):
        if isinstance(shape, Point):
            return PointDescriptor
        elif isinstance(shape, Line):
            return LineDescriptor
        elif isinstance(shape, Polygon):
            return PolygonDescriptor
        else:
            return None

    @classmethod
    def _create_tokens(cls, string):
        tokens = []
        for line in string.splitlines():
            if not line_regex.match(line):
                continue
            splitter = line.find(' ')
            if splitter == -1:
                token = Token(type = line.strip(),
                              args = '')
            else:
                token = Token(type = line[:splitter].strip(),
                              args = line[splitter:].strip())
            tokens.append(token)
        return tokens
    
    @classmethod
    def _read_vertices(cls, tokens):
        vertices = []
        for token in tokens:
            if token.type == 'v':
                x, y, z = (float(i) for i in token.args.split())
                v = Vector(x, y, z)
                vertices.append(v)
        return vertices
