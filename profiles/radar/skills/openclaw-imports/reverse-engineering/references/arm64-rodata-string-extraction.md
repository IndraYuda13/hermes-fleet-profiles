# Extracting Strings from ARM64 JNI .so files (.rodata)

When a native library exports JNI functions that just return a hardcoded string (common in obfuscation wrappers like Spice/Cardamom), the string is typically stored in the `.rodata` section. The function loads its address using a PC-relative `adrp` + `add` instruction pair and passes it to `NewStringUTF`.

You can extract these strings statically using Python and Capstone, avoiding the need for an emulator, Frida, or Ghidra decompilation.

## Python Extraction Script

```python
import struct
from capstone import *
import subprocess

SO_PATH = "libcardamom.so"

with open(SO_PATH, "rb") as f:
    data = f.read()

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

def get_exports():
    res = subprocess.run(["nm", "-D", SO_PATH], capture_output=True, text=True)
    exports = {}
    for line in res.stdout.split("\n"):
        parts = line.split()
        if len(parts) >= 3 and parts[1] == "T" and "Java_" in parts[2]:
            addr = int(parts[0], 16)
            exports[parts[2]] = addr
    return exports

def read_adrp_add(func_data, pc):
    # adrp format
    adrp_bytes = struct.unpack('<I', func_data[:4])[0]
    immlo = (adrp_bytes >> 29) & 0x3
    immhi = (adrp_bytes >> 5) & 0x7FFFF
    imm = (immhi << 2) | immlo
    if imm & (1 << 20): imm -= (1 << 21) # Sign extend
    page_offset = imm << 12
    
    # add format
    add_bytes = struct.unpack('<I', func_data[4:8])[0]
    add_imm = (add_bytes >> 10) & 0xFFF
    shift = (add_bytes >> 22) & 0x1
    if shift: add_imm <<= 12
        
    return page_offset, add_imm

exports = get_exports()
for name, addr in exports.items():
    # Disassemble first ~100 bytes of the function to find adrp
    func_code = data[addr:addr+100]
    adrp_addr = None
    for inst in md.disasm(func_code, addr):
        if inst.mnemonic == "adrp":
            adrp_addr = inst.address
            break
            
    if adrp_addr:
        # Get the 8 bytes for adrp + add
        adrp_offset = adrp_addr
        func_bytes = data[adrp_offset:adrp_offset+8]
        
        page_off, add_imm = read_adrp_add(func_bytes, adrp_addr)
        
        # Calculate target: (pc & ~0xFFF) + page_offset + add_imm
        pc_page = adrp_addr & ~0xFFF
        target = pc_page + page_off + add_imm
        
        # Read null-terminated string at target
        raw = data[target:target+128] # guess max size
        try:
            text = raw.split(b'\x00')[0].decode('ascii')
            print(f"{name}: {text}")
        except:
            print(f"{name}: [Binary/Hex] {raw.split(b'\x00')[0].hex()}")
```

## How It Works
1. `nm -D` finds the starting offset of exported JNI functions (e.g. `Java_com_example_getApiKey`).
2. `capstone` disassembles the function to locate the `adrp` instruction.
3. The script decodes the `adrp` (Address of Page) and subsequent `add` immediate values.
4. The target file offset is computed as `(PC & ~0xFFF) + page_offset + add_offset`.
5. The string is read directly from that offset in the binary.