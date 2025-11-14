# grammar_parser.py
import re
from typing import Dict, List, Set, Tuple

Production = Tuple[str, str]

def normalize_arrow(line: str) -> str:
    return line.replace("→", "->").replace("⇒", "->").replace("⟶", "->")

def parse_grammar(text: str) -> Dict:
    """
    Convierte un texto como:
        S -> aSb | ab
        A -> aA | b
    en una estructura interna.
    """
    nonterminals: Set[str] = set()
    terminals: Set[str] = set()
    productions: List[Production] = []

    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]

    for line in lines:
        line = normalize_arrow(line)
        if "->" not in line:
            continue
        left, right = line.split("->", 1)
        left = left.strip()
        right = right.strip()

        if not left:
            continue

        nonterminals.add(left)

        # dividir alternativas
        alts = [alt.strip() for alt in right.split("|")]
        for alt in alts:
            if alt in ("ε", "epsilon", "EPS", "lambda", "λ"):
                rhs = ""
            else:
                rhs = alt.replace(" ", "")
            productions.append((left, rhs))

    for _, rhs in productions:
        for ch in rhs:
            if ch.isupper():
                nonterminals.add(ch)
            else:
                terminals.add(ch)

    # adivinar símbolo inicial 
    start_symbol = productions[0][0] if productions else "S"

    return {
        "start": start_symbol,
        "nonterminals": sorted(nonterminals),
        "terminals": sorted(terminals),
        "productions": productions,
    }


def parse_automaton_json(text: str) -> Dict:
    """
    Parser muy simple: espera un JSON tipo:
      {
        "type": "AFD",
        "states": ["q0","q1"],
        "alphabet": ["a","b"],
        "start": "q0",
        "accepting": ["q1"],
        "transitions": {
          "q0": {"a":"q1","b":"q0"},
          "q1": {"a":"q1","b":"q0"}
        }
      }
    """
    import json
    try:
        data = json.loads(text)
        return data
    except Exception as e:
        raise ValueError(f"Error al leer el autómata en JSON: {e}")
