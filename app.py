"""Email Spam Pattern Detector using Finite Automata - Streamlit app."""
import streamlit as st

from automata.dfa import build_literal_dfa
from automata.nfa import build_search_nfa
from automata.pattern_matcher import MultiPatternDFA, normalize_text
from data.spam_patterns import EXAMPLE_EMAILS, PATTERN_CATEGORIES, SPAM_PATTERNS
from utils.highlighting import highlight_email
from utils.scoring import SPAM_THRESHOLD, evaluate
from utils.visualization import automaton_to_dot, trie_to_dot

st.set_page_config(page_title="Spam Pattern Detector (Finite Automata)", page_icon="📧",
                   layout="wide")


@st.cache_resource
def get_detector(patterns):
    """Build the multi-pattern DFA once and reuse it."""
    return MultiPatternDFA(list(patterns))


def visible(symbol):
    return "\u2423 (space)" if symbol == " " else symbol


# ---------------------------------------------------------------- state ----
st.session_state.setdefault("email_text", "")
st.session_state.setdefault("analysis", None)
st.session_state.setdefault("empty_input", False)


def load_example(name):
    st.session_state.email_text = EXAMPLE_EMAILS[name]
    st.session_state.analysis = None
    st.session_state.empty_input = False


def run_detection():
    text = st.session_state.email_text
    if not text.strip():
        st.session_state.analysis = None
        st.session_state.empty_input = True
        return
    st.session_state.empty_input = False
    matches, trace = get_detector(tuple(SPAM_PATTERNS)).scan(text)
    st.session_state.analysis = {"text": text, "matches": matches,
                                 "trace": trace, "result": evaluate(matches)}


# ------------------------------------------------------------------ UI -----
st.title("📧 Email Spam Pattern Detector")
st.caption("A rule-based detector built on Finite Automata (Theory of Computation mini-project). "
           "It is an educational tool, not a real-world spam filter.")

tab_detect, tab_sim, tab_diagram, tab_toc = st.tabs(
    ["🔍 Detector", "▶️ Automaton Simulation", "🧩 Automaton Diagrams", "📚 TOC Concepts"])

# ============================ TAB 1: DETECTOR ==============================
with tab_detect:
    st.write("**Load an example (optional):**")
    cols = st.columns(len(EXAMPLE_EMAILS))
    for col, name in zip(cols, EXAMPLE_EMAILS):
        col.button(name, on_click=load_example, args=(name,))

    st.text_area("Paste an email here", key="email_text", height=180,
                 placeholder="Type or paste the email text...")
    st.button("Detect Spam", type="primary", on_click=run_detection)

    if st.session_state.empty_input:
        st.warning("Please enter some email text first.")

    analysis = st.session_state.analysis
    if analysis:
        result = analysis["result"]
        st.divider()
        if result["is_spam"]:
            st.error("🚨 SPAM DETECTED")
        else:
            st.success("✅ NOT SPAM")

        m1, m2, m3 = st.columns(3)
        m1.metric("Risk Score", f"{result['risk_score']}/5")
        m2.metric("Distinct patterns found", len(result["rows"]))
        m3.metric("Total matches", result["total_matches"])
        st.caption(f"Total pattern weight = {result['total_weight']}. "
                   f"The email is called spam when the weight is at least {SPAM_THRESHOLD}.")

        st.subheader("Detected patterns")
        if result["rows"]:
            st.dataframe(result["rows"], hide_index=True)
        else:
            st.info("No suspicious pattern was accepted by the automaton.")

        st.subheader("Highlighted email")
        st.markdown(highlight_email(analysis["text"], analysis["matches"]),
                    unsafe_allow_html=True)

        with st.expander("Automaton information"):
            info = get_detector(tuple(SPAM_PATTERNS)).info()
            st.write(f"- Patterns loaded: **{info['patterns']}**\n"
                     f"- States in the DFA: **{info['states']}**\n"
                     f"- Alphabet size (distinct symbols in the patterns): **{info['alphabet_size']}**\n"
                     f"- Transitions in the DFA: **{info['transitions']}**\n"
                     f"- Accepting states (a pattern ends there): **{info['accepting_states']}**")

# ======================== TAB 2: SIMULATION ================================
with tab_sim:
    st.markdown(
        "**Detection** = using the automaton to decide *whether* a pattern occurs.  \n"
        "**Simulation** = watching the automaton move from state to state, one symbol at a time.")

    analysis = st.session_state.analysis
    detected = [row["Pattern"] for row in analysis["result"]["rows"]] if analysis else []
    options = detected or list(SPAM_PATTERNS)
    if not detected:
        st.info("Run a detection first to see detected patterns here. "
                "Meanwhile you can simulate any built-in pattern.")

    pattern = st.selectbox("Pattern to simulate", options)

    st.subheader(f"Pattern recognizer for {pattern}")
    dfa = build_literal_dfa(pattern)
    accepted, steps = dfa.run(pattern)
    st.dataframe(
        [{"Step": s["step"], "Current state": s["current_state"],
          "Input symbol": visible(s["symbol"]), "Next state": s["next_state"]} for s in steps],
        hide_index=True)
    last = steps[-1]["next_state"]
    if accepted:
        st.success(f"{last} = ACCEPTING STATE → Pattern found ✓")
    else:
        st.error("Pattern rejected")

    st.subheader("Scanning the whole email")
    if analysis:
        trace = analysis["trace"]
        shown = trace[:500]
        st.caption("The multi-pattern DFA reads the email one character at a time. "
                   "Rows where a pattern is accepted are shown in the last column.")
        st.dataframe(
            [{"Position": t["position"], "Symbol": visible(t["symbol"]),
              "Current state": t["current_state"], "Next state": t["next_state"],
              "Pattern found": t["pattern_found"]} for t in shown],
            hide_index=True, height=350)
        if len(trace) > len(shown):
            st.caption(f"Showing the first {len(shown)} of {len(trace)} steps.")
    else:
        st.info("Run a detection to see the scan trace of your email.")

