class NegativeNumbersError(ValueError):
    pass


def Add(numbers: str) -> float:
    # if not numbers:
    #     return 0
    # numbers = numbers.replace("\n")
    
    delimiter = ","
    body = numbers
    
    # if numbers.startswith("//"):
        # header, _, rest - numbers.partition("\n")
        # body = rest
        # delimiter = header[2:] or ","
        
    # body = body.replace("\n", delimiter)
    

    parts = [p for p in body.split(delimiter) if p != ""]
    
    negs = []
    vals = []
    for p in parts:
        n = (float(p))
        if n < 0:
            negs.append(n)
        else:
            vals.append(n)
        
    if negs:
        raise NegativeNumbersError(f"negative not allowed: {','.join(map(str, negs))}")
    return sum(vals)
    
    return sum(float(p) for p in parts if p != "")
    # if len(parts) == 2:
    #     a,b = parts
    #     return int(a) +int(b)
    
    
    
if __name__ == "__main__":
    assert Add("") == 0
    assert Add("1") == 1
    assert Add("4") == 4
    assert Add("15") == 15
    assert Add(".5") == .5
    assert Add("1,2") == 3
    assert Add("10,10") == 20
    assert Add("1,2,3,4,5") == 15
    assert Add(".5, .5") == 1
    assert Add(".5, .5, .5") == 1.5
    print("All checks have passed")
    
    try:
        Add("-1,-2")
        assert False, "should raise"
    except NegativeNumbersError as e:
        assert "-2" in str(e) and "-1" in str(e)