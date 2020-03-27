# This picture describes the board and all the pieces
# The piece are represented by letters.  Vertexes are
# represented by X's.  This picture is just for reference
# a simpler representation can be achieved.
"""\
... ... ... ... ... ... ... ... ... ... ... ... ... 
... ... ... ... ... .X. ... .X. ... ... ... ... ... 
... ... ... ... ... ..a ... a.. ... ... ... ... ... 

... ... ... ... ... ... a.a ... ... ... ... ... ...
... ... .X. ... .Xi ... iXa ... aX. ... .X. ... ...
... ... ..i ... i.i ... j.j ... a.a ... b.. ... ...

... ... ... i.i ... i.j ... j.a ... a.b ... ... ... 
... .Xh ... hXi ... iXj ... jXk ... kXb ... bX. ... 
... ..h ... g.l ... l.l ... j.k ... k.k ... b.. ... 

... ... h.g ... l.l ... l.j ... k.k ... k.b ... ...
.Xh ... hXg ... gXl ... lXj ... jXk ... kXb ... bX.
... ... h.g ... g.l ... d.d ... d.c ... c.b ... ...

... ..h ... g.g ... l.d ... d.d ... c.c ... b.. ... 
... .Xh ... hXg ... gXd ... dXd ... dXc ... cX. ... 
... ... ... f.f ... f.f ... f.e ... c.c ... ... ... 

... ... ..f ... f.f ... f.f ... e.c ... c.. ... ...
... ... .X. ... .Xe ... eXe ... eX. ... .X. ... ...
... ... ... ... ... ... e.e ... ... ... ... ... ...

... ... ... ... ... ..e ... e.. ... ... ... ... ...
... ... ... ... ... .X. ... .X. ... ... ... ... ...
... ... ... ... ... ... ... ... ... ... ... ... ..."""


# The string representation of the graph.
# Each vertex has two possible vertexes above and below it, but to fit it in a rectangular grid this can't be capture.
# The "odd" rows exclude the right most vertex (see image below)
# The "even" rows exclude the left most vertex (see image below)
# The "even" rows are offset one to the left (see image below)
#
# E x x x x x x
#  x x x x x x E
# E x x x x x x
#  x x x x x x E
board_string_rep = """\
.......................................... 
................X.....X................... 
.................a...a.................... 
..................a.a.....................
.......X.....Xi...iXa...aX.....X..........
........i...i.i...j.j...a.a...b...........
.........i.i...i.j...j.a...a.b............ 
....Xh...hXi...iXj...jXk...kXb...bX....... 
.....h...g.l...l.l...j.k...k.k...b........ 
......h.g...l.l...l.j...k.k...k.b.........
.Xh...hXg...gXl...lXj...jXk...kXb...bX....
......h.g...g.l...d.d...d.c...c.b.........
.....h...g.g...l.d...d.d...c.c...b........ 
....Xh...hXg...gXd...dXd...dXc...cX....... 
.........f.f...f.f...f.e...c.c............ 
........f...f.f...f.f...e.c...c...........
.......X.....Xe...eXe...eX.....X..........
..................e.e.....................
.................e...e....................
................X.....X...................
.........................................."""

def subtract(a, b):
    return tuple(aa - bb for aa,bb in zip(a,b))

def add(a, b):
    return tuple(aa + bb for aa,bb in zip(a,b))

def cube_to_evenr_cord(cube_cord):
    x, y, z = cube_cord
    col = int(x + (z + (z & 1)) / 2)
    row = z
    return (col, row)

def evenr_to_cube_cord(evenr_cord):
    col, row = evenr_cord
    x = int(col - (row + (row & 1)) / 2)
    z = row
    y = -x - z
    return (x, y, z)

def is_even(num):
    return num % 2 == 0

def is_odd(num):
    return num % 2 == 1


