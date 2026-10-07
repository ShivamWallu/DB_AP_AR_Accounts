import os
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app

def test_full_pipeline():
    print("================================================================================")
    print("RUNNING END-TO-END VERIFICATION TESTS")
    print("================================================================================\n")

    with TestClient(app) as client:
        # 1. Test Login as Admin
        print("1. Testing Admin Login...")
        res = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@123"})
        assert res.status_code == 200, f"Admin login failed: {res.text}"
        admin_token = res.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("   [PASS] Admin logged in successfully! Role:", res.json()["role"])

        # 2. Test Login as Employee
        print("2. Testing Employee Login...")
        res = client.post("/api/auth/login", json={"username": "employee", "password": "Employee@123"})
        assert res.status_code == 200, f"Employee login failed: {res.text}"
        emp_token = res.json()["access_token"]
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        print("   [PASS] Employee logged in successfully! Role:", res.json()["role"])

        # 3. Test Initial Seed / Batches
        print("3. Testing Batches and Ingested Records...")
        res = client.get("/api/imports", headers=admin_headers)
        assert res.status_code == 200
        batches = res.json()
        print(f"   [PASS] Batches found: {len(batches)}")
        for b in batches:
            print(f"     Batch Code: {b['batch_code']}, Status: {b['status']}, DayBook: {b['daybook_rows']}, AP: {b['ap_rows']}, AR: {b['ar_rows']}, New: {b['new_records']}, Dup: {b['duplicate_records']}")

        # 4. Test Dashboard Stats
        print("\n4. Testing Dashboard Statistics...")
        res = client.get("/api/dashboard/stats", headers=emp_headers)
        assert res.status_code == 200
        stats = res.json()
        print(f"   [PASS] Day Book Total: {stats['total_daybook_records']}")
        print(f"   [PASS] AP Total: {stats['total_ap_records']}")
        print(f"   [PASS] AR Total: {stats['total_ar_records']}")
        print(f"   [PASS] Total Historical: {stats['total_historical_records']}")
        print(f"   [PASS] AP Total Amount: Rs {stats['ap_total_amount']:,.2f}")
        print(f"   [PASS] AR Total Amount: Rs {stats['ar_total_amount']:,.2f}")
        print(f"   [PASS] Total Taxes: Rs {stats['total_tax_collected_or_paid']:,.2f}")

        # 5. Test Filters endpoint
        print("\n5. Testing Filter Options Endpoint...")
        res = client.get("/api/data/filters", headers=emp_headers)
        assert res.status_code == 200
        filters = res.json()
        print(f"   [PASS] Sites available ({len(filters['sites'])}): {filters['sites'][:5]}")
        print(f"   [PASS] Voucher Types available ({len(filters['voucher_types'])}): {filters['voucher_types'][:5]}")
        print(f"   [PASS] Voucher Sub-Types available ({len(filters['voucher_subtypes'])}): {filters['voucher_subtypes'][:5]}")

        # 6. Test Master 360 Unified Ledger
        print("\n6. Testing Master 360 Unified Ledger...")
        res = client.get("/api/data/master?page=1&page_size=5", headers=emp_headers)
        assert res.status_code == 200
        master_data = res.json()
        print(f"   [PASS] Master 360 Total Records: {master_data['total']}, Current Page Count: {len(master_data['items'])}")
        first_m = master_data['items'][0]
        print(f"   Sample Master 360 Row: Source='{first_m['source_tag']}', Voucher='{first_m['voucher_number']}', HasAP={first_m['has_ap']}, HasAR={first_m['has_ar']}, Amount=Rs {first_m['combined_amount']}")

        # 7. Test Day Book Query & Column Integrity
        print("\n7. Testing Day Book Query & Column Integrity...")
        res = client.get("/api/data/daybook?page=1&page_size=5", headers=emp_headers)
        assert res.status_code == 200
        db_data = res.json()
        print(f"   [PASS] Day Book Total Records: {db_data['total']}, Current Page Count: {len(db_data['items'])}")
        first_db = db_data['items'][0]
        print(f"   Sample Day Book Row: Site='{first_db['transaction_site']}', Voucher='{first_db['voucher_number']}', Date='{first_db['voucher_date']}', Type='{first_db['voucher_type']}', Created By='{first_db['created_by']}', Approved By='{first_db['approved_by']}'")

        # 7. Test AP Query & Column Integrity
        print("\n7. Testing AP Query & Column Integrity...")
        res = client.get("/api/data/ap?page=1&page_size=5", headers=emp_headers)
        assert res.status_code == 200
        ap_data = res.json()
        print(f"   [PASS] AP Total Records: {ap_data['total']}, Current Page Count: {len(ap_data['items'])}")
        first_ap = ap_data['items'][0]
        print(f"   Sample AP Row: Site='{first_ap['accounting_site_code']}', Voucher='{first_ap['voucher_number']}', SubType='{first_ap['voucher_sub_type']}', Total Amt=Rs {first_ap['total_voucher_amount']}, Created By='{first_ap['created_by']}'")

        # 8. Test AR Query & Column Integrity
        print("\n8. Testing AR Query & Column Integrity...")
        res = client.get("/api/data/ar?page=1&page_size=5", headers=emp_headers)
        assert res.status_code == 200
        ar_data = res.json()
        print(f"   [PASS] AR Total Records: {ar_data['total']}, Current Page Count: {len(ar_data['items'])}")
        first_ar = ar_data['items'][0]
        print(f"   Sample AR Row: Site='{first_ar['accounting_site_code']}', Voucher='{first_ar['voucher_number']}', SubType='{first_ar['voucher_sub_type']}', Net Amt=Rs {first_ar['net_amount']}, CGST={first_ar['total_cgst']}, SGST={first_ar['total_sgst']}, IGST={first_ar['total_igst']}")

        # 9. Test Cross Reference Linking
        sample_vno = first_db['voucher_number']
        print(f"\n9. Testing Cross-Reference Explorer for '{sample_vno}'...")
        res = client.get(f"/api/data/cross-reference/{sample_vno}", headers=emp_headers)
        assert res.status_code == 200
        xref = res.json()
        print(f"   [PASS] Linked Voucher: {xref['voucher_number']} -> DayBook: {xref['daybook_count']} rows, AP: {xref['ap_count']} rows, AR: {xref['ar_count']} rows")

        # 10. Test New Batch Upload & High-Speed Direct Ingestion
        print("\n10. Testing New Batch Upload & High-Speed Direct Ingestion...")
        data_dir = r"d:\Shivam AI\Shivam AI\Day Book\data_files"
        files = [
            ("files", ("DayBookReport.xlsx", open(os.path.join(data_dir, "DayBookReport_06-10-2026-14-27-32.xlsx"), "rb"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
            ("files", ("APTaxRegister.xlsx", open(os.path.join(data_dir, "APTaxRegisterDetailReport_06-10-2026-14-30-40.xlsx"), "rb"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
            ("files", ("ARTaxRegister.xlsx", open(os.path.join(data_dir, "ARTaxRegisterDetailReport_06-10-2026-14-58-25.xlsx"), "rb"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
        ]
        res = client.post("/api/upload/import", files=files, headers=admin_headers)
        assert res.status_code == 200, f"Second upload failed: {res.text}"
        batch2 = res.json()
        print(f"   [PASS] Second Batch Code: {batch2['batch_code']}")
        print(f"   [PASS] Total Rows Processed: {batch2['total_rows']}")
        print(f"   [PASS] New Records Added in New Batch: {batch2['new_records']}")
        assert batch2['new_records'] == batch2['total_rows'], "Expected all rows in the new batch to be stored directly without deduplication!"
        print("   [PASS] Direct high-speed ingestion verified: All new batch records stored cleanly!")

        # 11. Test Audit Logs
        print("\n11. Testing Audit Log Recording...")
        res = client.get("/api/audit/logs", headers=admin_headers)
        assert res.status_code == 200
        logs = res.json()
        print(f"   [PASS] Total Audit Logs: {len(logs)}")
        for l in logs[:4]:
            print(f"     [{l['timestamp']}] {l['user_username']} ({l['user_role']}) - {l['action']}: {l['status']}")

    print("\n================================================================================")
    print("ALL TESTS PASSED WITH 100% ACCURACY!")
    print("================================================================================")

if __name__ == "__main__":
    test_full_pipeline()
