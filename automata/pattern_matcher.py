"""
Multi-pattern matcher built as a DFA (Aho-Corasick automaton).

Idea: put all patterns in one trie (a tree of states). Then add transitions so
that the automaton never has to "go back" in the text: on a mismatch it jumps
to the state that represents the longest suffix that is still a prefix of some
pattern (the "failure link"). After this completion step every state has a
transition for every symbol, so it is a real DFA, and one pass over the email
(one character = one transition) finds ALL patterns at once.
"""
from collections import deque
from dataclasses import dataclass


@dataclass
class Match:
    pattern: str
    start: int  # index of first character (inclusive)
    end: int    # index of last character (inclusive)


def normalize_text(text):
    """
    Upper-case the text and turn any whitespace (newline, tab...) into a space.
    The length never changes, so match positions still fit the original text.
    """
    chars = []
    for ch in text:
        if ch.isspace():
            chars.append(" ")
        else:
            up = ch.upper()
            chars.append(up if len(up) == 1 else ch)
    return "".join(chars)


class MultiPatternDFA:
    def __init__(self, patterns):
        self.patterns = [normalize_text(p) for p in patterns]
        self.goto = [{}]          # trie edges: goto[state][char] -> state
        self.terminal = [None]    # pattern that ENDS exactly at this state
        self._build_trie()

        self.fail = [0] * len(self.goto)
        self.output = [set() for _ in self.goto]  # all patterns ending here
        self.delta = [dict() for _ in self.goto]  # complete DFA transitions
        self.alphabet = sorted({c for p in self.patterns for c in p})
        self._complete_automaton()

    # -- construction ------------------------------------------------------
    def _build_trie(self):
        for pattern in self.patterns:
            state = 0
            for ch in pattern:
                if ch not in self.goto[state]:
                    self.goto.append({})
                    self.terminal.append(None)
                    self.goto[state][ch] = len(self.goto) - 1
                state = self.goto[state][ch]
            self.terminal[state] = pattern

    def _complete_automaton(self):
        """Breadth-first: compute failure links, outputs and full delta."""
        for state, pattern in enumerate(self.terminal):
            if pattern:
                self.output[state].add(pattern)
        queue = deque([0])
        while queue:
            state = queue.popleft()
            for ch in self.alphabet:
                if ch in self.goto[state]:
                    self.delta[state][ch] = self.goto[state][ch]
                elif state == 0:
                    self.delta[state][ch] = 0
                else:
                    self.delta[state][ch] = self.delta[self.fail[state]][ch]
            for ch, child in self.goto[state].items():
                self.fail[child] = 0 if state == 0 else self.delta[self.fail[state]][ch]
                self.output[child] |= self.output[self.fail[child]]
                queue.append(child)

    # -- running -----------------------------------------------------------
    def step(self, state, ch):
        """delta(state, ch). A symbol outside the alphabet sends us to q0."""
        return self.delta[state].get(ch, 0)

    def info(self):
        return {
            "patterns": len(self.patterns),
            "states": len(self.goto),
            "alphabet_size": len(self.alphabet),
            "transitions": sum(len(d) for d in self.delta),
            "accepting_states": sum(1 for o in self.output if o),
        }

    def scan(self, text):
        """
        Run the DFA over the email.
        Returns (matches, trace): `matches` = detection result,
        `trace` = state-by-state simulation of the whole scan.
        """
        text = normalize_text(text)
        matches, trace = [], []
        state = 0
        for i, ch in enumerate(text):
            next_state = self.step(state, ch)
            found = []
            for pattern in sorted(self.output[next_state]):
                start, end = i - len(pattern) + 1, i
                if self._is_whole_word(text, start, end):
                    matches.append(Match(pattern, start, end))
                    found.append(pattern)
            trace.append({"position": i, "symbol": ch,
                          "current_state": f"q{state}",
                          "next_state": f"q{next_state}",
                          "pattern_found": ", ".join(found)})
            state = next_state
        return matches, trace

    @staticmethod
    def _is_whole_word(text, start, end):
        """Avoid matching WIN inside WINDOW: neighbours must not be letters/digits."""
        before_ok = start == 0 or not text[start - 1].isalnum()
        after_ok = end == len(text) - 1 or not text[end + 1].isalnum()
        return before_ok and after_ok
