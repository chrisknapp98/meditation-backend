#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

python3 -m robot \
--variablefile $SCRIPT_DIR/variables.py \
--outputdir $SCRIPT_DIR/integration_test_results \
-L DEBUG $SCRIPT_DIR

