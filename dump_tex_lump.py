import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import font
import tkinter.ttk as ttk
import sys
import struct
import json


# for animspeed
# and light
# read their value from value
SURF_FLAGS = {
    'light' : 0x1, #value will hold the light strength
    'slick' : 0x2, #effects game physics
    'sky' : 0x4, # don't draw, but add to skybox
    'warp' : 0x8, # turbulent water warp
    'trans33_deprec' : 0x10, # Used to clarify view in the editor - not used in game
    'trans66_deprec' : 0x20, # Deprecated - recycle
    'flowing' : 0x40, # scroll towards angle
    'nodraw' : 0x80, # don't bother referencing the texture
    'no_detail' : 0x400, # face doesn't draw the detail texture normally assigned to it
    'alpha_texture' : 0x800, # texture has alpha in it, and should show through in bsp process
    'animspeed' : 0x1000, # value will hold the anim speed in fps
    'undulate' : 0x2000, # rock surface up and down...
    'skyreflect' : 0x4000, # liquid will somewhat reflect the sky - not quite finished....
    'map' : 0x8000, # used for the auto-map
    'region' : 0x10000,
    'simple_spherical' : 0x20000
}

def grab_lump(lump_num,a_sof_map):
    bsp_header_size = 8
    lump_header_size = 8
    lump_offset = struct.unpack_from('<i',a_sof_map,bsp_header_size+lump_header_size*lump_num)[0]
    lump_size = struct.unpack_from('<i',a_sof_map,bsp_header_size+lump_header_size*lump_num + 4)[0]
    # print(f"offset = {lump_offset}\nsize = {lump_size}")
    
    mview = memoryview(a_sof_map)
    return (mview[lump_offset:lump_offset+lump_size],lump_size)


def openBSP():
    
    if not app.needle:
        # show tkinter dialog
        messagebox.showinfo("MAKE ME GREEN","You must specify a part of texture string as search term, use * for all. eg. pikachu")
        return
    filename = filedialog.askopenfilename()
    if len(filename) == 0:
        return

    with open(filename,'rb') as bsp_file:
        data = bsp_file.read()

    alltex,lump_size = grab_lump(5,data)

    # offsets and size
    texinfo_t = {
        "size" : 76,
        "flags" : 32,
        "value" : 36,
        "name" : 40
    }

    tex_entries = []
    index = 0
    while index < lump_size:
        name = struct.unpack_from('32s',alltex,index+texinfo_t['name'])[0].decode('latin-1').rstrip("\x00")
        flags = struct.unpack_from('<i',alltex,index+texinfo_t['flags'])[0]
        value = struct.unpack_from('<i',alltex,index+texinfo_t['value'])[0]
        d = {
        'name' : name,
        'flags' : flags,
        'value' : value
        }
        tex_entries.append(d)
        index += texinfo_t['size']

    window = tk.Toplevel(app.master)
    tb = TextScrollCombo(window)
    tb.pack(fill="both", expand=True)
    tb.config(width=600, height=600)

    tb.txt.config(font=("consolas", 12), undo=True, wrap='word')
    tb.txt.config(borderwidth=3, relief="sunken")

    style = ttk.Style()
    style.theme_use('clam')


    # tb = tk.Text(window)
    # tb.pack();



    # scrollb = tk.Scrollbar(tb, command=tb.yview)
    # scrollb.pack(side=tk.RIGHT,fill=tk.Y);
    # tb['yscrollcommand'] = scrollb.set

    count = 0
    text_line = 1
    text_column = 0
    for d in tex_entries:
        # specific texture only
        if app.needle in d['name'] or app.needle == "*":
            count += 1
            
            f = d['flags']
            matched = False
            for key in SURF_FLAGS:
                if f & SURF_FLAGS[key]:

                    output = f"{d['name']} :"
                    print(output)
                    # tb.insert(f"{text_line}.{text_column}",output)
                    tb.txt.insert(tk.END,output + "\n")
                    text_column +=  len(output)
                    text_line += 1
                    text_column = 0

                    # on
                    output = f"{key}"
                    print(output)
                    # tb.insert(f"{text_line}.{text_column}",output)
                    tb.txt.insert(tk.END,output + "\n")
                    text_column +=  len(output)
                    text_line += 1
                    text_column = 0
                    matched=True
                    if key == "light" or key == "animspeed":
                        output = f"  value == {d['value']}"
                        print(output)
                        # tb.insert(f"{text_line}.{text_column}",output)
                        tb.txt.insert(tk.END,output + "\n")
                        text_column +=  len(output)
                        text_line += 1
                        text_column = 0

            if matched:
                print("")
                tb.txt.insert(tk.END,output + "\n\n")
                text_line += 1
                text_column = 0

    print("DONE")


class TextScrollCombo(ttk.Frame):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    # ensure a consistent GUI size
        self.grid_propagate(False)
    # implement stretchability
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    # create a Text widget
        self.txt = tk.Text(self)
        self.txt.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

    # create a Scrollbar and associate it with txt
        scrollb = ttk.Scrollbar(self, command=self.txt.yview)
        scrollb.grid(row=0, column=1, sticky='nsew')
        self.txt['yscrollcommand'] = scrollb.set


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

        self.master.title("True Texture Flags Revealer")

        self.needle = ""
    def create_widgets(self):
        f = font.Font(family='Helvetica', name='appHighlightFont', size=12, weight='bold')

        self.button_bsp = tk.Button(self,font=f,fg="red",bg="black")
        self.button_bsp["text"] = "Click Me For Info"
        self.button_bsp["command"] = openBSP
        self.button_bsp.pack(side="top")

        

        self.needle_string = tk.StringVar()
        self.callback = self.register(self.typed)
        self.needle_entry = tk.Entry(self,
            justify=tk.CENTER,
            width=44,
            textvariable=self.needle_string,
            font=f,
            insertbackground="red",
            bg="black",
            fg="white",
            validate='key',
             validatecommand=(self.callback, '%P'))

        self.needle_entry.pack(side="bottom")

        # self.quit = tk.Button(self, text="QUIT", fg="red",
        #                       command=self.master.destroy)
        # self.quit.pack(side="bottom")

        self.canvas = tk.Canvas(root, width = 400, height = 400)      
        
        self.sofimg_r = tk.PhotoImage(file="sof1r.ppm")
        self.sofimg_g = tk.PhotoImage(file="sof1g.ppm")
        self.sofimg = self.canvas.create_image(0,0, anchor=tk.NW, image=self.sofimg_r)
        self.canvas.pack(side="bottom")

        self.needle_entry.focus()

    def typed(self,becomes):
        # self.master.update()
        self.needle = becomes
        if not self.needle:
            self.button_bsp["fg"] = "red"
            self.needle_entry["insertbackground"] = "red"
            self.canvas.itemconfigure(self.sofimg, image=self.sofimg_r)
            self.button_bsp["text"] = "Click Me For Info"
        else:
            self.button_bsp["fg"] = "green"
            self.needle_entry["insertbackground"] = "green"
            self.canvas.itemconfigure(self.sofimg, image=self.sofimg_g)
            self.button_bsp["text"] = "Click Me To Search In Bsp File"
        return True

root = tk.Tk()
app = Application(master=root)

app.mainloop()