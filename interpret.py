#!/usr/bin/env python
# filename: interpret.py
# author: David Rubý (xrubyd)
# date: 04-04-2020
# project: IPP 2020 (Principy programovacích jazyků a objektově orientovaného programování)
# part: 2/interpret.py

import xml.etree.ElementTree as XML
import sys
import getopt
import re
from enum import Enum

TOP = -1

def main():
    # ==================================== argument parsing ====================================
    options = ["help", "source=", "input=", "stats=", "insts", "vars"]             # possible arguments
    try:
        # arguments with value will be stored in opts and arguments without value will be stored in args
        opts, args = getopt.getopt(sys.argv[1:], "", options)
    except getopt.error:
        # if argument, that is not in options list, is given.
        exit(10)

    input_not_added = True
    source_not_added = True
    stats_not_added = True

    insts = False
    vars = False

    global input_arg
    input_arg = sys.stdin
    source_arg = sys.stdin
    stats_arg = None

    # redirecting input based on arguments
    for option, value in opts:
        if option in ("--source",):
            source_not_added = False
            source_arg = value
        elif option in ("--input",):
            input_not_added = False
            input_arg = value
        elif option in ("--help",):
            if source_not_added and input_not_added:
                help()
            else:
                exit(10)
        elif option in ("--stats",):
            stats_not_added = False
            stats_arg = value
        elif option in ("--insts",):
            insts = True
        elif option in ("--vars",):
            vars = True


    if (source_not_added and input_not_added) or opts is None:
        # --source or --input must always be given
        exit(10)

    if input_arg != sys.stdin:
        try:
            global input_words
            input_file = open(input_arg, 'r')
            for line in input_file:
                input_words.append(line)
        except IOError:
            exit(11)


    # ============ STATI ============
    if insts and stats_not_added:
        exit(10)

    if vars and stats_not_added:
        exit(10)


    # ==================================== XML parsing ====================================

    try:
        tree = XML.parse(source_arg)
        program = tree.getroot()
    except:
        exit(31)


    if program.tag != "program": exit(32)
    program = sort_xml(program)

    if not xml_structure_ok(program): exit(32)

    # first pass through to define all labels...

    global pc
    global instruction_counter

    while pc < len(program):
        if program[pc].attrib["opcode"] == "LABEL":
            check_label(program[pc])
            instruction_counter += 1
        pc += 1

    global orders
    orders = []


    # second pass through to execute the rest of the instructions
    pc = 0
    while pc < len(program):
        instruction_switch(program[pc])
        instruction_counter += 1
        pc += 1


# ================= STATI ==============
    if not stats_not_added:
        try:
            stats_file = open(stats_arg, 'w')
        except IOError:
            exit(12)
        if insts:
            stats_file.write(str(instruction_counter) + "\n")
        if vars:
            stats_file.write(str(gf_counter + lf_counter + tf_counter) + "\n")

        stats_file.close()



def instruction_switch(instruction):
    switcher = {
        "MOVE"          : check_move,
        "CREATEFRAME"   : check_createframe,
        "PUSHFRAME"     : check_pushframe,
        "POPFRAME"      : check_popframe,
        "DEFVAR"        : check_defvar,
        "CALL"          : check_call,
        "RETURN"        : check_return,
        "PUSHS"         : check_pushs,
        "POPS"          : check_pops,
        "CLEARS"        : check_clears,
        "ADDS"          : check_adds,
        "SUBS"          : check_subs,
        "MULS"          : check_muls,
        "IDIVS"         : check_idivs,
        "LTS"           : check_lts,
        "GTS"           : check_gts,
        "EQS"           : check_eqs,
        "ANDS"          : check_ands,
        "ORS"           : check_ors,
        "NOTS"          : check_nots,
        "INT2CHARS"     : check_int2chars,
        "STRI2INTS"     : check_stri2ints,
        "JUMPIFEQS"     : check_jumpifeqs,
        "JUMPIFNEQS"    : check_jumpifneqs,
        "ADD"           : check_add,
        "SUB"           : check_sub,
        "MUL"           : check_mul,
        "IDIV"          : check_idiv,
        "DIV"           : check_div,
        "LT"            : check_lt,
        "GT"            : check_gt,
        "EQ"            : check_eq,
        "AND"           : check_and,
        "OR"            : check_or,
        "NOT"           : check_not,
        "INT2CHAR"      : check_int2char,
        "STRI2INT"      : check_stri2int,
        "INT2FLOAT"     : check_int2float,
        "FLOAT2INT"     : check_float2int,
        "READ"          : check_read,
        "WRITE"         : check_write,
        "CONCAT"        : check_concat,
        "STRLEN"        : check_strlen,
        "GETCHAR"       : check_getchar,
        "SETCHAR"       : check_setchar,
        "TYPE"          : check_type,
        "LABEL"         : nothing,
        "JUMP"          : check_jump,
        "JUMPIFEQ"      : check_jumpifeq,
        "JUMPIFNEQ"     : check_jumpifneq,
        "EXIT"          : check_exit,
        "DPRINT"        : check_dprint,
        "BREAK"         : check_break
    }

    return switcher.get(instruction.attrib['opcode'].upper(), invalid_instruction)(sort_xml(instruction))


