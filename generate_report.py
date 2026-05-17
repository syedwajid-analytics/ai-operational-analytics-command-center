import os
from pypdf import PdfWriter

pdfs = [
    "screenshots/executive-overview.pdf",
    "screenshots/operational-diagnostics.pdf",
    "screenshots/customer-channel-analytics.pdf",
    "screenshots/ai-assistant.pdf",
]


output = "AI_Operational_Analytics_Report.pdf"

writer = PdfWriter()

for pdf in pdfs:
    if not os.path.exists(pdf):
        raise FileNotFoundError(f"Missing file: {pdf}")

    print(f"Adding: {pdf}")
    writer.append(pdf)

with open(output, "wb") as f:
    writer.write(f)

print(f"Done. Created: {output}")