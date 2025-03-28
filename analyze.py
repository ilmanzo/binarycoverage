#!/usr/bin/env python3
# take as input a file with the function list (from gdb) and a file with a callgrind_annotate output
import sys,re,argparse,os

def gdb_extract_function_name(line):
    # Find the position of the '(' and extract the substring from the end of the line
    paren_index = line.rfind('(')
    if paren_index == -1:
        return None  # No function found in this line
    # Look backward from the '(' to find the function name
    sub_line = line[:paren_index]
    # Find the last word before the '(' (function name)
    function_name = sub_line.strip().split()[-1]
    # Remove any '*' from the function name (if it's a pointer)
    function_name = function_name.replace('*', '')
    # If there are multiple dots, keep only the first part
    function_name = function_name.split('.')[0]
    return function_name

def callgrind_extract_function_name(line):
    colon_index = line.find(':')
    if colon_index == -1:
        return None
    sub_line = line[colon_index+1:]
    dot_index = sub_line.find('.')
    if dot_index != -1:
        sub_line=sub_line[:dot_index]
    space_index = sub_line.find(' ')
    if space_index == -1:
        return sub_line
    return sub_line[:space_index]


def parse_annotated_execution(file, binary_name):
    #parse the callgrind annotate output and returns a tuple with
    #(set of functions executed, number of lines executed)
    header=True # we start with the function list
    pattern=f"/usr/src/debug/{binary_name}"
    executed_functions=set()
    while line:=file.readline():
        line=line.strip()
        if "Auto-annotated source" in line:
            header=False
            continue
        if header:
            if pattern in line:
                func=callgrind_extract_function_name(line)
                if func:
                    executed_functions.add(func)
            continue
        # TODO here we count lines of code
    #print(f"DEBUG EXE: {executed_functions}")
    return (executed_functions, 0)

def parse_gdb_output(file, binary_name):
    relevant=False
    patterns=[f"/usr/src/debug/{binary_name}", "<artificial>"]
    regex = re.compile(r'\b(?:static\s+|_Bool\s+)?(?:\w+\s+)+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
    all_functions=set()
    while line := file.readline():
        line=line.strip()
        if any((p in line) for p in patterns):
            relevant=True
            continue
        if relevant:
            if not line:
                relevant=False
                continue
            func=gdb_extract_function_name(line)
            if func:
                all_functions.add(func)
    #print(f"DEBUG ALL: {all_functions}")
    return all_functions

def main():
    parser = argparse.ArgumentParser(description="Process a binary file with optional parameters.")
    parser.add_argument("--binary", "-b", required=True, help="name of the binary file [ex. gzip]")
    parser.add_argument("--cloc", "-c", type=int, help="Optional number for lines of code")
    parser.add_argument("--coverdir", "-d", required=True, help="Path to the coverage data directory")

    args = parser.parse_args()
    with open(os.path.join(args.coverdir,"executed.log")) as f:
        executed_funcs, executed_lines=parse_annotated_execution(f,args.binary)

    with open(os.path.join(args.coverdir,"all_funcs.log")) as f:
        total_funcs=parse_gdb_output(f,args.binary)

    total_lines = args.cloc
    func_coverage = 100*len(executed_funcs)/len(total_funcs)
    executed=",".join(sorted(list(executed_funcs)))
    missing=",".join(sorted(list(total_funcs - executed_funcs)))
    print("--- binary coverage report ---")
    print(f"Functions     executed: {executed}")
    print(f"Functions not executed: {missing}")
    print()
    print(f"Number of executed functions: {len(executed_funcs)}/{len(total_funcs)}")
    print(f"Functions coverage: {func_coverage:.2f}%")
    if total_lines:
        line_coverage = 100*executed_lines/total_lines
        print(f"Number of executed lines: {executed_lines}/{total_lines}")
        print(f"Line coverage: {line_coverage:.2f}%")

if __name__ == "__main__":
    main()
