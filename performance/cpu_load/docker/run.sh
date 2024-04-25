#!/bin/bash

# running cmd: bash run.sh logs inner_list.json chrome

set -e

SELFPATH=$(dirname $(realpath "$0"))

LOGS=$(realpath "${1}")
DOMAINS_LIST=$(realpath "${2}")
METRIC=${3}
BROWSER=${4}

mkdir -p ${LOGS}

pushd "${SELFPATH}/chrome" > /dev/null
make docker
popd > /dev/null

# wrapper.py assumes that various files are in the same directory
# pushd "${SELFPATH}/../docker" > /dev/null

# source ~/work/pes/pes/bin/activate
source ~/pes/venv_measure/bin/activate

# while true; do
UUID=$(uuidgen -t)
echo "Starting measurement run '${UUID}' at $(date)"
python3 data_wrapper.py \
${LOGS}/${UUID}.log \
${DOMAINS_LIST} \
${METRIC} \
${BROWSER}
echo "Completed measurement run '${UUID}' at $(date)"
# done

# popd > /dev/null
