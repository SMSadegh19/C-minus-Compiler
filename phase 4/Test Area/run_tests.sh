#!/bin/sh

echo "" > log.txt
echo "" > brief_results.txt
for dir in ../PA4_sample_cases/*; do
    cp "${dir}/input.txt" ./input.txt
    echo "${dir}"
    python3 ../../compiler.py
    wine tester_Windows.exe > expected.txt
    printf "\n\n\n\n=====================================>>>>> Running Test ${dir}...\n" >> log.txt
    printf "\n\n=====================================>>>>> Running Test ${dir}...\n" >> brief_results.txt
    printf "\n\n              *** output.txt diffrences ***\n" >> log.txt
    diff -i -s -B -W 500 -w output.txt "${dir}/output.txt" >> log.txt
    diff -i -y -B -W 500 -w -q output.txt "${dir}/output.txt" >> brief_results.txt
    printf "\n\n              *** expected.txt diffrences ***\n" >> log.txt
    diff -i -s -y -B -W 250 -w expected.txt "${dir}/expected.txt" >> log.txt
    diff -i -y -B -W 250 -w -q expected.txt "${dir}/expected.txt" >> brief_results.txt
done
