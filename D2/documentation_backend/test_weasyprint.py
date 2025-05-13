from weasyprint import HTML

HTML(string='<h1>Тест WeasyPrint</h1><p>Привет, мир!</p>').write_pdf('test.pdf')
print("PDF создан: test.pdf")