# Class: HexVertex
# This class vertex which can have up to 6 edges in this orientation.
#            0   1
#             \ /
#            5-x-2
#             / \
#            4   3
# This also hold the coordinates of the vertex within a graph in offset
# and cubic coordinates. https://www.redblobgames.com/grids/hexagons/
class HexVertex:
    def __init__(self):
        self.edges = [None for i in range(0,6)]
        self.cube_cord = None
        self.offset_cord = None
        pass

    def __eq__(self, other):
        for i in range(6):
            if (self.edges[i] is None) != (other.edges[i] is None):
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def IsEmpty(self):
        return all([e is None for e in self.edges])

    def FlipVirtically(self, count=1):
        temp = self.edges[0]; self.edges[0] = self.edges[4]; self.edges[4] = temp
        temp = self.edges[1]; self.edges[1] = self.edges[3]; self.edges[3] = temp

    def Rotate(self, count=1):
        for i in range(count):
            self.edges.insert(0, self.edges[-1])
            del self.edges[-1]

    def Copy(self):
        v = HexVertex()
        for i in range(6):
            v.edges[i] = True if self.edges[i] is not None else None
            v.cube_cord = self.cube_cord
            v.offset_cord = self.offset_cord
        return v

    def __str__(self):
        def EdgeToStr(e):
            if e is None:
                return " "
            else:
                return "x"
        return "(%s)" % ",".join([EdgeToStr(e) for e in self.edges])
        
    def __repr__(self):
        return str(self)


def rotate_cube_position_around_center(center, pos):
    # 1. Create the vector from the current position to the center
    # 2. Rotate the vector. This is accomplished by [x, y, z] to [-z, -x, -y]
    # 3. Get the new position by adding the rotated vector to the center
    vector = subtract(pos, center)
    rotated_vector = (vector[2] * -1, vector[0] * -1, vector[1] * -1)
    new_pos = add(center, rotated_vector)
    return new_pos


