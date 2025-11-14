## Descripción general

Chomsky Classifier AI es una aplicación educativa creada en Python + Streamlit que permite:
- Clasificar gramáticas según la Jerarquía de Chomsky (Tipo 0, 1, 2, 3).
- Clasificar autómatas (AFD, AFN, AP, MT).
- Convertir expresiones regulares → gramáticas regulares (demo).
- Visualizar grafos con Graphviz.
- Generar ejemplos aleatorios.
- Comparar dos gramáticas.
- Practicar con un modo tutor interactivo.
- Generar reportes PDF.

## Requisitos

- Python 3.10 o superior
- streamlit, graphviz, reportlab, pydot

## Instalación

```bash
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install streamlit graphviz reportlab pydot
```

## Ejecutar la aplicación

```bash
streamlit run main.py
```

La aplicación abrirá en:

```
http://localhost:8501
```

