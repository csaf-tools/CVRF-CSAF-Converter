#!/bin/bash

cd ..

mkdir outdir 2>/dev/null

#subdirs=("1.2" "examples_cisco" "examples_redhat")
subdirs=("examples_oracle")

c=0
for subdir in ${subdirs[@]}; do
  FILES=$(find examples/$subdir -type f)

  for f in $FILES; do
      echo -e "------------------- \n -------------------- \n"
      echo "INPUT FILE: $f "
      cvrf2csaf --force --input-file $f --output-file outdir/$(basename $f).json

#      read
      let c=$((c+=1))
      [[ $c -gt 100 ]] && break;
  done
done
