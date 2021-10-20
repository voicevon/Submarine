import xlsxwriter

class Logger:
    def __init__(self) -> None:
        # Create an new Excel file and add a worksheet.
        workbook = xlsxwriter.Workbook('demo.xlsx')
        self.worksheet = workbook.add_worksheet()
        self.last_rowid = 1

    def write(self, row_value:list):
        # Write some numbers, with row/column notation.
        for col in range(row_value.count()):
            self.worksheet.write(self.last_rowid, col, row_value[col])

    def close(self):
        self.workbook.close()
        

# # Widen the first column to make the text clearer.
# worksheet.set_column('A:A', 20)

# # Add a bold format to use to highlight cells.
# bold = workbook.add_format({'bold': True})

# # Write some simple text.
# worksheet.write('A1', 'Hello')

# # Text with formatting.
# worksheet.write('A2', 'World', bold)


# # Insert an image.
# # worksheet.insert_image('B5', 'logo.png')
