#!/bin/sh

if [ $# -ne 1 ]; then
  echo "Use: $0 <serial port>" 1>&2
  echo "     e.g. $0 a0" 1>&2
  exit 1
fi

mpremote $1 mount . run main.py | tee ../log/$1-$(date +%Y-%m-%d_%H-%M).log
