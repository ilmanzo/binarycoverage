#!/bin/sh
BINARY=/usr/bin/gzip

TEMP_DIR=$(mktemp -d)

# Check if the directory was created successfully
if [[ -z "$TEMP_DIR" ]]; then
  echo "Error: Failed to create temporary directory."
  exit 1
fi

valgrind --tool=callgrind --trace-children=yes --callgrind-out-file=$TEMP_DIR/%p pytest
# annotate only the one with greater PID (TODO: possible bug when PID rolls)
CHILD_FILE=$(ls $TEMP_DIR | sort -n | tail -1)
echo $CHILD_FILE
callgrind_annotate --auto=no $TEMP_DIR/$CHILD_FILE | grep $BINARY > $TEMP_DIR/executed.txt
cat $TEMP_DIR/executed.txt
gdb -ex 'set pagination off' -ex 'info functions' -ex quit $BINARY > $TEMP_DIR/allfunctions.txt

python3 analyze.py $TEMPDIR/executed.txt $TEMP_DIR/allfunctions.txt

# Clean up: Remove the temporary directory and its contents
rm -rf "$temp_dir"


