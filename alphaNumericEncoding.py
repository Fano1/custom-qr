ALPHANUMERIC_TABLE = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"

def encode_alphanumeric_qr(data: str, version: int = 3) -> str:
    # Ensure uppercase (QR alphanumeric only supports uppercase)
    data = data.upper()

    # Validate characters
    for ch in data:
        if ch not in ALPHANUMERIC_TABLE:
            raise ValueError(f"Character '{ch}' not supported in QR alphanumeric mode")

    bitstream = ""

    bitstream += "0010"

    # Version 1–9 uses 9 bits for alphanumeric
    if 1 <= version <= 9:
        bitstream += format(len(data), "09b")
    else:
        raise ValueError("This function currently supports version 1–9 only")

    i = 0
    while i + 1 < len(data):
        first = ALPHANUMERIC_TABLE.index(data[i])
        second = ALPHANUMERIC_TABLE.index(data[i + 1])

        value = 45 * first + second
        bitstream += format(value, "011b")

        i += 2

    if i < len(data):
        last_value = ALPHANUMERIC_TABLE.index(data[i])
        bitstream += format(last_value, "06b")

    return bitstream


print(encode_alphanumeric_qr("abc"))