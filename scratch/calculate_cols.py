def excel_col_to_idx(col_str):
    exp = 0
    idx = 0
    for char in reversed(col_str.upper()):
        idx += (ord(char) - ord('A') + 1) * (26 ** exp)
        exp += 1
    return idx - 1

print(f"LH: {excel_col_to_idx('LH')}")
print(f"LL: {excel_col_to_idx('LL')}")
