import streamlit as st
from grammar_parser import parse_grammar, parse_automaton_json
from classifier import (
    classify_grammar,
    classify_automaton_kind,
    compare_grammars,
    TYPE_LABELS,
)
from visualizer import grammar_to_graphviz, automaton_to_graphviz
from utils_examples import get_example_grammar_text, pretty_print_classification
from report_generator import generate_pdf_report
import os

st.set_page_config(
    page_title="Chomsky Classifier AI",
    layout="wide",
)

st.title("Chomsky Classifier AI")
mode = st.sidebar.radio(
    "Modo de trabajo",
    [
        "1. Clasificar Gramática",
        "2. Clasificar Autómata",
        "3. Conversores Regex ⇄ AFD ⇄ Gramática Regular (demo)",
        "4. Generador de Ejemplos",
        "5. Modo Tutor / Quiz",
        "6. Comparar dos Gramáticas",
        "7. Generar Reporte PDF",
    ],
)


#Clasificar Gramatica
if mode == "1. Clasificar Gramática":
    st.header("Clasificar Gramática (Jerarquía de Chomsky)")

    st.markdown(
        "Introduce las reglas de la gramática, una por línea, por ejemplo:\n"
        "`S -> aSb | ab`"
    )

    default_grammar = """S -> aSb | ab"""
    grammar_text = st.text_area("Gramática:", value=default_grammar, height=200)

    if st.button("Clasificar gramática"):
        try:
            grammar = parse_grammar(grammar_text)
            type_id, expl = classify_grammar(grammar)
            st.success(f"Resultado: {pretty_print_classification(type_id)}")
            st.subheader("Modo explicativo (paso a paso)")
            for e in expl:
                st.markdown(f"- {e}")

            st.subheader("Visualización (grafo de no terminales)")
            dot = grammar_to_graphviz(grammar)
            st.graphviz_chart(dot)

            with st.expander("Ver gramática parseada (debug)"):
                st.json(grammar)

        except Exception as e:
            st.error(f"Error al analizar la gramática: {e}")


#Clasificar Automata
elif mode == "2. Clasificar Autómata":
    st.header("Clasificar Autómata (AFD, AP, MT)")

    st.markdown(
        "Pega la definición del autómata en formato JSON simple. Ejemplo para un AFD:\n"
        "```json\n"
        "{\n"
        '  "type": "AFD",\n'
        '  "states": ["q0","q1"],\n'
        '  "alphabet": ["a","b"],\n'
        '  "start": "q0",\n'
        '  "accepting": ["q1"],\n'
        '  "transitions": {\n'
        '    "q0": {"a":"q1", "b":"q0"},\n'
        '    "q1": {"a":"q1", "b":"q0"}\n'
        "  }\n"
        "}\n"
        "```"
    )

    default_automaton = """{
  "type": "AFD",
  "states": ["q0","q1"],
  "alphabet": ["a","b"],
  "start": "q0",
  "accepting": ["q1"],
  "transitions": {
    "q0": {"a": "q1", "b": "q0"},
    "q1": {"a": "q1", "b": "q0"}
  }
}"""
    automaton_text = st.text_area("Autómata (JSON):", value=default_automaton, height=250)

    if st.button("Clasificar autómata"):
        try:
            automaton = parse_automaton_json(automaton_text)
            type_id, expl = classify_automaton_kind(automaton)
            st.success(f"Resultado: {pretty_print_classification(type_id)}")
            st.markdown(f"**Explicación:** {expl}")

            st.subheader("Visualización de transiciones")
            dot = automaton_to_graphviz(automaton)
            st.graphviz_chart(dot)

            with st.expander("Ver JSON parseado"):
                st.json(automaton)
        except Exception as e:
            st.error(f"Error al analizar el autómata: {e}")


#Conversores Regex AFD Gramatica Regular
elif mode == "3. Conversores Regex ⇄ AFD ⇄ Gramática Regular (demo)":
    st.header("Conversores Regex ⇄ AFD ⇄ Gramática Regular (demo)")

    st.markdown(
        "En esta sección se demuestra, de forma **simplificada**, la conversión entre:\n"
        "- Expresión regular → Gramática Regular\n"
        "Para fines académicos se asume una expresión con alfabeto {a,b} y patron típico `(a|b)*abb`."
    )

    regex = st.text_input("Expresión regular:", value="(a|b)*abb")

    def regex_to_regular_grammar(regex_str: str) -> str:
        """
        Implementación DEMO: para (a|b)*abb devolvemos una gramática regular conocida.
        En un proyecto más completo se implementaría Thompson + construcción formal.
        """
        if regex_str.strip() == "(a|b)*abb":
            return """S -> aS | bS | aA
A -> bB
B -> bC
C -> ε"""
        else:
            return f"""S -> aS | bS | {regex_str.replace('*','')}"""

    if st.button("Convertir Regex a Gramática Regular"):
        gram = regex_to_regular_grammar(regex)
        st.subheader("Gramática Regular (demo):")
        st.code(gram, language="text")
        grammar = parse_grammar(gram)
        dot = grammar_to_graphviz(grammar)
        st.graphviz_chart(dot)
        st.info("Conversor completo es un trabajo más extenso; aquí se muestra un ejemplo demostrativo.")


