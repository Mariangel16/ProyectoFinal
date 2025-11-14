# report_generator.py
from typing import Dict, List
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime


def generate_pdf_report(
    filename: str,
    grammar_text: str,
    type_label: str,
    explanations: List[str],
    extra_notes: str = "",
) -> str:
    """
    Genera un PDF sencillo con:
    - Gramática
    - Tipo detectado
    - Explicación
    - Notas adicionales
    Devuelve la ruta al archivo generado.
    """
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Reporte de Clasificación de Gramática — Chomsky Classifier AI")
    y -= 25

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 20

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Gramática analizada:")
    y -= 15
    c.setFont("Helvetica", 10)

    for line in grammar_text.splitlines():
        if not line.strip():
            continue
        c.drawString(60, y, line)
        y -= 12
        if y < 80:
            c.showPage()
            y = height - 50

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Clasificación:")
    y -= 15
    c.setFont("Helvetica", 10)
    c.drawString(60, y, type_label)
    y -= 20

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Explicación paso a paso:")
    y -= 15
    c.setFont("Helvetica", 10)
    for exp in explanations:
        for frag in split_text(exp, max_chars=80):
            c.drawString(60, y, "- " + frag)
            y -= 12
            if y < 80:
                c.showPage()
                y = height - 50

    if extra_notes:
        y -= 15
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Notas adicionales:")
        y -= 15
        c.setFont("Helvetica", 10)
        for line in split_text(extra_notes, max_chars=80):
            c.drawString(60, y, line)
            y -= 12
            if y < 80:
                c.showPage()
                y = height - 50

    c.showPage()
    c.save()
    return filename


def split_text(text: str, max_chars: int = 80):
    """
    Divide un texto largo en líneas cortas para el PDF.
    """
    words = text.split()
    current = []
    for w in words:
        if len(" ".join(current + [w])) > max_chars:
            yield " ".join(current)
            current = [w]
        else:
            current.append(w)
    if current:
        yield " ".join(current)
