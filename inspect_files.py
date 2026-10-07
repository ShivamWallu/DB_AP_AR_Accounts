import os
import openpyxl
from openpyxl.utils import get_column_letter

data_dir = r"d:\Shivam AI\Shivam AI\Day Book\data_files"
files = [f for f in os.listdir(data_dir) if f.endswith(".xlsx")]

print(f"Found {len(files)} files in {data_dir}:")
for f in files:
    print(f" - {f}")

print("\n" + "="*80)

def inspect_file(filename):
    filepath = os.path.join(data_dir, filename)
    wb = openpyxl.load_workbook(filepath, data_only=True, read_only=False)
    sheet_names = wb.sheetnames
    print(f"\nFILE: {filename}")
    print(f"Sheets: {sheet_names}")
    
    for sname in sheet_names:
        sheet = wb[sname]
        max_row = sheet.max_row
        max_col = sheet.max_column
        print(f"\n--- Sheet: {sname} (Rows: {max_row}, Cols: {max_col}) ---")
        
        # Look at the first 5 rows to identify the actual header row
        print("First 5 rows preview:")
        for r in range(1, min(6, max_row + 1)):
            row_vals = [sheet.cell(r, c).value for c in range(1, min(15, max_col + 1))]
            print(f"  Row {r}: {row_vals[:10]}...")
            
        # Determine header row (usually row 1, but let's check)
        header_row = 1
        headers = {}
        for c in range(1, max_col + 1):
            col_letter = get_column_letter(c)
            val = sheet.cell(header_row, c).value
            headers[col_letter] = (c, str(val).strip() if val is not None else None)
            
        print(f"\nAll Headers count: {len(headers)}")
        print("Header listing (Column Letter: Header Name):")
        for col_letter, (col_idx, hname) in headers.items():
            if hname:
                print(f"  [{col_letter}] (Col {col_idx}): {hname}")
                
        # Sample 3 data rows
        print("\nSample Data Row 2:")
        for col_letter, (col_idx, hname) in headers.items():
            if hname:
                v = sheet.cell(2, col_idx).value
                print(f"    {col_letter} ({hname}): {v!r}")
                
        # Count non-empty data rows
        data_row_count = 0
        for r in range(2, max_row + 1):
            # check if row has any non-empty cell
            has_val = any(sheet.cell(r, c).value is not None for c in range(1, min(10, max_col + 1)))
            if has_val:
                data_row_count += 1
        print(f"\nActual non-empty data rows: {data_row_count}")

for f in sorted(files):
    inspect_file(f)
