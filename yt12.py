"""
Badger-8: A self-contained 8-bit CPU simulator.

This is the student template.  You must implement the functions below;
do not change their names or signatures.
"""

from debugger_b8 import debugger, print_registers
from helpers_b8 import *

# ============================================================================
#
# TODO (Task 1): implement the following 8-bit arithmetic and logic functions.
# Use the half_add / full_add / half_sub / full_sub / multiplex_four_to_one
# building blocks provided in badger4.py as your starting point.
#
#   eight_bit_add(a7..a0, b7..b0, c0)        → (carry_out, s7..s0)
#   eight_bit_sub(x7..x0, y7..y0, b0)        → (borrow_out, d7..d0)
#   eight_bit_and(a7..a0, b7..b0)            → (r7..r0)
#   eight_bit_not(a7..a0)                    → (r7..r0)
#   eight_bit_multiplex_four_to_one(         → (z7..z0)
#       a7..a0, b7..b0, c7..c0, d7..d0,
#       s1, s0)
#
# You may also keep any helper functions you need (half_add, full_add, etc.)
# see badger4.py / lecture16.py / lecture17.py
# ============================================================================

def alu(a7, a6, a5, a4, a3, a2, a1, a0, b7, b6, b5, b4, b3, b2, b1, b0, f1, f0, opcode1, opcode0):
  """
  4-opcode 8-bit ALU.

  Opcodes (opcode1, opcode0):
    0 0 = ADD   (use f1 as carry-in)
    0 1 = SUB   (use f1 as borrow-in)
    1 0 = AND
    1 1 = NOT   (operates on first operand only)

  f1 = carry/borrow flag in,  f0 = zero flag in (unused by ALU logic itself).

  Returns: (carry_flag_out, zero_flag_out, r7, r6, r5, r4, r3, r2, r1, r0)
    carry_flag_out  — carry out for ADD, borrow out for SUB, unchanged otherwise
    zero_flag_out   — 1 when the result is all zeros
  """
  # TODO (Task 1): implement this function using your eight_bit_* functions above.
  pass


# ============================================================================
# badger-8 CPU Implementation
# ============================================================================

def sel_register(register_file, sel3, sel2, sel1, sel0):
  """Select a register from the register file using a 4-bit selector."""
  return register_file[bits_to_integer([sel3, sel2, sel1, sel0])]

def eight_bit_add_no_carry(a7, a6, a5, a4, a3, a2, a1, a0, b7, b6, b5, b4, b3, b2, b1, b0):
  """8-bit adder ignoring carry in/out — used for IP arithmetic."""
  _, s7, s6, s5, s4, s3, s2, s1, s0 = eight_bit_add(a7, a6, a5, a4, a3, a2, a1, a0, b7, b6, b5, b4, b3, b2, b1, b0, 0)
  return s7, s6, s5, s4, s3, s2, s1, s0

def sixteen_bit_add_no_carry(a15, a14, a13, a12, a11, a10, a9, a8, a7, a6, a5, a4, a3, a2, a1, a0,
                              b15, b14, b13, b12, b11, b10, b9, b8, b7, b6, b5, b4, b3, b2, b1, b0):
  """16-bit adder (two chained 8-bit adds) ignoring carry out — used for CS:IP fetch."""
  c, s7, s6, s5, s4, s3, s2, s1, s0 = eight_bit_add(a7, a6, a5, a4, a3, a2, a1, a0, b7, b6, b5, b4, b3, b2, b1, b0, 0)
  _, s15, s14, s13, s12, s11, s10, s9, s8 = eight_bit_add(a15, a14, a13, a12, a11, a10, a9, a8, b15, b14, b13, b12, b11, b10, b9, b8, c)
  return s15, s14, s13, s12, s11, s10, s9, s8, s7, s6, s5, s4, s3, s2, s1, s0

def _bits_to_int(bits):
    value = 0
    for b in bits:
        value = (value << 1) | b
    return value


