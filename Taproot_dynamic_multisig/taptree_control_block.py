#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  1 23:03:18 2025

@author: ssarasw2
"""
from ecc import PrivateKey
from op import encode_minimal_num
from hash import hash_tapleaf, hash_tapbranch
from helper import big_endian_to_int, int_to_byte
from taproot import TapScript, TapLeaf, TapBranch
p = PrivateKey(90909).point
pubkey_1 = PrivateKey(11111).point.xonly()
pubkey_2 = PrivateKey(20202).point.xonly()
pubkey_3 = PrivateKey(30303).point.xonly()
# pubkey_4 = PrivateKey(40404).point.xonly()

tap_script_1 = TapScript([pubkey_1, 0xAC, pubkey_2, 0xBA, pubkey_3, 0xBA, 0x52, 0x87])
tap_script_2 = TapScript([encode_minimal_num(100240+1), 0xB1, 0x75, pubkey_1, 0xAC, pubkey_2, 0xBA, pubkey_3, 0xBA, 0x51, 0x87])
tap_script_3 = TapScript([encode_minimal_num(100240+3), 0xB1, 0x75, pubkey_3, 0xAC])
# Tap leaf with the TapScript
tap_leaf_1 = TapLeaf(tap_script_1)
tap_leaf_2 = TapLeaf(tap_script_2)
tap_leaf_3 = TapLeaf(tap_script_3)
# tap_leaf_4 = TapLeaf(tap_script_4)
# Two Tap branches from Tap leaves
tap_branch_1 = TapBranch(tap_leaf_1, tap_leaf_2)
tap_branch_2 = TapBranch(tap_branch_1, tap_leaf_3)
# From tap branches get merkle root hash
merkle_root = (tap_branch_2).hash()
# the external public key (Q) is the internal public key (P) tweaked with the Merkle Root (m)
internal_pubkey = p.tweaked_key(merkle_root)

# print(internal_pubkey.xonly().hex())
# tap_branch_1 = TapBranch(tap_leaf_1, tap_leaf_2)
# tap_branch_2 = TapBranch(tap_branch_1, tap_leaf_3)
# m = TapBranch(tap_leaf_1, tap_leaf_2).hash()
# print(m.hex())
# print('tf3', tap_leaf_3.hash().hex())
# print('pub4', pubkey_4.hex())

q_xonly = bytes.fromhex(internal_pubkey.xonly().hex()) #previous exercise internal key q
p = PrivateKey(90909).point
# hash_1 = bytes.fromhex(tap_leaf_3.hash().hex()) #tapleaf hash of tap_leaf_3
hash_2 = bytes.fromhex(tap_branch_1.hash().hex()) #tapbranch hash of tap leaves 1 and 2
pubkey_4 = bytes.fromhex(pubkey_3.hex()) #hash of 40404 pubkey
# create the TapScript and TapLeaf for pubkey 4
tap_script_4 = TapScript([encode_minimal_num(100240+3), 0xB1, 0x75, pubkey_3, 0xAC])
tap_leaf_4 = TapLeaf(tap_script_4)
# set the current hash to the TapLeaf's hash
current = tap_leaf_4.hash()
# loop through hash_1 and hash_2
for h in (hash_2, ):
    # update current hash to be the hash_tapbranch of h and the current hash, sorted alphabetically
    if h < current:
        current = hash_tapbranch(h + current)
    else:
        current = hash_tapbranch(current + h)
# set the merkle root m to be the current hash
m = current
# q is p tweaked with m
q = p.tweaked_key(m)
# check to see if the external pubkey's xonly is correct
print(q.xonly() == q_xonly)


p2tr_address = internal_pubkey.p2tr_address(merkle_root, network="testnet")
print(p2tr_address)







