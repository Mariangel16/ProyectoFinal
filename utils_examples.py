from typing import Dict
from classifier import TYPE_LABELS, get_random_example_by_type

def get_example_grammar_text(type_id: int) -> str:
    return get_random_example_by_type(type_id)


def pretty_print_classification(type_id: int) -> str:
    return TYPE_LABELS.get(type_id, "Tipo desconocido")
