from io import BytesIO
from collections import defaultdict
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

VERDE = colors.HexColor("#27ae60")
ROJO = colors.HexColor("#c0392b")
AZUL_OSCURO = colors.HexColor("#2c3e50")
GRIS_BORDE = colors.HexColor("#bdc3c7")
GRIS_CLARO = colors.HexColor("#f4f6f7")


def _fmt_monto(valor):
    return f"${valor:,.2f}"


def _pie_de_pagina(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1 * cm, "Smart Expense Tracker")
    canvas.drawRightString(letter[0] - 2 * cm, 1 * cm, f"Página {doc.page}")
    canvas.restoreState()


def _tabla_resumen(total_ingresos, total_gastos, balance):
    tabla = Table(
        [
            ["Total Ingresos", "Total Gastos", "Balance"],
            [
                _fmt_monto(total_ingresos),
                _fmt_monto(total_gastos),
                _fmt_monto(balance),
            ],
        ],
        colWidths=[5.6 * cm, 5.6 * cm, 5.6 * cm],
    )
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), AZUL_OSCURO),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TEXTCOLOR", (0, 1), (0, 1), VERDE),
                ("TEXTCOLOR", (1, 1), (1, 1), ROJO),
                (
                    "TEXTCOLOR",
                    (2, 1),
                    (2, 1),
                    VERDE if balance >= 0 else ROJO,
                ),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 1), (-1, 1), 13),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 1), (-1, 1), 10),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, GRIS_BORDE),
            ]
        )
    )
    return tabla


def _tabla_por_categoria(titulo, transacciones, estilos):
    if not transacciones:
        return None

    totales = defaultdict(lambda: {"monto": 0.0, "cantidad": 0})
    for t in transacciones:
        totales[t.categoria]["monto"] += t.monto
        totales[t.categoria]["cantidad"] += 1

    datos = [[titulo, "Cant.", "Total"]]
    ordenadas = sorted(totales.items(), key=lambda x: x[1]["monto"], reverse=True)
    for categoria, info in ordenadas:
        datos.append(
            [categoria, str(info["cantidad"]), _fmt_monto(info["monto"])]
        )

    tabla = Table(datos, colWidths=[8 * cm, 2 * cm, 4 * cm])
    color = VERDE if transacciones[0].tipo == "ingreso" else ROJO
    filas = len(datos)
    estilo_base = [
        ("SPAN", (0, 0), (-1, 0)),
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_OSCURO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, GRIS_BORDE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
        ("TEXTCOLOR", (2, 1), (2, -1), color),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    tabla.setStyle(TableStyle(estilo_base))
    return tabla


def _tabla_detalle(transacciones, estilos):
    estilo_celda = ParagraphStyle(
        "CeldaDetalle", parent=estilos["Normal"], fontSize=8, leading=10
    )
    encabezado = ["Fecha", "Tipo", "Categoría", "Descripción", "Monto"]
    datos = [encabezado]

    for t in transacciones:
        descripcion = Paragraph(t.descripcion or "-", estilo_celda)
        datos.append(
            [
                t.fecha.strftime("%d/%m/%Y") if t.fecha else "-",
                t.tipo.capitalize(),
                t.categoria,
                descripcion,
                _fmt_monto(t.monto),
            ]
        )

    tabla = Table(
        datos,
        colWidths=[2.2 * cm, 1.8 * cm, 3.5 * cm, 6.3 * cm, 3 * cm],
        repeatRows=1,
    )
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), AZUL_OSCURO),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("ALIGN", (4, 1), (4, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, GRIS_BORDE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return tabla


def generar_pdf(email_usuario, transacciones, fecha_inicio=None, fecha_fin=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        title="Reporte de Gastos e Ingresos",
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.8 * cm,
    )

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "TituloReporte", parent=estilos["Title"], fontSize=18, spaceAfter=6
    )
    estilo_meta = ParagraphStyle(
        "MetaReporte",
        parent=estilos["Normal"],
        textColor=colors.grey,
        fontSize=9,
    )
    estilo_seccion = ParagraphStyle(
        "SeccionReporte",
        parent=estilos["Heading2"],
        fontSize=12,
        spaceBefore=14,
        spaceAfter=6,
    )

    ingresos = [t for t in transacciones if t.tipo == "ingreso"]
    gastos = [t for t in transacciones if t.tipo == "gasto"]
    total_ingresos = sum(t.monto for t in ingresos)
    total_gastos = sum(t.monto for t in gastos)
    balance = total_ingresos - total_gastos

    elementos = [
        Paragraph("Reporte de Gastos e Ingresos", estilo_titulo),
        Paragraph(f"Usuario: {email_usuario}", estilo_meta),
        Paragraph(
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            estilo_meta,
        ),
    ]

    if fecha_inicio or fecha_fin:
        desde = (
            fecha_inicio.strftime("%d/%m/%Y") if fecha_inicio else "inicio"
        )
        hasta = fecha_fin.strftime("%d/%m/%Y") if fecha_fin else "hoy"
        elementos.append(Paragraph(f"Período: {desde} - {hasta}", estilo_meta))

    elementos.append(Spacer(1, 14))
    elementos.append(_tabla_resumen(total_ingresos, total_gastos, balance))

    tabla_gastos_cat = _tabla_por_categoria(
        "Gastos por categoría", gastos, estilos
    )
    if tabla_gastos_cat:
        elementos.append(Paragraph("Desglose por categoría", estilo_seccion))
        elementos.append(tabla_gastos_cat)

    tabla_ingresos_cat = _tabla_por_categoria(
        "Ingresos por categoría", ingresos, estilos
    )
    if tabla_ingresos_cat:
        if not tabla_gastos_cat:
            elementos.append(
                Paragraph("Desglose por categoría", estilo_seccion)
            )
        elementos.append(Spacer(1, 10))
        elementos.append(tabla_ingresos_cat)

    elementos.append(Paragraph("Detalle de transacciones", estilo_seccion))
    if transacciones:
        elementos.append(_tabla_detalle(transacciones, estilos))
    else:
        elementos.append(
            Paragraph(
                "No hay transacciones registradas en el período seleccionado.",
                estilos["Normal"],
            )
        )

    doc.build(elementos, onFirstPage=_pie_de_pagina, onLaterPages=_pie_de_pagina)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
