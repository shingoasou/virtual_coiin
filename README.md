# VirtualCoiin

仮想の仮想通貨です。

## 準備

### 必要なモジュールのインストール
- pip install base58
- pip install ecdsa
- pip install filelock
## 使い方

### 公開鍵と秘密鍵の生成

```shell
# 公開鍵および秘密鍵の生成
$ python key.py

# 電子署名$python key.py
$ python sign.py _input_secret_key_ _input_public_key_ _output_public_key_

# 署名の検証
$ python verify.py

# マイニング
$ python key.py
$ python mine.py _output_reward_public_key_ verbose

# ウォレット
$ python wallet.py

# ピアツーピア
# カレントディレクトをuser1へ変更
$ python -m http.server 8001
# カレントディレクトリをuser2へ変更
$ python -m http.server 8002
# カレントディレクトリuser1でマイニング実行
$ python ../peer.py
# user1で残高を確認
$ python ../wallet.py
# private_key
# public_key
# user2でkey.pyを実行して、鍵を生成
$ python ../key.py
# 最後に表示されるpublic_keyを使用(final_public_key)
# user1でsign.pyを実行して、user2に送金
$ python ../sign.py private_key public_key final_public_key
# user1でマイニングを実行
$ python ../peer.py
# user2でマイニングを実行
$ python ../peer.py
# user2でコインの残高を確認
$ python ../wallet.py
# 自動的にユーザ間でブロックやトランザクションを共有し、自動的にマイニングを実行
# user1およびuser2でmycoind.pyを実行
$ python ../mycoind.py
```
