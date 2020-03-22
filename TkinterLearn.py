import Tkinter as tk
from PIL import ImageTk, Image # PhotoImage in python 2.7 doesn't handle .jpg

# Window
window = tk.Tk()
window.title("Test window")
window.configure(background="black")

# Image
img = ImageTk.PhotoImage(Image.open("TriangleEdges - original.jpg"))
tk.Label(window, image=img, bg="black").grid(row=0, column=0, sticky=tk.E)

# Label
tk.Label(window, text="test", bg="black", fg="white", font="none 12 bold").grid(row=1, column=0, sticky=tk.W)

# Text Entry
text_entry = tk.Entry(window, width=20, bg="white")
text_entry.grid(row=2, column=0, sticky=tk.W)

# Submit button
def Click():
    entered_text = text_entry.get()
    output.delete(0.0, tk.END)
    output.insert(tk.END, entered_text)
tk.Button(window, text="Submit", width=6, command=Click).grid(row=3,column=0, sticky=tk.W)

# Output Label
output = tk.Text(window, width=30, height=1, wrap=tk.WORD, background="white")
output.grid(row=5, column=0, sticky=tk.W)

# Exit Label
def CloseWindow():
    window.destroy()
    exit()
tk.Button(window, text="Exit", width=6, command=CloseWindow).grid(row=7,column=0, sticky=tk.W)

# Canvas
# create_bitmap
# create_image
# create_line
# create_oval
# create_polygon
# create_rectangle
# create_text
# create_window

c = tk.Canvas(window, height=500, width=300, bg="grey")
c.grid(row=0, column=1)

c.create_image(3, 3, image=img, anchor=tk.NW)

c.create_line(5,205, 100,280, width=30, fill="black", capstyle=tk.ROUND)
c.create_line(5,205, 100,280, width=27, fill="red",   capstyle=tk.ROUND)

c.create_oval(20,0, 100,100, fill="red")
c.create_arc(200, 8, 240, 140, extent=140, fill="pink")
c.create_arc(200, 208, 240, 340, extent=140)

import pdb
pdb.set_trace()

window.mainloop()
