from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)


def generate_pdf(report_data, filename):

    pdf = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    content = []

    title = Paragraph(
        "Sales Forecasting & Inventory Optimization Report",
        styles["Title"]
    )

    content.append(title)

    content.append(
        Spacer(1, 20)
    )

    for item in report_data:

        paragraph = Paragraph(
            str(item),
            styles["BodyText"]
        )

        content.append(
            paragraph
        )

        content.append(
            Spacer(1, 10)
        )

    pdf.build(content)