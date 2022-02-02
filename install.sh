#!/usr/bin/env bash

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# symlink note file into local bindir
[[ -d ~/.local/bin ]] || mkdir ~/.local/bin
ln -s "${SCRIPT_DIR}/note" ~/.local/bin

echo "symlink created in ~/.local/bin"

