import base58
import ecdsa
import filelock
import hashlib
import json
import sys


# 入力 = 支払元、出力 = 支払先
# コマンドライン引数の処理
if len(sys.argv) != 4:
    print('usage:', sys.argv[0], 'in-private in-public out-public')
    exit()

# 鍵（入力の秘密鍵、入力の公開鍵、出力の公開鍵をバイト列に変換
tx_key = base58.b58decode(sys.argv[1])
tx_in = base58.b58decode(sys.argv[2])
tx_out = base58.b58decode(sys.argv[3])

# 鍵を16進数で表示
print('key hex:', tx_key.hex())
print('in hex:', tx_in.hex())
print('out hex:', tx_out.hex())

# トランザクションハッシュの作成
sha = hashlib.sha256()
sha.update(tx_in)
sha.update(tx_out)
hash = sha.digest()

# トランザクションハッシュの長さと内容を表示
print('hash len:', len(hash))
print('hash hex:', hash.hex())

# トランザクションハッシュに対して署名を実行
key = ecdsa.SigningKey.from_string(tx_key, curve=ecdsa.SECP256k1)
sig = key.sign(hash)

# 署名の長さと内容を表示
print('sig len:', len(sig))
print('sig hex:', sig.hex())

# トランザクションをtrans.txtへ出力
with filelock.FileLock('trans.lock', timeout=10):
    try:
        with open('trans.txt', 'r') as file:
            tx_list = json.load(file)
    except:
        tx_list = []

    tx_list.append({
        'in': tx_in.hex(),
        'out': tx_out.hex(),
        'sig': sig.hex()
    })

    with open('trans.txt', 'w') as file:
        json.dump(tx_list, file, indent=2)
