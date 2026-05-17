from pypdf import PdfReader, PdfWriter

input_pdf = "AI_Operational_Analytics_Report.pdf"
output_pdf = "AI_Operational_Analytics_Report_Fixed.pdf"

reader = PdfReader(input_pdf)
writer = PdfWriter()

for i, page in enumerate(reader.pages, start=1):
    if i in [4, 7]:
        page.rotate(90)
    writer.add_page(page)

with open(output_pdf, "wb") as f:
    writer.write(f)

print(f"Fixed PDF created: {output_pdf}")