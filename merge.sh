#!/bin/bash

fout="merged.csv" # fix output name
i=0 # reset counter

for filename in ./*.csv; do
 if [ "$filename" != "$OutName" ]; # avoid recursion
 then
   if [[ $i -eq 0 ]]; then
      head -1 $filename >> $fout # copy header if first file
   fi
   tail -n +2 $filename >> $fout # append from 2nd line each file
   i=$(( $i + 1 )) # increment counter
 fi
done
