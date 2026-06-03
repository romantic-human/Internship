import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side


class ExcelHandler:

    @staticmethod
    def export(headers, rows, file_path):
        wb = openpyxl.Workbook()
        ws = wb.active
        font = Font(name="微软雅黑", size=11)
        align = Alignment(horizontal="center", vertical="center")
        thin = Side(style="thin")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(name="微软雅黑", size=11, bold=True)
            cell.alignment = align
            cell.border = border

        for row in rows:
            ws.append(row)
            for cell in ws[ws.max_row]:
                cell.font = font
                cell.alignment = align
                cell.border = border

        wb.save(file_path)

    @staticmethod
    def import_excel(file_path):
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        rows = []
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i == 0:
                continue
            rows.append(list(row))
        return rows
