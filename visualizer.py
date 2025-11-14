from typing import Dict
import graphviz
import networkx as nx

def grammar_to_graphviz(grammar: Dict) -> graphviz.Digraph:
    """
    Crea un grafo sencillo: nodos = no terminales; aristas A->B si B aparece en RHS.
    """
    dot = graphviz.Digraph(comment="Gramática")

    for nt in grammar["nonterminals"]:
        shape = "doublecircle" if nt == grammar["start"] else "circle"
        dot.node(nt, nt, shape=shape)

    for left, rhs in grammar["productions"]:
        # buscando NT en el RHS
        for ch in rhs:
            if ch.isupper():
                dot.edge(left, ch, label=rhs or "ε")
    return dot


def automaton_to_graphviz(automaton: Dict) -> graphviz.Digraph:
    """
    Visualiza un autómata finito simple a partir del JSON descrito en grammar_parser.py.
    """
    dot = graphviz.Digraph(comment="Autómata")
    states = automaton.get("states", [])
    start = automaton.get("start", "")
    accepting = set(automaton.get("accepting", []))
    transitions = automaton.get("transitions", {})

    for s in states:
        shape = "doublecircle" if s in accepting else "circle"
        dot.node(s, s, shape=shape)

    # Flecha de inicio
    if start:
        dot.node("start", "", shape="point")
        dot.edge("start", start)

    for src, trans in transitions.items():
        for symbol, dst in trans.items():
            dot.edge(src, dst, label=str(symbol))

    return dot


def graphviz_to_networkx(dot_source: str) -> nx.DiGraph:
    """
    Conversión opcional a networkx si se quiere hacer algo más avanzado.
    """
    G = nx.DiGraph()
    lines = dot_source.splitlines()
    for line in lines:
        line = line.strip()
        if "->" in line and not line.startswith("digraph"):
            # ejemplo: A -> B [label="a"];
            parts = line.split("->")
            left = parts[0].strip()
            rest = parts[1].strip()
            right = rest.split()[0].strip().strip(";")
            G.add_edge(left, right)
    return G