def nothing(instruction):
    pass


def check_move(instruction):
    if len(instruction) != 2: exit(32)

    value = get_value(instruction[1])
    set_value_to_var(instruction[0], value)


def check_createframe(instruction):
    if len(instruction) != 0: exit(32)

    global tf
    tf = {}


def check_pushframe(instruction):
    if len(instruction) != 0: exit(32)

    global tf
    try:
        lf.append(tf)
        del tf
    except NameError:
        exit(55)


def check_popframe(instruction):
    if len(instruction) != 0: exit(32)

    if stack_empty(lf):
        exit(55)
    else:
        global tf
        tf = lf.pop()


def check_defvar(instruction):
    if len(instruction) != 1: exit(32)

    set_value_to_var(instruction[0], None, "defvar")


def check_call(instruction):
    if len(instruction) != 1: exit(32)

    pc_stack.append(pc)
    check_jump(instruction)

def check_return(instruction):
    if len(instruction) != 0: exit(32)

    if stack_empty(pc_stack):
        exit(56)
    else:
        global pc
        pc = pc_stack.pop()


def check_pushs(instruction):
    if len(instruction) != 1: exit(32)

    value = get_value(instruction[0])
    data_stack.append(value)


def check_pops(instruction):
    if len(instruction) != 1: exit(32)

    if stack_empty(data_stack):
        exit(56)
    else:
        value = data_stack.pop()
        set_value_to_var(instruction[0], value)


def check_clears(instruction):
    if len(instruction) != 0: exit(32)

    global data_stack
    data_stack = []


def check_adds(instruction):
    if len(instruction) != 0: exit(32)

    values = read_stack_values(2)

    if type(values[0]) is int and type(values[1]) is int:
        data_stack.append(values[0] + values[1])
    else:
        exit(53)


def check_subs(instruction):
    if len(instruction) != 0: exit(32)

    values = read_stack_values(2)

    if type(values[0]) is int and type(values[1]) is int:
        data_stack.append(values[1] - values[0])
    else:
        exit(53)


def check_muls(instruction):
    if len(instruction) != 0: exit(32)

    values = read_stack_values(2)

    if type(values[0]) is int and type(values[1]) is int:
        data_stack.append(values[0] * values[1])
    else:
        exit(53)


