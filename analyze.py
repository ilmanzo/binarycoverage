#!/usr/bin/env python3
# take as input a file with the function list (from gdb) and a file with a callgrind_annotate output
import sys


def parse_annotated_execution(file):
    #parse the callgrind annotate output and returns a tuple with
    #(number of functions executed, number of lines executed)
    return (1, 4)

def parse_gdb_output(binary_name, file):
    relevant=False
    pattern="/usr/src/debug/" + binary_name
    functions=0
    while line := file.readline():
        line=line.strip()
        if pattern in line:
            relevant=True
            continue
        if relevant:
            if not line:
                relevant=False
                continue
            functions+=1
    return functions
            
if len(sys.argv) < 3:
    print("Usage: analyze.py <binary_name> <annotated_file> <gdb_functions_file>")
    sys.exit(1)

binary_name=sys.argv[1]

with open(sys.argv[2]) as f:
    executed_funcs, executed_lines=parse_annotated_execution(f)

with open(sys.argv[3]) as f:
    total_funcs=parse_gdb_output(binary_name,f)

# TODO dummy values. Parse gdb output and count total lines of code
total_lines = 100

func_coverage = 100*executed_funcs/total_funcs
line_coverage = 100*executed_lines/total_lines

print(f"Number of executed functions: {executed_funcs}/{total_funcs}")
print(f"Number of executed lines: {executed_lines}/{total_lines}")
print(f"Functions coverage: {func_coverage}%")
print(f"Line coverage: {line_coverage}%")
