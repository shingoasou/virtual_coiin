import base58
import ecdsa
import filelock
import hashlib
import json
import re
import sys


# 難易度と経過表示
DIFFICULTY = 4
VERBOSE = False

# コマンドライン引数の処理（使い方）
if len(sys.argv) != 2 and len(sys.argv) != 3:
    print('usage:', sys.args[0], 'public-key verbose')
    exit()

# コマンドライン引数の処理（経過表示）
if len(sys.argv) == 3 and sys.argv[2] == 'verbose':
    VERBOSE = True

# マイニング用公開鍵を16進数表記に変換
public_key = base58.b58decode(sys.argv[1]).hex()

# ブロックチェーンをblock.txtから入力
with filelock.FileLock('block.lock', timeout=10):
    try:
        with open('block.txt', 'r') as file:
            block_list = json.load(file)
            previous_hash = block_list[-1]['hash']
    except:
        block_list = []
        previous_hash = ''

# トランザクションをtrans.txtから入力
with filelock.FileLock('trans.lock', timeout=10):
    try:
        with open('trans.txt', 'r') as file:
            tx_list = json.load(file)
    except:
        tx_list = []

# 既存トランザクション入出力のリストを作成
old_in = []
old_out = []
for block in block_list:
    for tx in block['tx']:
        old_in.append(tx['in'])
        old_out.append(tx['out'])

# トランザクションの検証
file_tx_list = tx_list
tx_list = []
for tx in file_tx_list:
    sha = hashlib.sha256()
    sha.update(bytes.fromhex(tx['in']))
    sha.update(bytes.fromhex(tx['out']))
    hash = sha.digest()
    key = ecdsa.VerifyingKey.from_string(bytes.fromhex(tx['in']), curve=ecdsa.SECP256k1)

    if not key.verify(bytes.fromhex(tx['sig']), hash):
        print('invalid signature:', tx['sig'])
    elif tx['in'] in old_in:
        print('tx-in has already been spent:', tx['in'])
    elif tx['in'] not in old_out:
        print('tx-out for tx-in is not found:', tx['in'])
    elif tx['out'] in old_in or tx['out'] in old_out:
        print('tx-out is reused:', tx['out'])
    else:
        tx_list.append(tx)
        old_in.append(tx['in'])
        old_out.append(tx['out'])

# マイニング用公開鍵の検証
if public_key in old_in or public_key in old_out:
    print('public-key is reused:', public_key)
    exit()
old_out.append(public_key)

# ジェネレーショントランザクションの追加
tx_list.insert(0, {
    'in': '',
    'out': public_key,
    'sig': ''
})

# トランザクションハッシュの計算
sha = hashlib.sha256()
for tx in tx_list:
    sha.update(bytes.fromhex(tx['in']))
    sha.update(bytes.fromhex(tx['out']))
    sha.update(bytes.fromhex(tx['sig']))
tx_hash = sha.digest()

# ノンスの探索
for nonce in range(100000000):
    sha = hashlib.sha256()
    sha.update(bytes(nonce))
    sha.update(bytes.fromhex(previous_hash))
    sha.update(tx_hash)
    hash = sha.digest()

    if VERBOSE:
        print('nonce:{0:08d}'.format(nonce), 'hash hex:', hash.hex())

    if re.match(r'0{' + str(DIFFICULTY) + r'}', hash.hex()):
        break

# ゴールデンノンスの表示
if not VERBOSE:
    print('nonce:{0:08d}'.format(nonce), 'hash hex:', hash.hex())

# ブロックチェーンへのブロックの追加
block_list.append({
    'hash': hash.hex(),
    'nonce': nonce,
    'previous hash': previous_hash,
    'tx_hash': tx_hash.hex(),
    'tx': tx_list
})

# ブロックチェーンをblock.txtへ出力
with filelock.FileLock('block.lock', timeout=10):
    with open('block.txt', 'w') as file:
        json.dump(block_list, file, indent=2)

# ブロックに登録したトランザクションをtrans.txtから削除
with filelock.FileLock('trans.lock', timeout=10):
    try:
        with open('trans.txt', 'r') as file:
            file_tx_list = json.load(file)
    except:
        file_tx_list = []

    tx_list = []
    for tx in file_tx_list:
        if tx['in'] not in old_in and tx['out'] not in old_in and tx['out'] not in old_out:
            tx_list.append(tx)

    with open('trans.txt', 'w') as file:
        json.dump(tx_list, file, indent=2)
