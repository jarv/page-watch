#!/bin/bash
set -e
cp test_files/* .
for test_file in narrow shorter-narrow shorter; do
    cp capture.png "test-${test_file}.png"
    cmd="../compare.sh "test-${test_file}.png" capture-${test_file}.png ${test_file}-h1.png ${test_file}-h2.png ${test_file}-mask.png ${test_file}-mask-blur.png ${test_file}-mask-blur-monochrome.png"
    echo Running "$cmd"
    $cmd
done