# Class: HexGraph
# A graph of connected HexVertexes.
class HexGraph:
    def __init__(self, width, height, is_first_row_right_shifted = True):
        self.width = width
        self.height = height
        self.is_first_row_right_shifted = is_first_row_right_shifted
        self.grid = []
        for w in range(self.width):
            self.grid.append([HexVertex() for h in range(self.height)])        

    def __eq__(self, other):
        if self.width != other.width:
            return False
        if self.height != other.height:
            return False
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[x][y] != other.grid[x][y]:
                    return False
        return True

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        hash_sum = 0
        for x in range(self.width):
            for y in range(self.height):
                hash_str = "%d,%d: " % (x,y)
                hash_str += ",".join([str(e is None) for e in self.grid[x][y].edges])
                hash_sum += hash(hash_str)
        return hash_sum

    def ChangeEdgesToVertexes(self):
        # The graph vertex edges were initialized to True or None
        # Change the Trues into vertex references (this way we can do graph
        # searches)
        for x in range(self.width):
            for y in range(self.height):    
                odd = 1 if is_odd(y) else 0
                even = 1 if is_even(y) else 0
                #            0   1
                #             \ /
                #            5-x-2
                #             / \
                #            4   3
                for i in range(6):
                    if self.grid[x][y].edges[i] is not None:
                        if i == 0:
                            v_pos = (x - odd, y - 1)
                        if i == 1:
                            v_pos = (x + even, y - 1)
                        if i == 2:
                            v_pos = (x + 1, y)
                        if i == 3:
                            v_pos = (x + even, y + 1)
                        if i == 4:
                            v_pos = (x - odd, y + 1)
                        if i == 5:
                            v_pos = (x - 1, y)
                        self.grid[x][y].edges[i] = self.grid[v_pos[0]][v_pos[1]]

    def UpdateVertexCoordinates(self):
        for x in range(self.width):
            for y in range(self.height):
                self.grid[x][y].offset_cord = (x,y)
                self.grid[x][y].cube_cord = evenr_to_cube_cord((x,y))

    def Copy(self):
        graph = HexGraph(self.width, self.height, self.is_first_row_right_shifted)
        for x in range(graph.width):
            for y in range(graph.height):
                graph.grid[x][y] = self.grid[x][y].Copy()
        graph.ChangeEdgesToVertexes()
        return graph

    def Flip(self):
        # Return a flipped version of the graph
        graph = self.Copy()

        # We want an odd number of rows, so when the bottom row becomes the top, it's
        # goes from right-shifted to right-shifted.
        if is_even(graph.height):
            for col in graph.grid:
                col.append(HexVertex())
            graph.height += 1

        for x in range(graph.width):
            graph.grid[x].reverse()
            for v in graph.grid[x]:
                v.FlipVirtically()
        return graph

    def Rotate(self):
        # Rotate clockwise 60 degrees
        # Go though each of the vertexes and create a copy in a new position after rotating around the center

        self.UpdateVertexCoordinates()
        
        rotated_vertexes_by_offset = {}
        min_x = 99999
        min_y = 99999
        max_x = -99999
        max_y = -99999

        center = self.grid[0][0].cube_cord
        for x in range(self.width):
            for y in range(self.height):

                v = self.grid[x][y].Copy()
                v.cube_cord = rotate_cube_position_around_center(center, v.cube_cord)
                v.offset_cord = cube_to_evenr_cord(v.cube_cord)
                v.Rotate()  # Rotate the edges too
                if False and not v.IsEmpty():
                    print("Rotated", (x,y), "to", v.offset_cord)

                min_x = min((min_x, v.offset_cord[0]))
                min_y = min((min_y, v.offset_cord[1]))

                max_x = max((max_x, v.offset_cord[0]))
                max_y = max((max_y, v.offset_cord[1]))

                rotated_vertexes_by_offset[v.offset_cord] = v

        # Create a new grid to accommodate the new positions after rotating
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        right_shift = self.is_first_row_right_shifted if (min_y % 2 == 0) else (not self.is_first_row_right_shifted)
        if False:
            print("width", width, \
                  "heigth", height, \
                  "(min_x,max_x)", (min_x, max_x), \
                  "(min_y,max_y)", (min_y,max_y), \
                  "right", self.is_first_row_right_shifted)
            
        graph = HexGraph(width, height, right_shift)
        for y in range(height):
            for x in range(width):
                # We're shifting all points on the graph to all positive coordinates, but look them up by original coordinates
                original_cords = add((min_x, min_y), (x,y))
                if original_cords in rotated_vertexes_by_offset:
                    graph.grid[x][y] = rotated_vertexes_by_offset[original_cords]
        return graph

    def Trim(self):
        self.SqueezeUpAndRight()
        self.TrimRows()
        self.TrimColumns()

    def IsRowEmpty(self, y):
        for x in range(self.width):
            if not self.grid[x][y].IsEmpty():
                return False
        return True

    def SqueezeUpAndRight(self):

        # Shift stuff up and to the right into any empty rows
        empty_count = 0
        for y in range(self.height):
            if self.IsRowEmpty(y):
                empty_count += 1
            else:
                break

        #print("empty_count", empty_count)
        #self.PrintPretty()

        # Add columns to allow shifting to the right
        for i in range(empty_count):
            self.grid.append([HexVertex() for h in range(self.height)])
            self.width += 1

        # Shift up and to the right
        def ShiftUpAndRight():
            for y in range(0, self.height-1):
                self.grid[0][y] = HexVertex()
                for x in range(0, self.width-1):
                    if is_odd(y):
                        self.grid[x+1][y] = self.grid[x][y+1]  # up and right
                    else:
                        self.grid[x][y] = self.grid[x][y+1]  # just up
                    self.grid[x][y+1] = HexVertex()

        for i in range(empty_count):
            ShiftUpAndRight()

        #self.PrintPretty()


    def TrimColumns(self):
        new_grid = []
        for col in self.grid:
            if not all([c.IsEmpty() for c in col]):
                new_grid.append(col)
        self.grid = new_grid
        self.width = len(self.grid)

    def TrimRows(self):
        empty_row_indexes = []
        for y in range(self.height):
            is_empty_row = True
            for x in range(self.width):
                if not self.grid[x][y].IsEmpty():
                    is_empty_row = False
            if is_empty_row:
                empty_row_indexes.append(y)

        num_to_remove_from_top = 0
        for y in range(self.height):
            if y in empty_row_indexes:
                num_to_remove_from_top += 1
            else:
                break

        # Rows must be trimed 2-at-a-time to maintain the even-r or odd-r coordinate system
        if is_odd(num_to_remove_from_top):
            empty_row_indexes.pop(0)
        
        empty_row_indexes.reverse()  # Must delete these in reverse index order
        for empty_row_index in empty_row_indexes:
            for col in self.grid:
                del col[empty_row_index]
        self.height -= len(empty_row_indexes)

        if is_odd(num_to_remove_from_top):
            for x in range(self.width):
                if x == 0:
                    assert(self.grid[x][0].IsEmpty())
                else:
                    self.grid[x-1][0] = self.grid[x][0]


    def Print(self):
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                row += str(self.grid[x][y]) + " "
            print(row)

    def PrintPretty(self):
    
        def GetTok(scan, vertex):
            if scan == "up":
                truth = (vertex.edges[0] is not None, vertex.edges[1] is not None)
                if truth == (True, True):
                    return "\\ /"
                if truth == (True, False):
                    return "\\  "
                if truth == (False, True):
                    return "  /"
                if truth == (False, False):
                    return "   "
                    
            if scan == "mid":
                truth = (vertex.edges[5] is not None, vertex.edges[2] is not None)
                if truth == (True, True):
                    return "-x-"
                if truth == (True, False):
                    return "-x "
                if truth == (False, True):
                    return " x-"
                if truth == (False, False):
                    return " x "
                    
            if scan == "low":
                truth = (vertex.edges[4] is not None, vertex.edges[3] is not None)
                if truth == (True, True):
                    return "/ \\"
                if truth == (True, False):
                    return "/  "
                if truth == (False, True):
                    return "  \\"
                if truth == (False, False):
                    return "   "
            assert(False)

        for y in range(self.height):
            shift_even_check = 0 if self.is_first_row_right_shifted else 1
            offset = ""
            if y % 2 == shift_even_check:
                offset = "   "
            for scan in ["up", "mid", "low"]:
                row = offset
                for x in range(self.width):
                    row += GetTok(scan, self.grid[x][y]) + "   "
                print(row)


