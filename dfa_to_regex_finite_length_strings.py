# The below code is courtesy of [Alok Menghrajani](https://www.quaxio.com).
# Unlike the version in `dfa_to_regex.py`, it generates regex patterns for *finite* length strings in the alphabet.
# You need to install greenery==3.3.7 because lego was removed in greenery 4.x.x versions.

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "greenery==3.3.7",
# ]
# ///

from greenery import fsm, lego

def buildRE(n, parity):
    alphabet = set()
    for c in range(0, n):
        alphabet.add(str(c))
    states = range(0, 2 * n)

    map = {}
    for fromState in states:
        transitions = {}
        for c in alphabet:
            t = int(c)
            nextState = -1
            if fromState < n:
                nextState = (t + fromState) % n + n
            else:
                double = t * 2
                if double >= n:
                    double = double - n + 1
                nextState = (double + fromState - n) % n
            transitions[c] = nextState        
        map[fromState] = transitions
    print(map)

    initial = 0 if parity else n
    print(f"{initial=}")

    machine = fsm.fsm(
        initial,
        {n},
        alphabet,
        states,
        map
    )
    print(machine)

    rex = lego.from_fsm(machine)
    return machine, rex


print("even length strings")
for i in range(2, 8):
    re = str(buildRE(i, False))
    if len(re) < 100:
        print("{0}, {1}, {2}".format(i, len(re), re))
    else:
        print("{0}, {1}".format(i, len(re)))

print()
print("odd length strings")
for i in range(2, 8):
    re = str(buildRE(i, True))
    if len(re) < 100:
        print("{0}, {1}, {2}".format(i, len(re), re))
    else:
        print("{0}, {1}".format(i, len(re)))


## Length 8
regex8 = str(buildRE(8, False))
with open("regex8-False.txt", "w") as f:
    f.write(regex8)

## Length 9 - False
regex9 = str(buildRE(9, False))
with open("regex9-False.txt", "w") as f:
    f.write(regex9)

## Length 10 - False
regex10 = str(buildRE(10, False))
with open("regex10-False.txt", "w") as f:
    f.write(regex10)
