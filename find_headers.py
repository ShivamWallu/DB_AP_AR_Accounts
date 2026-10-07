import os
import openpyxl
from openpyxl.utils import get_column_letter

data_dir = r"d:\Shivam AI\Shivam AI\Day Book\data_files"

def find_table_header(filename):
    filepath = os.path.join(data_dir, filename)
    wb = openpyxl.load_workbook(filepath, data_only=True)
    sheet = wb.active
    print(f"\n==================================================")
    print(f"FILE: {filename} (Sheet: {sheet.title})")
    print(f"Dimensions: max_row={sheet.max_row}, max_col={sheet.max_column}")
    print(f"==================================================")
    
    # Print the first 25 rows to see structure
    for r in range(1, min(25, sheet.max_row + 1)):
        row_vals = [sheet.cell(r, c).value for c in range(1, min(30, sheet.max_column + 1))]
        non_empty = [(c, val) for c, val in enumerate(row_vals, 1) if val is not None]
        if non_empty:
            print(f"Row {r:2d} ({len(non_empty)} cells): {[(get_column_letter(c), str(v)[:30]) for c, v in non_empty[:8]]}")
            
    # Find the header row (the row with the maximum number of string column names)
    best_row = 1
    max_non_empty_cols = 0
    for r in range(1, min(30, sheet.max_row + 1)):
        non_empty_cnt = sum(1 for c in range(1, sheet.max_column + 1) if sheet.cell(r, c).value is not None)
        if non_empty_cnt > max_non_empty_cols:
            max_non_empty_cols = non_empty_cnt
            best_row = r
            
    print(f"\n>>> Detected Header Row: Row {best_row} with {max_non_empty_cols} non-empty column headers")
    
    headers = {}
    for c in range(1, sheet.max_column + 1):
        col_letter = get_column_letter(c)
        val = sheet.cell(best_row, c).value
        headers[col_letter] = (c, str(val).strip() if val is not None else None)
        
    print(f"\nAll Headers on Row {best_row}:")
    for col_letter, (col_idx, hname) in headers.items():
        if hname:
            print(f"  {col_letter:4s} (col {col_idx:3d}): {hname}")
            
    # Sample row right after header
    first_data_row = best_row + 1
    print(f"\nFirst Data Row (Row {first_data_row}):")
    for col_letter, (col_idx, hname) in headers.items():
        if hname:
            val = sheet.cell(first_data_row, col_idx).value
            print(f"  {col_letter:4s} | {hname[:35]:35s} | {val!r}")
            
    # Total data rows
    data_rows = 0
    empty_trailing = 0
    for r in range(best_row + 1, sheet.max_row + 1):
        # check if row is a data row or summary row (like 'Total' or empty)
        vals = [sheet.cell(r, c).value for c in range(1, sheet.max_column + 1)]
        if any(v is not None for v in vals):
            data_rows += 1
        else:
            empty_trailing += 1
    print(f"\nData rows count below header: {data_rows} (Empty trailing rows: {empty_trailing})")

files = [
    "DayBookReport_06-10-2026-14-27-32.xlsx",
    "APTaxRegisterDetailReport_06-10-2026-14-30-40.xlsx",
    "ARTaxRegisterDetailReport_06-10-2026-14-58-25.xlsx"
]

for f in files:
    find_table_header(f)
