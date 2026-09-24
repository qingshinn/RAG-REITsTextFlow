'''
去除页眉页脚的操作
'''

import pymupdf

doc = pymupdf.open(
    "红土创新深圳安居REIT：红土创新深圳安居保障性租赁住房封闭式基础设施证券投资基金2026年第1季度报告.pdf"
    )
for page in doc:
    header = pymupdf.Rect(0, 0, page.rect.width, 50)
    footer = pymupdf.Rect(0, page.rect.height - 55, page.rect.width, page.rect.height)

    page.add_redact_annot(header, fill=(1, 1, 1))  # 白色覆盖
    page.add_redact_annot(footer, fill=(1, 1, 1))
    page.apply_redactions()

doc.save("output.pdf")