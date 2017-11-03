from Tkinter import *
from math import hypot
from constants import *
from gates import *
from save_load import CircuitFileIO ## TEST

class Handler(object):
    def __init__(self, main):
        self.main = main
        self.canvas = self.main.frame2.canvas
        self.aliases = {}
        self.connectors = []
        self.wires = {}
        self.gate_mode = None
        self.curs = None
        self.mouse_mode = None
        
        ### VARIABLES/FLAGS FOR DRAWING WIRES
        self.highlighted = 0
        self.dyn_id = 0
        self.dyn_tag = None
        self.output_conn = False
        
        self.drawing = Drawing(self.canvas)
        self.menu = self.main.frame1
        self.circuit = Circuit(self)
        
        self.io = CircuitFileIO(self)
        self.save = self.io.save
        self.load = self.io.load
    
    def click_handler(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
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
                    del self.aliases[closest_item]
        elif self.mouse_mode == CONNECT:
            if self.highlighted:
                x1, y1, x2, y2 = self.canvas.coords(self.highlighted)
                if self.dyn_id:
                    if self.dyn_tag == self.canvas.gettags(self.highlighted)[0]:
                        self.canvas.delete(self.dyn_id)
                        self.dyn_id = 0
                        self.dyn_tag = None
                    else:
                        xd1, yd1, xd2, yd2 = self.canvas.coords(self.dyn_id)
                        tag = self.canvas.gettags(self.highlighted)[0]
                        self.canvas.coords(self.dyn_id, xd1, yd1, (x1 + x2)/2, (y1 + y2)/2)
                        if self.output_conn:
                            self.circuit.connect(self.dyn_tag, tag)
                        else:
                            self.circuit.connect(self.dyn_tag, tag, forward=False)
                        self.wires[self.dyn_tag].append(self.dyn_id)
                        self.wires[tag].append(self.dyn_id)
                        self.dyn_id = 0
                        self.dyn_tag = None
                else:
                    tag = self.canvas.gettags(self.highlighted)[0]
                    self.dyn_tag = tag
                    self.dyn_id = self.canvas.create_line((x1 + x2)/2, (y1 + y2)/2, (x1 + x2)/2, (y1 + y2)/2)
                    xb1, yb1, xb2, yb2 = self.canvas.bbox(tag)
                    self.output_conn = (int(x2) == xb2)
                self.canvas.itemconfig(self.highlighted, fill="")
                self.highlighted = 0
            elif self.dyn_id:
                self.canvas.delete(self.dyn_id)
                self.dyn_id = 0
                self.dyn_tag = None
        elif self.mouse_mode == RENAME:
            closest_item = self.canvas.gettags(self.canvas.find_closest(x, y))
            if len(closest_item) > 0:
                closest_item = closest_item[0]
                x1, y1, x2, y2 = self.canvas.bbox(closest_item)
                if isinstance(self.circuit.elements[closest_item], IN) or isinstance(self.circuit.elements[closest_item], OUT) and x > x1 and x < x2 and y > y1 and y < y2:
                    uin = self.main.input_box(self.main, "Set Name", "Set")
                    self.main.wait_window(uin.top)
                    try:
                        self.aliases[closest_item] = uin.value
                        s = "{}".format(uin.value)
                        self.canvas.itemconfig(self.canvas.find_withtag(closest_item)[-1], text=s)
                    except AttributeError:
                        pass
        else:
            if self.gate_mode is not None:
                self.drawing.decrement(self.curs)
                self.canvas.delete(self.curs)
                tag, connectors = self.drawing.draw(self.gate_mode, x, y)
                self.connectors.extend(connectors)
                self.aliases[tag] = tag
                self.circuit.add(self.gate_mode, tag)
                self.wires[tag] = []
                self.menu.listbox.selection_clear(0, END)
                self.curs = None
                self.gate_mode = None
            else:
                None # for drag/drop function
    
    def move_handler(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.mouse_mode == CONNECT:
            if self.dyn_id:
                xd1, yd1, xd2, yd2 = self.canvas.coords(self.dyn_id)
                self.canvas.coords(self.dyn_id, xd1, yd1, x, y)
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
        None # for drag/drop function
    
    def release_handler(self, event):
        None # for drag/drop function
    
    def list_handler(self, event):
        listbox = event.widget
        self.gate_mode = listbox.get(listbox.curselection()[0])
        self.mouse_mode = None
        self.menu.active = [0, 0, 0, 0, 0, 0, 0]
        for btn in self.menu.mode_buttons:
            btn.config(highlightbackground="grey") 
        if self.curs is not None:
            self.canvas.delete(self.curs)
            self.curs = None
    
    def mode_handler(self, mode):
        if self.menu.active[mode]:
            self.menu.mode_buttons[mode].config(highlightbackground="grey")
            self.menu.active[mode] = 0
            self.mouse_mode = None
            if mode == CONNECT:
                self.toggle_CONNECT()
        else:
            self.menu.mode_buttons[mode].config(highlightbackground="black")
            self.menu.active[mode] = 1
            self.menu.listbox.selection_clear(0, END)
            self.gate_mode = None
            self.mouse_mode = mode
            for i in range(len(self.menu.mode_buttons)):
                if i != mode:
                    self.menu.mode_buttons[i].config(highlightbackground="grey")
                    self.menu.active[i] = 0
            if self.curs is not None:
                self.canvas.delete(self.curs)
                self.curs = None
            if mode == DELETE:
                self.toggle_CONNECT()
            elif mode == CLEAR:
                None # clear the circuit
            elif mode == TRUTH:
                self.toggle_CONNECT()
                tab = self.main.truth_table(self.main, self.circuit)
                try:
                    self.main.wait_window(tab.top)
                except AttributeError:
                    pass
                self.menu.mode_buttons[TRUTH].config(highlightbackground="grey")
                self.menu.active[TRUTH] = 0
            elif mode == SAVE:
                uin = self.main.input_box(self.main, "Set Filename", "Save")
                self.main.wait_window(uin.top)
                try:
                    filename = "{}.json".format(uin.value)
                    self.save(filename)
                except AttributeError:
                    pass
                self.menu.mode_buttons[SAVE].config(highlightbackground="grey")
                self.menu.active[SAVE] = 0
            elif mode == LOAD:
                None # load circuit from JSON
                # self.menu.mode_buttons[LOAD].config(highlightbackground="grey")
                # self.menu.active[LOAD] = 0
                
    def toggle_CONNECT(self):
        if self.dyn_id:
            self.canvas.delete(self.dyn_id)
            self.dyn_id = 0
            self.dyn_tag = None
        if self.highlighted:
            self.canvas.itemconfig(self.highlighted, fill="")
            self.highlighted = 0

class Circuit(object):
    def __init__(self, master):
        self.master = master
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
            try:
                i.inputs.remove(self.elements[tag])
            except:
                pass
        del self.elements[tag]
        
    def connect(self, tag1, tag2, forward=True):
        if forward:
            self.elements[tag2].add_input(self.elements[tag1])
        else:
            self.elements[tag1].add_input(self.elements[tag2])
    
    def simulate(self):
        output_vals = {}
        for t in self.elements:
            if isinstance(self.elements[t], OUT):
                output = self.elements[t].output()
                if output == FAIL:
                    return FAIL
                output_vals[t] = output
        return output_vals
    
    def truth_table(self):
        input_gates = []
        output_gates = []
        output_sets = []
        for t in self.elements:
            if isinstance(self.elements[t], IN):
                input_gates.append(t)
        input_gates.sort()
        if not len(input_gates):
            return FAIL
        for i in range(2**len(input_gates)):
            bi = [int(v) for v in list(format(i, "0{}b".format(len(input_gates))))]
            for j in range(len(bi)):
                self.elements[input_gates[j]].inputs = []
                self.elements[input_gates[j]].add_input(bi[j])
            res = self.simulate()
            if res == FAIL or not len(res):
                return FAIL
            c = 0
            s = []
            for t in res:
                if t not in output_gates:
                    output_gates.append(t)
                s.append(res[t])
            output_sets.append(s)
        return input_gates, output_gates, output_sets

class Drawing(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self.gate_cnt = 0
        self.in_cnt = 0
        self.out_cnt = 0
        self.draw_fncts = {
            "INPUT": self.draw_IN,
            "OUTPUT": self.draw_OUT,
            "NOT": self.draw_NOT,
            "AND2": self.draw_AND2,
            "OR2": self.draw_OR2,
        }
    
    def draw(self, element, x, y):
        return self.draw_fncts[element](x, y)
    
    def decrement(self, tag):
        tags = self.canvas.gettags(self.canvas.find_withtag(tag)[0])
        if "IN" in tags:
            self.in_cnt -= 1
        elif "OUT" in tags:
            self.out_cnt -= 1
        else:
            self.gate_cnt -= 1
    
    def draw_IN(self, x, y):
        tags = ("I{}".format(self.in_cnt), "IN")
        connectors = []
        self.canvas.create_line(x + 5, y, x + 35, y, tags=tags)
        self.canvas.create_line(x - 10, y - 10, x + 5, y, tags=tags)
        self.canvas.create_line(x - 10, y + 10, x + 5, y, tags=tags)
        self.canvas.create_line(x - 40, y - 10, x - 10, y - 10, tags=tags)
        self.canvas.create_line(x - 40, y + 10, x - 10, y + 10, tags=tags)
        self.canvas.create_line(x - 40, y - 10, x - 40, y + 10, tags=tags)
        connectors.append(self.canvas.create_oval(x + 35 - CONN_RADIUS, y - CONN_RADIUS, x + 35 + CONN_RADIUS, y + CONN_RADIUS, tags=tags, outline=""))
        self.canvas.create_text(x - 37, y - 6, text=tags[0], font=("Times", 12), anchor="nw", tags=tags+("text",))
        self.in_cnt += 1
        return tags[0], connectors
        
    
    def draw_OUT(self, x, y):
        tags = ("O{}".format(self.out_cnt), "OUT")
        connectors = []
        self.canvas.create_line(x - 5, y, x - 35, y, tags=tags)
        self.canvas.create_line(x + 10, y - 10, x - 5, y, tags=tags)
        self.canvas.create_line(x + 10, y + 10, x - 5, y, tags=tags)
        self.canvas.create_line(x + 40, y - 10, x + 10, y - 10, tags=tags)
        self.canvas.create_line(x + 40, y + 10, x + 10, y + 10, tags=tags)
        self.canvas.create_line(x + 40, y - 10, x + 40, y + 10, tags=tags)
        connectors.append(self.canvas.create_oval(x - 35 - CONN_RADIUS, y - CONN_RADIUS, x - 35 + CONN_RADIUS, y + CONN_RADIUS, tags=tags, outline=""))
        self.canvas.create_text(x + 37, y - 6, text=tags[0], font=("Times", 12), anchor="ne", tags=tags+("text",))
        self.out_cnt += 1
        return tags[0], connectors
    
    def draw_NOT(self, x, y):
        tags = ("NOT{}".format(self.gate_cnt), "NOT")
        connectors = []
        self.canvas.create_line(x - 40, y, x - 10, y, tags=tags)
        self.canvas.create_line(x + 11, y, x + 41, y, tags=tags)
        self.canvas.create_line(x - 10, y - 10, x - 10, y + 10, tags=tags)
        self.canvas.create_line(x - 10, y - 10, x + 5, y, tags=tags)
        self.canvas.create_line(x - 10, y + 10, x + 5, y, tags=tags)
        self.canvas.create_oval(x + 5, y - 3, x + 11, y + 3, tags=tags)
        connectors.append(self.canvas.create_oval(x - 40 - CONN_RADIUS, y - CONN_RADIUS, x - 40 + CONN_RADIUS, y + CONN_RADIUS, tags=tags, outline=""))
        connectors.append(self.canvas.create_oval(x + 41 - CONN_RADIUS, y - CONN_RADIUS, x + 41 + CONN_RADIUS, y + CONN_RADIUS, tags=tags, outline=""))
        self.gate_cnt += 1
        return tags[0], connectors
    
    def draw_AND2(self, x, y):
        tags = ("2AND{}".format(self.gate_cnt), "AND2")
        connectors = []
        self.canvas.create_line(x - 44, y - 10, x - 14, y - 10, tags=tags)
        self.canvas.create_line(x - 44, y + 10, x - 14, y + 10, tags=tags)
        self.canvas.create_line(x + 28, y, x + 58, y, tags=tags)
        self.canvas.create_line(x - 14, y - 15, x - 14, y + 15, tags=tags)
        self.canvas.create_line(x - 14, y - 15, x + 13, y - 15, tags=tags)
        self.canvas.create_line(x - 14, y + 15, x + 13, y + 15, tags=tags)
        self.canvas.create_arc(x - 2, y - 15, x + 28, y + 15, start=-90, extent=180, style=ARC, tags=tags)
        connectors.append(self.canvas.create_oval(x - 44 - CONN_RADIUS, y - 10 - CONN_RADIUS, x - 44 + CONN_RADIUS, y - 10 + CONN_RADIUS, tags=tags, outline=""))
        connectors.append(self.canvas.create_oval(x - 44 - CONN_RADIUS, y + 10 - CONN_RADIUS, x - 44 + CONN_RADIUS, y + 10 + CONN_RADIUS, tags=tags, outline=""))
        connectors.append(self.canvas.create_oval(x + 58 - CONN_RADIUS, y - CONN_RADIUS, x + 58 + CONN_RADIUS, y + CONN_RADIUS, tags=tags, outline=""))
        self.gate_cnt += 1
        return tags[0], connectors

    def draw_OR2(self, x, y):
        tags = ("2OR{}".format(self.gate_cnt), "OR2")
        connectors = []
        self.canvas.create_line(x - 44, y - 10, x - 14, y - 10, tags=tags)
        self.canvas.create_line(x - 44, y + 10, x - 14, y + 10, tags=tags)
        self.canvas.create_line(x + 28, y, x + 58, y, tags=tags)
        self.canvas.create_arc(x - 22, y - 15, x - 12, y + 15, start=-90, extent=180, style=ARC, tags=tags)
        self.canvas.create_arc(x - 87, y - 15, x + 53, y + 115, start=50, extent=40, style=ARC, tags=tags)
        self.canvas.create_arc(x - 87, y - 115, x + 53, y + 15, start=-90, extent=40, style=ARC, tags=tags)
        connectors.append(self.canvas.create_oval(x - 44 - CONN_RADIUS, y - 10 - CONN_RADIUS, x - 44 + CONN_RADIUS, y - 10 + CONN_RADIUS, tags=tags, outline=""))
        connectors.append(self.canvas.create_oval(x - 44 - CONN_RADIUS, y + 10 - CONN_RADIUS, x - 44 + CONN_RADIUS, y + 10 + CONN_RADIUS, tags=tags, outline=""))
        connectors.append(self.canvas.create_oval(x + 58 - CONN_RADIUS, y - CONN_RADIUS, x + 58 + CONN_RADIUS, y + CONN_RADIUS, tags=tags, outline=""))
        self.gate_cnt += 1
        return tags[0], connectors
