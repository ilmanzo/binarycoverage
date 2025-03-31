#!/bin/bash
BINARY=gzip

TEMP_DIR=$(mktemp -d)
echo "Using temp directory: $TEMP_DIR"

# Check if the directory was created successfully
if [[ -z "$TEMP_DIR" ]]; then
  echo "Error: Failed to create temporary directory."
  exit 1
fi
# ensure tools are installed or give error
for program in valgrind gdb python3; do
  if ! command -v $program &> /dev/null; then
    echo "Please install $program to continue"
    exit 1
  fi
done
  
valgrind --tool=callgrind --trace-children=yes --callgrind-out-file=$TEMP_DIR/callgrind.%p pytest 2> /dev/null
# annotate all the files
for f in $TEMP_DIR/callgrind.* 
do 
  base=$(basename $f)
  # auto annotation with --context=0 can be useful to have precise source code line execution
  callgrind_annotate --auto=yes --context=0 $f > $TEMP_DIR/"${base#*.}".log 2>/dev/null
done
# dump all the functions in the binary
gdb -ex 'set pagination off' -ex 'info functions' -ex quit $(which $BINARY) > $TEMP_DIR/all_funcs.gdb
# experimental: count lines of code
#CODELINES=$(find /usr/src/debug/$BINARY* -name *.c -type f | xargs c_count | grep 'lines containing code' | cut -f1)
python3 calc_coverage.py --binary $BINARY -d $TEMP_DIR -v

# Clean up: Remove the temporary directory and its contents
#rm -rf "$TEMP_DIR
