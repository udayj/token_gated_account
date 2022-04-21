# SPDX-License-Identifier: MIT
%lang starknet


from starkware.cairo.common.cairo_builtins import HashBuiltin
from library import (
    AccountCallArray
)
from starkware.cairo.common.registers import get_fp_and_pc
from starkware.cairo.common.uint256 import Uint256
from starkware.cairo.common.alloc import alloc

# function calls dummy with parameters to set the value

@contract_interface
namespace IAccount:

    func __execute__(
        call_array_len: felt,
        call_array: AccountCallArray*,
        calldata_len: felt,
        calldata: felt*,
        nonce: felt) -> (response_len: felt, response: felt*):
    end

    func get_nonce() -> (res:felt):
    end

    func transferFrom(
        from_: felt, 
        to: felt, 
        tokenId: Uint256
    ) -> ():
    end
 
end

@external
func set_dummy_value{
        syscall_ptr : felt*, 
        pedersen_ptr : HashBuiltin*,
        range_check_ptr
    }(address:felt, val:felt) -> ():

    alloc_locals
    let (__fp__, _) = get_fp_and_pc()
    let (nonce)=IAccount.get_nonce(address)

    let call_array_len = 1

    # the to is just hardcoded for now to the dummy contract deployed locally, can make this a function parameter
    local call_array:AccountCallArray = AccountCallArray(
                                        to=1647056820853998435206193401686715679947059402351372120481244754576671587053,
                                        selector=1737806834891659957988373423388711239891733974125793472992920296585311412419,
                                        data_offset=0,
                                        data_len=1)

   # [call_array].to=915467798312581260633126264016657380654328197130958125403255549563813859781
   # [call_array].selector=1737806834891659957988373423388711239891733974125793472992920296585311412419
   
   # [call_array].data_offset=0
   # [call_array].len=1

    let calldata_len=1
    local calldata = val
    

    let (response_len,response)= IAccount.__execute__(address,
                                                call_array_len,
                                                cast(&call_array,AccountCallArray*),
                                                calldata_len,
                                                cast(&calldata,felt*),
                                                nonce)
    return()
end


