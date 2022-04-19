%lang starknet


from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func value()->(res:felt):
end

@view
func get_value{
        syscall_ptr : felt*, 
        pedersen_ptr : HashBuiltin*,
        range_check_ptr
    }() -> (res:felt):

    let (val) = value.read()
    return (val)
end

@external
func set_value{
        syscall_ptr : felt*, 
        pedersen_ptr : HashBuiltin*,
        range_check_ptr
    }(val:felt) -> ():

    value.write(val)
    return()
end