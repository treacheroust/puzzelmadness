import re

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

"""\
...........a..a...........
............aa............
.........i..ia..a.........
.....i..ii..jj..aa..b.....
......ii..ij..ja..ab......
...h..hi..ij..jk..kb..b...
...h..gl..ll..jk..kk..b...
....hg..ll..lj..kk..kb....
.h..hg..gl..lj..jk..kb..b.
....hg..gl..dd..dc..cb....
...h..gg..ld..dd..cc..b...
...h..hg..gd..dd..dc..c...
......ff..ff..fe..cc......
.....f..ff..ff..ec..c.....
.........e..ee..e.........
............ee............
...........e..e..........."""

grid_data_pieces = """\
     aa     
     i a    
  iiijjaab   
  h i j k b 
 hgllljkkkb 
 h g l j k b 
 hggldddccb 
  h g d d c  
  fffffecc  
     e e    
     ee
"""

grid_data_orientation = r"""
     \/     
     - -       
  \/\/\/\/   
  - - - - -
 \/\/\/\/\/ 
 - - - - - -
 /\/\/\/\/\ 
  - - - - -  
  /\/\/\/\  
     - -    
     /\
"""

class Matrix:
    def __init__(self, string):
        self.rows = string.split("\n")
        self.rows = [r.rstrip() for r in self.rows]
        self.rows = [r for r in self.rows if len(r) > 0]
        self.height = len(self.rows)
        self.width = max([len(r) for r in self.rows])
        for i in range(0, len(self.rows)):
            while len(self.rows[i]) < self.width:
               self.rows[i] += " "               
        self.columns = []
        for columnIndex in range(0,self.width):
            column = [row[columnIndex] for row in self.rows]
            self.columns.append(column)
            
    def get(self, x,y):
        return self.rows[y][x]
        
    def __str__(self):
        out = ""
        out += "height is %d\n" % self.height
        out += "width is %d\n" % self.width
        for row in self.rows:
            out += row + "\n"
        return out

class Piece:
    def __init__(self, letter, string):
        self.letter = letter
        self.string = string
        
pieces = []


def FindPieces():
    def FindPiece(piece_letter):
        piece_matrix = Matrix(grid_data_pieces)
        orient_matrix = Matrix(grid_data_orientation)
        out = ""
        for y in range(0, piece_matrix.height):
            line = ""
            found = False
            for x in range(0, piece_matrix.width):
                if piece_matrix.get(x,y) == piece_letter:
                    orient = orient_matrix.get(x,y)
                    if orient == " ":
                        print "unexpected", orient, x,y
                    line += orient_matrix.get(x,y)
                    found = True
                else:
                    line += " "
            if found:
                out += line + "\n"
        pieces.append(Piece(piece_letter, out))
        
    for letter in "abcdefghijkl":
        FindPiece(letter)

FindPieces()        
for p in pieces:
    print 'Piece "%s"' % (p.letter,)
    print p.string
