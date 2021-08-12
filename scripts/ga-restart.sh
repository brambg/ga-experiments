#!/usr/bin/env bash

# https://textrepo.readthedocs.io/en/latest/usage.html#elasticsearch
if [ $(sysctl -n vm.max_map_count) -lt 262144 ] ; then
  echo Increase vm.max_map_count for elasticsearch
  sudo sysctl -w vm.max_map_count=262144
fi
cd ~/workspaces/golden-agents/ga-ner-experiment/docker && (
        echo Stop current ga containers && \
        ./stop.sh && \
        echo Start new ga containers && \
        ./start.sh && \
        echo Show ga containers logs && \
        ./log.sh 100
)