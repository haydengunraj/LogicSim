from Tkinter import *
from constants import *
from objects import Handler
from math import log

class MainWindow(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("LogicSim")
        self.geometry = "{}x{}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight())
        self.frame1 = MenuFrame(self, bg="grey")
        self.frame2 = CircuitFrame(self, highlightbackground="black", highlightcolor="black", highlightthickness=1, width=200)
        self.handler = Handler(self)
        self.frame1.grid(row=0, column=0, sticky="ns")
        self.frame2.grid(row=0, column=1, sticky="ns")
        self.input_box = InputBox
        self.truth_table = TruthTable
        self.bind_handlers()
    
    def bind_handlers(self):
        self.frame1.listbox.bind("<<ListboxSelect>>", self.handler.list_handler)
        self.frame1.mode_buttons[0].config(command=lambda:self.handler.mode_handler(0))
        self.frame1.mode_buttons[1].config(command=lambda:self.handler.mode_handler(1))
        self.frame1.mode_buttons[2].config(command=lambda:self.handler.mode_handler(2))
        self.frame1.mode_buttons[3].config(command=lambda:self.handler.mode_handler(3))
        self.frame1.mode_buttons[4].config(command=lambda:self.handler.mode_handler(4))
        self.frame1.mode_buttons[5].config(command=lambda:self.handler.mode_handler(5))
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
        self.listbox.grid(row=0, columnspan=2, sticky="nsew")
        scrollbar.grid(row=0, column=2)
        self.listbox.update()
    
    def modebuttons_setup(self):
        self.mode_buttons = []
        self.active = [0, 0, 0, 0, 0, 0]
        self.mode_buttons.append(Button(self, text="Delete", highlightbackground="grey"))
        self.mode_buttons.append(Button(self, text="Connect", highlightbackground="grey"))
        self.mode_buttons.append(Button(self, text="Set Values", highlightbackground="grey"))
        self.mode_buttons.append(Button(self, text="Rename I/O", highlightbackground="grey"))
        self.mode_buttons.append(Button(self, text="Simulate", highlightbackground="grey"))
        self.mode_buttons.append(Button(self, text="Truth Table", highlightbackground="grey"))
        self.mode_buttons[DELETE].grid(row=1, column=0, sticky="nsew")
        self.mode_buttons[CONNECT].grid(row=1, column=1, sticky="nsew")
        self.mode_buttons[SET_VALS].grid(row=2, column=0, sticky="nsew")
        self.mode_buttons[RENAME].grid(row=2, column=1, sticky="nsew")
        self.mode_buttons[SIMULATE].grid(row=3, columnspan=2, sticky="nsew")
        self.mode_buttons[TRUTH].grid(row=4, columnspan=2, sticky="nsew")

class CircuitFrame(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)
        self.master = master
        self.canvas = Canvas(self, width=self.master.winfo_screenwidth()-215, height=self.master.winfo_screenheight())
        self.canvas.grid(row=0)

class InputBox(object):
    def __init__(self, master, title, submitlabel):
        self.top = Toplevel(master)
        self.top.title(title)
        self.entry = Entry(self.top)
        self.set = Button(self.top, text=submitlabel, command=self.execute)
        self.entry.grid(row=0, column=0)
        self.set.grid(row=1, column=0, sticky="nsew")
    
    def execute(self):
        self.value = self.entry.get()
        self.top.destroy()

class TruthTable(object):
    def __init__(self, master, circuit):
        self.top = Toplevel(master)
        self.top.title("Truth Table")
        input_gates, output_gates, output_sets = circuit.truth_table()
        input_cnt = len(input_gates)
        output_cnt = len(output_gates)
        for g in range(input_cnt):
            head = Label(self.top, text=circuit.master.aliases[input_gates[g]], width=6, font=("TkDefaultFont", 14, "bold", "underline"))
            head.grid(row=0, column=g, sticky="nsew")
        for o in range(output_cnt):
            head = Label(self.top, text=circuit.master.aliases[output_gates[o]], width=6, fg="red", font=("TkDefaultFont", 14, "bold", "underline"))
            head.grid(row=0, column=o+input_cnt, sticky="nsew")
        for i in range(input_cnt):
            num = 2**input_cnt/(2**(i + 1))
            val = 0
            for j in range(2**(i + 1)):
                for k in range(num):
                    lab = Label(self.top, text=str(val))
                    lab.grid(row=num*j+k+1, column=i, sticky="nsew")
                val = abs(val - 1)
        for r in range(2**input_cnt):
            for c in range(output_cnt):
                lab = Label(self.top, text=str(output_sets[r][c]), fg="red")
                lab.grid(row=r+1, column=c+input_cnt, sticky="nsew")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()