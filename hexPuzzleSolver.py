# This is the solver for the hex puzzle

from hexPuzzle import *
import tkinter as tk
import collections
import threading
import time
import random
import copy
import os.path
from PIL import Image   # pip install Pillow to get the PIL package, then ghostscript
                        # also needs to be installed, and it's bin directory added to the path


color_piece = "#5A2D0D"  # dark brown
color_piece_border = "black"
color_bg = "grey"


def DrawHexEdge(edge, canvas, row_height, padding, **kwargs):

    line_width = kwargs.get("line_width", 4)
    line_color = kwargs.get("line_color", "black")
    capstyle = kwargs.get("capstyle", tk.ROUND)
    xstretch = kwargs.get("xstretch")
    pixel_shift = kwargs.get("pixel_shift", (0,0))
    graph_offset = kwargs.get("graph_offset", (0, 0))
    tags = kwargs.get("tags")

    right_shift = int(padding * xstretch) + pixel_shift[0]
    down_shift = padding + pixel_shift[1]
    row_width = int(row_height * xstretch)

    def pos_to_pixel_pos(pos):
        x, y = pos
        if is_even(y):
            x += graph_offset[0] - (graph_offset[1] // 2)
        else:
            x += graph_offset[0] - ((graph_offset[1]+1) // 2)
        y += graph_offset[1]
        offset = 0
        if is_even(y):
            offset = row_width // 2
        return (right_shift + offset + x * row_width,
                down_shift + row_height * y)

    def draw_line_helper(x, y, x2, y2):
        canvas.create_line(x, y,
                           x2, y2,
                           fill=line_color,
                           width=line_width,
                           capstyle=capstyle,
                           tags=tags)
    x, y = pos_to_pixel_pos(edge[0])
    x2, y2 = pos_to_pixel_pos(edge[1])
    draw_line_helper(x, y, x2, y2)


def DrawHexGraph(graph, canvas, row_height, padding, **kwargs):

    line_width = kwargs.get("line_width", 4)
    line_color = kwargs.get("line_color", "black")
    capstyle = kwargs.get("capstyle", tk.ROUND)
    draw_grid = kwargs.get("draw_grid", False)
    xstretch = kwargs.get("xstretch")
    border_width = kwargs.get("border_width", 0)
    border_color = kwargs.get("border_color", "black")
    highlight = kwargs.get("highlight", None)
    vertex_highlights = kwargs.get("vertex_highlights", [])
    vertex_highlight_color = kwargs.get("vertex_highlight_color", "yellow")
    vertex_highlight_size = kwargs.get("vertex_highlight_size", 10)
    graph_offset = kwargs.get("graph_offset", (0, 0))
    tags = kwargs.get("tags")

    if vertex_highlights == "all":
        vertex_highlights = []
        for x in range(graph.width):
            for y in range(graph.height):
                vertex_highlights.append((x,y))

    # Draw a grid
    if draw_grid:
        for y in range(0, 1000, 20):
            canvas.create_line(0, y, 1000, y, width=1, fill="red", capstyle=capstyle, tags=tags)
            canvas.create_line(y, 0, y, 1000, width=1, fill="red", capstyle=capstyle, tags=tags)

    right_shift = int(padding * xstretch)
    down_shift = padding
    row_width = int(row_height * xstretch)

    def pos_to_pixel_pos(pos):
        x, y = pos
        if is_even(y):
            x += graph_offset[0] - (graph_offset[1] // 2)
        else:
            x += graph_offset[0] - ((graph_offset[1]+1) // 2)
        y += graph_offset[1]
        offset = 0
        if is_even(y):
            offset = row_width // 2
        return (right_shift + offset + x * row_width,
                down_shift + row_height * y)

    draw_list = ["highlight", "border", "line"]
    if highlight is None:
        draw_list.remove("highlight")
    if border_width <= 0:
        draw_list.remove("border")

    for draw_this in draw_list:
        for y in range(graph.height):
            for x in range(graph.width):
                pixel_x, pixel_y = pos_to_pixel_pos((x, y))
                if False:
                    print("(x,y)", (x,y), "(pixel_x, pixel_y)", (pixel_x, pixel_y))
                    canvas.create_line(pixel_x, pixel_y, pixel_x, pixel_y, width=4, fill="red", capstyle=capstyle, tags=tags)

                #            0   1
                #             \ /
                #            5-x-2
                #             / \
                #            4   3
                def draw_line_helper(x, y, x2, y2):
                    if draw_this == "highlight":
                        canvas.create_rectangle(0, 0,
                                                100, 100,
                                                fill=highlight,
                                                tags=tags)
                    if draw_this == "border":
                        canvas.create_line(x, y,
                                           x2, y2,
                                           fill=border_color,
                                           width=border_width + line_width,
                                           capstyle=capstyle,
                                           tags=tags)
                    if draw_this == "line":
                        canvas.create_line(x, y,
                                           x2, y2,
                                           fill=line_color,
                                           width=line_width,
                                           capstyle=capstyle,
                                           tags=tags)

                if graph.grid[x][y].edges[0] is not None:
                    draw_line_helper(pixel_x, pixel_y, pixel_x - row_width // 2, pixel_y - row_height)
                if graph.grid[x][y].edges[1] is not None:
                    draw_line_helper(pixel_x, pixel_y, pixel_x + row_width // 2, pixel_y - row_height)
                if graph.grid[x][y].edges[2] is not None:
                    draw_line_helper(pixel_x, pixel_y, pixel_x + row_width // 2, pixel_y)
                if graph.grid[x][y].edges[3] is not None:
                    draw_line_helper(pixel_x, pixel_y, pixel_x + row_width // 2, pixel_y + row_height)
                if graph.grid[x][y].edges[4] is not None:
                    draw_line_helper(pixel_x, pixel_y, pixel_x - row_width // 2, pixel_y + row_height)
                if graph.grid[x][y].edges[5] is not None:
                    draw_line_helper(pixel_x, pixel_y, pixel_x - row_width // 2, pixel_y)

    for vertex in vertex_highlights:
        pixel_x, pixel_y = pos_to_pixel_pos(vertex)
        canvas.create_line(pixel_x, pixel_y,
                           pixel_x, pixel_y,
                           fill=vertex_highlight_color,
                           width=vertex_highlight_size,
                           capstyle=capstyle,
                           tags=tags)




        # This shows what's going on visually while the AI is solving the puzzle
class SolverGui:

    XSTRETCH = 315.0 // 270.0
    BOARD_HEIGHT = 476
    BOARD_WIDTH = int(BOARD_HEIGHT * XSTRETCH)
    PIECE_HEIGHT = 48
    PIECE_WIDTH = int(PIECE_HEIGHT * XSTRETCH)
    UPDATE_PERIOD_MS = 100

    def __init__(self, find_solutions_function, find_solutions_args):
        self.piece_row_height = 0
        self.board_row_height = 0
        self.update_lock = threading.Lock()
        self.update_work = []

        self.ui = tk.Tk()
        self.ui.title("Hex Puzzle Solver")

        # Create board view pane
        self.board_pane = tk.Frame(bg="dark grey")
        self.board_pane.grid(column=0, row=0, sticky=tk.N)

        if True:  # row 0
            board_height = SolverGui.BOARD_HEIGHT
            board_width = SolverGui.BOARD_WIDTH
            self.board = tk.Canvas(self.board_pane, height=board_height, width=board_width, bg=color_bg, borderwidth=0)
            self.board.grid(column=0, row=0)

        # Create info pane
        self.info_pane = tk.LabelFrame(self.board_pane, text="", bg=color_bg)
        self.info_pane.grid(column=0, row=1, sticky=tk.NSEW)

        if True:  # row 0
            def find_solutions_function_internal():
                find_solutions_function(find_solutions_args, self)
            button = tk.Button(self.info_pane, text="Find Solutions", command=find_solutions_function_internal)
            button.grid(column=0, row=0, sticky=tk.N, padx=5, pady=5)

            self.status = tk.StringVar()
            self.status.set("")
            self.status_label = tk.Label(self.info_pane, textvariable=self.status, bg="grey", font=("Arial", 8), width=60)
            self.status_label.grid(column=1, row=0, padx=5, pady=5)

        if True:  # row 1
            tk.Label(self.info_pane, text="Verbosity", bg="grey").grid(column=0, row=1, padx=5, pady=5)
            self.verbosity = tk.Scale(self.info_pane, from_=0, to=7, orient=tk.HORIZONTAL, length=360)
            self.verbosity.set(0)
            self.verbosity.grid(column=1, row=1, padx=5, pady=5)

        if True:  # row 2
            tk.Label(self.info_pane, text="Speed", bg="grey").grid(column=0, row=2, padx=5, pady=5)
            self.speed_scale = tk.Scale(self.info_pane, from_=100, to=0, orient=tk.HORIZONTAL, length=360)
            self.speed_scale.set(50)
            self.speed_scale.grid(column=1, row=2, padx=5, pady=5)

        # Create pieces section
        self.pieces_pane = tk.LabelFrame(text="")
        self.pieces_pane.grid(column=1, row=0, rowspan=2, sticky=tk.N)

        # Add a canvas for each rotation and flip of each piece
        piece_height = SolverGui.PIECE_HEIGHT
        piece_width = SolverGui.PIECE_WIDTH
        self.pieces = {}
        for y in range(12):
            for x in range(12):
                c = tk.Canvas(self.pieces_pane, height=piece_height, width=piece_width, bg=color_bg, borderwidth=0)
                c.grid(column=x, row=y)
                self.pieces[(x, y)] = c

    def AddUiUpdate(self, work):
        with self.update_lock:
            self.update_work.append(work)


    def DrawPiece(self, piece_graph, **kwargs):
        def draw_func():
            self.pieces[piece_graph.gui_pos].delete("all")
            self.pieces[piece_graph.gui_pos].configure(bg=color_bg)
            DrawHexGraph(piece_graph,
                         self.pieces[piece_graph.gui_pos],
                         self.piece_row_height,
                         padding,
                         line_width=3,
                         border_width=2,
                         border_color="black",
                         xstretch=SolverGui.XSTRETCH,
                         line_color=color_piece,
                         ** kwargs)
        self.AddUiUpdate(draw_func)

    def SetStatus(self, string):
        def set_func():
            self.status.set(string)
        self.AddUiUpdate(set_func)

    def ClearBoard(self, tags="all"):
        def clear_func():
            self.board.delete(tags)
        self.AddUiUpdate(clear_func)

    def DrawBoard(self, board_graph, **kwargs):
        def draw_func():
            kwargs["line_color"] = kwargs.get("line_color", "dark grey")
            kwargs["line_width"] = kwargs.get("line_width", 16)
            kwargs["border_color"] = kwargs.get("border_color", "black")
            kwargs["border_width"] = kwargs.get("border_width", 7)
            DrawHexGraph(board_graph,
                        self.board,
                        self.board_row_height,
                        self.board_padding,
                        xstretch=SolverGui.XSTRETCH,
                        **kwargs)
        self.AddUiUpdate(draw_func)

    def DrawEdge(self, edge, **kwargs):
        def draw_func():
            kwargs["line_color"] = kwargs.get("line_color", "red")
            DrawHexEdge(edge,
                        self.board,
                        self.board_row_height,
                        self.board_padding,
                        xstretch=SolverGui.XSTRETCH,
                        **kwargs)
        self.AddUiUpdate(draw_func)

    def Run(self):
        # When an external thread wants to update the ui, then it adds a callable to the update_work array.
        # The ui periodically checks if there's work to do
        def update_ui_periodically():
            with self.update_lock:
                for work in self.update_work:
                    work()
                self.update_work = []
                self.ui.after(solverGui.UPDATE_PERIOD_MS, update_ui_periodically)

        update_ui_periodically()
        self.ui.mainloop()


# Calculate the row height that would fill a certain canvas height for the given graph
def GetRowHeightToFitCanvas(pixel_height, graph_rows, pad, fits_perfect=[False]):
    pixel_height = pixel_height - (pad * 2)
    pixels_between_rows = pixel_height // (graph_rows - 1)
    row_height = pixels_between_rows
    actual_pixel_height = pixels_between_rows * (graph_rows - 1)  # Account for integer rounding
    fits_perfect[0] = True
    if pixel_height != actual_pixel_height:
        fits_perfect[0] = False
        #print("pixel_height", pixel_height, "!=" "actual_pixel_height", actual_pixel_height)
    if False:
        print("pixel_height", pixel_height, "pad", pad, graph_rows, "graph_rows", graph_rows, "hex_height", row_height)
    return row_height


# This is the logic to find solutions to the puzzle.  It can use the solveGui to visualize progress.
def FindSolutions(board_graph_external, piece_graphs, gui):

    def adjust_pos(pos, graph_offset):
        # Adjust the postion by the given offset.
        # This is more tricky than it sounds because with a hex grid, each vertical
        # movement also needs a 0.5 units of horizontal movement
        x, y = pos
        if is_even(y):
            x += graph_offset[0] - (graph_offset[1] // 2)
        else:
            x += graph_offset[0] - ((graph_offset[1] + 1) // 2)
        y += graph_offset[1]
        return (x, y)


    class Finder:
        def __init__(self, board_graph, piece_graphs, gui):
            self.board_graph_original = board_graph
            self.piece_graphs = piece_graphs
            self.gui = gui
            self.available_pieces = []
            self.placed_pieces = {}
            self.max_placed_pieces = 0
            self.board_graph = None
            self.board_graph_previous = []
            self.available_pieces_previous = []
            self.placed_pieces_previous = []

            self.continuously_search_for_solutions = True
            self.gui_sleep_time = 0.2
            self.gui_highlight_piece_sleep_time = 0.0
            self.gui_show_each_try = False
            self.gui_show_removals = False
            self.gui_show_stranded_tree_walk = False
            self.gui_show_stranded = False
            self.gui_show_piece_highlights = True
            self.gui_show_target_vertex = True
            self.gui_show_placed_pieces = True


        def gui_update_settings(self):
            verbosity = self.gui.verbosity.get()
            self.gui_show_each_try = verbosity >= 7
            self.gui_show_removals = verbosity >= 6
            self.gui_show_stranded_tree_walk = verbosity >= 5
            self.gui_show_stranded = verbosity >= 4
            self.gui_show_piece_highlights = verbosity >= 3
            self.gui_show_target_vertex = verbosity >= 2
            self.gui_show_placed_pieces = verbosity >= 1

            if False:
                # Linear speed
                #  y = mx + b
                top_speed = 0.02
                slow_speed = 5.0
                m = (top_speed - slow_speed)/100.0
                b = 5.0
                x = self.gui.speed_scale.get()
                new_sleep_time = m * x + b
            else:
                # Quadratic (MyCurveFit.com)
                x = 100 - self.gui.speed_scale.get()
                new_sleep_time = 0.01 - 0.0023 * x + 0.000522 * (x ** 2)

            if new_sleep_time != self.gui_sleep_time:
                print("new sleep time is", new_sleep_time)
                self.gui_sleep_time = new_sleep_time

        def gui_set_status(self, string):
            self.gui.SetStatus(string)

        def gui_target_vertex(self, vertex_pos, color="black", delay_multiplier=1):
            if self.gui_show_target_vertex:
                self.gui.SetStatus("target vertex (%d, %d)" % vertex_pos)
                self.gui.ClearBoard("target_vertex")
                self.gui.DrawBoard(HexGraph(1, 1), vertex_highlights=[vertex_pos], vertex_highlight_color=color, tags="target_vertex")
                time.sleep(self.gui_sleep_time * delay_multiplier)

        def gui_try_piece_on_board(self, piece_graph, offset, delay_multiplier=1):
            if self.gui_show_each_try:
                self.gui_update_settings()
                if self.gui_show_each_try:
                    self.gui.DrawBoard(piece_graph,
                                       graph_offset=offset,
                                       line_color=color_piece,
                                       tags="piece_on_board")
                    time.sleep(self.gui_sleep_time * delay_multiplier)


        def gui_clear_try_piece_on_board(self, delay_multiplier=1):
            if self.gui_show_each_try:
                self.gui.ClearBoard("piece_on_board")
                time.sleep(self.gui_sleep_time * delay_multiplier)

        def gui_placed_piece(self, piece_graph, offset, delay_multiplier=1):
            if self.gui_show_placed_pieces:
                self.gui.DrawBoard(piece_graph,
                                   graph_offset=offset,
                                   line_color=piece_graph.color,
                                   tags="placed_piece")
                time.sleep(self.gui_sleep_time * delay_multiplier)

        def gui_redraw_placed_pieces(self):
            if self.gui_show_placed_pieces:
                self.gui.ClearBoard("placed_piece")
                for piece_id, (piece_graph, offset) in self.placed_pieces.items():
                    self.gui_placed_piece(piece_graph, offset, 0)

        def gui_force_redraw_placed_pieces(self):
            old = self.gui_show_placed_pieces
            self.gui_show_placed_pieces = True
            self.gui_redraw_placed_pieces()
            self.gui_show_placed_pieces = old

        def gui_clear_placed_pieces(self, delay_multiplier=1):
            if self.gui_show_placed_pieces:
                self.gui.ClearBoard("placed_piece")
                time.sleep(self.gui_sleep_time * delay_multiplier)

        def gui_highlight_piece(self, piece_graph, color, delay_multiplier=1):
            if self.gui_show_piece_highlights:
                self.gui.DrawPiece(piece_graph, highlight=color)
                time.sleep(self.gui_highlight_piece_sleep_time * delay_multiplier)

        def gui_highlight_remaining_board(self):
            if self.gui_show_removals:
                self.gui.DrawBoard(self.board_graph,
                                   line_color="light yellow",
                                   tags="board_highlight")
                time.sleep(2)
                self.gui.ClearBoard("board_highlight")
                time.sleep(.1)

        def start_over(self):
            self.gui_clear_placed_pieces()
            self.available_pieces = []
            for piece_id, graphs in self.piece_graphs.items():
                for graph in graphs:
                    self.available_pieces.append(graph)
            self.placed_pieces = {}
            self.board_graph = self.board_graph_original.Copy()
            self.board_graph_previous = []
            self.available_pieces_previous = []
            self.placed_pieces_previous = []

            self.gui_highlight_remaining_board()

        def get_vertex_with_fewest_edges(self):
            v = None
            min_edges = 99999
            for x in range(self.board_graph.width):
                for y in range(self.board_graph.height):
                    edges = len([e for e in self.board_graph.grid[x][y].edges if e is not None])
                    if edges > 0:
                        if edges < min_edges:
                            min_edges = edges
                            v = (x, y)
            return v

        def subtract_piece_from_board(self, piece_graph, graph_offset):
            for x in range(piece_graph.width):
                for y in range(piece_graph.height):

                    piece_vertex = piece_graph.grid[x][y]
                    if piece_vertex.IsEmpty():
                        continue

                    board_x, board_y = adjust_pos((x, y), graph_offset)
                    if board_x < 0 or board_x >= self.board_graph.width:
                        continue
                    if board_y < 0 or board_y >= self.board_graph.height:
                        continue
                    board_vertex = self.board_graph.grid[board_x][board_y]
                    assert(board_vertex is not None)

                    for i in range(len(piece_vertex.edges)):
                        if piece_vertex.edges[i] is not None and board_vertex.edges[i] is not None:

                            if self.gui_show_removals:
                                self.gui.DrawEdge((board_vertex.offset_cord, board_vertex.edges[i].offset_cord), tags="removed")
                            pointed_to_vertex = board_vertex.edges[i]
                            if pointed_to_vertex is not None:
                                #print("subtracting edge", i, "from", piece_vertex.offset_cord, "affecting", pointed_to_vertex.offset_cord)
                                for k in range(len(pointed_to_vertex.edges)):
                                    if pointed_to_vertex.edges[k] is not None:
                                        if pointed_to_vertex.edges[k].offset_cord == board_vertex.offset_cord:
                                            pointed_to_vertex.edges[k] = None
                            board_vertex.edges[i] = None
            if self.gui_show_removals:
                time.sleep(3)
                self.gui.ClearBoard("removed")
                time.sleep(1)
    
        def fits_on_board_with_offset(self, piece_graph, board_graph, vertex_pos, graph_offset):
            vertex_covered = False
            for x in range(piece_graph.width):
                for y in range(piece_graph.height):

                    piece_vertex = piece_graph.grid[x][y]
                    if piece_vertex.IsEmpty():
                        continue

                    board_x, board_y = adjust_pos((x, y), graph_offset)
                    if board_x < 0 or board_x >= self.board_graph.width:
                        continue
                    if board_y < 0 or board_y >= self.board_graph.height:
                        continue

                    if (board_x, board_y) == vertex_pos:
                        vertex_covered = True

                    board_vertex = self.board_graph.grid[board_x][board_y]

                    for i in range(len(piece_vertex.edges)):
                        if piece_vertex.edges[i] is not None and board_vertex.edges[i] is None:
                            return False
            return vertex_covered
        
        # Check if the piece fits on the board, touching the provided vertex
        # if so, return the (x, y) offset to place the piece there
        def fits_on_board(self, piece_graph, board_graph, vertex_pos):
            # Find all the offsets such that this piece could overlap with the provided vertex position.
            # Wart: This should be optimized to only try offsets that would potentially touch
            # the target vertex (vertex_pos), but it's tricky to figure out. To annoying hex grid maths.
            x_range = range(0, vertex_pos[0] + board_graph.width + 1)
            x_range = [x for x in x_range if x >= 0]
            y_range = range(vertex_pos[1] - (piece_graph.height), vertex_pos[1] + 1)
            y_range = [y for y in y_range if y >= 0 and y < board_graph.height]
            for x_shift in x_range:
                for y_shift in y_range:
                    offset = (x_shift, y_shift)
                    self.gui_try_piece_on_board(piece_graph, offset)
                    if self.fits_on_board_with_offset(piece_graph, board_graph, vertex_pos, offset):
                        self.gui_clear_try_piece_on_board()
                        return offset
                    self.gui_clear_try_piece_on_board()
            return None

        # Look to see if there is a stranded region with an edge count that are not a multiple of 5
        # pieces are all 5 edges, so we need an even 5 edges for a region to have a chance of being
        # filled
        def board_has_stranded_regions(self):

            # Determine which edges are reachable from a given direction.
            # E.g. if a piece covers 0 and 3, then another piece can't go from 1 to 4.
            #            0   1
            #             \ /
            #            5-x-2
            #             / \
            #            4   3
            def reachable_edge_indexes(from_edge_index, v):
                if from_edge_index is None:
                    return range(6)
                else:
                    def open_to_the_left(x):
                        left = [5,4,3,2,1,0,5,4,3,2,1,0,5,4,3,2,1,0]
                        slice_start = left.index(x)+1
                        open = []
                        for i in left[slice_start:slice_start + 6]:
                            if v.edges[i] is None:
                                break
                            open.append(i)
                        return open

                    def open_to_the_right(x):
                        right = [0,1,2,3,4,5,0,1,2,3,4,5,0,1,2,3,4,5,]
                        slice_start = right.index(x) + 1
                        open = []
                        for i in right[slice_start:slice_start + 6]:
                            if v.edges[i] is None:
                                break
                            open.append(i)
                        return open

                    to_index_map = {0: 3, 1: 4, 2: 5, 3: 0, 4: 1, 5: 2}
                    to_index = to_index_map[from_edge_index]
                    reachable = set()
                    for i in open_to_the_left(to_index):
                        reachable.add(i)
                    for i in open_to_the_right(to_index):
                        reachable.add(i)
                    return reachable

            def search_region(v, from_edge_index, edge_set, visited):
                if v is None:
                    return
                if v.offset_cord in visited:
                    return
                visited[v.offset_cord] = True
                for edge_index in reachable_edge_indexes(from_edge_index, v):
                    edge = v.edges[edge_index]
                    if edge is not None:
                        # Sort it, so our results are non-directional
                        edge_val = tuple(sorted((v.offset_cord, edge.offset_cord)))
                        if self.gui_show_stranded_tree_walk:
                            self.gui.DrawEdge(edge_val, line_color="orange", tags="tree_walk")
                            time.sleep(self.gui_sleep_time / 8)
                        edge_set.add(edge_val)
                        search_region(edge, edge_index, edge_set, visited)

            vertex_visited = {}
            for x in range(self.board_graph.width):
                for y in range(self.board_graph.height):
                    edges = set()
                    current_v = self.board_graph.grid[x][y]
                    search_region(current_v, None, edges, vertex_visited)

                    if self.gui_show_stranded_tree_walk:
                        if len(edges) > 0:
                            self.gui_set_status("Graph section has %d edges" % len(edges))
                            time.sleep(self.gui_sleep_time * 8)
                            self.gui.ClearBoard("tree_walk")

                    if len(edges) % 5 != 0:
                        if self.gui_show_stranded:
                            for edge in edges:
                                self.gui.DrawEdge(edge, line_color="red", line_width=8, tags="stranded")
                                self.gui_set_status("Stranded graph section has %d edges" % len(edges))
                            time.sleep(self.gui_sleep_time * 5)
                            self.gui.ClearBoard("stranded")
                            time.sleep(self.gui_sleep_time / 2)
                        return True
            return False


        def place_piece(self, piece_graph, fits_offset):
            
            # Remember the previous state
            self.board_graph_previous.append(self.board_graph.Copy())
            self.available_pieces_previous.append(copy.copy(self.available_pieces))
            self.placed_pieces_previous.append(copy.copy(self.placed_pieces))

            self.gui_placed_piece(piece_graph, fits_offset)
            self.subtract_piece_from_board(piece_graph, fits_offset)
            self.placed_pieces[piece_graph.name] = (piece_graph, fits_offset)
            now_available = []
            for piece in self.available_pieces:
                if piece.name == piece_graph.name:
                    if piece_graph != piece:
                        self.gui_highlight_piece(piece, "light green", 0)
                else:
                    now_available.append(piece)

            self.available_pieces = now_available
            if len(self.placed_pieces) >= self.max_placed_pieces:
                self.max_placed_pieces = len(self.placed_pieces)
                self.gui_force_redraw_placed_pieces()

            self.gui_highlight_remaining_board()

        def rollback(self, count):
            for i in range(count):
                if len(self.board_graph_previous) > 0:
                    self.board_graph = self.board_graph_previous.pop(-1)
                    self.available_pieces = self.available_pieces_previous.pop(-1)
                    self.placed_pieces = self.placed_pieces_previous.pop(-1)
            self.gui_redraw_placed_pieces()

        def save_to_file(self, solution_hash):
            time.sleep(1)  # Allow time for the image to be written to the canvas
            file_name = "./solutions/" + solution_hash
            if not os.path.exists(file_name + ".png"):
                self.gui.board.postscript(file=file_name + ".eps")
                img = Image.open(file_name + ".eps")
                img.save(file_name + ".png")
            else:
                print("Solution file already exists")

        # Create string that uniquely describes the solution
        def create_solution_hash(self):
            hash_array = []
            for piece_id, piece_placement in self.placed_pieces.items():
                piece_graph, piece_offset = piece_placement
                hash_array.append((piece_id, piece_offset[0], piece_offset[1]))

            solution_hash = ""
            hash_array = sorted(hash_array)
            for info in hash_array:
                solution_hash += "%s%02d%02d" % info

            return solution_hash

        def run(self):
            # ------ Main ----------------
            # 1. Find a vertexes in the graph with the fewest edges (this will be the sides at first)
            # 2. Try pieces randomly until a fit is found
            # 3a. If a fit is found, then "place the piece" and update the board graph to non-longer include the edges
            # 4a. Go to 1
            # 3b. If no pieces fit, start over. (This can be optimized a lot)

            cli_display_count = 0
            solutions = []
            solutions_found = 0
            duplicates_found = 0
            while True:  # Keep finding more and more solutions
                attempt_num = 1
                rollback_one_count = 0
                rollback_two_count = 0
                startover_count = 0
                self.max_placed_pieces = 0
                self.gui_force_redraw_placed_pieces()
                self.start_over()

                while self.continuously_search_for_solutions:

                    cli_display_count += 1
                    if self.gui_show_placed_pieces or cli_display_count % 100 == 0:
                        print("unique solutions %4d: solutions found %4d: duplicates %4d: attempt %5d" %
                              (solutions_found - duplicates_found, solutions_found, duplicates_found, attempt_num))

                    self.gui_update_settings()
                    vertex_pos = self.get_vertex_with_fewest_edges()
                    if vertex_pos is None or len(self.placed_pieces) == 12:  # Did we find a solution?

                        solutions_found += 1
                        solution = self.create_solution_hash()
                        print("Found solution: ", solution)
                        if solution not in solutions:
                            solutions.append(solution)
                            self.save_to_file(solution)
                        else:
                            duplicates_found += 1

                        self.gui_force_redraw_placed_pieces()
                        break

                    self.gui_target_vertex(vertex_pos)

                    # Try all the pieces in random order

                    to_try_list = copy.copy(self.available_pieces)
                    random.shuffle(to_try_list)
                    for to_try in to_try_list:
                        self.gui_highlight_piece(to_try, "gray", 0)

                    found_fit = False
                    for to_try in to_try_list:
                        self.gui_highlight_piece(to_try, "yellow")
                        fits_offset = self.fits_on_board(to_try, board_graph, vertex_pos)
                        if fits_offset is not None:
                            self.gui_highlight_piece(to_try, "pink")
                            self.place_piece(to_try, fits_offset)
                            if self.board_has_stranded_regions():
                                self.gui_highlight_piece(to_try, "dark red", 5)
                                self.rollback(1)
                            else:
                                self.gui_highlight_piece(to_try, "green")
                                found_fit = True
                                break
                        self.gui_highlight_piece(to_try, "red", .1)

                    # We got stuck, so rollback some pieces or start over

                    if not found_fit:
                        self.gui_target_vertex(vertex_pos, "red")
                        attempt_num += 1

                        if False:  # This optimization didn't help

                            # The more successfully placed pieces the less likely we are to start over and rollback extra
                            if len(self.placed_pieces) > 0:
                                random_percent = random.random()
                                if random_percent < 1/(len(self.placed_pieces)):
                                    self.start_over()
                                    startover_count += 1
                                elif random_percent < 2/(len(self.placed_pieces)):
                                    self.rollback(2)
                                    rollback_two_count += 1
                                else:
                                    self.rollback(1)
                                    rollback_one_count += 1
                        else:
                            self.start_over()
                            startover_count += 1

    finder = Finder(board_graph_external, piece_graphs, gui)
    finder.run()

# Launch the thread that will search for solutions
def LaunchFindSolutionsThread(args, solverGui):
    board_graph, piece_graphs = args
    thread = threading.Thread(target=FindSolutions, args=(board_graph, piece_graphs, solverGui))
    thread.setDaemon(True)
    thread.start()


if __name__== '__main__':

    # Create the board graph

    all_pieces = "a b c d e f g h i k j l".split()
    board_graph = GenerateHexGraph(board_string_rep, all_pieces)

    # Create the pieces in each unique flip/rotation

    padding = 6
    piece_graphs = collections.defaultdict(set)  # Use as set, so duplicate shapes are removed
    for piece_id in all_pieces:
        graph = None
        for i in ["normal", 0,1,2,3,4,5, "flipped", 1,2,3,4,5]:
            if i == "normal":
                graph = GenerateHexGraph(board_string_rep, piece_id)
            elif i == "flipped":
                graph = graph.Flip()
            else:
                graph = graph.Rotate()
            graph.Trim()
            piece_graphs[piece_id].add(graph)

    # Calculate row height for displaying pieces

    if False:
        # Print info to help figure out a good pixel height for the pieces
        results = {}
        for h in range(40, 80):
            for pad in range(3,9):

                fits_count = 0
                fits = [False]
                for piece_id, graphs in piece_graphs.items():
                    piece_graphs[piece_id] = list(graphs)  # Convert the set to a list
                    for graph in graphs:
                        GetRowHeightToFitCanvas(h, graph.height, pad, fits)
                        fits_count += 0 if fits[0] else 1
                results[(h, pad)] = fits_count

        for k, v in results.items():
            print(k, v)


    min_row_height = 9999
    for piece_id, graphs in piece_graphs.items():
        piece_graphs[piece_id] = list(graphs)  # Convert the set to a list
        for graph in graphs:
            row_height = GetRowHeightToFitCanvas(SolverGui.PIECE_HEIGHT, graph.height, padding)
            if row_height < min_row_height:
                min_row_height = row_height

    # Give each piece a unique color



    # Create the UI

    solverGui = SolverGui(LaunchFindSolutionsThread, (board_graph, piece_graphs))
    solverGui.piece_row_height = min_row_height
    solverGui.board_padding = 20
    solverGui.board_row_height = GetRowHeightToFitCanvas(SolverGui.BOARD_HEIGHT,
                                                         board_graph.height,
                                                         solverGui.board_padding)

    piece_colors = ["#95D47A",
                    "#52CCCE",
                    "#00B0B2",
                    "#9FC1D3",
                    "#688FAD",
                    "#3F647E",
                    "#A09ED6",
                    "#6F5495",
                    "#4B256D",
                    "#F68FA0",
                    "#F26279",
                    "#EF3E5B"]

    for piece_id in all_pieces:
        color = piece_colors.pop(0)
        for graph in piece_graphs[piece_id]:
            y = all_pieces.index(piece_id)
            x = piece_graphs[piece_id].index(graph)
            graph.name = piece_id
            graph.gui_pos = (x, y)
            graph.color = color
            solverGui.DrawPiece(graph)

    solverGui.DrawBoard(board_graph,
                        line_color="light yellow",
                        line_width=18,
                        border_width=5,
                        border_color="#444444",
                        tags="board")

    solverGui.Run()



