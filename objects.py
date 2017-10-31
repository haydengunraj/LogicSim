from Tkinter import END, ARC
from constants import *
from gates import *
from math import hypot

class Handler(object):
    def __init__(self, main):
        self.canvas = main.frame2.canvas
        self.elements = []
        self.gate_mode = None
        self.curs = None
        self.mouse_mode = None
        self.drawing = Drawing(self.canvas)
        self.menu = main.frame1
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
        elif self.mouse_mode == CONNECT:
            None
        else:
            if temp is None:
                None
            else:
                self.drawing.itm_cnt -= 1
                tag = self.drawing.draw(temp, x, y)
                self.elements.append(tag)
                self.circuit.add(temp, tag)
                print self.circuit.elements
    
    def move_handler(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.curs is not None:
            x1, y1, x2, y2 = self.canvas.bbox(self.curs)
            self.canvas.move(self.curs, x - (x2 + x1)/2, y - (y2 + y1)/2)
        else:
            if self.gate_mode is not None and self.mouse_mode is None:
                self.curs = self.drawing.draw(self.gate_mode, x, y)
    
    def drag_handler(self, event):
        None
    
    def release_handler(self, event):
        None
    
    def list_handler(self, event):
        listbox = event.widget
        self.gate_mode = listbox.get(listbox.curselection()[0])
        self.mouse_mode = None
        self.menu.active = [0,0]
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
            activate = False
        else:
            self.menu.mode_buttons[mode].config(highlightbackground="black")
            self.menu.mode_buttons[mode - 1].config(highlightbackground="grey")
            self.menu.active[mode] = 1
            self.menu.active[mode - 1] = 0
            activate = True
        if activate:
            if self.curs is not None:
                self.canvas.delete(self.curs)
                self.curs = None
            self.gate_mode = None
            self.mouse_mode = mode
        else:
            self.mouse_mode = None

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
            i.next.remove(self.elements[tag])
        for n in self.elements[tag].next:
            i.inputs.remove(self.elements[tag])
        del self.elements[tag]
        print self.elements
        
    def connect(self, tag1, tag2):
        None

class Drawing(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self.itm_cnt = 0
        self.draw_fncts = {
            "NOT": self.draw_NOT,
            "AND2": self.draw_AND2,
            "OR2": self.draw_OR2,
        }
    
    def draw(self, element, x, y):
        return self.draw_fncts[element](x, y)
    
    def draw_NOT(self, x, y):
        tag = "tag{}".format(self.itm_cnt)
        self.canvas.create_line(x - 40, y, x - 10, y, tags=(tag))
        self.canvas.create_line(x + 11, y, x + 41, y, tags=(tag))
        self.canvas.create_line(x - 10, y - 10, x - 10, y + 10, tags=(tag))
        self.canvas.create_line(x - 10, y - 10, x + 5, y, tags=(tag))
        self.canvas.create_line(x - 10, y + 10, x + 5, y, tags=(tag))
        self.canvas.create_oval(x + 5, y - 3, x + 11, y + 3, tags=(tag))
        self.itm_cnt += 1
        return tag
    
    def draw_AND2(self, x, y):
        tag = "tag{}".format(self.itm_cnt)
        self.canvas.create_line(x - 44, y - 10, x - 14, y - 10, tags=(tag))
        self.canvas.create_line(x - 44, y + 10, x - 14, y + 10, tags=(tag))
        self.canvas.create_line(x + 28, y, x + 58, y, tags=(tag))
        self.canvas.create_line(x - 14, y - 15, x - 14, y + 15, tags=(tag))
        self.canvas.create_line(x - 14, y - 15, x + 13, y - 15, tags=(tag))
        self.canvas.create_line(x - 14, y + 15, x + 13, y + 15, tags=(tag))
        self.canvas.create_arc(x - 2, y - 15, x + 28, y + 15, start=-90, extent=180, style=ARC, tags=(tag))
        self.itm_cnt += 1
        return tag

    def draw_OR2(self, x, y):
        tag = "tag{}".format(self.itm_cnt)
        self.canvas.create_line(x - 44, y - 10, x - 14, y - 10, tags=(tag))
        self.canvas.create_line(x - 44, y + 10, x - 14, y + 10, tags=(tag))
        self.canvas.create_line(x + 28, y, x + 58, y, tags=(tag))
        self.canvas.create_arc(x - 22, y - 15, x - 12, y + 15, start=-90, extent=180, style=ARC, tags=(tag))
        self.canvas.create_arc(x - 87, y - 15, x + 53, y + 115, start=50, extent=40, style=ARC, tags=(tag))
        self.canvas.create_arc(x - 87, y - 115, x + 53, y + 15, start=-90, extent=40, style=ARC, tags=(tag))
        self.itm_cnt += 1
        return tag
