import re

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

#Piece "a"
r"""
\/      /        
  -     -
  /\    \       -     
        -     \/\      \/
        /     -         -
                        /\
"""

#Piece "b"
r"""
         /         
          -        -
          /        \
           -       -
          \       /\
                              
"""
#Piece "c"
r"""
        \/
          -
        /\
"""
#Piece "d"
r"""
     /\/
      - -
"""
#Piece "e"
r"""
       \
     - -
     /\
"""
#Piece "f"
r"""
  /\/\/
"""
#Piece "g"
r"""
  /
   -
  \/
    -
"""
#Piece "h"
r"""
  -
 \
 -
 /
  -
"""
#Piece "i"
r"""
     -
  \/\
    -
"""
#Piece "j"
r"""
     /\
      -
      /
       -
"""
#Piece "k"
"""
        -
       \/\
         -
"""
#Piece "l"
r"""
   \/\
     -
    \
"""

# This class allows you to treat a multi-line
# string as a two-dimentional matrix.
class Matrix:
    def __init__(self, string):
        self.rows = string.split("\n")
        #self.rows = [r.rstrip() for r in self.rows]
        self.rows = [r for r in self.rows if len(r) > 0]
        self.height = len(self.rows)
        self.width = max([len(r) for r in self.rows])
        for i in range(0, len(self.rows)):
            while len(self.rows[i]) < self.width:
               self.rows[i] += " "               
        self.make_columns()
        
    def make_columns(self):
        self.columns = []
        for columnIndex in range(0,self.width):
            column = "".join([row[columnIndex] for row in self.rows])
            self.columns.append(column)
            
    def get(self, x,y):
        return self.rows[y][x]
        
    def set(self, x,y, char):
        rowList = list(self.rows[y])
        rowList[x] = char
        self.rows[y] = ''.join(rowList)

    def trim(self):
        # remove empty rows
        def NotEmpty(r):
            r = r.replace(" ", "")
            r = r.replace(".", "")
            return len(r) > 0
        self.rows = [r for r in self.rows if NotEmpty(r)]
        self.height = len(self.rows)
        self.make_columns()
        
        # remove empty columns
        for left in range(0, self.width):
            if NotEmpty(self.columns[left]):
                break
        for right in range(self.width-1,0,-1):
            if NotEmpty(self.columns[right]):
                break
        self.rows = [r[left:right+1] for r in self.rows]
        self.width = max([len(r) for r in self.rows])
        
    def __str__(self):
        out = ""
        out += "height is %d\n" % self.height
        out += "width is %d\n" % self.width
        for row in self.rows:
            out += row + "\n"
        return out

test = r"""
 \
  \
   \    
"""
def rotate(m):
    blank = ""
    for y in range(0, m.height+10):
        for x in range(0, m.width+10):
            blank += " "
        blank += "\n"
    new = Matrix(blank)
    
    #print "input", m
    #print "blank", new
    xshift = 0
    yshift = 0
    for y in range(0, m.height):
        for x in range(0, m.width):
            upper =  y < m.height/2
            char = m.get(x,y)
            #print "char", char, "upper", upper

            if True:
                if char == "\\":
                    new.set((x+5)+xshift+1,(y+5)+yshift, "/")
                    xshift += -1
                if char == "/":
                    new.set((x+5)+xshift,(y+5)+yshift+1, "-")
                    yshift += 1
                    xshift += -1
                if char == "-":
                    new.set((x+5)+xshift,(y+5)+yshift+1, "\\")
                    yshift += 1
                    xshift += -1
                    
            else:
                if char == "\\":
                    if upper:
                        new.set((x+5)+1,(y+5), "/")
                    else:
                        new.set((x+5)-1,(y+5), "/")
                        
                if char == "/":
                    if upper:
                        new.set((x+5)+1,(y+5)+1, "-")
                    else:
                        new.set((x+5)-1,(y+5)-1, "-")
                    
                if char == "-":
                    if upper:
                        new.set((x+5),(y+5)+1, "\\")
                    else:
                        new.set((x+5),(y+5)+1, "\\")
            #print new
    new.trim()                
    #print "output", new
    return new
    
print test

m = Matrix(test)    
for i in range(0,7):
    m = rotate(m)
    if True: #i % 6 == 6:
        print i, m

exit(0)


# This class represents a puzzle piece.         
# There are 12 possible ways the piece can be oriented.
# Two sides with each side can be rotated 6 times.
class Piece:
    def __init__(self, letter, string):
        self.letter = letter
        self.string = string
        self.orientations = None
        
        
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

    
    
    
    
#-----------------------------------    
# Reference
#-----------------------------------    

# Each rotation is 60 degrees:
# '\' to '/' 
#
# '/' to ' '
#        '-'
#
# '-' to ' '
#        '\'
#
# '\' to '/'      
#
#        '-'  
# '/' to ' '
#
#        '\'
# '-' to ' '
# 
# ~~~~~~~~~~~~~~~~~~~~
#
# /\/\/   -
#         /     \   
#         -     -   /\/\/ 
#         /     \
#         -     -
#               \
#
    
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

# This is a more compact representation where the
# Vertexes are not shown.  But this is not used as
# we can further simplify things.
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

    
    
    
    
    
    