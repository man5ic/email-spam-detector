# 📧 Email Spam Pattern Detector Using Finite Automata

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Theory of Computation](https://img.shields.io/badge/Domain-Theory%20of%20Computation%20(TOC)-purple.svg)](#theory-of-computation-toc-foundations)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An interactive, educational **Theory of Computation (TOC)** project that demonstrates how formal language theory, regular expressions, and finite automata can detect spam patterns in text without machine learning or external APIs.

The system builds an **Aho-Corasick Multi-Pattern Deterministic Finite Automaton (DFA)** to scan email text in a single pass ($O(N)$ time complexity), tracks state transitions step-by-step, calculates an explainable risk score, and renders dynamic automaton transition graphs with high-visibility visual styling.

---

## 📌 Table of Contents

- [Problem Statement & Motivation](#-problem-statement--motivation)
- [Key Features](#-key-features)
- [Theory of Computation (TOC) Foundations](#-theory-of-computation-toc-foundations)
  - [1. Regular Expressions & Regular Languages](#1-regular-expressions--regular-languages)
  - [2. Deterministic Finite Automata (DFA)](#2-deterministic-finite-automata-dfa)
  - [3. Non-deterministic Finite Automata (NFA)](#3-non-deterministic-finite-automata-nfa)
  - [4. Subset Construction (NFA → DFA)](#4-subset-construction-nfa--dfa)
  - [5. Aho-Corasick Multi-Pattern DFA (Trie + Failure Transitions)](#5-aho-corasick-multi-pattern-dfa-trie--failure-transitions)
  - [6. Simulation vs. Detection](#6-simulation-vs-detection)
- [System Architecture & Detection Pipeline](#-system-architecture--detection-pipeline)
- [Spam Scoring Logic & Thresholds](#-spam-scoring-logic--thresholds)
- [Technology Stack](#-technology-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Installation & Getting Started](#-installation--getting-started)
- [Usage Guide & UI Walkthrough](#-usage-guide--ui-walkthrough)
- [Example Scenarios & Results](#-example-scenarios--results)
- [Limitations & Future Scope](#-limitations--future-scope)
- [Contributing & License](#-contributing--license)

---

## 🎯 Problem Statement & Motivation

Many spam emails exhibit characteristic trigger phrases and keywords, such as:
- **Urgency:** `ACT NOW`, `LIMITED TIME`, `URGENT`, `EXPIRES TODAY`
- **Prize / Lottery:** `FREE`, `PRIZE`, `WINNER`, `YOU HAVE WON`, `CASH`
- **Call-to-Action:** `CLICK HERE`, `CLAIM NOW`, `BUY NOW`, `VERIFY YOUR ACCOUNT`

While modern production spam filters rely on statistical machine learning and NLP transformers, this project explores the foundational question:

> **Can we reliably detect multi-word spam triggers in email text using only the mathematical machinery of Formal Languages and Finite Automata?**

By modeling spam signatures as **regular languages**, constructing individual DFAs/NFAs, and unifying them into an optimal **Aho-Corasick Multi-Pattern DFA**, we achieve single-pass $O(N)$ string matching with transparent state transitions.

---

## ✨ Key Features

- **🔍 Interactive Spam Detector:**
  - Paste any custom email text or load built-in sample emails.
  - Generates instant `SPAM DETECTED` or `NOT SPAM` verdicts with risk scores ($0 - 5$).
  - Full breakdown table of identified patterns, categories, occurrences, and risk weights.
  - Color-coded HTML email highlighter emphasizing detected trigger words.
- **▶️ Step-by-Step Automaton Simulation:**
  - **Single Pattern Simulation:** View state-by-state execution ($q_i \xrightarrow{\sigma} q_j$) for any pattern.
  - **Full Email Scan Trace:** Inspect the character-by-character trace table showing current states, input symbols, next states, and accepted patterns.
- **🧩 Dynamic Automaton Diagrams:**
  - Graphviz visualizations of:
    1. **Literal Pattern DFA** ($q_0 \to q_1 \to \dots \to q_n$)
    2. **Search NFA** ($\Sigma^*$ self-loop non-determinism)
    3. **Subset Construction DFA** (DFA equivalent of the search NFA)
    4. **Multi-Pattern Trie / AC Automaton** (with optional dashed failure links)
  - **High-Visibility Visual Modes:** Built-in switcher between **White Canvas (High Visibility)** for clean presentation and **Dark Theme (White Lines)** for dark mode contrast.
- **📚 TOC Concepts Knowledge Hub:**
  - Viva-ready reference guide covering definitions, 5-tuples, formal language classifications, and comparison tables.

---

## 🧠 Theory of Computation (TOC) Foundations

### 1. Regular Expressions & Regular Languages
A language $L$ is **regular** if and only if there exists a finite automaton $M$ such that $L(M) = L$.
Each spam trigger pattern (e.g., `FREE`, `CLICK HERE`) is a finite literal string, inherently forming a regular language:
$$L_{pattern} = \{ w \}$$
Since regular languages are closed under finite union, the set of all spam trigger patterns $P = \{p_1, p_2, \dots, p_k\}$ is also a regular language:
$$L_{spam} = \bigcup_{i=1}^{k} L_{p_i}$$
To detect whether a pattern occurs *anywhere* in an email over alphabet $\Sigma$, we search for strings in:
$$L_{search} = \Sigma^* \cdot L_{pattern} \cdot \Sigma^*$$

### 2. Deterministic Finite Automata (DFA)
A DFA is formally defined as a 5-tuple:
$$M = (Q, \Sigma, \delta, q_0, F)$$
Where:
- $Q$: Finite set of states
- $\Sigma$: Input alphabet (ASCII uppercase characters and symbols)
- $\delta: Q \times \Sigma \to Q$: Deterministic transition function
- $q_0 \in Q$: Start state
- $F \subseteq Q$: Set of accepting / final states

In a literal pattern DFA for `FREE` of length 4:
$$q_0 \xrightarrow{\text{F}} q_1 \xrightarrow{\text{R}} q_2 \xrightarrow{\text{E}} q_3 \xrightarrow{\text{E}} q_4 \quad (q_4 \in F)$$

### 3. Non-deterministic Finite Automata (NFA)
In an NFA, the transition function maps to powersets of states:
$$\delta: Q \times (\Sigma \cup \{\varepsilon\}) \to \mathcal{P}(Q)$$
The search NFA features a non-deterministic self-loop at $q_0$:
- $\delta(q_0, \sigma) = \{q_0\}$ for all $\sigma \in \Sigma$
- $\delta(q_0, p[0]) = \{q_0, q_1\}$ (the automaton non-deterministically "guesses" when the pattern begins)

### 4. Subset Construction (NFA → DFA)
To make the search automaton deterministic and executable in $O(1)$ per character, the NFA is converted to an equivalent DFA using **Subset Construction (Powerset Construction)**:
- Each state in the DFA represents a subset of states from the NFA: $S \in \mathcal{P}(Q_{NFA})$.
- Start state: $S_0 = \varepsilon\text{-closure}(\{q_0\})$.
- Transition: $\delta_{DFA}(S, a) = \bigcup_{q \in S} \varepsilon\text{-closure}(\delta_{NFA}(q, a))$.
- Accepting states: Any subset $S$ where $S \cap F_{NFA} \neq \emptyset$.

### 5. Aho-Corasick Multi-Pattern DFA (Trie + Failure Transitions)
Rather than executing $k$ separate automata sequentially ($O(k \cdot N)$), this project uses the **Aho-Corasick algorithm**:
1. **Trie Construction:** Inserts all spam keywords into a prefix tree where common prefixes share states.
2. **Failure Links (Suffix Links):** Computed via Breadth-First Search (BFS). If a mismatch occurs at state $u$ on symbol $c$, the automaton transitions to the state representing the longest proper suffix that is also a prefix in the trie:
   $$\text{fail}(u) = v \quad \text{where } \text{path}(v) = \text{longest proper suffix of } \text{path}(u)$$
3. **Dictionary / Output Links:** Emits all pattern matches ending at the current state.
4. **Time Complexity:** Preprocessing is $O(\sum |p_i|)$, and scanning the email takes strictly **$O(N)$** transitions for an email of length $N$.

### 6. Simulation vs. Detection
- **Simulation:** Observing the physical step-by-step state traversal $(q_{curr}, \sigma) \to q_{next}$.
- **Detection:** Applying boundary verification on accepted states, summing pattern weights, and calculating the final risk score.

---

## 🏗️ System Architecture & Detection Pipeline

```
[ Incoming Email Text ]
         │
         ▼
[ 1. Normalization ]
  • Convert to uppercase
  • Normalize whitespace (\s+ -> " ")
         │
         ▼
[ 2. Aho-Corasick DFA Scan ]
  • Start at q0
  • Transition δ(q, char) for each character in O(1)
  • Record match when accepting state is reached
         │
         ▼
[ 3. Whole-Word Boundary Filtering ]
  • Verify preceding and succeeding characters are delimiters
  • Prevents substring false positives (e.g., 'WIN' inside 'WINDOW')
         │
         ▼
[ 4. Weight Aggregation & Risk Scoring ]
  • Calculate distinct pattern weights (1 - 3 per category)
  • Compute Risk Score: min(5, ceil(total_weight / 2))
         │
         ▼
[ 5. Decision & Visualization ]
  • Verdict: Total Weight >= 4 ? "SPAM" : "NOT SPAM"
  • Render highlighted text, pattern table, and Graphviz charts
```

---

## ⚖️ Spam Scoring Logic & Thresholds

Each pattern is assigned a category and a risk weight:

| Category | Example Patterns | Weight | Risk Level |
|---|---|:---:|:---:|
| **Prize / Reward** | `PRIZE`, `WINNER`, `YOU HAVE WON`, `CASH`, `LOTTERY` | **3** | High |
| **Urgency** | `ACT NOW`, `LIMITED TIME`, `LAST CHANCE`, `EXPIRES TODAY` | **2** | Medium |
| **Financial / Scams** | `MONEY BACK`, `EARN MONEY`, `CREDIT CARD`, `LOAN` | **2** | Medium |
| **Call To Action** | `CLICK HERE`, `CLAIM NOW`, `BUY NOW`, `VERIFY YOUR ACCOUNT` | **2 - 3** | Medium - High |
| **Promotional** | `FREE`, `OFFER`, `DISCOUNT`, `NO COST`, `100% GUARANTEED` | **1 - 3** | Low - High |

### Mathematical Formula
- Let $M_{distinct}$ be the set of distinct patterns found in the email.
- **Total Weight:**
  $$W = \sum_{p \in M_{distinct}} \text{weight}(p)$$
- **Risk Score ($0 - 5$ scale):**
  $$\text{Risk Score} = \min\left(5, \left\lfloor \frac{W + 1}{2} \right\rfloor\right)$$
- **Decision Threshold:**
  $$\text{Verdict} = \begin{cases} \textbf{SPAM}, & \text{if } W \ge 4 \\ \textbf{NOT SPAM}, & \text{if } W < 4 \end{cases}$$

---

## 💻 Technology Stack

| Component | Technology | Description |
|---|---|---|
| **Core Language** | Python 3.9+ | Clean, dependency-light object-oriented implementation |
| **Web Framework** | [Streamlit](https://streamlit.io/) (1.30+) | Interactive, responsive web UI with state management |
| **Diagram Engine** | Graphviz DOT / `st.graphviz_chart` | Client-side SVG graph rendering for finite state machines |
| **Styling & UX** | Custom Vanilla CSS | High-visibility white canvas cards and sleek dark mode |
| **Machine Learning** | *None (Deliberate)* | 100% deterministic, rule-based formal automata |

---

## 📁 Project Directory Structure

```text
email-spam-detector/
├── .streamlit/
│   └── config.toml               # Streamlit server and theme configuration
├── automata/
│   ├── __init__.py               # Package marker
│   ├── dfa.py                    # DFA class & literal pattern DFA builder
│   ├── nfa.py                    # NFA class, search NFA & subset construction
│   └── pattern_matcher.py        # Aho-Corasick multi-pattern DFA with boundary checks
├── data/
│   ├── __init__.py               # Package marker
│   └── spam_patterns.py          # Pattern dictionary, weights, and sample test emails
├── utils/
│   ├── __init__.py               # Package marker
│   ├── highlighting.py           # HTML color-coded email text highlighting
│   ├── scoring.py                # Weight aggregation and risk score evaluator
│   └── visualization.py          # DOT string generators with White Canvas & Dark themes
├── .gitignore                    # Git exclusions
├── app.py                        # Main Streamlit application and tab layouts
├── README.md                     # Comprehensive documentation
└── requirements.txt              # Project dependencies
```

---

## 🚀 Installation & Getting Started

### 1. Prerequisites
- **Python 3.9** or higher installed on your system.
- Git installed.

### 2. Clone the Repository
```bash
git clone https://github.com/man5ic/email-spam-detector.git
cd email-spam-detector
```

### 3. (Optional) Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
- **Windows (One-Click):** Double-click `start.bat` or run:
  ```cmd
  start.bat
  ```
- **Command Line:**
  ```bash
  streamlit run app.py
  ```

The application will launch automatically in your browser at:
`http://localhost:8501`

---

## 🖥️ Usage Guide & UI Walkthrough

The web interface is organized into 4 distinct tabs:

### 1. 🔍 Detector Tab
- Click any of the 4 pre-loaded example buttons or paste your own email text.
- Click **Detect Spam**.
- View the metric cards: **Risk Score**, **Distinct Patterns Found**, and **Total Matches**.
- Inspect the detected pattern table and the highlighted email text.
- Expand **Automaton Information** to see DFA state counts, alphabet size, and transition counts.

### 2. ▶️ Automaton Simulation Tab
- Select any pattern to inspect its linear DFA step-by-step transition table.
- View the complete email scan trace showing character-by-character state transitions.

### 3. 🧩 Automaton Diagrams Tab
- Select a trigger pattern from the dropdown.
- Choose your **Visual Theme**:
  - **White Canvas (High Visibility):** Renders diagrams inside a clean white card container with dark borders and high-contrast labels.
  - **Dark Theme (White Lines):** Renders transparent diagrams with crisp white lines and glowing accents.
- Explore 4 types of diagrams: Literal DFA, Search NFA, Subset Construction DFA, and Multi-Pattern Trie.

### 4. 📚 TOC Concepts Tab
- Review definitions of regular languages, regular expressions, DFAs, NFAs, and subset construction.
- Ideal for college coursework review, exams, and project viva preparation.

---

## 📊 Example Scenarios & Results

| Example Email | Detected Triggers | Total Weight | Risk Score | Verdict |
|---|---|:---:|:---:|:---:|
| *"Congratulations! You have won a FREE prize. Click here to claim your CASH reward!"* | `CONGRATULATIONS`, `YOU HAVE WON`, `FREE`, `PRIZE`, `CLICK HERE`, `CASH`, `REWARD` | 16 | **5 / 5** | 🚨 **SPAM** |
| *"URGENT! ACT NOW to claim your limited time offer. You are a WINNER!"* | `URGENT`, `ACT NOW`, `LIMITED TIME`, `OFFER`, `WINNER` | 10 | **5 / 5** | 🚨 **SPAM** |
| *"Hi all, lunch is free for everyone after tomorrow's meeting. Please open the window..."* | `FREE` (note: `WIN` inside `WINDOW` is filtered out) | 2 | **1 / 5** | ✅ **NOT SPAM** |
| *"Hi team, the meeting has been scheduled for tomorrow at 10 AM. Please bring docs."* | *None* | 0 | **0 / 5** | ✅ **NOT SPAM** |

---

## ⚠️ Limitations & Future Scope

### Current Limitations
- **Exact Literal Matching:** Does not recognize deliberate obfuscations or leetspeak (e.g., `FR33`, `C@SH`).
- **Context Insensitive:** Cannot distinguish between a legitimate promotional newsletter and malicious phishing.
- **Fixed Vocabulary:** Triggers are predetermined rather than learned dynamically.

### Future Enhancements
- [ ] Implement fuzzy automata / Levenshtein distance NFAs for misspelled triggers.
- [ ] Add regex pattern compilation support for variable patterns (e.g., currency amounts, tracking links).
- [ ] Add user-editable pattern and weight management interface.
- [ ] Export detection traces and Graphviz diagrams to PNG/PDF reports.

---

## 📄 License & Author

- **Author:** [Mansi Chandwad](https://github.com/man5ic)
- **Repository:** [man5ic/email-spam-detector](https://github.com/man5ic/email-spam-detector)
- **License:** MIT License — feel free to use this project for learning, academic coursework, and educational demonstrations!
