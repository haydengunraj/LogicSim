from Tkinter import *
from constants import *
from objects import Handler

class MainWindow(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Circuit Builder")
        self.geometry = "{}x{}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight())
        self.frame1 = MenuFrame(self, bg="grey")
        self.frame2 = CircuitFrame(self, highlightbackground="black", highlightcolor="black", highlightthickness=1, width=200)
        self.handler = Handler(self)
        self.frame1.grid(row=0, column=0, sticky="ns")
        self.frame2.grid(row=0, column=1, sticky="ns")
        self.mode = ""
        self.bind_handlers()
    
    def bind_handlers(self):
        self.frame1.listbox.bind("<<ListboxSelect>>", self.handler.list_handler)
        self.frame1.mode_buttons[0].config(command=lambda:self.handler.mode_handler(0))
        self.frame1.mode_buttons[1].config(command=lambda:self.handler.mode_handler(1))
        self.frame1.mode_buttons[2].config(command=lambda:self.handler.mode_handler(2))
        self.frame1.mode_buttons[3].config(command=lambda:self.handler.mode_handler(3))
        self.frame1.mode_buttons[4].config(command=lambda:self.handler.mode_handler(4))
        self.frame2.canvas.bind("<Button-1>", self.handler.click_handler)
        self.frame2.canvas.bind("<B1-Motion>", self.handler.drag_handler)
        self.frame2.canvas.bind("<Motion>", self.handler.move_handler)
        self.frame2.canvas.bind("<ButtonRelease-1>", self.handler.release_handler)

class MenuFrame(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)
        self.master = master
        self.listbox_setup()
        self.modebuttons_setup()
        
    def listbox_setup(self):
        scrollbar = Scrollbar(self)
        self.listbox = Listbox(self, height=10, selectmode=SINGLE)
        for i in range(len(GATES)):
            self.listbox.insert(i, GATES[i])
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.grid(row=0, columnspan=2)
        scrollbar.grid(row=0, column=2)
        self.listbox.update()
    
    def modebuttons_setup(self):
        self.mode_buttons = []
        self.active = [0, 0, 0, 0, 0]
        self.mode_buttons.append(Button(self, text="DELETE", highlightbackground="grey"))
        self.mode_buttons.append(Button(self, text="CONNECT", highlightbackground="grey"))
        self.mode_buttons.append(Button(self, text="SET VALUES", highlightbackground="grey"))
        self.mode_buttons.append(Button(self, text="RENAME", highlightbackground="grey"))
        self.mode_buttons.append(Button(self, text="SIMULATE", highlightbackground="grey"))
        self.mode_buttons[DELETE].grid(row=1, column=0, sticky="nsew")
        self.mode_buttons[CONNECT].grid(row=1, column=1, sticky="nsew")
        self.mode_buttons[SET_VALS].grid(row=2, column=0, sticky="nsew")
        self.mode_buttons[RENAME].grid(row=2, column=1, sticky="nsew")
        self.mode_buttons[SIMULATE].grid(row=3, columnspan=2, sticky="nsew")

class CircuitFrame(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)
        self.master = master
        self.canvas = Canvas(self, width=self.master.winfo_screenwidth()-215, height=self.master.winfo_screenheight())
        self.canvas.grid(row=0)

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()