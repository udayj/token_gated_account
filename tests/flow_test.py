from starkware.crypto.signature.signature import private_to_stark_key, sign
from starkware.starknet.core.os.transaction_hash import (
    TransactionHashPrefix,
    calculate_transaction_hash_common,
)

from starkware.crypto.signature.signature import private_to_stark_key
from starkware.starknet.definitions.general_config import StarknetChainId
from starkware.starknet.public.abi import get_selector_from_name

from nile.core.call_or_invoke import call_or_invoke
import os
import subprocess

# deploy account, dummy contract, owner contract
# sign transaction to set value to 1
# send call to owner contract to ultimately call set value (should error out)
# transfer NFT to owner contract
# sign transaction to set value to 3 (should error)
# send call to owner contract to ultimately call set value to 2 (should work)

TRANSACTION_VERSION = 0


def from_call_to_call_array(calls):
    """Transform from Call to CallArray."""
    call_array = []
    calldata = []
    for _, call in enumerate(calls):
        assert len(call) == 3, "Invalid call parameters"
        entry = (
            int(call[0], 16),
            get_selector_from_name(call[1]),
            len(calldata),
            len(call[2]),
        )
        call_array.append(entry)
        calldata.extend(call[2])
    return (call_array, calldata)


def get_transaction_hash(account, call_array, calldata, nonce, max_fee):
    """Calculate the transaction hash."""
    execute_calldata = [
        len(call_array),
        *[x for t in call_array for x in t],
        len(calldata),
        *calldata,
        nonce,
    ]

    return calculate_transaction_hash_common(
        TransactionHashPrefix.INVOKE,
        TRANSACTION_VERSION,
        account,
        get_selector_from_name("__execute__"),
        execute_calldata,
        max_fee,
        StarknetChainId.TESTNET.value,
        [],
    )


def sign_transaction(sender, calls, nonce, max_fee=0):
        """Sign a transaction for an Account."""
        (call_array, calldata) = from_call_to_call_array(calls)
        print("callarray:",call_array)
        print("calldata:",calldata)
        message_hash = get_transaction_hash(
            int(sender, 16), call_array, calldata, nonce, max_fee
        )
        print("message_hash:",message_hash)
        print("public key:",private_to_stark_key(1234))
        sig_r, sig_s = sign(msg_hash=message_hash, priv_key=1234)
        return (call_array, calldata, sig_r, sig_s)

def run(nre):

    account_address="0x071083328c943fedc9f6b06086571c1d50d8435da99fa4bf857c9e310952d304"
    dummy_address="0x03a4337ce788ef608b904b806e222f7f5f1d2f16a9ecf9dd71ccdaf2098d3aed"

    command = [
        "starknet",
        "call",
        "--address",
        account_address,
        "--abi",
        "/root/eth/test_cairo/token_gated_account/artifacts/abis/Account.json",
        "--function",
        "get_nonce",
    ]

    command.append("--feeder_gateway_url=http://127.0.0.1:5000/")

    nonce = int(subprocess.check_output(command).strip().decode("utf-8"))
    
    print("nonce:",nonce)

    (call_array, calldata, sig_r, sig_s) = sign_transaction(
            sender=account_address, calls=[[dummy_address, "set_value", [1]]], nonce=nonce
        )

    params = []
    params.append(str(len(call_array)))
    params.extend([str(elem) for sublist in call_array for elem in sublist])
    params.append(str(len(calldata)))
    params.extend([str(param) for param in calldata])
    params.append(str(nonce))

    print(params)


    command = [
        "starknet",
        "invoke",
        "--address",
        account_address,
        "--abi",
        "/root/eth/test_cairo/token_gated_account/artifacts/abis/Account.json",
        "--function",
        "__execute__",
    ]

    command.append("--gateway_url=http://127.0.0.1:5000/")

    command.append("--inputs")
    command.extend(params)

    command.append("--signature")
    command.extend([str(sig_r), str(sig_s)])

    val= subprocess.check_output(command).strip().decode("utf-8")
    
    print(val)    


