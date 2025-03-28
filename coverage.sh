#!/bin/bash
BINARY=gzip

TEMP_DIR=$(mktemp -d)
echo "Using temp directory: $TEMP_DIR"

# Check if the directory was created successfully
if [[ -z "$TEMP_DIR" ]]; then
  echo "Error: Failed to create temporary directory."
  exit 1
fi

# TODO: ensure tools are installed or give error


valgrind --tool=callgrind --trace-children=yes --callgrind-out-file=$TEMP_DIR/%p pytest 2> /dev/null
# annotate only the one with greater PID (TODO: possible bug when PID rolls)
CHILD_FILE=$(ls $TEMP_DIR | sort -n | tail -1)
# auto annotation with --context=1 can be useful for have precise source code line execution
callgrind_annotate --auto=yes --context=0 $TEMP_DIR/$CHILD_FILE > $TEMP_DIR/executed.log 2>/dev/null
gdb -ex 'set pagination off' -ex 'info functions' -ex quit $(which $BINARY) > $TEMP_DIR/all_funcs.log
# experimental: count lines of code
CODELINES=$(find /usr/src/debug/$BINARY* -name *.c -type f | xargs c_count | grep 'lines containing code' | cut -f1)
python3 analyze.py --binary $BINARY -d $TEMP_DIR -c $CODELINES

# Clean up: Remove the temporary directory and its contents
#rm -rf "$TEMP_DIR