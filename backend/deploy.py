import os, json
from web3 import Web3

p = os.path.join(os.path.dirname(__file__), '..', 'blockchain', 'build', 'contracts', 'S.json')
with open(p, "r") as f:
    c = json.load(f)

a = c['abi']
b = c['bytecode']

ru = os.environ.get("RPC_URL")
pk = os.environ.get("PRIVATE_KEY")
ad = os.environ.get("ACCOUNT_ADDRESS")

w = Web3(Web3.HTTPProvider(ru))
sc = w.eth.contract(abi=a, bytecode=b)

tx = sc.constructor().build_transaction({
    'from': ad,
    'nonce': w.eth.get_transaction_count(ad),
    'gas': 2000000,
    'gasPrice': w.to_wei('50', 'gwei')
})

sn = w.eth.account.sign_transaction(tx, pk)
th = w.eth.send_raw_transaction(sn.rawTransaction)
rc = w.eth.wait_for_transaction_receipt(th)

print(rc.contractAddress)