# ======================== TAB 3: DIAGRAMS ==================================
with tab_diagram:
    col_legend, col_theme = st.columns([3, 1])
    with col_legend:
        st.markdown("Legend: **blue** = start state, **green double circle** = accepting state, "
                    "arrows = transitions. `␣` means a space.")
    with col_theme:
        diagram_style = st.selectbox(
            "Visual Theme",
            ["White Canvas (High Visibility)", "Dark Theme (White Lines)"],
            index=0,
            key="diagram_style"
        )
    
    current_theme = "white" if "White" in diagram_style else "dark"

    if current_theme == "white":
        st.markdown("""
        <style>
        .stGraphvizChart {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
            overflow-x: auto;
            margin-bottom: 20px;
        }
        .stGraphvizChart svg {
            background-color: #ffffff !important;
            border-radius: 8px;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stGraphvizChart {
            background-color: transparent;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            overflow-x: auto;
            margin-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

    analysis = st.session_state.analysis
    detected = [row["Pattern"] for row in analysis["result"]["rows"]] if analysis else []
    pattern_d = st.selectbox("Pattern", list(SPAM_PATTERNS),
                             index=list(SPAM_PATTERNS).index(detected[0]) if detected else 0,
                             key="diagram_pattern")

    st.subheader("1. DFA that recognizes exactly this pattern")
    st.graphviz_chart(automaton_to_dot(build_literal_dfa(pattern_d), theme=current_theme))

    st.subheader("2. NFA that searches for the pattern anywhere in the text")
    st.caption("q0 loops on every symbol AND may also move on the first letter: "
               "this choice is the non-determinism.")
    nfa = build_search_nfa(pattern_d)
    st.graphviz_chart(automaton_to_dot(nfa, theme=current_theme))

    st.subheader("3. Same NFA converted to a DFA (subset construction)")
    st.caption("Each DFA state is a set of NFA states. Now every symbol has exactly one move.")
    st.graphviz_chart(automaton_to_dot(nfa.to_dfa(), theme=current_theme))

    st.subheader("4. Trie of the multi-pattern automaton (part of it)")
    default_pick = (detected or ["FREE", "PRIZE", "CASH"])[:4]
    picked = st.multiselect("Choose a few patterns (keep it small to stay readable)",
                            list(SPAM_PATTERNS), default=default_pick)
    show_fail = st.checkbox("Show failure links (dashed)")
    if picked:
        st.graphviz_chart(trie_to_dot(MultiPatternDFA(picked), show_fail, theme=current_theme))
    else:
        st.info("Select at least one pattern.")

# ======================== TAB 4: TOC CONCEPTS ==============================
with tab_toc:
    st.markdown("""
### Pipeline
`Email → Suspicious pattern → Regular language → Finite automaton → State transitions → Pattern match → Risk score → Spam / Not spam`

### Regular language
A language is **regular** if some finite automaton (or regular expression) accepts exactly its strings.
Every spam pattern here (like `FREE` or `CLICK HERE`) is a finite set of fixed strings, so it is a regular language.
A finite union of regular languages is regular, so the set of *all* our patterns is regular too.

### Regular expression
A regular expression is a short way to write a regular language. `|` means "or".
For example, the Urgency category is the language of the expression below, and an email
contains such a pattern if it belongs to `Σ* (pattern) Σ*`.
""")
    for category, group in PATTERN_CATEGORIES.items():
        st.code(f"{category}:  ({'|'.join(group)})", language="text")
    st.markdown("""
### Finite automaton
A machine with a **finite** number of **states**. It reads the input one **symbol** at a time and
each symbol triggers a **transition** to another state. Some states are **accepting**; if the machine is in one
after reading (or while reading) the input, the pattern is found. It has no memory except its current state.

### DFA (Deterministic Finite Automaton)
Formally a 5-tuple **(Q, Σ, δ, q0, F)**: states, alphabet, transition function, start state, accepting states.
*Deterministic* = for every state and symbol there is **exactly one** next state. Our detector is a DFA,
so the scan is fast: one transition per character.

### NFA (Non-deterministic Finite Automaton)
Same idea, but a state may have **several** (or zero) moves on one symbol. The NFA accepts if **any** path reaches an
accepting state. NFAs are often easier to design (see diagram 2), but they accept the **same** languages as DFAs,
because any NFA can be converted to a DFA by **subset construction** (diagram 3).

| | DFA | NFA |
|---|---|---|
| Moves per (state, symbol) | exactly 1 | 0, 1 or many |
| Easy to run | very (one path) | needs to track a set of states |
| Power | regular languages | regular languages (same) |

### Pattern matching
To find a pattern *anywhere* in the email, the automaton keeps reading and, whenever the input
breaks a partial match, falls back to the longest useful partial match (failure link).
That's why we never need to re-read the text.

### Multiple patterns (Aho-Corasick)
All patterns are merged into one trie (tree of states); failure links then turn it into a complete DFA.
So one pass over the email checks all patterns at the same time instead of searching one pattern after another.

### Simulation vs Detection
*Simulation* shows the state-by-state execution. *Detection* uses the final result of that execution
(did we reach an accepting state?) to decide which patterns exist, then the risk score decides spam / not spam.
""")
