# coding: UTF-8

import hashlib
import json

from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []

        self.chain.append(block)
        return block
    
    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        SHA-256 Hash
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        シンプルなプルーフ・オブ・ワークのアルゴリズム:
        - hash(pp')の最初の４つが0となるようなp'を探す
        - pは前のプルーフ、p'は新しいプルーフ
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        プルーフが正しいかを確認する: hash(last_proof, proof)の最初の４つが0となっているか？
        :param last_proof: <int> 前のプルーフ
        :param proof: <int> 現在のプルーフ
        :return: <bool> 正しければ true、そうでなければfalse
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:4] == "0000"


# ノードを作る
app = Flask(__name__)

# このノードのグローバルにユニークなアドレスを作る
node_identifire = str(uuid4()).replace('-', '')

# ブロックチェーンクラスをインスタンス化する
blockchain = Blockchain()

# メソッドはPOSTで/transactions/newエンドポイントを作る、メソッドはPOSTなのでデータを送信する
@app.route('/transactions/new', methods=['POST'])
def new_transactions():
    values = request.get_json()

    # POSTされたデータに必要なデータがあるかを確認
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # 新しいトランザクションを作る
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'トランザクションはブロック {index} に追加されました'}
    return jsonify(response), 201

# メソッドはGETで/mineエンドポイントを作る
@app.route('/mine', methods=['GET'])
def mine():
    return '新しいブロックを採掘します'

# メソッドはGETで、フルのブロックチェーンをリターンする/chainエンドポイントを作る
@app.route('/chain', methods=['GET'])
def full_chain():
    responce = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(responce), 200


# port5000でサーバーを起動する
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)