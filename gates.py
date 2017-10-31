### BASE CLASS ###
class Gate(object):
    def __init__(self):
        self.inputs = []
        self.next = []
    
    def addInput(self, inputGate):
        self.inputs.append(inputGate)
        inputGate.next.append(self)
        
    def operate(self):
        return self.output()

### INPUT AND OUTPUT CLASSES ###

class IN(Gate):
    def output(self):
        return self.inputs[0]

class OUT(Gate):
    def output(self):
        return self.inputs[0].operate()

### GATE CLASSES ###

class NOT(Gate):
    def output(self):
        if self.inputs[0].operate():
            return 0
        return 1

class AND2(Gate):
    def output(self):
        for i in self.inputs:
            if i.operate() != 1:
                return 0
        return 1

class OR2(Gate):
    def output(self):
        for i in self.inputs:
            if i.operate() == 1:
                return 1
        return 0

"""circ = Circuit()
circ.addInput("A", 1)
circ.addInput("B", 0)
circ.addInput("C", 1)
circ.addOR("D")
circ.setInputs("D", "A", "B")
circ.addAND("E", "D", "C")
circ.addOutput("F", "E")
circ.test()"""