def _int_to_bits(value, width=8):
    value = value % (2 ** width)
    return tuple((value >> i) & 1 for i in range(width - 1, -1, -1))


def eight_bit_add(a7, a6, a5, a4, a3, a2, a1, a0,
                  b7, b6, b5, b4, b3, b2, b1, b0, c_in):
    a = _bits_to_int((a7, a6, a5, a4, a3, a2, a1, a0))
    b = _bits_to_int((b7, b6, b5, b4, b3, b2, b1, b0))
    total = a + b + c_in
    carry = 1 if total > 255 else 0
    return (carry,) + _int_to_bits(total, 8)


def eight_bit_sub(x7, x6, x5, x4, x3, x2, x1, x0,
                  y7, y6, y5, y4, y3, y2, y1, y0, b_in):
    x = _bits_to_int((x7, x6, x5, x4, x3, x2, x1, x0))
    y = _bits_to_int((y7, y6, y5, y4, y3, y2, y1, y0))
    result = x - y - b_in
    borrow = 1 if result < 0 else 0
    return (borrow,) + _int_to_bits(result, 8)


def eight_bit_and(a7, a6, a5, a4, a3, a2, a1, a0,
                  b7, b6, b5, b4, b3, b2, b1, b0):
    return (
        a7 & b7, a6 & b6, a5 & b5, a4 & b4,
        a3 & b3, a2 & b2, a1 & b1, a0 & b0
    )


def eight_bit_not(a7, a6, a5, a4, a3, a2, a1, a0):
    return (
        1 - a7, 1 - a6, 1 - a5, 1 - a4,
        1 - a3, 1 - a2, 1 - a1, 1 - a0
    )


def eight_bit_multiplex_four_to_one(
    a7, a6, a5, a4, a3, a2, a1, a0,
    b7, b6, b5, b4, b3, b2, b1, b0,
    c7, c6, c5, c4, c3, c2, c1, c0,
    d7, d6, d5, d4, d3, d2, d1, d0,
    s1, s0
):
    a = (a7, a6, a5, a4, a3, a2, a1, a0)
    b = (b7, b6, b5, b4, b3, b2, b1, b0)
    c = (c7, c6, c5, c4, c3, c2, c1, c0)
    d = (d7, d6, d5, d4, d3, d2, d1, d0)

    selector = (s1, s0)

    if selector == (0, 0):
        return a
    if selector == (0, 1):
        return b
    if selector == (1, 0):
        return c
    return d


def alu(a7, a6, a5, a4, a3, a2, a1, a0,
        b7, b6, b5, b4, b3, b2, b1, b0,
        f1, f0, opcode1, opcode0):

    a = (a7, a6, a5, a4, a3, a2, a1, a0)
    b = (b7, b6, b5, b4, b3, b2, b1, b0)

    if opcode1 == 0 and opcode0 == 0:
        result = eight_bit_add(*a, *b, 0)
        carry = result[0]
        z = result[1:]

    elif opcode1 == 0 and opcode0 == 1:
        result = eight_bit_sub(*a, *b, 0)
        carry = result[0]
        z = result[1:]

    elif opcode1 == 1 and opcode0 == 0:
        carry = 0
        z = eight_bit_and(*a, *b)

    else:
        carry = 0
        z = eight_bit_not(*a)

    zero = 1 if all(bit == 0 for bit in z) else 0
    return (carry, zero) + tuple(z)

