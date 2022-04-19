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

    account_address="0x00df974c74f6beb6bab039c8a1b83aa062974307f1cd10cc81fd0ca3c21a3d03"
    dummy_address="0x020622ebe1f04d8d071d76e285df3fe58895a2a93e7427183cb1fa89322d91c5"

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

    from_address=int("0x1f3c942d7f492a37608cde0d77b884a5aa9e11d2919225968557370ddb5a5aa",16)
    to_address=int("0x03ca3930dbff97547adae053fb98d281d1273ef6457cd0ef7fe57dd87e32851f",16)

    (call_array, calldata, sig_r, sig_s) = sign_transaction(
            sender=account_address, calls=[
                [account_address, "approve", [int(account_address,16),0,0]],
                [account_address, "transferFrom", [from_address,to_address,0,0]]], nonce=nonce
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


