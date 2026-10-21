"""
Non-deterministic Finite Automaton (NFA) and subset construction.

An NFA is like a DFA, but (state, symbol) may lead to SEVERAL next states
(or none). It accepts if at least one path ends in an accepting state.
Every NFA can be converted to an equivalent DFA (subset construction).
"""
from collections import deque

from automata.dfa import DFA

OTHER = "other"  # stands for "any symbol that is not in the pattern"


def _state_key(name):
    return (len(name), name)  # q2 < q10


class NFA:
    def __init__(self, states, alphabet, transitions, start_state, accepting_states):
        self.states = list(states)
        self.alphabet = set(alphabet)
        self.transitions = {k: set(v) for k, v in transitions.items()}  # -> SET of states
        self.start_state = start_state
        self.accepting_states = set(accepting_states)

    def edges(self):
        return [(src, sym, dst)
                for (src, sym), dsts in self.transitions.items() for dst in dsts]

    def move(self, current_states, symbol):
        """Set of states reachable from ANY current state on `symbol`."""
        result = set()
        for state in current_states:
            result |= self.transitions.get((state, symbol), set())
        return result

    def to_dfa(self):
        """Subset construction: each DFA state = a SET of NFA states."""
        def name(subset):
            return "{" + ",".join(sorted(subset, key=_state_key)) + "}"

        start = frozenset({self.start_state})
        seen = {start}
        queue = deque([start])
        transitions = {}
        while queue:
            subset = queue.popleft()
            for symbol in sorted(self.alphabet):
                target = frozenset(self.move(subset, symbol))
                if not target:
                    continue
                transitions[(name(subset), symbol)] = name(target)
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
        ordered = sorted(seen, key=lambda s: (len(s), name(s)))
        accepting = {name(s) for s in seen if s & self.accepting_states}
        return DFA([name(s) for s in ordered], self.alphabet, transitions,
                   name(start), accepting)


def build_search_nfa(pattern):
    """
    NFA for the language  Sigma* . pattern . Sigma*  ("text CONTAINS pattern").

    q0 loops on every symbol (keeps searching) and, on the first letter of the
    pattern, ALSO guesses "the match starts here" -> that is the non-determinism.
    The last state loops too, so once found the NFA stays accepting.
    """
    alphabet = set(pattern) | {OTHER}
    states = [f"q{i}" for i in range(len(pattern) + 1)]
    transitions = {}
    for sym in alphabet:
        transitions.setdefault((states[0], sym), set()).add(states[0])
        transitions.setdefault((states[-1], sym), set()).add(states[-1])
    for i, ch in enumerate(pattern):
        transitions.setdefault((states[i], ch), set()).add(states[i + 1])
    return NFA(states, alphabet, transitions, states[0], {states[-1]})
