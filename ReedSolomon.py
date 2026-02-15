# reed_solomon.py

def generate_gf_tables():
    exp = [0] * 512
    log = [0] * 256

    x = 1
    for i in range(255):
        exp[i] = x
        log[x] = i
        x <<= 1
        if x & 0x100:
            x ^= 0x11D  # QR primitive polynomial

    for i in range(255, 512):
        exp[i] = exp[i - 255]

    return exp, log


GF_EXP, GF_LOG = generate_gf_tables()


def gf_mul(a, b):
    if a == 0 or b == 0:
        return 0
    return GF_EXP[GF_LOG[a] + GF_LOG[b]]


def generate_generator_poly(degree):
    gen = [1]

    for i in range(degree):
        new_gen = [0] * (len(gen) + 1)
        for j in range(len(gen)):
            new_gen[j] ^= gf_mul(gen[j], 1)
            new_gen[j + 1] ^= gf_mul(gen[j], GF_EXP[i])
        gen = new_gen

    return gen


def reed_solomon_encode(data_bytes, ecc_length):
    generator = generate_generator_poly(ecc_length)
    message = data_bytes + [0] * ecc_length

    for i in range(len(data_bytes)):
        coef = message[i]
        if coef != 0:
            for j in range(len(generator)):
                message[i + j] ^= gf_mul(generator[j], coef)

    return message[-ecc_length:]
