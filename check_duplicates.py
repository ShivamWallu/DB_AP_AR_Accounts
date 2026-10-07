import os
import pandas as pd

data_dir = r"d:\Shivam AI\Shivam AI\Day Book\data_files"

def check_uniqueness():
    db_df = pd.read_excel(os.path.join(data_dir, "DayBookReport_06-10-2026-14-27-32.xlsx"), header=12)
    ap_df = pd.read_excel(os.path.join(data_dir, "APTaxRegisterDetailReport_06-10-2026-14-30-40.xlsx"), header=13)
    ar_df = pd.read_excel(os.path.join(data_dir, "ARTaxRegisterDetailReport_06-10-2026-14-58-25.xlsx"), header=14)

    # Filter out footer/null rows
    db_df = db_df[db_df["Voucher Number"].notna() & ~db_df["Voucher Number"].astype(str).str.startswith("Exported")]
    ap_df = ap_df[ap_df["Voucher Number"].notna() & ~ap_df["Voucher Number"].astype(str).str.startswith("Exported")]
    ar_df = ar_df[ar_df["Voucher Number"].notna() & ~ar_df["Voucher Number"].astype(str).str.startswith("Exported")]

    print(f"Cleaned Row counts: Day Book={len(db_df)}, AP={len(ap_df)}, AR={len(ar_df)}")

    # Day Book duplicate check
    print("\n--- Day Book Duplicate Check ---")
    print(f"Total rows: {len(db_df)}")
    print(f"Unique Voucher Numbers: {db_df['Voucher Number'].nunique()}")
    # Check if (Transaction Site, Voucher Number, Account Code/Description, Party Code, Amount) makes it unique
    print(f"Unique (Site, Voucher No): {db_df.drop_duplicates(subset=['Transaction Site', 'Voucher Number']).shape[0]}")
    # Full row duplicates
    print(f"Exact duplicate rows in Day Book: {db_df.duplicated().sum()}")

    # AP duplicate check
    print("\n--- AP Duplicate Check ---")
    print(f"Total rows: {len(ap_df)}")
    print(f"Unique Voucher Numbers: {ap_df['Voucher Number'].nunique()}")
    print(f"Unique (Site, Voucher No, Invoice No, Item/Service Description): {ap_df.drop_duplicates(subset=['Accounting Site Code', 'Voucher Number', 'Invoice Number', 'Item/Service Description']).shape[0]}")
    print(f"Exact duplicate rows in AP: {ap_df.duplicated().sum()}")

    # AR duplicate check
    print("\n--- AR Duplicate Check ---")
    print(f"Total rows: {len(ar_df)}")
    print(f"Unique Voucher Numbers: {ar_df['Voucher Number'].nunique()}")
    print(f"Exact duplicate rows in AR: {ar_df.duplicated().sum()}")

check_uniqueness()
