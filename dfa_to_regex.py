# /// script
# requires-python = "==3.14.4"
# dependencies = [
#     "greenery",
# ]
# ///

# Unlike the version in `dfa_to_regex_finite_length_strings.py`, this script generates regex patterns that decide arbitrary-length strings in the alphabet.
# Note that the resulting regexes take many minutes to generate, are very large (multi-MB), and are not intended for human consumption.
# For convenience, we construct the even and odd length regexes separately.
# But, of course, the union of the two regexes is also a regex for all Luhn strings.

# If you use the resulting regexes, note that awk, grep, and ripgrep might run out of memory when trying to run them on even a small sample input.
# But, re.fullmatch in Python works! It uses up a lot of memory and is slow, but it works.

import time
from pathlib import Path

import greenery


def build_luhn_dfa(parity: int) -> greenery.fsm.Fsm:
    def luhn_double(d: int) -> int:
        return 2 * d if 2 * d < 10 else 2 * d - 9

    # This part is a bit clunky since greenery changed its FSM construction
    # to require a full partition of the Unicode space as the alphabet.
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
    print("Building DFAs...")
    for parity in ("even", "odd"):
        print(f"== DFA for parity {parity} ==")
        dfa = build_luhn_dfa(0 if parity == "even" else 1)
        print(dfa)

        start = time.time()
        regex: greenery.Pattern = greenery.rxelems.from_fsm(dfa)
        print(
            f"Built regex for decimal {parity}-length strings in {time.time() - start:.1f}s"
        )
        regex_str = str(regex)
        print(f"{len(regex_str)=} with {regex_str[:100]=}")
        Path(f"luhn-regex-{parity}.txt").write_text(regex_str)
