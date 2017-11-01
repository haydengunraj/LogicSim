from Tkinter import *
from math import hypot
from constants import *
from gates import *


class Handler(object):
    def __init__(self, main):
        self.main = main
        self.canvas = self.main.frame2.canvas
        self.elements = []
        self.connectors = []
        self.wires = {} ## keys are tags, values are lists of wires
        self.gate_mode = None
        self.curs = None
        self.mouse_mode = None
        
        ### VARIABLES/FLAGS FOR DRAWING CONNECTORS
        self.highlighted = 0
        self.dyn_line = Wire()
        self.output_conn = False
        
        self.drawing = Drawing(self.canvas)
        self.menu = self.main.frame1
        self.circuit = Circuit()
    
    def click_handler(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.menu.listbox.selection_clear(0, END)
        self.canvas.delete(self.curs)
        self.curs = None
        temp = self.gate_mode
        self.gate_mode = None
        if self.mouse_mode == DELETE:
            closest_item = self.canvas.gettags(self.canvas.find_closest(x, y))
            if len(closest_item) > 0:
                closest_item = closest_item[0]
                x1, y1, x2, y2 = self.canvas.bbox(closest_item)
                if hypot(x - (x1 + x2)/2, y - (y1 + y2)/2) < GRAB_RADIUS:
                    self.canvas.delete(closest_item)
                    self.circuit.remove(closest_item)
                    for w in self.wires[closest_item]:
                        self.canvas.delete(w)
        elif self.mouse_mode == CONNECT:
            if self.highlighted:
                x1, y1, x2, y2 = self.canvas.coords(self.highlighted)
                if self.dyn_line.id:
                    if self.dyn_line.tags[0] == self.canvas.gettags(self.highlighted)[0]:
                        self.canvas.delete(self.dyn_line.id)
                        self.dyn_line.id = 0
                        self.dyn_line.tags = []
                    else:
                        xd1, yd1, xd2, yd2 = self.canvas.coords(self.dyn_line.id)
                        tag = self.canvas.gettags(self.highlighted)[0]
                        self.dyn_line.tags.append(tag)
                        self.canvas.coords(self.dyn_line.id, xd1, yd1, (x1 + x2)/2, (y1 + y2)/2)
                        if self.output_conn:
                            self.circuit.connect(self.dyn_line.tags[0], tag)
                        else:
                            self.circuit.connect(self.dyn_line.tags[0], tag, forward=False)
                        self.wires[self.dyn_line.tags[0]].append(self.dyn_line.id)
                        self.wires[self.dyn_line.tags[1]].append(self.dyn_line.id)
                        self.dyn_line.id = 0
                        self.dyn_line.tags = []
                else:
                    tag = self.canvas.gettags(self.highlighted)[0]
                    self.dyn_line.tags.append(tag)
                    self.dyn_line.id = self.canvas.create_line((x1 + x2)/2, (y1 + y2)/2, (x1 + x2)/2, (y1 + y2)/2)
                    xb1, yb1, xb2, yb2 = self.canvas.bbox(tag)
                    self.output_conn = (int(x2) == xb2)
                self.canvas.itemconfig(self.highlighted, fill="")
                self.highlighted = 0
        elif self.mouse_mode == SET_VALS or self.mouse_mode == RENAME:
            closest_item = self.canvas.gettags(self.canvas.find_closest(x, y))
            if len(closest_item) > 0:
                closest_item = closest_item[0]
                x1, y1, x2, y2 = self.canvas.bbox(closest_item)
                if isinstance(self.circuit.elements[closest_item], IN) or isinstance(self.circuit.elements[closest_item], OUT) and x > x1 and x < x2 and y > y1 and y < y2:
                    if self.mouse_mode == RENAME:
                        print "good1"
                        # rename element
                    elif isinstance(self.circuit.elements[closest_item], IN):
                        uin = InputBox(self.main)
                        self.main.wait_window(uin.top)
                        self.circuit.elements[closest_item].inputs = []
                        self.circuit.elements[closest_item].addInput(int(uin.value))
        else:
            if temp is not None:
                self.drawing.itm_cnt -= 1
                tag, connectors = self.drawing.draw(temp, x, y)
                self.connectors.extend(connectors)
                self.elements.append(tag)
                self.circuit.add(temp, tag)
                self.wires[tag] = []
            else:
                None # NON-CRITICAL: drag/drop functionality
    
    def move_handler(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.mouse_mode == CONNECT:
            if self.dyn_line.id:
                xd1, yd1, xd2, yd2 = self.canvas.coords(self.dyn_line.id)
                self.canvas.coords(self.dyn_line.id, xd1, yd1, x, y)
            closest = self.canvas.find_overlapping(x - 3, y - 3, x + 3, y + 3)
            if self.highlighted and self.highlighted not in closest:
                self.canvas.itemconfig(self.highlighted, fill="")
                self.highlighted = 0
            else:
                for i in closest:
                    if i in self.connectors:
                        x1, y1, x2, y2 = self.canvas.coords(i)
                        if hypot(x - (x1 + x2)/2, y - (y1 + y2)/2) < CONN_RADIUS:
                            self.canvas.itemconfig(i, fill="red")
                            self.highlighted = i
        else:
            if self.curs is not None:
                x1, y1, x2, y2 = self.canvas.bbox(self.curs)
                self.canvas.move(self.curs, x - (x2 + x1)/2, y - (y2 + y1)/2)
            else:
                if self.gate_mode is not None and self.mouse_mode is None:
                    self.curs, conn = self.drawing.draw(self.gate_mode, x, y)
    
    def drag_handler(self, event):
        None
    
    def release_handler(self, event):
        None
    
    def list_handler(self, event):
        listbox = event.widget
        self.gate_mode = listbox.get(listbox.curselection()[0])
        self.mouse_mode = None
        self.menu.active = [0, 0, 0, 0, 0]
        for btn in self.menu.mode_buttons:
            btn.config(highlightbackground="grey") 
        if self.curs is not None:
            self.canvas.delete(self.curs)
            self.curs = None
    
    def mode_handler(self, mode):
        self.menu.listbox.selection_clear(0, END)
        if self.menu.active[mode]:
            self.menu.mode_buttons[mode].config(highlightbackground="grey")
            self.menu.active[mode] = 0
            self.mouse_mode = None
            if mode == CONNECT:
                self.toggle_CONNECT()
        else:
            self.menu.mode_buttons[mode].config(highlightbackground="black")
            self.menu.active[mode] = 1
            for i in range(len(self.menu.mode_buttons)):
                if i != mode:
                    self.menu.mode_buttons[i].config(highlightbackground="grey")
                    self.menu.active[i] = 0
            if self.curs is not None:
                self.canvas.delete(self.curs)
                self.curs = None
            self.gate_mode = None
            self.mouse_mode = mode
            if mode == DELETE:
                self.toggle_CONNECT()
            if mode == SIMULATE:
                self.toggle_CONNECT()
                self.circuit.simulate()
            if mode == CLEAR:
                self.toggle_CONNECT()
    def toggle_CONNECT(self):
        if self.dyn_line.id:
            self.canvas.delete(self.dyn_line.id)
            self.dyn_line.id = 0
            self.dyn_line.tags = []
        if self.highlighted:
            self.canvas.itemconfig(self.highlighted, fill="")
            self.highlighted = 0

class Circuit(object):
    def __init__(self):
        self.elements = {}
        self.gate_classes = {
            "INPUT": IN,
            "OUTPUT": OUT,
            "NOT": NOT,
            "AND2": AND2,
            "OR2": OR2
        }
    
    def add(self, element, tag):
        self.elements[tag] = self.gate_classes[element]()
    
    def remove(self, tag):
        for i in self.elements[tag].inputs:
            try:
                i.next.remove(self.elements[tag])
            except:
                pass
        for n in self.elements[tag].next:
            i.inputs.remove(self.elements[tag])
        del self.elements[tag]
        
    def connect(self, tag1, tag2, forward=True):
        if forward:
            self.elements[tag2].addInput(self.elements[tag1])
        else:
            self.elements[tag1].addInput(self.elements[tag2])
    
    def simulate(self):
        for t in self.elements:
            if isinstance(self.elements[t], OUT):
                print self.elements[t].output()

class InputBox(object):
    def __init__(self, master):
        self.top = Toplevel(master)
        self.label = Label(self.top, text="Set Value")
        self.label.grid(row=0, column=0)
        self.entry = Entry(self.top)
        self.entry.grid(row=1, column=0)
        self.set = Button(self.top, text="Set", command=self.execute)
        self.set.grid(row=2, column=0, sticky="nsew")
    
    def execute(self):
        self.value = self.entry.get()
        self.top.destroy()

class Drawing(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self.itm_cnt = 0
        self.draw_fncts = {
            "INPUT": self.draw_IN,
            "OUTPUT": self.draw_OUT,
            "NOT": self.draw_NOT,
            "AND2": self.draw_AND2,
            "OR2": self.draw_OR2,
        }
    
    def draw(self, element, x, y):
        return self.draw_fncts[element](x, y)
    
    def draw_IN(self, x, y):
        tag = "IN{}".format(self.itm_cnt)
        connectors = []
        self.canvas.create_line(x + 5, y, x + 35, y, tags=(tag))
        self.canvas.create_line(x - 10, y - 10, x + 5, y, tags=(tag))
        self.canvas.create_line(x - 10, y + 10, x + 5, y, tags=(tag))
        self.canvas.create_line(x - 40, y - 10, x - 10, y - 10, tags=(tag))
        self.canvas.create_line(x - 40, y + 10, x - 10, y + 10, tags=(tag))
        self.canvas.create_line(x - 40, y - 10, x - 40, y + 10, tags=(tag))
        connectors.append(self.canvas.create_oval(x + 35 - CONN_RADIUS, y - CONN_RADIUS, x + 35 + CONN_RADIUS, y + CONN_RADIUS, tags=(tag), outline=""))
        self.itm_cnt += 1
        return tag, connectors
        
    
    def draw_OUT(self, x, y):
        tag = "OUT{}".format(self.itm_cnt)
        connectors = []
        self.canvas.create_line(x - 5, y, x - 35, y, tags=(tag))
        self.canvas.create_line(x + 10, y - 10, x - 5, y, tags=(tag))
        self.canvas.create_line(x + 10, y + 10, x - 5, y, tags=(tag))
        self.canvas.create_line(x + 40, y - 10, x + 10, y - 10, tags=(tag))
        self.canvas.create_line(x + 40, y + 10, x + 10, y + 10, tags=(tag))
        self.canvas.create_line(x + 40, y - 10, x + 40, y + 10, tags=(tag))
        connectors.append(self.canvas.create_oval(x - 35 - CONN_RADIUS, y - CONN_RADIUS, x - 35 + CONN_RADIUS, y + CONN_RADIUS, tags=(tag), outline=""))
        self.itm_cnt += 1
        return tag, connectors
    
    def draw_NOT(self, x, y):
        tag = "NOT{}".format(self.itm_cnt)
        connectors = []
        self.canvas.create_line(x - 40, y, x - 10, y, tags=(tag))
        self.canvas.create_line(x + 11, y, x + 41, y, tags=(tag))
        self.canvas.create_line(x - 10, y - 10, x - 10, y + 10, tags=(tag))
        self.canvas.create_line(x - 10, y - 10, x + 5, y, tags=(tag))
        self.canvas.create_line(x - 10, y + 10, x + 5, y, tags=(tag))
        self.canvas.create_oval(x + 5, y - 3, x + 11, y + 3, tags=(tag))
        connectors.append(self.canvas.create_oval(x - 40 - CONN_RADIUS, y - CONN_RADIUS, x - 40 + CONN_RADIUS, y + CONN_RADIUS, tags=(tag), outline=""))
        connectors.append(self.canvas.create_oval(x + 41 - CONN_RADIUS, y - CONN_RADIUS, x + 41 + CONN_RADIUS, y + CONN_RADIUS, tags=(tag), outline=""))
        self.itm_cnt += 1
        return tag, connectors
    
    def draw_AND2(self, x, y):
        tag = "2AND{}".format(self.itm_cnt)
        connectors = []
        self.canvas.create_line(x - 44, y - 10, x - 14, y - 10, tags=(tag))
        self.canvas.create_line(x - 44, y + 10, x - 14, y + 10, tags=(tag))
        self.canvas.create_line(x + 28, y, x + 58, y, tags=(tag))
        self.canvas.create_line(x - 14, y - 15, x - 14, y + 15, tags=(tag))
        self.canvas.create_line(x - 14, y - 15, x + 13, y - 15, tags=(tag))
        self.canvas.create_line(x - 14, y + 15, x + 13, y + 15, tags=(tag))
        self.canvas.create_arc(x - 2, y - 15, x + 28, y + 15, start=-90, extent=180, style=ARC, tags=(tag))
        connectors.append(self.canvas.create_oval(x - 44 - CONN_RADIUS, y - 10 - CONN_RADIUS, x - 44 + CONN_RADIUS, y - 10 + CONN_RADIUS, tags=(tag), outline=""))
        connectors.append(self.canvas.create_oval(x - 44 - CONN_RADIUS, y + 10 - CONN_RADIUS, x - 44 + CONN_RADIUS, y + 10 + CONN_RADIUS, tags=(tag), outline=""))
        connectors.append(self.canvas.create_oval(x + 58 - CONN_RADIUS, y - CONN_RADIUS, x + 58 + CONN_RADIUS, y + CONN_RADIUS, tags=(tag), outline=""))
        self.itm_cnt += 1
        return tag, connectors

    def draw_OR2(self, x, y):
        tag = "2OR{}".format(self.itm_cnt)
        connectors = []
        self.canvas.create_line(x - 44, y - 10, x - 14, y - 10, tags=(tag))
        self.canvas.create_line(x - 44, y + 10, x - 14, y + 10, tags=(tag))
        self.canvas.create_line(x + 28, y, x + 58, y, tags=(tag))
        self.canvas.create_arc(x - 22, y - 15, x - 12, y + 15, start=-90, extent=180, style=ARC, tags=(tag))
        self.canvas.create_arc(x - 87, y - 15, x + 53, y + 115, start=50, extent=40, style=ARC, tags=(tag))
        self.canvas.create_arc(x - 87, y - 115, x + 53, y + 15, start=-90, extent=40, style=ARC, tags=(tag))
        connectors.append(self.canvas.create_oval(x - 44 - CONN_RADIUS, y - 10 - CONN_RADIUS, x - 44 + CONN_RADIUS, y - 10 + CONN_RADIUS, tags=(tag), outline=""))
        connectors.append(self.canvas.create_oval(x - 44 - CONN_RADIUS, y + 10 - CONN_RADIUS, x - 44 + CONN_RADIUS, y + 10 + CONN_RADIUS, tags=(tag), outline=""))
        connectors.append(self.canvas.create_oval(x + 58 - CONN_RADIUS, y - CONN_RADIUS, x + 58 + CONN_RADIUS, y + CONN_RADIUS, tags=(tag), outline=""))
        self.itm_cnt += 1
        return tag, connectors
