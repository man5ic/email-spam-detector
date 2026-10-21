"""
Deterministic Finite Automaton (DFA).

A DFA is a 5-tuple (Q, Sigma, delta, q0, F):
    Q      - finite set of states
    Sigma  - input alphabet
    delta  - transition function: (state, symbol) -> exactly ONE next state
    q0     - start state
    F      - set of accepting (final) states
"""


class DFA:
    def __init__(self, states, alphabet, transitions, start_state, accepting_states):
        self.states = list(states)
        self.alphabet = set(alphabet)
        self.transitions = dict(transitions)  # {(state, symbol): next_state}
        self.start_state = start_state
        self.accepting_states = set(accepting_states)

    def edges(self):
        """All transitions as (source, symbol, destination) triples."""
        return [(src, sym, dst) for (src, sym), dst in self.transitions.items()]

    def run(self, symbols):
        """
        Feed the symbols to the DFA one by one.

        Returns (accepted, trace). `trace` has one entry per step so the UI can
        show the simulation. A missing transition means the DFA goes to an
        implicit DEAD (trap) state and the input is rejected.
        """
        state = self.start_state
        trace = []
        for step, symbol in enumerate(symbols, start=1):
            next_state = self.transitions.get((state, symbol))
            trace.append({
                "step": step,
                "current_state": state,
                "symbol": symbol,
                "next_state": next_state if next_state is not None else "DEAD",
            })
            if next_state is None:
                return False, trace
            state = next_state
        return state in self.accepting_states, trace


def build_literal_dfa(pattern):
    """
    DFA that accepts exactly the string `pattern` (a chain of states).

    FREE ->  q0 -F-> q1 -R-> q2 -E-> q3 -E-> q4   (q4 accepting)
    """
    states = [f"q{i}" for i in range(len(pattern) + 1)]
    transitions = {(states[i], ch): states[i + 1] for i, ch in enumerate(pattern)}
    return DFA(states, set(pattern), transitions, states[0], {states[-1]})