#Generador de Ejemplos 
elif mode == "4. Generador de Ejemplos":
    st.header("Generador Automático de Ejemplos de Gramáticas")

    type_choice = st.selectbox(
        "Tipo de gramática a generar",
        options=[3, 2, 1, 0],
        format_func=lambda x: TYPE_LABELS[x],
    )

    if st.button("Generar ejemplo"):
        txt = get_example_grammar_text(type_choice)
        st.subheader("Ejemplo generado:")
        st.code(txt, language="text")

        grammar = parse_grammar(txt)
        dot = grammar_to_graphviz(grammar)
        st.subheader("Visualización:")
        st.graphviz_chart(dot)


# ====== 5. Modo Tutor 
elif mode == "5. Modo Tutor / Quiz":
    st.header(" Modo Tutor de Chomsky (Quiz)")

    st.markdown("Clasifica mentalmente la gramática y luego comprueba tu respuesta.")

    from classifier import get_quiz_question
    if "quiz_grammar" not in st.session_state:
        g, t = get_quiz_question()
        st.session_state.quiz_grammar = g
        st.session_state.quiz_answer = t

    if st.button("Nueva gramática"):
        g, t = get_quiz_question()
        st.session_state.quiz_grammar = g
        st.session_state.quiz_answer = t

    st.subheader("Gramática a clasificar:")
    st.code(st.session_state.quiz_grammar, language="text")

    user_choice = st.radio(
        "¿Qué tipo crees que es?",
        ["Tipo 3", "Tipo 2", "Tipo 1", "Tipo 0"],
    )

    if st.button("Comprobar respuesta"):
        correct = st.session_state.quiz_answer
        if user_choice == correct:
            st.success(f"¡Correcto! La respuesta era: {correct}.")
        else:
            st.error(f"Tu respuesta: {user_choice}. Correcto: {correct}.")
        st.info(
            "Recuerda: Tipo 3 ⊂ Tipo 2 ⊂ Tipo 1 ⊂ Tipo 0. "
            "Cada nivel permite producciones más generales."
        )


# ====== 6. Comparar dos Gramáticas ======
elif mode == "6. Comparar dos Gramáticas":
    st.header("Comparar dos Gramáticas (modo comparativo / desempeño)")

    st.markdown(
        "Esta herramienta genera cadenas de cada gramática hasta cierta longitud y las compara.\n"
        "La equivalencia total es indecidible en general, pero esto ofrece una **aproximación heurística**."
    )

    col1, col2 = st.columns(2)

    with col1:
        g1_text = st.text_area("Gramática 1:", value="S -> aSb | ab", height=200)
    with col2:
        g2_text = st.text_area(
            "Gramática 2:",
            value="""S -> aA
A -> Sb | b""",
            height=200,
        )

    max_len = st.slider("Longitud máxima de cadenas", min_value=1, max_value=8, value=5)
    max_steps = st.slider("Profundidad de derivación (pasos)", min_value=2, max_value=10, value=6)

    if st.button("Comparar gramáticas"):
        from grammar_parser import parse_grammar
        from classifier import compare_grammars

        try:
            g1 = parse_grammar(g1_text)
            g2 = parse_grammar(g2_text)
            result = compare_grammars(g1, g2, max_len=max_len, max_steps=max_steps)

            if result["equivalent"]:
                st.success("Las gramáticas parecen **equivalentes** para las cadenas generadas (hasta la longitud dada).")
            else:
                st.warning("Las gramáticas NO parecen equivalentes (según la exploración limitada).")

            st.write("Cadenas en común:")
            st.code(", ".join(result["common"]) or "(ninguna)", language="text")

            st.write("Sólo en Gramática 1:")
            st.code(", ".join(result["only1"]) or "(ninguna)", language="text")

            st.write("Sólo en Gramática 2:")
            st.code(", ".join(result["only2"]) or "(ninguna)", language="text")

        except Exception as e:
            st.error(f"Error al comparar gramáticas: {e}")


# ====== 7. Generar Reporte PDF ======
elif mode == "7. Generar Reporte PDF":
    st.header("Generación de Reportes PDF")

    st.markdown(
        "Aquí puedes generar un **reporte PDF** con:\n"
        "- Gramática analizada\n"
        "- Tipo de lenguaje detectado\n"
        "- Explicación paso a paso\n"
        "Este reporte se puede adjuntar a tu informe final."
    )

    grammar_text = st.text_area("Gramática para el reporte:", value="S -> aSb | ab", height=200)

    if st.button("Analizar y generar PDF"):
        try:
            grammar = parse_grammar(grammar_text)
            type_id, expl = classify_grammar(grammar)
            type_label = pretty_print_classification(type_id)

            st.success(f"Clasificación: {type_label}")
            st.subheader("Explicación:")
            for e in expl:
                st.markdown(f"- {e}")

            # Generar PDF temporal
            out_name = "reporte_chomsky_classifier.pdf"
            path = generate_pdf_report(out_name, grammar_text, type_label, expl)

            # leer binario para descargar
            with open(path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                label="Descargar reporte PDF",
                data=pdf_bytes,
                file_name=out_name,
                mime="application/pdf",
            )

            st.info("El reporte incluye la gramática, la clasificación y las explicaciones paso a paso.")

        except Exception as e:
            st.error(f"Error al generar el reporte PDF: {e}")
