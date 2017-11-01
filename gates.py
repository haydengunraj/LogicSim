### BASE CLASS ###
class Gate(object):
    def __init__(self):
        self.inputs = []
        self.next = []
    
    def addInput(self, inputGate):
        self.inputs.append(inputGate)
        try:
            inputGate.next.append(self)
        except:
            pass

class Wire(object):
    def __init__(self):
        self.id = 0
        self.tags = []

### INPUT AND OUTPUT CLASSES ###

class IN(Gate):
    def output(self):
        return self.inputs[0]

class OUT(Gate):
    def output(self):
        return self.inputs[0].output()

### GATE CLASSES ###

class NOT(Gate):
    def output(self):
        if self.inputs[0].output():
            return 0
        return 1

class AND2(Gate):
    def output(self):
        for i in self.inputs:
            if i.output() != 1:
                return 0
        return 1

class OR2(Gate):
    def output(self):
        for i in self.inputs:
            if i.output() == 1:
                return 1
        return 0