from constants import FAIL, BAD_INPUT_NUM, NOT_SET

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
            return NOT_SET
        return self.inputs[0]

class OUT(Gate):
    def output(self):
        if len(self.inputs) != 1:
            return BAD_INPUT_NUM
        o = self.inputs[0].output()
        if o < 0:
            return FAIL
        return o

### GATE CLASSES ###

class NOT(Gate):
    def output(self):
        if len(self.inputs) != 1:
            return BAD_INPUT_NUM
        o = self.inputs[0].output()
        if o < 0:
            return FAIL
        if o == 1:
            return 0
        return 1

class AND2(Gate):
    def output(self):
        if len(self.inputs) != 2:
            return BAD_INPUT_NUM
        for i in self.inputs:
            o = i.output()
            if o < 0:
                return FAIL
            if o == 0:
                return 0
        return 1

class OR2(Gate):
    def output(self):
        if len(self.inputs) != 2:
            return BAD_INPUT_NUM
        for i in self.inputs:
            o = i.output()
            if o < 0:
                return FAIL
            if o == 1:
                return 1
        return 0