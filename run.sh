#! /bin/bash

export PYTHONPATH=$PYTHONPATH:./src/booking_system
# Create virtual environment if one doesn't exist
if [ ! -d "$PWD/serviceEnv" ]; then
    python3 -m "venv" "serviceEnv"
    source ./serviceEnv/bin/activate
    # install requirements
    pip install -r requirements.txt
else
    source ./serviceEnv/bin/activate
fi

python src/service.py
