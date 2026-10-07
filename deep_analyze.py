import os
import openpyxl
import pandas as pd
from openpyxl.utils import get_column_letter

data_dir = r"d:\Shivam AI\Shivam AI\Day Book\data_files"

def analyze_all():
    print("================================================================================")
    print("DEEP DATA INSPECTION & RELATIONSHIP ANALYSIS")
    print("================================================================================\n")
    
    files = {
        "Day Book": {
            "file": "DayBookReport_06-10-2026-14-27-32.xlsx",
            "header_row": 13, # 1-based
        },
        "AP": {
            "file": "APTaxRegisterDetailReport_06-10-2026-14-30-40.xlsx",
            "header_row": 14,
        },
        "AR": {
            "file": "ARTaxRegisterDetailReport_06-10-2026-14-58-25.xlsx",
            "header_row": 15,
        }
    }
    
    dfs = {}
    
    for doc_type, cfg in files.items():
        filepath = os.path.join(data_dir, cfg["file"])
        # pandas read_excel with header = cfg['header_row'] - 1
        df = pd.read_excel(filepath, header=cfg["header_row"] - 1)
        # Drop rows where all elements are NaN or summary rows
        print(f"\n--- {doc_type} (Raw rows: {len(df)}, Raw cols: {len(df.columns)}) ---")
        
        # Check summary rows
        # In financial reports, bottom rows often have 'Report Total' or NaN voucher numbers
        first_col = df.columns[0]
        print(f"First column name: '{first_col}'")
        print("Last 5 rows:")
        print(df.iloc[-5:, :5])
        
        # Clean dataframe by filtering out null voucher number or empty rows
        # Let's find the voucher number column in this df
        v_cols = [c for c in df.columns if "voucher number" in str(c).lower() or "voucher no" in str(c).lower()]
        print(f"Voucher column found: {v_cols}")
        
        # Let's inspect unique sites, voucher types, voucher subtypes
        site_cols = [c for c in df.columns if "site" in str(c).lower()]
        vtype_cols = [c for c in df.columns if "voucher type" in str(c).lower()]
        vsubtype_cols = [c for c in df.columns if "voucher sub" in str(c).lower()]
        
        print(f"Site columns: {site_cols}")
        print(f"Voucher Type columns: {vtype_cols}")
        print(f"Voucher Sub-Type columns: {vsubtype_cols}")
        
        if site_cols:
            print(f"Unique Sites ({len(df[site_cols[0]].dropna().unique())}): {list(df[site_cols[0]].dropna().unique())[:10]}")
        if vtype_cols:
            print(f"Unique Voucher Types ({len(df[vtype_cols[0]].dropna().unique())}): {list(df[vtype_cols[0]].dropna().unique())}")
        if vsubtype_cols:
            print(f"Unique Voucher Sub-Types ({len(df[vsubtype_cols[0]].dropna().unique())}): {list(df[vsubtype_cols[0]].dropna().unique())}")
            
        dfs[doc_type] = df

    # Cross-file relationship analysis
    db_df = dfs["Day Book"]
    ap_df = dfs["AP"]
    ar_df = dfs["AR"]
    
    db_vouchers = set(db_df["Voucher Number"].dropna().astype(str).unique())
    ap_vouchers = set(ap_df["Voucher Number"].dropna().astype(str).unique())
    ar_vouchers = set(ar_df["Voucher Number"].dropna().astype(str).unique())
    
    print("\n================================================================================")
    print("VOUCHER OVERLAP & RELATIONSHIP ANALYSIS")
    print("================================================================================")
    print(f"Day Book unique vouchers: {len(db_vouchers)}")
    print(f"AP unique vouchers: {len(ap_vouchers)}")
    print(f"AR unique vouchers: {len(ar_vouchers)}")
    
    print(f"Day Book & AP Voucher Overlap: {len(db_vouchers.intersection(ap_vouchers))} vouchers")
    print(f"Day Book & AR Voucher Overlap: {len(db_vouchers.intersection(ar_vouchers))} vouchers")
    print(f"AP & AR Voucher Overlap: {len(ap_vouchers.intersection(ar_vouchers))} vouchers")
    
    # Let's inspect a shared voucher between Day Book and AP
    overlap_ap = list(db_vouchers.intersection(ap_vouchers))
    if overlap_ap:
        sample_v = overlap_ap[0]
        print(f"\nSample Overlapping Voucher (Day Book <-> AP): {sample_v}")
        print("Day Book record:")
        print(db_df[db_df["Voucher Number"].astype(str) == sample_v][["Transaction Site", "Voucher Number", "Voucher Date", "Voucher Type", "Narration", "Created By", "Approved By"]].to_dict(orient="records"))
        print("AP record:")
        print(ap_df[ap_df["Voucher Number"].astype(str) == sample_v][["Accounting Site Code", "Voucher Number", "Voucher Type", "Voucher Sub Type", "Invoice Number"]].to_dict(orient="records"))

    overlap_ar = list(db_vouchers.intersection(ar_vouchers))
    if overlap_ar:
        sample_v = overlap_ar[0]
        print(f"\nSample Overlapping Voucher (Day Book <-> AR): {sample_v}")
        print("Day Book record:")
        print(db_df[db_df["Voucher Number"].astype(str) == sample_v][["Transaction Site", "Voucher Number", "Voucher Date", "Voucher Type", "Narration", "Created By", "Approved By"]].to_dict(orient="records"))
        print("AR record:")
        print(ar_df[ar_df["Voucher Number"].astype(str) == sample_v][["Accounting Site Code", "Voucher Number", "Voucher Type", "Voucher Sub Type"]].to_dict(orient="records"))

if __name__ == "__main__":
    analyze_all()
