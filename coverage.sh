#!/bin/bash
BINARY=gzip

TEMP_DIR=$(mktemp -d)
echo "Using temp directory: $TEMP_DIR"

# Check if the directory was created successfully
if [[ -z "$TEMP_DIR" ]]; then
  echo "Error: Failed to create temporary directory."
  exit 1
fi

valgrind --tool=callgrind --trace-children=yes --callgrind-out-file=$TEMP_DIR/%p pytest 2> /dev/null
# annotate only the one with greater PID (TODO: possible bug when PID rolls)
CHILD_FILE=$(ls $TEMP_DIR | sort -n | tail -1)
# auto annotation with --context=1 can be useful for have precise source code line execution
callgrind_annotate --auto=yes --context=0 $TEMP_DIR/$CHILD_FILE > $TEMP_DIR/executed.log 2>/dev/null
gdb -ex 'set pagination off' -ex 'info functions' -ex quit $(which $BINARY) > $TEMP_DIR/all_funcs.log

python3 analyze.py --binary $BINARY -d $TEMP_DIR

# Clean up: Remove the temporary directory and its contents
#rm -rf "$TEMP_DIR