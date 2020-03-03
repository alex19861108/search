#!/usr/bin/env sh
PORT="8000"
ps aux | grep "8000" | grep -v "grep" | awk '{print $2}' | xargs kill -9