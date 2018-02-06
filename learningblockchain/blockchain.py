# coding: UTF-8

import hashlib
import json

from time import time
from uuid import uuid4


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