def check_idivs(instruction):
    if len(instruction) != 0: exit(32)

    values = read_stack_values(2)

    if type(values[0]) is int and type(values[1]) is int:
        if values[0] == 0:
            exit(57)
        else:
            data_stack.append(values[1] // values[0])
    else:
        exit(53)


def check_lts(instruction):
    if len(instruction) != 0: exit(32)

    values = read_stack_values(2)

    if type(values[0]) is not type(values[1]) or values[0] is None or values[1] is None:
        exit(53)
    else:
        data_stack.append(values[1] < values[0])


def check_gts(instruction):
    if len(instruction) != 0: exit(32)

    values = read_stack_values(2)

    if type(values[0]) is not type(values[1]) or values[0] is None or values[1] is None:
        exit(53)
    else:
        data_stack.append(values[1] > values[0])


def check_eqs(instruction):
    if len(instruction) != 0: exit(32)

    values = read_stack_values(2)

    if values[0] is None and values[1] is None:
        data_stack.append(True)
    elif values[0] is None or values[1] is None:
        data_stack.append(values[0] == values[1])
    elif type(values[0]) is type(values[1]):
        data_stack.append(values[0] == values[1])
    else:
        exit(53)


def check_ands(instruction):
    if len(instruction) != 0: exit(32)

    values = read_stack_values(2)

    if type(values[0]) is not bool: exit(53)

    if type(values[1]) is not bool: exit(53)

    data_stack.append(values[0] and values[1])


def check_ors(instruction):
    if len(instruction) != 0: exit(32)

    values = read_stack_values(2)

    if type(values[0]) is not bool:
        exit(53)
    if type(values[1]) is not bool:
        exit(53)

    data_stack.append(values[0] or values[1])


def check_nots(instruction):
    if len(instruction) != 0: exit(32)

    values = read_stack_values(1)

    if type(values[0]) is not bool:
        exit(53)
    else:
        data_stack.append(not values[0])


def check_int2chars(instruction):
    if len(instruction) != 0: exit(32)

    values = read_stack_values(1)

    if type(values[0]) is not int:
        exit(53)
    else:
        try:
            value = chr(values[0])
        except:
            exit(58)

        data_stack.append(decode_string(value))


def check_stri2ints(instruction):
    if len(instruction) != 0: exit(32)

    values = read_stack_values(2)

    if type(values[0]) is not int: exit(53)
    if type(values[1]) is not str: exit(53)


    str_value = values[1]
    index_value = values[0]
    if index_value > len(str_value):
        exit(58)
    try:
        value = ord(str_value[index_value])
    except:
        exit(58)

    data_stack.append(value)


def check_jumpifeqs(instruction):
    if len(instruction) != 1: exit(32)

    values = read_stack_values(2)

    eq = False
    if values[0] is None and values[1] is None:
        eq = True
    elif values[0] is None or values[1] is None:
        pass
    elif type(values[0]) is type(values[1]):
        eq = values[0] == values[1]
    else:
        exit(53)

    jump(instruction, eq)


def check_jumpifneqs(instruction):
    if len(instruction) != 1: exit(32)

    values = read_stack_values(2)

    eq = False
    if values[0] is None and values[1] is None:
        exit(53)
    elif values[0] is None or values[1] is None:
        pass
    elif type(values[0]) is type(values[1]):
        eq = values[0] == values[1]
    else:
        exit(53)

    check_jump(instruction, not eq)



def check_add(instruction):
    if len(instruction) != 3: exit(32)

    if (get_type(instruction[1]) == "int" and get_type(instruction[2]) == "int") or (get_type(instruction[1]) == "float" and get_type(instruction[2]) == "float"):
        value1 = get_value(instruction[1])
        value2 = get_value(instruction[2])
        set_value_to_var(instruction[0], value1 + value2)
    else:
        exit(53)


def check_sub(instruction):
    if len(instruction) != 3: exit(32)

    if (get_type(instruction[1]) == "int" and get_type(instruction[2]) == "int") or (get_type(instruction[1]) == "float" and get_type(instruction[2]) == "float"):
        value1 = get_value(instruction[1])
        value2 = get_value(instruction[2])
        set_value_to_var(instruction[0], value1 - value2)
    else:
        exit(53)



def check_mul(instruction):
    if len(instruction) != 3: exit(32)

    if (get_type(instruction[1]) == "int" and get_type(instruction[2]) == "int") or (get_type(instruction[1]) == "float" and get_type(instruction[2]) == "float"):
        value1 = get_value(instruction[1])
        value2 = get_value(instruction[2])
        set_value_to_var(instruction[0], value1 * value2)
    else:
        exit(53)


def check_div(instruction):
    if len(instruction) != 3: exit(32)

    if get_type(instruction[1]) != "float" or get_type(instruction[2]) != "float":
        exit(53)
    else:
        value1 = get_value(instruction[1])
        value2 = get_value(instruction[2])
        if value2 == 0.0:
            exit(57)
        else:
            set_value_to_var(instruction[0], value1 / value2)


def check_idiv(instruction):
    if len(instruction) != 3: exit(32)

    if get_type(instruction[1]) != "int" or get_type(instruction[2]) != "int":
        exit(53)
    else:
        value1 = get_value(instruction[1])
        value2 = get_value(instruction[2])
        if(value2 == 0):
            exit(57)
        else:
            set_value_to_var(instruction[0], value1 // value2)


def check_lt(instruction):
    if len(instruction) != 3: exit(32)

    if get_type(instruction[1]) != get_type(instruction[2]) or get_type(instruction[1]) == "nil" or get_type(instruction[2]) == "nil":
        exit(53)
    else:
        value1 = get_value(instruction[1])
        value2 = get_value(instruction[2])
        set_value_to_var(instruction[0], value1 < value2)


def check_gt(instruction):
    if len(instruction) != 3: exit(32)

    if get_type(instruction[1]) != get_type(instruction[2]) or get_type(instruction[1]) == "nil" or get_type(instruction[2]) == "nil":
        exit(53)
    else:
        value1 = get_value(instruction[1])
        value2 = get_value(instruction[2])
        set_value_to_var(instruction[0], value1 > value2)


def check_eq(instruction):
    if len(instruction) != 3: exit(32)

    if get_type(instruction[1]) == "nil" and get_type(instruction[2]) == "nil":
        set_value_to_var(instruction[0], True)
    elif get_type(instruction[1]) == "nil" or get_type(instruction[2]) == "nil":
        value1 = get_value(instruction[1])
        value2 = get_value(instruction[2])
        set_value_to_var(instruction[0], value1 == value2)
    elif get_type(instruction[1]) == get_type(instruction[2]):
        value1 = get_value(instruction[1])
        value2 = get_value(instruction[2])
        set_value_to_var(instruction[0], value1 == value2)
    else:
        exit(53)

def check_and(instruction):
    if len(instruction) != 3: exit(32)
    if get_type(instruction[1]) != "bool": exit(53)
    if get_type(instruction[2]) != "bool": exit(53)

    value1 = get_value(instruction[1])
    value2 = get_value(instruction[2])
    set_value_to_var(instruction[0], value1 and value2)


def check_or(instruction):
    if len(instruction) != 3: exit(32)
    if get_type(instruction[1]) != "bool": exit(53)
    if get_type(instruction[2]) != "bool": exit(53)

    value1 = get_value(instruction[1])
    value2 = get_value(instruction[2])
    set_value_to_var(instruction[0], value1 or value2)


def check_not(instruction):
    if len(instruction) != 2: exit(32)

    if get_type(instruction[1]) != "bool": exit(53)

    value = get_value(instruction[1])
    set_value_to_var(instruction[0], not value)


def check_int2char(instruction):
    if len(instruction) != 2: exit(32)

    value = get_value(instruction[1])
    if type(value) is not int: exit(53)
    if value is None: exit(53)

    try:
        chr(value)
    except:
        exit(58)
    set_value_to_var(instruction[0], chr(value))


def check_stri2int(instruction):
    if len(instruction) != 3: exit(32)
    if get_type(instruction[1]) != "string": exit(53)
    if get_type(instruction[2]) != "int": exit(53)

    str_value = get_value(instruction[1])
    index_value = get_value(instruction[2])

    if index_value > len(str_value): exit(58)
    if index_value < 0: exit(58)
    try:
        value = ord(str_value[index_value])
    except:
        exit(58)
    set_value_to_var(instruction[0], value)


def check_int2float(instruction):
    if len(instruction) != 2: exit(32)

    if get_type(instruction[1]) != "int":
        exit(53)
    else:
        try:
            value = float(get_value(instruction[1]))
        except:
            exit(58)
        set_value_to_var(instruction[0], value)


def check_float2int(instruction):
    if len(instruction) != 2: exit(32)

    if get_type(instruction[1]) != "float":
        exit(53)
    else:
        try:
            value = int(get_value(instruction[1]))
        except:
            exit(58)
        set_value_to_var(instruction[0], value)


def check_read(instruction):
    if len(instruction) != 2: exit(32)

    type = instruction[1].text

    global input_arg
    if input_arg != sys.stdin:
        read = file_read()
    else:
        try:
            read = input()
        except:
            read = ""

    read = read.rstrip()

    if read == "":
        value = ""

    if type == "bool":
        if read.lower() == "true":
            value = True
        else:
            value = False
    elif type == "int":
        try:
            value = int(read)
        except ValueError:
            value = None
    elif type == "float":
        try:
            value = float.fromhex(read)
        except:
            value = ""
    elif type == "string":
        value = read
    else:
        exit(53)

    set_value_to_var(instruction[0], value)

def check_write(instruction):
    if len(instruction) != 1: exit(32)

    value = get_value(instruction[0])
    if value == None:
        print("", end = '')

    elif type(value) is bool:
        if value == True:
            print("true", end = '')
        elif value == False:
            print("false", end = '')
    elif type(value) is float:
        print(float.hex(value), end = '')
    else:
        print(value, end = '')


def check_concat(instruction):
    if len(instruction) != 3: exit(32)
    if get_type(instruction[1]) != "string": exit(53)
    if get_type(instruction[2]) != "string": exit(53)

    value1 = get_value(instruction[1])
    value2 = get_value(instruction[2])
    set_value_to_var(instruction[0], value1 + value2)


def check_strlen(instruction):
    if len(instruction) != 2: exit(32)

    if get_type(instruction[1]) != "string":
        exit(53)
    else:
        value = get_value(instruction[1])
        set_value_to_var(instruction[0], len(value))


def check_getchar(instruction):
    if len(instruction) != 3: exit(32)

    if get_type(instruction[1]) != "string": exit(53)
    if get_type(instruction[2]) != "int": exit(53)

    value = get_value(instruction[1])
    index = get_value(instruction[2])
    if 0 <= index < len(value):
        set_value_to_var(instruction[0], value[index])
    else:
        exit(58)


def check_setchar(instruction):
    if len(instruction) != 3: exit(32)

    if get_type(instruction[0]) != "string": exit(53)
    if get_type(instruction[1]) != "int": exit(53)
    if get_type(instruction[2]) != "string": exit(53)

    value = get_value(instruction[0])
    index = get_value(instruction[1])
    character = get_value(instruction[2])

    try:
        if 0 <= index < len(value):
            output = list(value)
            output[index] = character[0]
            set_value_to_var(instruction[0], "".join(output))
        else:
            exit(58)
    except:
        exit(58)


def check_type(instruction):
    if len(instruction) != 2: exit(32)

    argument = instruction[1]
    value = None

    if argument.attrib["type"] == "nil":
        set_value_to_var(instruction[0], "nil")
        return
    elif argument.attrib["type"] == "bool":
        set_value_to_var(instruction[0], "bool")
        return
    elif argument.attrib["type"] == "int":
        set_value_to_var(instruction[0], "int")
        return
    elif argument.attrib["type"] == "float":
        set_value_to_var(instruction[0], "float")
        return
    elif argument.attrib["type"] == "string":
        set_value_to_var(instruction[0], "string")
        return
    elif argument.attrib["type"] == "var":

        frame = argument.text[0:2]
        name = argument.text[3:]

        if frame == "GF":
            if name in gf:
                value = gf[name]
            else:
                exit(54)
        elif frame == "LF":
            if not stack_empty(lf):  # Stack of local frames is not empty
                if name in lf[TOP]:
                    value = lf[TOP][name]
                else:
                    exit(54)
            else:
                exit(55)

        elif frame == "TF":
            try:
                if name in tf:
                    value = tf[name]
                else:
                    exit(54)
            except NameError:
                exit(55)
        else:
            exit(31)
    else:
        exit(31)


        output = ""
    if type(value) is bool:
        output = "bool"
    elif type(value) is int:
        output = "int"
    elif type(value) is float:
        output = "float"
    elif type(value) is str:
        output = "string"
    elif value is None:
        output = ""

    set_value_to_var(instruction[0], output)


def check_label(instruction):
    if len(instruction) != 1: exit(32)

    if instruction[0].text in labels:
        exit(52)
    else:
        labels[instruction[0].text] = pc


def check_jump(instruction):
    if len(instruction) != 1:
        exit(32)
    else:
        jump(instruction)



def check_jumpifeq(instruction):
    if len(instruction) != 3: exit(32)

    eq = False
    if get_type(instruction[1]) == "nil" and get_type(instruction[2]) == "nil":
        eq = True
    elif get_type(instruction[1]) == "nil" or get_type(instruction[2]) == "nil":
        pass
    elif get_type(instruction[1]) == get_type(instruction[2]):
        value1 = get_value(instruction[1])
        value2 = get_value(instruction[2])
        eq = value1 == value2
    else:
        exit(53)

    jump(instruction, eq)



def check_jumpifneq(instruction):
    if len(instruction) != 3: exit(32)

    eq = False
    if get_type(instruction[1]) == "nil" and get_type(instruction[2]) == "nil":
        eq = True
    elif get_type(instruction[1]) == "nil" or get_type(instruction[2]) == "nil":
        pass
    elif get_type(instruction[1]) == get_type(instruction[2]):
        value1 = get_value(instruction[1])
        value2 = get_value(instruction[2])
        eq = value1 == value2
    else:
        exit(53)

    jump(instruction, not eq)


def check_exit(instruction):
    if len(instruction) != 1: exit(32)
    value = get_value(instruction[0])
    if (type(value) is not int): exit(53)
    if not (0 <= value <= 49):
        exit(57)
    else:
        exit(value)


def check_dprint(instruction):
    if len(instruction) != 1: exit(32)

    value = get_value(instruction[0])
    print(value, end = '', file=sys.stderr)


def check_break(instruction):
    if len(instruction) != 0: exit(32)

    stderrprint("\n\n==================== STATS ====================")
    stderrprint("instruction_counter: " + str(instruction_counter))

    stderrprint("\nPC: " + str(pc))
    stderrprint("pc stack: " + str(pc_stack) + " <-- TOP")

    stderrprint("\n========== Memory frame ==========")

    stderrprint("GF:")
    stderrprint(gf)

    stderrprint("\nLF:")
    stderrprint(str(lf) + " <-- TOP")

    try:
        stderrprint("\nTF:")
        stderrprint(tf)
    except NameError:
        stderrprint("TF does not exist in this scope")

    stderrprint("==================================")

    stderrprint("\ndata stack")
    stderrprint(str(data_stack) + " <-- TOP")

    stderrprint("\nlabels")
    stderrprint(labels)


def invalid_instruction(instruction):
    exit(32)


def jump(instruction, should_jump=True):
    if instruction[0].text not in labels:
        exit(52)

    if should_jump:
        global pc
        pc = labels[instruction[0].text]

# returns value from argument typed according to argument
def get_value(argument):
    value = None

    if argument.attrib["type"] == "nil":
        value = None
    elif argument.attrib["type"] == "bool":
        value = True if argument.text == "true" else False
    elif argument.attrib["type"] == "int":
        try:
            value = int(argument.text)
        except:
            exit(32)
    elif argument.attrib["type"] == "float":
        try:
            value = float.fromhex(argument.text)
        except:
            exit(32)
    elif argument.attrib["type"] == "string":
        value = argument.text
        value = decode_string(value)
    elif argument.attrib["type"] == "var":
        value = get_value_from_var(argument)
    else:
        exit(31)
    return value


# returns value stored in a frame given by argument with name given by argument
def get_value_from_var(argument):
    value = None
    name = argument.text[3:]
    frame = argument.text[0:2]

    if frame == "GF":
        if name in gf:
            value = gf[name]
        else:
            exit(54)

    elif frame == "LF":
        if not stack_empty(lf):        #Stack of local frames is not empty
            if name in lf[TOP]:
                value = lf[TOP][name]
            else:
                exit(54)
        else:
            exit(55)

    elif frame == "TF":
        try:
            if name in tf:
                value = tf[name]
            else:
                exit(54)
        except NameError:
            exit(55)
    else:
        exit(31)


    if value is None:
        exit(56)
    return value


# stores value to a frame based on argument with name given by argument
def set_value_to_var(argument, value, instruction=""):

    frame = argument.text[0:2]
    name = argument.text[3:]

    if type(value) is str:
        value = decode_string(value)

    if frame == "GF":
        if name in gf and instruction == "defvar": exit(52)

        if name not in gf and instruction != "defvar": exit(54)
        gf[name] = value
        global gf_counter
        gf_counter += 1

    elif frame == "LF":
        if stack_empty(lf): exit(55)
        if name in lf[TOP] and instruction == "defvar": exit(52)


        if name not in lf[TOP] and instruction != "defvar":
            exit(54)
        lf[TOP][name] = value
        global lf_counter
        lf_counter += 1

    elif frame == "TF":
        try:
            if name in tf and instruction == "defvar": exit(52)

            if name not in tf and instruction != "defvar": exit(54)
            tf[name] = value
            global tf_counter
            tf_counter += 1
        except NameError:
            exit(55)

    else:
        exit(31)


# returns string with information of type based on type
def get_type(argument):
    var_type = argument.attrib["type"]

    if argument.attrib["type"] == "var":
        value = get_value_from_var(argument)
        if type(value) is int:
            var_type = "int"
        elif type(value) is float:
            var_type = "float"
        elif type(value) is str:
            var_type = "string"
        elif type(value) is bool:
            var_type = "bool"
        elif  value is None:
            var_type = "nil"
        else:
            exit(31)
    return var_type


# decodes ASCII characters from decadic format to string
def decode_string(value):
    decoded = ""
    i = 0
    if value is None:
        value = ""

    if value == "": return ""

    while i < len(value):
        if value[i] == "\\":
            decoded = decoded + chr(int(value[i+1:i+4]))
            i += 4
        else:
            decoded = decoded + value[i]
            i += 1
    return decoded



# returns true, if stack is empty, otherwise returns false
def stack_empty(stack):
    return True if len(stack) == 0 else False


# prints value to standart error
def stderrprint(value):
    print(value, file = sys.stderr)


# function, that reads from file
def file_read():
    global input_words
    global input_words_counter

    value = input_words[input_words_counter]
    input_words_counter += 1
    return value


# keeps poping as many values from stack, asi given by "number" argument and returns array of theese values
def read_stack_values(number):
    values = []
    for i in range(number):
        if stack_empty(data_stack):
            exit(56)
        else:
            values.append(data_stack.pop())
    return values


def xml_structure_ok(program):
    global orders
    ok = True

    for instruction in program:

        if instruction.tag != "instruction": ok = False

        instruction = sort_xml(instruction)
        for i in range(0, len(instruction)):
            if instruction[i].tag != "arg" + str(i + 1): ok = False


        if 'opcode' not in instruction.keys(): ok = False

        if 'order' not in instruction.keys(): ok = False

        try:
            if int(instruction.attrib['order']) <= 0:
                ok = False
            if instruction.attrib['order'] in orders:
                #print(orders)
                #print(instruction.attrib['order'])
                ok = False
            orders.append(instruction.attrib['order'])
        except:
            ok = False
    return ok


def sort_xml(program):
    def get_key(instruction):
        if instruction.tag == "instruction":
            return int(instruction.get("order"))
        else:
            return instruction.tag

    roottag = program.tag
    roottext = program.text
    roottail = program.tail
    rootattrib = program.attrib
    sorted_tree = XML.Element(None)
    try:
        sorted_tree[:] = sorted(program, key = get_key)
    except:
        exit(32)
    sorted_tree.tag = roottag
    sorted_tree.text = roottext
    sorted_tree.tail = roottail
    sorted_tree.attrib = rootattrib
    return sorted_tree




def help():
    print("==================== HELP ====================")
    print("=========== arguments ==========")
    print("--help                   prints the help. Can not be used with other arguments")
    print("--source=file            input XML file with XML representation of IPPcode20. Otherwise read from stdin")
    print("--input=file             input file for interpretation. Otherwise read from stdin")
    print("================================")
    print("\n")
    print("========= return values =========")
    print("10                       missing argument or forbidden argument combination")
    print("11                       could not open an input file")
    print("12                       could not open an output file")
    print("31                       wrong XML file or not well-formed XML.")
    print("32                       not expected structure of XML.")
    print("53                       wrong types of operands.")
    print("54                       not existing variable access.")
    print("55                       not existing frame access.")
    print("56                       missing value of variable in memory.")
    print("57                       wrong value of operand{s]{zero division, wrong return value in EXIT instruction}")
    print("58                       error, when processing string")
    print("99                       Unexpected internal error {error at memory allocation, ...}")
    print("=================================")

if __name__ == "__main__":
    # Global variables initializations
    gf = {}         # Global Frame initialization
    lf = []         # Local Frame initialization

    gf_counter = 0
    lf_counter = 0
    tf_counter = 0

    pc = 0          # Program counter
    pc_stack = []

    data_stack = []
    labels = {}

    instruction_counter = 0

    input_words = []
    input_words_counter = 0

    orders = []

    main()
    