#!/usr/bin/env python2.7

# Copy source.iso and apply a patch to it.
# source.iso, patchfile.txt, sync.txt -> apply_patch.py -> patched.iso

# WIP

import argparse
import shutil
import cdrom_ecc
parser = argparse.ArgumentParser(description='Splits data out of iso mode-1 2352 data tracks.')
parser.add_argument('source', nargs='?', help='Input binary data. (Default: source.iso)')
parser.add_argument('patch', nargs='?', help='Patch file. (Default: patchfile.txt)')
parser.add_argument('sync', nargs='?', help='Sync locations. (Default: sync.txt)')
parser.add_argument('patched', nargs='?', help='Sync locations. (Default: patched.iso)')
args = parser.parse_args()

filename1 = 'source.iso'
filename2 = 'patchfile.txt'
filename3 = 'sync.txt'
filename4 = 'patched.iso'

if args.source:
    filename1 = args.source
if args.patch:
    filename2 = args.patch
if args.sync:
    filename3 = args.sync
if args.patched:
    filename4 = args.patched

shutil.copyfile(filename1, filename4)
patchfile = open(filename2, 'r')
syncfile = open(filename3, 'r')
patchedfile = open(filename4, 'r+b')

syncs = syncfile.readlines()

global pf_line
global current_index
global apply_bytes
global last_block
pf_line = ['']
current_index = 0  # ByteIndex after 16byte sync/header.
apply_bytes = ''

pf_line[0] = patchfile.readline()
s_line = pf_line[0].split(' ')
pf_index = int(s_line[0])
current_block = pf_index / 2048
pf_index -= (2048 * current_block)
last_block = current_block

while pf_line[0]:
    s_line = pf_line[0].split(' ')
    s_len = len(s_line[1])
    pf_bytes = lst = [s_line[1][i:i+2] for i in xrange(0, s_len - s_len % 2, 2)]
    pf_index = int(s_line[0])
    current_block = pf_index / 2048
    pf_index -= (2048 * current_block)
    current_index = int(syncs[current_block]) + 16

    if current_block > last_block:
        patchedfile.seek(current_index - 16)
        block_data = patchedfile.read(2048+16)
        patchedfile.write(cdrom_ecc.get_edc_ecc(block_data)[0])
        patchedfile.write(chr(0) * 8)
        patchedfile.write(cdrom_ecc.get_edc_ecc(block_data)[1])
        last_block = current_block

    patchedfile.seek(current_index + pf_index)
    apply_bytes = ''
    for b in pf_bytes:
        apply_bytes = apply_bytes + chr(int(b, 16))
    patchedfile.write(apply_bytes)
    pf_line[0] = patchfile.readline()

patchedfile.seek(current_index - 16)
block_data = patchedfile.read(2048 + 16)
patchedfile.write(cdrom_ecc.get_edc_ecc(block_data)[0])
patchedfile.write(chr(0) * 8)
patchedfile.write(cdrom_ecc.get_edc_ecc(block_data)[1])

print 'Done.'

patchfile.close()
syncfile.close()
patchedfile.close()

