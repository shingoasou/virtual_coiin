import os
import subprocess


# ピア・ツー・ピアのプログラムを繰り返し実行する
dir = os.path.dirname(os.path.abspath(__file__))
while True:
    subprocess.run(['python', os.path.join(dir, 'peer.py')])
