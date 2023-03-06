import random


def generate_code():
    code = int(''.join([str(random.randint(0, 10)) for _ in range(4)]))
    return code
