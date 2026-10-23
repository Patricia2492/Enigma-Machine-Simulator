wirings = {
    "Beta": "LEYJVCNIXWPBQMDRTAKZGFUHOS",
    "Gamma": "FSOKANUERHMBTIYCWLQPZXVGJD",
    "I": "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
    "II": "AJDKSIRUXBLHWTMCQGZNPYFVOE",
    "III": "BDFHJLCPRTXVZNYEIWGAKMUSQO",
    "IV": "ESOVPZJAYQUIRHXLNFTGKDCMWB",
    "V": "VZBRGITYUPSDNHLXAWMJQOFECK"}

notches = {
    "I": "Q",
    "II": "E",
    "III": "V",
    "IV": "J",
    "V": "Z",
    "Beta": None,
    "Gamma": None}

reflectors = {
    "A": "EJMZALYXVBWFCRQUONTSPIKHGD",
    "B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    "C": "FVPJIAOYEDRZXWGCTKUQSBNMHL"}

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class PlugLead:
    def __init__(self, mapping):
        if len(mapping) != 2:
            raise ValueError("PlugLead should only contain exactly 2 letters.")

        if not mapping.isalpha() or not mapping.isupper(): 
            raise ValueError("PlugLead must only contain uppercase letters A-Z.")

        if mapping [0] == mapping[1]:
            raise ValueError("PlugLead cannot connect to the same letter.")

        self.mapping = mapping
        

    def encode(self, c):
        if c == self.mapping[0]:
            return self.mapping[1]
        if c == self.mapping[1]:
            return self.mapping [0]

        return c
        

class Plugboard:
    def __init__(self):
        self.leads = []
        self.used_letters = set()
        
    def add(self, lead): 
        if len(self.leads) >= 10:
            raise ValueError("Plugboard only allows maximum 10  leads.")

        a, b = lead.mapping[0], lead.mapping[1]

        if a in self.used_letters or b in self.used_letters:
            raise ValueError(f"Letter conflict: {a} or {b} already connected.")

        self.leads.append(lead)
        self.used_letters.add(a)
        self.used_letters.add(b)

    def encode(self, c):
        for lead in self.leads:
            swapped = lead.encode(c)
            if swapped != c:
                return swapped
        return c

        
class Rotor:
    def __init__(self, name, wiring, notch=None, ring_setting=1, initial_position='A', is_reflector=False):
        self.name = name
        self.wiring = wiring
        self.notch = notch
        self.is_reflector = is_reflector

        #convert ring setting (1-26) to 0-25
        self.ring_setting = ring_setting - 1

        #convert initial position letter to 0-25
        self.position = ord(initial_position.upper()) - ord('A')
              

    def step(self):
        #reflectors do NOT step 
        if not self.is_reflector:
            self.position = (self.position + 1) % 26

    def at_notch(self):
        #reflectors have no notch
        if self.is_reflector or self.notch is None:
            return False
            
        #current letter shown in the rotor window
        current_letter = chr(self.position + ord('A'))
        return current_letter == self.notch

    def forward_encode(self, c):
        #Convert input letter to index
        index = ord(c) - ord('A')

        #reflectors do not rotate or use ring settings; they are direct substitution pairs
        if self.is_reflector:
            return self.wiring[index]

        #compute net offset (rotor's current position minus ring setting)
        offset = self.position - self.ring_setting

        #shift input forward
        shift_in = (index + offset) % 26

        #pass through wiring
        mapped_char = self.wiring[shift_in]
        mapped_index = ord(mapped_char) - ord('A')

        #shift output backward
        shift_out = (mapped_index - offset) % 26

        #convert back to letter
        return chr(shift_out + ord('A'))
       

    def backward_encode(self, c):
        index = ord(c) - ord('A')
        offset = self.position - self.ring_setting

        #shift input letter index by offset
        shift_in = (index + offset) % 26
        target_char = alphabet[shift_in]

        #find the pin in wiring that maps to this character
        mapped_index = self.wiring.index(target_char)

        shift_out = (mapped_index - offset) % 26
        return alphabet[shift_out]
    

class EnigmaMachine:
    def __init__(self, rotors, reflector, plugboard):
        self.rotors = rotors        #list of rotor objects
        self.reflector = reflector  #reflector rotor object
        self.plugboard = plugboard  #plugboard object
        
    def step_rotors(self):
        if len(self.rotors) >= 3:
            mid_at_notch = self.rotors[1].at_notch()
            right_at_notch = self.rotors[0].at_notch()
            self.rotors[0].step()

            if mid_at_notch or right_at_notch: 
                self.rotors[1].step()
            
            if mid_at_notch: 
                self.rotors[2].step()

        elif len(self.rotors) == 2: 
            if self.rotors[0].at_notch():
                self.rotors[1].step()
            self.rotors[0].step()
        else:
            self.rotors[0].step()
        
    def encode_character(self, c): 
        if not c.isalpha():
            return c
        c = c.upper()

        #step rotors first
        self.step_rotors()

        #plugboard entry
        c = self.plugboard.encode(c)

        #rotors pass from right to left
        for r in self.rotors:
            c = r.forward_encode(c)

        #reflector pass
        c = self.reflector.forward_encode(c)

        #rotors pass from left to right
        for r in reversed(self.rotors):
            c = r.backward_encode(c)

        #plugboard exit
        c = self.plugboard.encode(c)
        
        return c
        
    def encode_message(self, text):
       return "".join(self.encode_character(c) for c in text)
    

def machine_assembly(configuration):
    plugboard = Plugboard()
    for pair in configuration["plugboard"]:
        plugboard.add(PlugLead(pair))


    #create reflector object
    rfl_name = configuration["reflector"]
    reflector = Rotor(rfl_name, reflectors[rfl_name], is_reflector=True)

    #instantiate rotor objects
    rotor_selection = []
    for name, ring, pos  in  zip(configuration["rotors"], configuration["rings"], configuration["positions"]):
        rotor_selection.append(Rotor(name, wirings[name], notches[name], ring_setting=ring, initial_position=pos, is_reflector=False))
    
    return EnigmaMachine(rotor_selection, reflector, plugboard)

if __name__ == "__main__":

#Use configuration to input machine settings   
#Rotors need to be inputted backwards as the enigma machine passes from right to left
    configuration = {
        "rotors": [],               #e.g. ["I", "II", "III"]
        "rings": [],                #e.g. [1, 1, 1]
        "positions": [],            #e.g. ["A", "A", "Z"]
        "plugboard":[],             #e.g. [AG", "CX", "NI"]
        "reflector":""}              #e.g "B"

    machine = machine_assembly(configuration)
    print(machine.encode_message("INPUT_TEXT_HERE"))
        
