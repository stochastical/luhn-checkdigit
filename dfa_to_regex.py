# /// script
# requires-python = "==3.14.4"
# dependencies = [
#     "greenery",
# ]
# ///

# Unlike the version in `dfa_to_regex_finite_length_strings.py`, this script generates regex patterns that decide arbitrary-length strings in the alphabet.

import time

import greenery

def build_luhn_dfa(parity: int) -> greenery.fsm.Fsm:
    def luhn_double(d: int) -> int:
        return 2 * d if 2 * d < 10 else 2 * d - 9

    # NOTE: Sorry, this part is clunky since greenery changed their FSM construction
    # to require a full partition of the Unicode space as the alphabet,
    # which makes things more complicated than they need to be.
    digits = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
    non_digits = ~greenery.Charclass((("0", "9"),))
    alphabet = {greenery.Charclass(c) for c in digits}
    states = range(0, 2 * 10)
    initial = 0 if parity else 10
    finals = {10}

    transition_map = {}
    for from_state in states:
        state_transition = {}
        for c in digits:
            d = int(c)
            next_state = -1
            if from_state < 10:
                next_state = (d + from_state) % 10 + 10
            else:
                next_state = (luhn_double(d) + from_state - 10) % 10
            state_transition[greenery.Charclass(c)] = next_state
        state_transition[non_digits] = 0
        transition_map[from_state] = state_transition

    return greenery.fsm.Fsm(
        alphabet=alphabet | {non_digits},
        states=states,
        initial=initial,
        finals=finals,
        map=transition_map,
    )


if __name__ == "__main__":
    POSITIVE_CASES = [
        # Source: https://docs.stripe.com/testing#cards
        "4242424242424242",
        "4000056655665556",
        "5555555555554444",
        "2223003122003222",
        "5200828282828210",
        "5105105105105100",
        "378282246310005",
        "371449635398431",
        "6011111111111117",
        "6011000990139424",
        "6011981111111113",
        "3056930009020004",
        "36227206271667",
        "6555900000604105",
        "3566002020360505",
        "6200000000000005",
        "6200000000000047",
        "6205500000000000004",
        "4000002500001001",
        "5555552500001001",
        "4000050360000001",
        "5555050360000080",
        # Additional positive cases
        "0",
        "18",
    ]

    NEGATIVE_CASES = [
        "4242424242424241",
        "4000056655665555",
        "5555555555554443",
        "2223003122003221",
        "5200828282828211",
        "5105105105105101",
        "378282246310004",
        "371449635398430",
        "6011111111111116",
        "6011000990139423",
        "6011981111111112",
        "3056930009020003",
        "36227206271668",
        "6555900000604104",
        "3566002020360504",
        "6200000000000004",
        "6200000000000046",
        "6205500000000000003",
        "4000002500001000",
        "5555552500001000",
        "4000050360000000",
        "5555050360000081",
        "1",
        "1234567890123456",
        "9999999999999999",
        "1111111111111111",
        "2222222222222222",
        "3333333333333333",
        "4444444444444444",
        "123456789",
        "999",
        "5",
        "7",
        "9",
        "12",
        "25",
        "37",
        "44",
        "56",
        "73",
        "88",
        "95",
        "100",
        "111",
        "222",
        "333",
        "444",
        "555",
        "666",
        "777",
        "888",
        "1000",
        "10000",
        "100000",
        "1000000",
        "10000000",
        "100000000",
        "1000000000",
        "4242424242424243",
        "4000056655665557",
        "5555555555554445",
        "2223003122003223",
        "378282246310006",
        "371449635398432",
        "6011111111111118",
        "1010101010101010",
        "2020202020202020",
        "5656565656565656",
        "7878787878787878",
        "9090909090909090",
        "1234567890123456",
        "9876543210987654",
        "1357913579135791",
        "2468024680246802",
        "1001",
        "1111",
        "1221",
        "1331",
        "1441",
        "1551",
        "12321",
        "123321",
        "1234321",
        "123454321",
        "1234554321",
        "1000000000000000",
        "2000000000000000",
        "5000000000000000",
        "9000000000000000",
        "1000000000000001",
        "1000000000000002",
        "1000000000000005",
        "1000000000000003",
        "1000000000000004",
        "1000000000000006",
        "1000000000000007",
        "1000000000000009",
        "9876543210123456",
        "1357924680135792",
        "9999999999999998",
        "8888888888888887",
        "7777777777777776",
        "6666666666666665",
        "12345678901234567890",
        "10000000000000000000",
    ]

    # Build DFA for even length strings
    print("== Even length Luhn strings ==")
    luhn_dfa_even = build_luhn_dfa(0)
    print(luhn_dfa_even)

    # Test even cases
    assert all(luhn_dfa_even.accepts(s) for s in POSITIVE_CASES if len(s) % 2 == 0)
    assert all(not luhn_dfa_even.accepts(s) for s in NEGATIVE_CASES if len(s) % 2 == 0)
    print("Even length tests passed!")

    # Build even regex and save to file (warning: this will take a long time and produce a huge file)
    # (takes about 20m on my MacBook Air M1)
    start = time.time()
    regex_even: greenery.Pattern = greenery.rxelems.from_fsm(luhn_dfa_even)
    print(f"Successfully built regex for decimal even-length strings in {time.time() - start:.1f} s")
    regex_str_even = str(regex_even)
    print(f"{len(regex_str_even)=} with {regex_str_even[:100]=}")
    with open(f"luhn-regex-even.txt", "w") as f:
        f.write(regex_str_even)

    # Build DFA for odd length strings
    print("== Odd length Luhn strings ==")
    luhn_dfa_odd = build_luhn_dfa(1)
    print(luhn_dfa_odd)
    
    # Test odd cases
    assert all(luhn_dfa_odd.accepts(s) for s in POSITIVE_CASES if len(s) % 2 == 1)
    assert all(not luhn_dfa_odd.accepts(s) for s in NEGATIVE_CASES if len(s) % 2 == 1)
    print("Odd length tests passed!")

    # Build odd regex and save to file (warning: this will take a long time and produce a huge file)
    start = time.time()
    regex_odd: greenery.Pattern = greenery.rxelems.from_fsm(luhn_dfa_odd)
    print(f"Successfully built regex for decimal odd-length strings in {time.time() - start:.1f} s")
    regex_str_odd = str(regex_odd)
    print(f"{len(regex_str_odd)=} with {regex_str_odd[:100]=}")
    with open(f"luhn-regex-odd.txt", "w") as f:
        f.write(regex_str_odd)

    # NOTE: We can now union these two regexes together and we have the full Luhn regex! (but I'll keep them separate for now)

    # NOTE: awk, grep, and ripgrep are all being killed when trying to run the full even regex on a sample input "18"
    # but, re.fullmatch works! It uses up a bunch of memory, and it's slow 
    # (but not as slow as I expected), but it works!!
