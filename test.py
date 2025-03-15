from modules.gui import is_float

def test_is_float() -> None:
    assert is_float("3.14")
    assert is_float("3.141567868664545")
    assert is_float("2") # same as 2.0
    assert is_float("    5.62     ")
    assert is_float("-4.6")
    assert is_float("-8")
    assert not is_float("cat")
    assert not is_float("4.6.8")
    assert not is_float("4.6 lol")
    assert not is_float("6.4 7")