#!/bin/bash

packs=("flask" "twilio" "dotenv" "matplotlib" "seaborn" "pandas")

for package in "${packs[@]}"; do
    pip3 install $package
done