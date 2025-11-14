# classifier.py
from typing import Dict, List, Tuple, Set
import random

Production = Tuple[str, str]

TYPE_LABELS = {
    0: "Tipo 0 — Lenguaje Recursivamente Enumerable",
    1: "Tipo 1 — Lenguaje Sensible al Contexto",
    2: "Tipo 2 — Lenguaje Libre de Contexto",
    3: "Tipo 3 — Lenguaje Regular",
}


#FUNCIONES PARA CLASIFICAR
def _count_nonterminals_in_rhs(rhs: str) -> int:
    return sum(1 for ch in rhs if ch.isupper())


def _has_only_regular_forms(productions: List[Production]) -> bool:
    """
    Comprobación estricta de gramática REGULAR (Tipo 3) en forma derecha.

    Reglas que validamos:

    1. El lado izquierdo (LHS) de cada producción debe ser
       un ÚNICO no terminal (una sola letra mayúscula), por ejemplo: S, A, B...

    2. El lado derecho (RHS) debe cumplir una de estas formas:
        - ε (cadena vacía)   -> representada como "" en nuestro parser
        - una cadena SOLO de terminales: a, b, aa, bb, ab, ...
        - un terminal seguido de UN solo no terminal: aA, bS, 0B, ...

       Es decir, si hay un no terminal en el RHS:
        - solo puede haber UNO
        - tiene que estar al FINAL (forma regular derecha)
        - antes del no terminal solo puede haber terminales (minúsculas o dígitos)

    Cualquier cosa como aSb (terminal + NT + terminal) rompe la regularidad.
    """
    for left, rhs in productions:
        # 1) LHS debe ser EXACTAMENTE un no terminal mayúscula
        if not (len(left) == 1 and left.isupper()):
            return False

        # Permitimos ε (cadena vacía)
        if rhs == "":
            continue

        # Posiciones de no terminales en el RHS
        nt_positions = [i for i, ch in enumerate(rhs) if ch.isupper()]

        # Más de un no terminal en el RHS -> no regular
        if len(nt_positions) > 1:
            return False

        if len(nt_positions) == 1:
            # Hay exactamente un no terminal
            pos = nt_positions[0]

            # Debe estar al FINAL (forma regular derecha)
            if pos != len(rhs) - 1:
                return False

            for ch in rhs[:pos]:
                if not (ch.islower() or ch.isdigit()):
                    return False
        else:
            for ch in rhs:
                if not (ch.islower() or ch.isdigit()):
                    return False

    return True


def _is_context_free(productions: List[Production]) -> bool:
    """
    GLC: cada producción tiene exactamente un NO TERMINAL en el lado izquierdo.
    Es decir, el LHS debe ser una sola letra mayúscula: A -> β.
    """
    for left, _ in productions:
        if not (len(left) == 1 and left.isupper()):
            return False
    return True


def _is_context_sensitive(grammar: Dict) -> bool:
    """
    Sensible al contexto (Tipo 1):

    Para cada producción α -> β debe cumplirse |β| >= |α|,
    excepto permitir S -> ε como caso especial.

    Nota: aquí tomamos α = lado izquierdo (LHS) tal cual aparece.
    """
    start = grammar["start"]
    for left, rhs in grammar["productions"]:
        if left == start and rhs == "":
            # Permitimos S -> ε como caso especial
            continue
        if len(rhs) < len(left):
            return False
    return True


# CLASIFICADOR PRINCIPAL DE GRAMÁTICAS 
def classify_grammar(grammar: Dict) -> Tuple[int, List[str]]:
    """
    Devuelve (tipo, explicaciones paso a paso) según la Jerarquía de Chomsky.

    Orden de chequeo (de más restrictivo a menos):
      1. Regular (Tipo 3)
      2. Libre de Contexto (Tipo 2)
      3. Sensible al Contexto (Tipo 1)
      4. Tipo 0 (resto)
    """
    prods = grammar["productions"]
    explanations: List[str] = []

    # --- Comprobación Regular (Tipo 3) ---
    if _has_only_regular_forms(prods):
        explanations.append(
            "Todas las producciones tienen un solo no terminal en el lado izquierdo y "
            "en el lado derecho hay solo terminales o terminales seguidos de un solo no terminal, "
            "donde el no terminal aparece únicamente al final. "
            "Por lo tanto, la gramática es Regular (Tipo 3)."
        )
        return 3, explanations
    else:
        explanations.append(
            "No todas las producciones cumplen la forma regular derecha (A → aB, A → a o A → ε). "
            "Por lo tanto, NO puede ser Tipo 3."
        )

    # --- Comprobación GLC (Tipo 2) ---
    if _is_context_free(prods):
        explanations.append(
            "Cada producción tiene exactamente un no terminal en el lado izquierdo (A → β). "
            "La gramática es al menos Libre de Contexto (Tipo 2)."
        )
        if _is_context_sensitive(grammar):
            explanations.append(
                "Además, todas las producciones cumplen |α| ≤ |β|, por lo que también es sensible al contexto (Tipo 1). "
                "Sin embargo, en la jerarquía se clasifica con el tipo MÁS restrictivo que cumple: Tipo 2."
            )
        return 2, explanations
    else:
        explanations.append(
            "Existe al menos una producción cuyo lado izquierdo tiene más de un símbolo "
            "o no es un no terminal único. Por lo tanto, NO es Tipo 2 (GLC)."
        )

    # --- Comprobación Sensible al Contexto (Tipo 1) ---
    if _is_context_sensitive(grammar):
        explanations.append(
            "Todas las producciones satisfacen |α| ≤ |β| (la longitud del lado derecho es mayor o igual que la del izquierdo). "
            "Por lo tanto, la gramática es Sensible al Contexto (Tipo 1)."
        )
        return 1, explanations

    # --- Si no cumplió nada de lo anterior: Tipo 0 ---
    explanations.append(
        "Hay producciones donde la longitud del lado derecho es menor que la del izquierdo, "
        "violando |α| ≤ |β|. Por lo tanto, la gramática es de Tipo 0 (Recursivamente Enumerable)."
    )
    return 0, explanations


