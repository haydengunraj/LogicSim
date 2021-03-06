from constants import FAIL
### BASE CLASS ###
class Gate(object):
    def __init__(self):
        self.inputs = []
        self.next = []
    
    def add_input(self, input_gate):
        self.inputs.append(input_gate)
        try:
            input_gate.next.append(self)
        except:
            pass

### INPUT AND OUTPUT CLASSES ###

class IN(Gate):
    def output(self):
        if len(self.inputs) != 1:
            return FAIL
        return self.inputs[0]

class OUT(Gate):
    def output(self):
        if len(self.inputs) != 1:
            return FAIL
        return self.inputs[0].output()

### GATE CLASSES ###

class NOT(Gate):
    def output(self):
        if len(self.inputs) != 1:
            return FAIL
        if self.inputs[0].output() == 1:
            return 0
        return 1

class AND2(Gate):
    def output(self):
        if len(self.inputs) != 2:
            return FAIL
        for i in self.inputs:
            if i.output() == 0:
                return 0
        return 1

class OR2(Gate):
    def output(self):
        if len(self.inputs) != 2:
            return FAIL
        for i in self.inputs:
            if i.output() == 1:
                return 1
        return 0