#!/bin/sh
tmux new-session -s mysession \; \
    rename-window 'Node 0' \; \
    send-keys C-m 'clear' C-m 'python3 node.py 0' C-m \; \
    split-window -v \; \
    rename-window 'Node 1' \; \
    send-keys C-m 'clear' C-m 'python3 node.py 1' C-m \; \
    split-window -h \; \
    rename-window 'Node 2' \; \
    send-keys C-m 'clear' C-m 'python3 node.py 2' C-m \; \
    select-pane -t 0 \; \
    split-window -h \; \
    rename-window 'Node 3' \; \
    send-keys C-m 'clear' C-m 'python3 node.py 3' C-m \; \
    select-pane -t 0 \; \
    setw synchronize-panes on \; \
    attach -t mysession
