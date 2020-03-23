# This is the solver for the hex puzzle

from hexPuzzle import *
import tkinter as tk
import collections
import threading
import time
import random
import copy

color_piece = "#5A2D0D"  # dark brown
color_piece_border = "black"
color_bg = "grey"

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
    BOARD_HEIGHT = 400
    BOARD_WIDTH = int(BOARD_HEIGHT * XSTRETCH)
    PIECE_HEIGHT = 60
    PIECE_WIDTH = int(PIECE_HEIGHT * XSTRETCH)
    UPDATE_PERIOD_MS = 100

    def __init__(self, find_solutions_function, find_solutions_args):
        self.piece_row_height = 0
        self.board_row_height = 0
        self.update_lock = threading.Lock()
        self.update_work = []

        self.ui = tk.Tk()

        # Create board view pane
        self.board_pane = tk.LabelFrame(text="")
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
            self.status.set("status ...")
            self.status_label = tk.Label(self.info_pane, textvariable=self.status).grid(column=1, row=0, padx=5, pady=5)

        if True:  # row 1
            tk.Label(self.info_pane, text="Verbosity").grid(column=0, row=1, padx=5, pady=5)
            self.verbosity = tk.Scale(self.info_pane, from_=0, to=4, orient=tk.HORIZONTAL)
            self.verbosity.set(1)
            self.verbosity.grid(column=1, row=1, padx=5, pady=5)

        if True:  # row 2
            tk.Label(self.info_pane, text="Speed").grid(column=0, row=2, padx=5, pady=5)
            self.speed = tk.StringVar()
            self.speed.set("0.1")
            self.speed_entry = tk.Entry(self.info_pane, textvariable=self.speed).grid(column=1, row=2, padx=5, pady=5)


        # Create pieces section
        self.pieces_pane = tk.LabelFrame(text="")
        self.pieces_pane.grid(column=1, row=0, rowspan=2, sticky=tk.N)

        # Add a canvas for each rotation and flip of each piece
        piece_height = SolverGui.PIECE_HEIGHT
        piece_width = SolverGui.PIECE_WIDTH
        self.peices = {}
        for y in range(12):
            for x in range(12):
                c = tk.Canvas(self.pieces_pane, height=piece_height, width=piece_width, bg=color_bg, borderwidth=0)
                c.grid(column=x, row=y)
                self.peices[(x, y)] = c

    def AddUiUpdate(self, work):
        with self.update_lock:
            self.update_work.append(work)


    def DrawPiece(self, piece_graph, **kwargs):
        def draw_func():
            self.peices[piece_graph.gui_pos].delete("all")
            self.peices[piece_graph.gui_pos].configure(bg=color_bg)
            DrawHexGraph(piece_graph,
                         self.peices[piece_graph.gui_pos],
                         self.piece_row_height,
                         padding,
                         line_width=4,
                         border_width=3,
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
            DrawHexGraph(board_graph,
                        self.board,
                        self.board_row_height,
                        self.board_padding,
                        line_width=12,
                        border_width=5,
                        border_color="black",
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
def GetRowHeightToFitCanvas(pixel_height, graph_rows, pad):
    pixel_height = pixel_height - (pad * 2)
    pixels_between_rows = pixel_height // (graph_rows - 1)
    row_height = pixels_between_rows
    actual_pixel_height = pixels_between_rows * (graph_rows - 1)  # Account for integer rounding
    if pixel_height != actual_pixel_height:
        print("pixel_height", pixel_height, "!=" "actual_pixel_height", actual_pixel_height)
    if False:
        print("pixel_height", pixel_height, "pad", pad, graph_rows, "graph_rows", graph_rows, "hex_height", row_height)
    return row_height


# This is the logic to find solutions to the puzzle.  It can use the solveGui to visualize progress.
def FindSolutions(board_graph_original, piece_graphs, gui):

    def dup_check(piece_list):
        for i in range(len(piece_list)):
            if piece_list.index(piece_list[i]) != i:
                print("check list", hash(piece_list[i]), piece_list.index(piece_list[i]), i)
                piece_list[i].PrintPretty()
                piece_list[piece_list.index(piece_list[i])].PrintPretty()

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
            self.gui_sleep_time = 0.2
            self.gui_highlight_piece_sleep_time = 0.0
            self.gui_show_each_try = False
            self.gui_show_piece_highlights = True
            self.gui_show_target_vertex = True
            self.gui_show_placed_pieces = True
            self.available_pieces = []            
            self.placed_pieces = {}
            self.max_placed_pieces = 0
            self.board_graph = None

        def gui_update_settings(self):
            self.gui_show_placed_pieces = False
            self.gui_show_target_vertex = False
            self.gui_show_piece_highlights = False
            self.gui_show_each_try = False

            verbosity = self.gui.verbosity.get()
            if verbosity >= 1:
                self.gui_show_placed_pieces = True
            if verbosity >= 2:
                self.gui_show_target_vertex = True
            if verbosity >= 3:
                self.gui_show_piece_highlights = True
            if verbosity >= 4:
                self.gui_show_each_try = True
            try:
                speed = float(self.gui.speed.get())
                self.gui_sleep_time = speed
                self.gui_highlight_piece_sleep_time = speed / 4.0
            except:
                pass

        def gui_set_status(self, string):
            self.gui.SetStatus(string)

        def gui_target_vertex(self, vertex_pos, color="yellow", delay_multiplier=1):
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
                                       vertex_highlight_color="black",
                                       vertex_highlight_size=5,
                                       tags="piece_on_board")
                    time.sleep(self.gui_sleep_time * delay_multiplier)


        def gui_clear_try_piece_on_board(self, delay_multiplier=1):
            if self.gui_show_each_try:
                print(self.gui_sleep_time, delay_multiplier)
                self.gui.ClearBoard("piece_on_board")
                time.sleep(self.gui_sleep_time * delay_multiplier)

        def gui_placed_piece(self, piece_graph, offset, delay_multiplier=1):
            if self.gui_show_placed_pieces:
                self.gui.DrawBoard(piece_graph,
                                   graph_offset=offset,
                                   line_color="green",
                                   vertex_highlight_color="black",
                                   vertex_highlight_size=5,
                                   tags="placed_piece")
                time.sleep(self.gui_sleep_time * delay_multiplier)

        def gui_force_show_placed_pieces(self):
            old = self.gui_show_placed_pieces
            self.gui_show_placed_pieces = True
            self.gui.ClearBoard("placed_piece")
            for piece_id, (piece_graph, offset) in self.placed_pieces.items():
                self.gui_placed_piece(piece_graph, offset)
            self.gui_show_placed_pieces = old

        def gui_clear_placed_pieces(self, delay_multiplier=1):
            if self.gui_show_placed_pieces:
                self.gui.ClearBoard("placed_piece")
                time.sleep(self.gui_sleep_time * delay_multiplier)

        def gui_highlight_piece(self, piece_graph, color, delay_multiplier=1):
            if self.gui_show_piece_highlights:
                self.gui.DrawPiece(piece_graph, highlight=color)
                time.sleep(self.gui_highlight_piece_sleep_time * delay_multiplier)


        def start_over(self):
            self.gui_clear_placed_pieces()
            self.available_pieces = []
            for piece_id, graphs in self.piece_graphs.items():
                for graph in graphs:
                    self.available_pieces.append(graph)
            self.placed_pieces = {}
            self.board_graph = board_graph_original.Copy()

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
            #v = (2,6)
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

                    for i in range(len(piece_vertex.edges)):
                        if piece_vertex.edges[i] is not None:
                            board_vertex.edges[i] = None
    
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

        def place_piece(self, piece_graph, fits_offset):
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

            self.available_pieces = [a for a in self.available_pieces if a.name != piece_graph.name]
            if len(self.placed_pieces) >= self.max_placed_pieces:
                self.max_placed_pieces = len(self.placed_pieces)
                self.gui_force_show_placed_pieces()

        def run(self):
            # ------ Main ----------------
            # 1. Find a vertexes in the graph with the fewest edges (this will be the sides at first)
            # 2. Try pieces randomly until a fit is found
            # 3a. If a fit is found, then "place the piece" and update the board graph to non-longer include the edges
            # 4a. Go to 1
            # 3b. If no pieces fit, start over. (This can be optimized a lot)

            # Search until all vertexes are filled
            attempt_num = 1
            self.start_over()
            while True:
                self.gui_update_settings()
                vertex_pos = self.get_vertex_with_fewest_edges()
                if vertex_pos is None or len(self.placed_pieces) == 12:
                    self.gui_force_show_placed_pieces()
                    print("Done")
                    break
                self.gui_target_vertex(vertex_pos)
                
                # Try all the pieces in random order
                to_try_list = copy.copy(self.available_pieces)
                random.shuffle(to_try_list)
                dup_check(to_try_list)

                for to_try in to_try_list:
                    self.gui_highlight_piece(to_try, "gray", 0)

                found_fit = False
                for to_try in to_try_list:

                    self.gui_highlight_piece(to_try, "yellow")
                    fits_offset = self.fits_on_board(to_try, board_graph, vertex_pos)
                    if fits_offset is not None:
                        self.gui_highlight_piece(to_try, "green")
                        found_fit = True
                        self.place_piece(to_try, fits_offset)
                        break
                    self.gui_highlight_piece(to_try, "red", .1)
                if not found_fit:
                    self.gui_target_vertex(vertex_pos, "red")
                    print("attempt %5d: placed %2d pieces before getting stuck. Max is %2d" % (attempt_num , len(self.placed_pieces), self.max_placed_pieces))
                    attempt_num += 1
                    self.start_over()

    finder = Finder(board_graph_original, piece_graphs, gui)
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

    min_row_height = 9999
    for piece_id, graphs in piece_graphs.items():
        piece_graphs[piece_id] = list(graphs)  # Convert the set to a list
        for graph in graphs:
            row_height = GetRowHeightToFitCanvas(SolverGui.PIECE_HEIGHT, graph.height, padding)
            if row_height < min_row_height:
                min_row_height = row_height


    # Create the UI

    solverGui = SolverGui(LaunchFindSolutionsThread, (board_graph, piece_graphs))
    solverGui.piece_row_height = min_row_height
    solverGui.board_padding = 20
    solverGui.board_row_height = GetRowHeightToFitCanvas(SolverGui.BOARD_HEIGHT,
                                                         board_graph.height,
                                                         solverGui.board_padding)

    solverGui.DrawBoard(board_graph, tags="board")
    for piece_id in all_pieces:
        for graph in piece_graphs[piece_id]:
            y = all_pieces.index(piece_id)
            x = piece_graphs[piece_id].index(graph)
            graph.name = piece_id
            graph.gui_pos = (x, y)
            solverGui.DrawPiece(graph)

    solverGui.Run()



