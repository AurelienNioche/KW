#!/usr/bin/env bash

echo "Use Python 3.5.2 for compiling"
pyenv local 3.5.2
python3 setup.py build_ext --inplace

echo "Switch to python 2.7.12"
pyenv local 2.7.12

echo "Call 'avakas_launcher.py'"
qsub avakas_script.sh

echo "Come back to python 3.5.2"
pyenv local 3.5.2