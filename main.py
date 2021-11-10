from web3 import Web3
import json
import requests
from constants import INFURA_HTTP_PROVIDER, TRANSACTION_HASH, ETHERSCAN_API_KEY

# 0xfa59747f31bce72e916bf273e7d102e2f1f884d0fda1ae58705c019c7fab4dff

w3 = Web3(Web3.HTTPProvider(INFURA_HTTP_PROVIDER))

receipt = w3.eth.get_transaction_receipt(TRANSACTION_HASH)

log = receipt['logs'][0]

smart_contract = log['address']

# Get ABI Smart contract
abi_endpoint = f"https://api.etherscan.io/api?module=contract&action=getabi&address={smart_contract}&apikey={ETHERSCAN_API_KEY}"
abi = json.loads(requests.get(abi_endpoint).text)

# Create contract object
contract = w3.eth.contract(smart_contract, abi=abi["result"])

# Get event signature of log (first item in topics array)
receipt_event_signature_hex = w3.toHex(log["topics"][0])

# Find ABI events
abi_events = [abi for abi in contract.abi if abi["type"] == "event"]
print(abi_events)

for event in abi_events:
    #Get event signature component
    name = event['name']
    inputs = [param['type'] for param in event['inputs']]
    inputs = ','.join(inputs)

    event_signature_text = f"{name}({inputs})"
    print(event_signature_text)
    event_signature_hex = w3.toHex(w3.keccak(text=event_signature_text))

    if event_signature_hex == receipt_event_signature_hex:
        decoded_logs = contract.events[event['name']]().processReceipt(receipt)

# JSON
receipt_json = Web3.toJSON(receipt)

with open("out-data.json", "w+") as out_file:
    out_file.write(receipt_json)