# Generate a hex graph from a string representation
def GenerateHexGraph(data, included_pieces):
    rows = data.split()
    rows = [r for r in rows if len(r) > 0]

    # The string representation is 3x3 blocks, so divide by 3
    assert (len(rows) % 3 == 0)
    grid_height = int(len(rows) / 3)
    for row in rows:
        assert(len(row) % 3 == 0)

    # The string representation is 3x3 blocks, and every other is for spacing only, so divide by 3 and 2
    grid_width = int(len(rows[0]) / 3 / 2)

    def UpdateVertex(vertex, row_name, tok):
        tok = list(tok)
        if row_name == "up":
            vertex.edges[0] = True if tok[0] in included_pieces else None
            vertex.edges[1] = True if tok[2] in included_pieces else None
        if row_name == "mid":
            vertex.edges[5] = True if tok[0] in included_pieces else None
            vertex.edges[2] = True if tok[2] in included_pieces else None
        if row_name == "low":
            vertex.edges[4] = True if tok[0] in included_pieces else None
            vertex.edges[3] = True if tok[2] in included_pieces else None
        
    graph = HexGraph(grid_width, grid_height)
    grid = graph.grid

    for y in range(grid_height):
        for x in range(grid_width):

            # The info is in a block 3 lines high
            first_row = y * 3
            string_rows =  range(first_row, first_row + 3)

            # The info is in a block 3 characters wide, followed by 3 characters used for spacing only
            offset = 3 if y % 2 == 0 else 0
            left = (x * 3 * 2) + offset
            right = left + 3
            string_cols = range(left, right)

            for row in string_rows:
                for col in string_cols:
                    row_name = ["up", "mid", "low"][row - first_row]
                    if False:
                        rowDebug = list(rows[row])
                        rowDebug.insert(left, "[")
                        rowDebug.insert(right+1, "]")
                        rowDebug = "".join(rowDebug)
                        if False:
                            print(x,y, "row", row, "col", col, row_name, "string_rows", string_rows, "string_cols", string_cols, rowDebug)
                    UpdateVertex(grid[x][y], row_name, rows[row][left:right])
    graph.ChangeEdgesToVertexes()
    graph.UpdateVertexCoordinates()    
    return graph

