file_to_read = "code.bin"

with open(file_to_read, "rb") as f:
    bytes_data = f.read()
    # Join each raw byte formatted as a 2-digit hex code with a space
    hex_string = " ".join(f"{b:02X}" for b in bytes_data)
    print(hex_string)