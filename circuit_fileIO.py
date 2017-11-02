import json

class CircuitFileIO(object):
    def __init__(self, master):
        self.master = master
        self.circuit = master.circuit
        self.canvas = master.canvas
        self.wires = master.wires

    def save(self, filename):
        elements = []
        wires = []
        for t in self.circuit.elements:
            elements.append(self.element_to_json(t))
        for t in self.wires:
            wires.append(self.wire_to_json(t))
        json1 = {
            "elements": elements,
            "wires": wires
        }
        with open(filename, "w") as f:
            json.dump(json1, f, indent=4, sort_keys=True)

    def load(self, circ_file):
        None

    def element_to_json(self, tag):
        gate_type = self.canvas.gettags(self.canvas.find_withtag(tag)[0])[1]
        x1, y1, x2, y2 = self.canvas.bbox(tag)
        x = (x1 + x2)/2
        y = (y1 + y2)/2
        inputs = []
        outputs = []
        for e in self.circuit.elements[tag].inputs:
            inputs.append(self.circuit.elements.keys()[self.circuit.elements.values().index(e)])
        for e in self.circuit.elements[tag].next:
            outputs.append(self.circuit.elements.keys()[self.circuit.elements.values().index(e)])
        json1 = {
            "tag": tag,
            "type": gate_type,
            "location": {
                "x": x,
                "y": y
            },
            "inputs": inputs,
            "outputs": outputs
        }
        return json1
    
    def wire_to_json(self, tag):
        wires = []
        if len(self.wires[tag]):
            for i in self.wires[tag]:
                x1, y1, x2, y2 = self.canvas.bbox(i)
                json1 = {
                    "id": i,
                    "coords": {
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2
                    }
                }
                wires.append(json1)
        json2 = {
            "elemTag": tag,
            "wires": wires
        }
        return json2
		 
        
        