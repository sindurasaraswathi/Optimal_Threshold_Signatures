#import libraries
from ecc import PrivateKey, S256Point
from hash import sha256, hash_tapbranch
from script import address_to_script_pubkey
from taproot import TapScript, TapLeaf, TapBranch
from tx import Tx, TxIn, TxOut
from witness import Witness
from helper import int_to_byte
from requests import get, post
from op import encode_minimal_num

def build_taproot_tree(leaves, priv):
    if not leaves:
        raise ValueError("At least one leaf is required")
    if len(leaves) == 1:
        return leaves[0]

    nodes = leaves.copy()
    while len(nodes) > 1:
        new_level = []
        for i in range(0, len(nodes), 2):
            if i + 1 < len(nodes):
                branch = TapBranch(nodes[i], nodes[i+1])
                new_level.append(branch)
            else:
                new_level.append(nodes[i])
        nodes = new_level

    root_branch = nodes[0]
    merkle_root = root_branch.hash() if isinstance(root_branch, TapBranch) else root_branch.hash()
    internal_key = priv.point.tweaked_key(merkle_root)
    return merkle_root, root_branch, internal_key


def visualize_taproot_tree(node, prefix=" "):
    if isinstance(node, TapLeaf):
        print(f"{prefix}Leaf: {node.hash().hex()}")
    elif isinstance(node, TapBranch):
        print(f"{prefix}Branch: {node.hash().hex()}")
        # Show left and right children
        visualize_taproot_tree(node.left, prefix + "  |> ")
        visualize_taproot_tree(node.right, prefix + "  |> ")
    else:
        print(f"{prefix}Unknown node type")


def collect_txns(fromAddress):
    # utxo of fromAddress has to be populated
    response = get(f'https://mempool.space/testnet4/api/address/{fromAddress}/utxo').json()
    mega_utxo = [] #format of dict is {(prev_txid, prev_index):value}
    if response == []:
        print("Transaction cannot be created: UTXO empty")
    else:
        for i in response:
            prev_tx = i['txid']
            prev_index = i['vout']
            value = i['value']
            utxo = (prev_tx, prev_index, value)
            mega_utxo.append(utxo)
        return mega_utxo
    
    
def generate_p2tr_address(priv, merkle_root, network):
    return priv.point.p2tr_address(merkle_root, network=network)


def build_p2tr_txn(priv, pubkeys, tapscripts, internal_key, prev_tx, target_address, fee, amount, leaf_no, cltv):
    tap_leaf = []
    for i in tapscripts:
        tap_leaf.append(TapLeaf(i))
        
    prev_txid = bytes.fromhex(prev_tx[0])
    prev_index = prev_tx[1]

    merkle_root, root_branch, internal_key = build_taproot_tree(tap_leaf, priv)

    tx_in = TxIn(prev_txid, prev_index, sequence=0xfffffffe)
    target_amount = amount - fee
    print(target_amount)
    target_script = address_to_script_pubkey(target_address)
    tx_out = TxOut(target_amount, target_script)
    
    tx_obj = Tx(1, [tx_in], [tx_out], locktime=cltv, network="testnet", segwit=True)
    # for i in [pubkey_1, pubkey_2]:
    cb = root_branch.control_block(priv.point, tap_leaf[leaf_no-1])
    tx_in.witness = Witness([tapscripts[leaf_no-1].raw_serialize(), cb.serialize()])
    
    msg = tx_obj.sig_hash(0)
    sig = priv.sign_schnorr(msg).serialize()
    tx_in.witness.items.insert(0, sig)
    print(tx_obj.verify())
    return (tx_obj.serialize().hex())



# Example leaves
priv = PrivateKey(700)
pubkey_1 = PrivateKey(700).point.xonly()
pubkey_2 = PrivateKey(123).point.xonly()
pubkey_3 = PrivateKey(101).point.xonly()
tap_script_1 = TapScript([pubkey_1, 0xAC, pubkey_2, 0xBA, pubkey_3, 0xBA, 0x52, 0x87])
tap_script_2 = TapScript([encode_minimal_num(1), 0xB1, 0x75, pubkey_1, 0xAC, pubkey_2, 0xBA, pubkey_3, 0xBA, 0x51, 0x87])
tap_script_3 = TapScript([encode_minimal_num(2), 0xB1, 0x75,pubkey_1, 0xAC])
tapscripts = [tap_script_1, tap_script_2, tap_script_3]

pubkeys = [pubkey_1, pubkey_2, pubkey_3]
leaves = []
for i in tapscripts:
    leaves.append(TapLeaf(i))

merkle_root, root_branch, internal_key = build_taproot_tree(leaves, priv)

print("Merkle root:", merkle_root.hex())

# print the hex of the xonly of the external pubkey
print("Internal key:", internal_key.xonly().hex())

#Build txn
priv = PrivateKey(700)
pubkey_1 = PrivateKey(700).point.xonly()
pubkey_2 = PrivateKey(123).point.xonly()
pubkey_3 = PrivateKey(101).point.xonly()
tap_script_1 = TapScript([pubkey_1, 0xAC])
tap_script_2 = TapScript([encode_minimal_num(1), 0xB1, 0x75, pubkey_2, 0xAC])
tap_script_3 = TapScript([encode_minimal_num(2), 0xB1, 0x75, pubkey_3, 0xAC])
tapscripts = [tap_script_1, tap_script_2, tap_script_3]

pubkeys = [pubkey_1, pubkey_2, pubkey_3]
leaves = []
for i in tapscripts:
    leaves.append(TapLeaf(i))

merkle_root, root_branch, internal_key = build_taproot_tree(leaves, priv)

print("Merkle root:", merkle_root.hex())

# print the hex of the xonly of the external pubkey
print("Internal key:", internal_key.xonly().hex())


p2tr_address = generate_p2tr_address(priv, merkle_root, "testnet")
print("Address:", p2tr_address)

target_address = "tb1q0dzcgv7scppjxsnwlzpkt02vlmc5rtr40wyjgr"
utxo = collect_txns(p2tr_address)
prev_tx = (utxo[0][0], utxo[0][1])
print(prev_tx)
amount = utxo[0][2]//3
fee = 500
leaf_no = 1
priv = PrivateKey(700)
tx_obj = build_p2tr_txn(priv, pubkeys, tapscripts, internal_key, prev_tx, target_address, fee, amount, leaf_no, 2)
print(tx_obj)


merkle_root, root_branch, internal_key = build_taproot_tree(leaves, priv)

print("Taproot Tree")
visualize_taproot_tree(root_branch)