# This picture describes the board and all the pieces
# The piece are reprsented by letters.  Vertexes are
# represented by X's.  This picture is just for reference
# a simpler representation can be acheived.
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


# Class: HexVertex
# This class vertex which can have up to 6 edges in this orientation.
#            0   1
#             \ /
#            5-x-2
#             / \
#            4   3 
class HexVertex:
    def __init__(self):
        self.edges = [None for i in range(0,6)]
        pass
        
    def __str__(self):
        def EdgeToStr(e):
            if e is None:
                return " "
            else:
                return "x"
        return "(%s)" % ",".join([EdgeToStr(e) for e in self.edges])
        
    def __repr_(self):
        return str(self)
        
# Class: HexGraph
# A graph of connected HexVertexes.
# Each vertex has two possible vertexes above and below it, but to fit it in a rectangular grid this can't be capture.
# The "odd" rows exclude the right most vertex (see image below)
# The "even" rows exclude the left most vertex (see image below)
# The "even" rows are offset one to the left (see image below)
# 
# E x x x x x x 
#  x x x x x x E
# E x x x x x x 
#  x x x x x x E
#
class HexGraph:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = []
        for w in range(self.width):
            self.grid.append([HexVertex() for h in range(self.height)])        
        
    def Print(self):
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                row += str(self.grid[x][y]) + " "
            print row
            
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
            offset = ""
            if y % 2 == 0:
                offset = "   "
        
            for scan in ["up", "mid", "low"]:
                row = offset
                for x in range(self.width):
                    row += GetTok(scan, self.grid[x][y]) + "   "                    
                print row

            
data = """\
....................................... 
................X.....X................ 
.................a...a................. 
..................a.a..................
.......X.....Xi...iXa...aX.....X.......
........i...i.i...j.j...a.a...b........
.........i.i...i.j...j.a...a.b......... 
....Xh...hXi...iXj...jXk...kXb...bX.... 
.....h...g.l...l.l...j.k...k.k...b..... 
......h.g...l.l...l.j...k.k...k.b......
.Xh...hXg...gXl...lXj...jXk...kXb...bX.
......h.g...g.l...d.d...d.c...c.b......
.....h...g.g...l.d...d.d...c.c...b..... 
....Xh...hXg...gXd...dXd...dXc...cX.... 
.........f.f...f.f...f.e...c.c......... 
........f...f.f...f.f...e.c...c........
.......X.....Xe...eXe...eX.....X.......
..................e.e..................
.................e...e.................
................X.....X................
......................................."""

data = """\
....................................... 
................X.....X................ 
.................a...a................."""


data = """\
...a.a 
....x. 
...a..
..a...
.x....
a....."""
            
# Generate a hex graph from a string representation
def GenerateHexGraph(data):
    rows = data.split();
    rows = [r for r in rows if len(r) > 0]
    height = len(rows) / 3; 
    assert(len(rows) % 3 == 0)
    for row in rows:
        assert(len(row) % 3 == 0)
    width = len(rows[0]) / 3
    
    def UpdateVertex(vertex, scan, tok, line):
        if lineNum > 0:
            print "["+tok +"]"+scan, line
        tok = list(tok)
        if scan == "up":
            vertex.edges[0] = True if tok[0] != "." else None
            vertex.edges[1] = True if tok[2] != "." else None
        if scan == "mid":
            vertex.edges[5] = True if tok[0] != "." else None
            vertex.edges[2] = True if tok[2] != "." else None
        if scan == "low":
            vertex.edges[4] = True if tok[0] != "." else None
            vertex.edges[3] = True if tok[2] != "." else None
        
    graph = HexGraph(width, height)
    grid = graph.grid
    lineNum = 0
    while lineNum < len(rows):
        y = lineNum / 3
        offset = 0
        if y % 2 == 0:
            offset = 3
            
        for scan in ["up", "mid", "low"]:
            for column in range(width):
                x = column / 3
                if offset > 0 and x == width-1:
                    continue
                if (x+offset) % 2 == 0:
                    continue
                left = offset + (x*3)
                right = left+3
                #print left, right, rows[y]                
                UpdateVertex(grid[x][y], scan, rows[lineNum][left:right], rows[lineNum])
            lineNum += 1
                            
    return graph
    
    
#graph = HexGraph(4,5)
graph = GenerateHexGraph(data)
graph.Print()
graph.PrintPretty()