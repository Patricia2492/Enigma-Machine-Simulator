import streamlit as st
from enigma import machine_assembly

st.set_page_config(page_title="Enigma Machine Simulator", layout="wide")

st.title("🔐 Enigma Machine Simulator")
st.caption("Created by Patricia Amores")

# Short historical description of the Enigma Machine
st.markdown(
    "The Enigma machine was a legendary encryption device used by the German"
    " military during World War II to protect their top-secret communications."
    " Think of it like a typewriter connected to a shifting maze of electrical wires:"
    " every time you press a letter key, internal wheels click and rotate."
    " An electrical current zigzags through these spinning wheels and a plugboard,"
    " scrambling your letter into a completely different one. Because the wheels"
    " move with every single keystroke, pressing the same letter twice will never"
    " produce the same output. This makes the code change constantly and look"
    " completely unbreakable at the time. This interactive simulator brings this"
    " historic cryptography engine to life, letting you build custom rotor setups,"
    " adjust ring positions, and test your own encrypted messages."
)
st.markdown("---")
st.markdown("Configure your machine settings below to encrypt or decrypt messages (the exact same configuration must be used for both).")
all_rotors = ["Beta", "Gamma", "I", "II", "III", "IV", "V"]
column_labels = ["Right rotor (1st)", "Middle rotor (2nd)", "Left rotor (3rd)", "Furthest rotor (4th, Optional)"]

for i in range(4):
    if f"rotor_{i}" not in st.session_state:
        st.session_state[f"rotor_{i}"] = ""


st.subheader("Rotor Configuration (Right-to-Left Mechanical Order)")

cols = st.columns(4)

rotor_selections = []
ring_selections = []
pos_selections = []

for i, col in enumerate(cols):
    with col:
        st.markdown(f"**{column_labels[i]}**")
        
        # Find already selected rotors in other columns to exclude them
        other_selected = [st.session_state[f"rotor_{j}"] for j in range(4) if j != i and st.session_state[f"rotor_{j}"] != ""]
        available_options = [""] + [r for r in all_rotors if r not in other_selected]
        
        # Ensure current session state value is valid in options
        current_val = st.session_state[f"rotor_{i}"]
        if current_val not in available_options:
            current_val = ""
            st.session_state[f"rotor_{i}"] = ""

        r = st.selectbox("Select Rotor", available_options, index=available_options.index(current_val), key=f"rotor_{i}")
        ring = st.text_input("Ring (1-26)", value="", key=f"ring_{i}")
        pos = st.text_input("Start Pos (A-Z)", value="", key=f"pos_{i}")
        
        rotor_selections.append(r)
        ring_selections.append(ring)
        pos_selections.append(pos)
    
st.markdown("---")

col_plug, col_ref = st.columns(2)
with col_plug:
    plugboard_input = st.text_input("Plugboard Pairs (write up to 10 pairs of any letter, comma separated, e.g. HL, MO)", "")
with col_ref:
    reflector_input = st.selectbox("Reflector", ["", "A", "B", "C"])

message_input = st.text_input("Message to Encrypt or Decrypt (ALL CAPS)", "")

submitted = st.button("Encrypt or Decrypt Message")

if submitted:
    try:
        rotors = []
        rings = []
        positions = []

        # Collect from Right (index 3) to Left (index 0) to match Enigma mechanical order
        for i in range(3, -1, -1):
            r_val = rotor_selections[i]
            if r_val != "":
                rotors.append(r_val)
                
                ring_val = ring_selections[i].strip()
                if not ring_val.isdigit():
                    raise ValueError(f"Ring setting for {column_labels[i]} must be a valid number.")
                rings.append(int(ring_val))

                pos_val = pos_selections[i].strip().upper()
                if not pos_val.isalpha() or len(pos_val) != 1:
                    raise ValueError(f"Starting position for {column_labels[i]} must be a single letter (A-Z).")
                positions.append(pos_val)

        if not rotors:
            st.error("Please select at least one rotor.")
        elif not reflector_input:
            st.error("Please select a reflector.")
        elif not message_input.strip():
            st.error("Please enter a message to encode.")
        else:
            # Clean plugboard
            plugboard = []
            if plugboard_input.strip():
                pairs = plugboard_input.split(",")
                for p in pairs:
                    p_clean = p.strip().upper()
                    if p_clean:
                        if len(p_clean) != 2 or not p_clean.isalpha():
                            raise ValueError("Plugboard pairs must be two letters separated by commas (e.g. HL, MO).")
                        plugboard.append(p_clean)
                    
            configuration = {
                "rotors": rotors,
                "rings": rings,
                "positions": positions,
                "plugboard": plugboard,
                "reflector": reflector_input
            }

            machine = machine_assembly(configuration)
            encoded_result = machine.encode_message(message_input.strip().upper())

            st.success("Enigma Encryption/Decryption Complete!")
            st.code(encoded_result, language="")

    except Exception as e:
        st.error(f"Configuration Error: {str(e)}")