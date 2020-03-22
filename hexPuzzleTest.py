# This is code used to test hexPuzzle.py

from hexPuzzle import *


# Print out the board and all the pieces
all_pieces = "a b c d e f g h i k j l".split()
if False:
    graph = GenerateHexGraph(board_string_rep, all_pieces)
    graph.PrintPretty()

    for piece in all_pieces:
        print "Piece", piece
        graph = GenerateHexGraph(board_string_rep, [piece])
        graph.Trim()
        graph.PrintPretty()


# Trim and print out a single piece
if False:
    graph = GenerateHexGraph(board_string_rep, ["b"])
    graph.Print()
    graph.PrintPretty()
    graph.TrimColumns()
    graph.Print()
    graph.PrintPretty()
    graph.TrimRows()
    graph.Print()
    graph.PrintPretty()


# Test vertex rotation
if False:
    graph = HexGraph(3, 3)
    graph.grid[1][1].edges[0] = True
    graph.grid[1][1].edges[4] = True
    graph.PrintPretty()
    for i in range(6):
        graph.grid[1][1].Rotate()
        graph.PrintPretty()

# Rotate a single piece
if False:
    graph = None
    for i in range(7):
        print "-------------", i
        if graph is None:
            graph = GenerateHexGraph(board_string_rep, ["e"])
        else:
            graph = graph.Rotate()
        graph.PrintPretty()
        graph.Trim()
        graph.PrintPretty()

# Fully rotate each piece
if False:
    for piece in all_pieces:
        print "Piece", piece
        graph = GenerateHexGraph(board_string_rep, [piece])
        graph.Trim()
        graph.PrintPretty()
        for i in range(6):
            graph = graph.Rotate()
        graph.Trim()
        graph.PrintPretty()

# Flip each piece
if True:
    for piece in all_pieces:
    #for piece in ['k']:
        print "Piece", piece
        graph = GenerateHexGraph(board_string_rep, [piece])
        graph.Trim()
        graph.PrintPretty()
        #graph.Print()
        print "  flipped"
        graph = graph.Flip()
        graph.Trim()
        graph.PrintPretty()
        #graph.Print()

# Look for pieces that are wide or tall after rotation and trim
if False:
    graphs = []
    for piece in all_pieces:
        print "Piece", piece
        graph = GenerateHexGraph(board_string_rep, [piece])
        graph.Trim()
        graphs.append(graph)

        for i in range(6):
            graph = graph.Rotate()
            graph.Trim()
            graphs.append(graph)

    tallest = max(graphs, key=lambda g: g.height)
    widest = max(graphs, key=lambda g: g.width)

    for graph in graphs:
        if graph.height == tallest.height or graph.width == widest.width:
            print "------------------"
            graph.PrintPretty()
