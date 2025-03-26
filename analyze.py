#!/usr/bin/env python3
# take as input a file with the function list (from gdb) and a file with a callgrind_annotate output
import sys


def parse_annotated_execution(file):
    #TODO dummy values
    return (1, 4)


if len(sys.argv) < 2:
    print("Usage: analyze.py <annotated_file> <gdb_functions_file>")
    sys.exit(1)


with open(sys.argv[1]) as f:
    executed_funcs, executed_lines=parse_annotated_execution(f)

# TODO dummy values. Parse gdb output and count total lines of code
total_funcs = 10
total_lines = 100

func_coverage = 100*executed_funcs/total_funcs
line_coverage = 100*executed_lines/total_lines

print(f"Number of executed functions: {executed_funcs}/{total_funcs}")
print(f"Number of executed lines: {executed_lines}/{total_lines}")
print(f"Functions coverage: {func_coverage}%")
print(f"Line coverage: {line_coverage}%")