def cpu(memory, debug=False):
  """Execute a program loaded into memory on the Badger-8 CPU."""

  al = Register(8, "al")
  ah = Register(8, "ah")
  bl = Register(8, "bl")
  bh = Register(8, "bh")
  cl = Register(8, "cl")
  ch = Register(8, "ch")
  dl = Register(8, "dl")
  dh = Register(8, "dh")
  cs = Register(8, "cs")
  ds = Register(8, "ds")
  inp = Register(8, "inp")
  out = Register(8, "out")
  flags = Register(8, "flags")
  ip = Register(8, "ip")

  register_file = [
    al, ah, bl, bh,
    cl, ch, dl, dh,
    cs, ds, inp, out,
    None, None,
    flags, ip
  ]

  if not debug:
    start_keyboard_hardware(flags, inp)

  while True:
    if bit(flags.read(), 7) == 1:
      break

    address = cs.read() + ip.read()
    opcode = memory.read(address)

    next_ip = eight_bit_add_no_carry(*ip.read(), *integer_to_bits(1, 8))
    operand_address = cs.read() + list(next_ip)
    operand = memory.read(operand_address)

    if debug:
      if not debugger(al, ah, bl, bh, cl, ch, dl, dh, cs, ds, inp, out, flags, ip, opcode, operand, memory):
        break

    mode = opcode[0]
    op = bits_to_integer(opcode[1:4])
    target_number = bits_to_integer(opcode[4:8])
    target = register_file[target_number]

    if mode == 0:
      source_number = bits_to_integer(operand[0:4])
      source = register_file[source_number]
      value = source.read()
    else:
      value = operand

    jumped = False

    if op == 7:
      # Task 3: jumps
      # mode 0 = JE register
      # mode 1 = JA register
      zf = bit(flags.read(), 0)
      cf = bit(flags.read(), 1)

      if mode == 0:
        if zf == 1:
          ip.write(target.read().copy())
          jumped = True
      else:
        if zf == 0 and cf == 0:
          ip.write(target.read().copy())
          jumped = True

    elif op == 0:
      result = alu(*target.read(), *value, 0, 0, 0, 0)
      set_flag(flags, 1, result[0])
      set_flag(flags, 0, result[1])
      target.write(list(result[2:]))

    elif op == 1:
      result = alu(*target.read(), *value, 0, 0, 0, 1)
      set_flag(flags, 1, result[0])
      set_flag(flags, 0, result[1])
      target.write(list(result[2:]))

    elif op == 2:
      result = alu(*target.read(), *value, 0, 0, 1, 0)
      set_flag(flags, 1, result[0])
      set_flag(flags, 0, result[1])
      target.write(list(result[2:]))

    elif op == 3:
      if mode == 0:
        result = alu(*target.read(), *value, 0, 0, 1, 1)
        set_flag(flags, 1, result[0])
        set_flag(flags, 0, result[1])
        target.write(list(result[2:]))
      else:
        pass

    elif op == 4:
      target.write(value.copy())

      if target.name == "out":
        print(chr(bits_to_integer(target.read())), end="", flush=True)
        set_flag(flags, 3, 1)

      if target.name == "inp":
        set_flag(flags, 2, 0)

    elif op == 5:
      address = ds.read() + value
      target.write(memory.read(address))

    elif op == 6:
      address = ds.read() + value
      memory.write(address, target.read().copy())

    if not jumped:
      ip.write(list(eight_bit_add_no_carry(*ip.read(), *integer_to_bits(2, 8))))

  print_registers(al, ah, bl, bh, cl, ch, dl, dh, cs, ds, inp, out, flags, ip)


# ============================================================================
# Main Program
# ============================================================================

if __name__ == '__main__':
  import sys

  # Setup memory
  memory = Memory(8, 2**16)
  size = 0
  # Check if a binary file is provided
  if len(sys.argv) > 1:
    filename = sys.argv[1]
    print(f"Loading program from {filename}...")
    size = memory.load_binary(filename)
  else:
    raise ValueError("Please specify the .o binary file")

  if len(sys.argv) > 2 and sys.argv[2] == '--debug':
    # Run the CPU with debugger
    print("\nStarting Badger-8 CPU...")
    print("Commands: 's' to step, 'x <addr>' to examine memory, 'i' to provide an input character, 'q' to quit\n")
    cpu(memory, debug=True)
  else:
    cpu(memory, debug=False)
