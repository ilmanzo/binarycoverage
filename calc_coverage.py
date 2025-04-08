#!/usr/bin/env python3
# take as input a folder with the function list (from gdb) and files from callgrind_annotate output
import sys,argparse,os,glob,subprocess


def gdb_extract_function_name(line):
    "take as input a single line from gdb output, and extracts the function name"
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
    "take as input a single line from callgrind_annotate output, and extracts the function name"
    colon_index = line.find(':')
    if colon_index == -1:
        return None
    sub_line = line[colon_index+1:]
    dot_index = sub_line.find('.')
    if dot_index != -1:
        sub_line = sub_line[:dot_index]
    space_index = sub_line.find(' ')
    if space_index == -1:
        return sub_line
    return sub_line[:space_index]


def parse_annotated_execution(lines, binary_name):
    "parse the callgrind annotate output and returns a set of functions executed"
    "input: multilne string (standard output of callgrind_annotate)"
    pattern = f"/usr/src/debug/{binary_name}"
    executed_functions = set()
    for line in lines.splitlines():  # walrus operator
        line = line.strip()
        if pattern in line:
            func = callgrind_extract_function_name(line)
            if func:
                executed_functions.add(func)
    return executed_functions


def parse_gdb_output(file, binary_name):
    "process the gdb output file looking for functions"
    relevant = False
    all_functions = set()
    while line := file.readline():
        line = line.strip()
        if line.startswith('File '):
            relevant = True
            continue
        if relevant:
            if not line:
                relevant = False
                continue
            func = gdb_extract_function_name(line)
            if func:
                all_functions.add(func)
    # print(f"DEBUG ALL: {all_functions}")
    return all_functions


def main():
    "program entry point"
    parser = argparse.ArgumentParser(description="Process a binary file with optional parameters.")
    parser.add_argument("--binary", "-b", required=True, help="name of the binary file [ex. gzip]")
    parser.add_argument("--coverdir", "-d", required=True, help="Path to the coverage data directory")
    parser.add_argument("--verbose", "-v", required=False, help="Output also the names of functions", action='store_true')

    args = parser.parse_args()
    executed_funcs = set()

    for file in glob.glob(os.path.join(args.coverdir, 'callgrind.*')):
        try:
            result = subprocess.run(
                        ["callgrind_annotate", "--auto=yes", "--context=0", file],
                        capture_output=True,  # Capture stdout and stderr
                        text=True,  # Decode stdout and stderr as text
                        check=True, # Raise exception on non-zero exit code.
                    )
        except subprocess.CalledProcessError as e:
            print(f"Error processing {f}: {e}")
        except FileNotFoundError:
            print("callgrind_annotate command not found. Please install it.")
            sys.exit(1)
        ef = parse_annotated_execution(result.stdout, args.binary)
        executed_funcs.update(ef)  # join the sets

    with open(os.path.join(args.coverdir, "all_funcs.gdb")) as f:
        total_funcs = parse_gdb_output(f, args.binary)

    func_coverage = 100*len(executed_funcs)/len(total_funcs)
    print("--- Binary coverage report ---")
    print(f"Functions coverage: {len(executed_funcs)}/{len(total_funcs)} {func_coverage:.2f}%")   
    if args.verbose:
        executed = ",".join(sorted(list(executed_funcs)))
        missing = ",".join(sorted(list(total_funcs - executed_funcs)))
        print(f"\nExecuted functions: {executed}")
        print(f"\nMissing functions : {missing}")


if __name__ == "__main__":
    main()