# CLASIFICACIÓN DE AUTOMATAS
def classify_automaton_kind(automaton: Dict) -> Tuple[int, str]:
    """
    Dado un autómata en formato JSON con un campo "type" (AFD, AFN, AP, MT),
    devolvemos su tipo en la Jerarquía de Chomsky.
    """
    kind = automaton.get("type", "").upper()

    if kind in ("AFD", "AFN", "NFA", "DFA"):
        return 3, "Un autómata finito (AFD/AFN) reconoce lenguajes regulares, por lo tanto es Tipo 3."
    if kind in ("AP", "PDA"):
        return 2, "Un autómata con pila (AP/PDA) reconoce lenguajes libres de contexto, por lo tanto es Tipo 2."
    if kind in ("MT", "TM", "TURING"):
        return 0, "Una Máquina de Turing reconoce lenguajes recursivamente enumerables, por lo tanto es Tipo 0."
    return 0, "No se reconoce el tipo de autómata. Por defecto se asume Máq. de Turing (Tipo 0)."


# GENERADOR DE EJEMPLOS 
EXAMPLE_GRAMMARS = [
    (
        "Tipo 3",
        """S -> aS | bS | a | b"""
    ),
    (
        "Tipo 2",
        """S -> aSb | ab"""
    ),
    (
        "Tipo 1",
        """S -> aSB
S -> ab
B -> b"""
    ),
    (
        "Tipo 0",
        """S -> aSb | SS | ε"""
    ),
]


def get_random_example_by_type(type_id: int) -> str:
    label = TYPE_LABELS[type_id]
    candidates = [g for t, g in EXAMPLE_GRAMMARS if t in label]
    if not candidates:
        candidates = [g for _, g in EXAMPLE_GRAMMARS]
    return random.choice(candidates)


def get_quiz_question() -> Tuple[str, str]:
    """
    Devuelve (texto_gramatica, respuesta_correcta_tipo).
    """
    t, g = random.choice(EXAMPLE_GRAMMARS)
    return g, t


#GENERACIÓN DE CADENAS Y COMPARACIÓN 
def _has_nonterminal(s: str, nonterminals: Set[str]) -> bool:
    return any(ch in nonterminals for ch in s)


def generate_strings(grammar: Dict, max_len: int = 5, max_steps: int = 6) -> Set[str]:
    """
    Genera cadenas desde la gramática de forma heurística, hasta cierta profundidad.
    Solo sirve para comparación aproximada.
    """
    start = grammar["start"]
    prods = grammar["productions"]
    nonterminals = set(grammar["nonterminals"])
    results: Set[str] = set()

    from collections import deque
    queue = deque()
    queue.append((start, 0))

    while queue:
        current, steps = queue.popleft()
        if steps > max_steps:
            continue
        if not _has_nonterminal(current, nonterminals):
            if 0 < len(current) <= max_len:
                results.add(current)
            continue
        if len(current) > max_len + 2:
            continue

        idx_nt = None
        for i, ch in enumerate(current):
            if ch in nonterminals:
                idx_nt = i
                break
        if idx_nt is None:
            continue

        A = current[idx_nt]
        for left, rhs in prods:
            if left == A:
                new_string = current[:idx_nt] + rhs + current[idx_nt + 1:]
                queue.append((new_string, steps + 1))

    return results


def compare_grammars(g1: Dict, g2: Dict, max_len: int = 5, max_steps: int = 6) -> Dict:
    """
    Compara dos gramáticas generando cadenas hasta cierta longitud y profundidad.
    Devuelve un informe con las diferencias.
    """
    L1 = generate_strings(g1, max_len=max_len, max_steps=max_steps)
    L2 = generate_strings(g2, max_len=max_len, max_steps=max_steps)

    only1 = sorted(L1 - L2)
    only2 = sorted(L2 - L1)
    common = sorted(L1 & L2)

    equivalent = (only1 == [] and only2 == [])

    return {
        "equivalent": equivalent,
        "only1": only1,
        "only2": only2,
        "common": common,
        "max_len": max_len,
    }
