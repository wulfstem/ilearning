import hashlib
from pathlib import Path

digits = [];
ranking = [];
sorted_hashes = [];

def convert_hex(hash: str) -> int:

    product = 1;

    for c in hash:
        product *= int(c, 16) + 1;

    return product;

for file in Path(r"C:\GitRepos\ilearning\ex2\task2").iterdir():
    data = file.read_bytes()
    digest = hashlib.sha3_256(data).hexdigest()
    digit = convert_hex(digest);
    digits.append(digit);
    ranking.append((digit, digest));

digits.sort();
for digit in digits:
    for d, h in ranking:
        if d == digit:
            sorted_hashes.append(h);
            break;

long_hash = hashlib.sha3_256(("".join(sorted_hashes) + "vilkaitis.ervinas@gmail.com").encode()).hexdigest();
print(long_hash);