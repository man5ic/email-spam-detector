"""Build Graphviz DOT strings (rendered with st.graphviz_chart, no extra install)."""
from collections import defaultdict


def _esc(text):
    return str(text).replace("\\", "\\\\").replace('"', '\\"')


def _sym(symbol):
    return "\u2423" if symbol == " " else symbol  # show a space as a visible symbol


def _label(symbols, alphabet):
    """Compact edge label, so loops over many symbols stay readable."""
    missing = sorted(set(alphabet) - set(symbols))
    if not missing:
        return "any symbol"
    names = sorted(symbols)
    if len(names) > 5 and len(missing) <= 4:
        return "all except " + ",".join(_sym(m) for m in missing)
    return ",".join(_sym(s) for s in names[:5]) + ("..." if len(names) > 5 else "")


def automaton_to_dot(automaton, theme="white"):
    """Works for both DFA and NFA objects (they share the same attributes).
    
    theme="white": White background card with crisp, visible dark lines, arrows, and labels.
    theme="dark": Transparent background with glowing white lines, arrows, and labels.
    """
    grouped = defaultdict(set)
    for src, sym, dst in automaton.edges():
        grouped[(src, dst)].add(sym)

    if theme == "white":
        lines = [
            "digraph G {",
            "rankdir=LR;",
            'bgcolor="#ffffff";',
            'node [shape=circle, fontsize=12, color="#2b2d42", fontcolor="#111111", penwidth=1.6];',
            'edge [fontsize=11, color="#2b2d42", fontcolor="#111111", penwidth=1.5];',
            '__start [shape=point, color="#2b2d42", fillcolor="#2b2d42", width=0.12, label=""];'
        ]
        for state in automaton.states:
            accepting = state in automaton.accepting_states
            start = state == automaton.start_state
            shape = "doublecircle" if accepting else "circle"
            fill = "#c8e6c9" if accepting else ("#bbdefb" if start else "#ffffff")
            border = "#2e7d32" if accepting else ("#1976d2" if start else "#455a64")
            lines.append(f'"{_esc(state)}" [shape={shape}, style=filled, '
                         f'fillcolor="{fill}", color="{border}", fontcolor="#111111"];')
        lines.append(f'__start -> "{_esc(automaton.start_state)}";')
        for (src, dst), symbols in grouped.items():
            lines.append(f'"{_esc(src)}" -> "{_esc(dst)}" '
                         f'[label="{_esc(_label(symbols, automaton.alphabet))}"];')
        lines.append("}")
        return "\n".join(lines)
    else:
        lines = [
            "digraph G {",
            "rankdir=LR;",
            'bgcolor="transparent";',
            'node [shape=circle, fontsize=12, color="#ffffff", fontcolor="#ffffff", penwidth=1.6];',
            'edge [fontsize=11, color="#ffffff", fontcolor="#ffffff", penwidth=1.5];',
            '__start [shape=point, color="#ffffff", fillcolor="#ffffff", width=0.12, label=""];'
        ]
        for state in automaton.states:
            accepting = state in automaton.accepting_states
            start = state == automaton.start_state
            shape = "doublecircle" if accepting else "circle"
            fill = "#1b5e20" if accepting else ("#0d47a1" if start else "#262730")
            border = "#81c784" if accepting else ("#64b5f6" if start else "#ffffff")
            lines.append(f'"{_esc(state)}" [shape={shape}, style=filled, '
                         f'fillcolor="{fill}", color="{border}", fontcolor="#ffffff"];')
        lines.append(f'__start -> "{_esc(automaton.start_state)}";')
        for (src, dst), symbols in grouped.items():
            lines.append(f'"{_esc(src)}" -> "{_esc(dst)}" '
                         f'[label="{_esc(_label(symbols, automaton.alphabet))}"];')
        lines.append("}")
        return "\n".join(lines)


def trie_to_dot(detector, show_failure_links=False, theme="white"):
    """Trie part of the multi-pattern automaton (dashed = failure links)."""
    if theme == "white":
        lines = [
            "digraph G {",
            "rankdir=LR;",
            'bgcolor="#ffffff";',
            'node [shape=circle, fontsize=11, color="#2b2d42", fontcolor="#111111", penwidth=1.5];',
            'edge [fontsize=11, color="#2b2d42", fontcolor="#111111", penwidth=1.5];',
            '__start [shape=point, color="#2b2d42", fillcolor="#2b2d42", width=0.12, label=""];'
        ]
        for state, pattern in enumerate(detector.terminal):
            if pattern:
                lines.append(f'q{state} [shape=doublecircle, style=filled, fillcolor="#c8e6c9", '
                             f'color="#2e7d32", fontcolor="#111111", label="q{state}\\n{_esc(pattern)}"];')
            else:
                fill = "#bbdefb" if state == 0 else "#ffffff"
                border = "#1976d2" if state == 0 else "#455a64"
                lines.append(f'q{state} [style=filled, fillcolor="{fill}", color="{border}", fontcolor="#111111"];')
        lines.append("__start -> q0;")
        for state, edges in enumerate(detector.goto):
            for ch, child in edges.items():
                lines.append(f'q{state} -> q{child} [label="{_esc(_sym(ch))}"];')
        if show_failure_links:
            for state, target in enumerate(detector.fail):
                if state and target:
                    lines.append(f'q{state} -> q{target} [style=dashed, color="#d32f2f", '
                                 f'fontcolor="#d32f2f", label="fail"];')
        lines.append("}")
        return "\n".join(lines)
    else:
        lines = [
            "digraph G {",
            "rankdir=LR;",
            'bgcolor="transparent";',
            'node [shape=circle, fontsize=11, color="#ffffff", fontcolor="#ffffff", penwidth=1.5];',
            'edge [fontsize=11, color="#ffffff", fontcolor="#ffffff", penwidth=1.5];',
            '__start [shape=point, color="#ffffff", fillcolor="#ffffff", width=0.12, label=""];'
        ]
        for state, pattern in enumerate(detector.terminal):
            if pattern:
                lines.append(f'q{state} [shape=doublecircle, style=filled, fillcolor="#1b5e20", '
                             f'color="#81c784", fontcolor="#ffffff", label="q{state}\\n{_esc(pattern)}"];')
            else:
                fill = "#0d47a1" if state == 0 else "#262730"
                border = "#64b5f6" if state == 0 else "#ffffff"
                lines.append(f'q{state} [style=filled, fillcolor="{fill}", color="{border}", fontcolor="#ffffff"];')
        lines.append("__start -> q0;")
        for state, edges in enumerate(detector.goto):
            for ch, child in edges.items():
                lines.append(f'q{state} -> q{child} [label="{_esc(_sym(ch))}"];')
        if show_failure_links:
            for state, target in enumerate(detector.fail):
                if state and target:
                    lines.append(f'q{state} -> q{target} [style=dashed, color="#ef5350", '
                                 f'fontcolor="#ef5350", label="fail"];')
        lines.append("}")
        return "\n".join(lines)
