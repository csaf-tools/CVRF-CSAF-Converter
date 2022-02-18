#!/bin/bash

cd ..

mkdir outdir 2>/dev/null

#subdirs=("1.2" "examples_cisco" "examples_redhat")
subdirs=("examples_cisco")

for subdir in ${subdirs[@]}; do
  FILES=$(find examples/$subdir -type f)

  for f in $FILES; do
      echo -e "------------------- \n -------------------- \n"
      echo "INPUT FILE: $f "
      cvrf2csaf --force --input-file $f --output-file outdir/$(basename $f).json 2>&1 |grep "CSAF schema validation OK"

#      read
  done
done
