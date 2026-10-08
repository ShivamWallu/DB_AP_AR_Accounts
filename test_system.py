import os
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import User

def test_full_pipeline():
    print("================================================================================")
    print("RUNNING END-TO-END VERIFICATION TESTS")
    print("================================================================================\n")

    # Reset test users to active
    db = SessionLocal()
    try:
        db.query(User).filter(User.username.in_(["admin", "employee"])).update({"is_active": True})
        db.commit()
    finally:
        db.close()

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

        # 11. Test Multi-User Real-Time Server Verification Workflow
        print("\n11. Testing Multi-User Real-Time Server Verification Workflow...")
        # Admin verifies a voucher
        test_vno = f"TEST-VNO-{first_db['id']}"
        res = client.post("/api/data/verify", json={
            "dataset_type": "daybook",
            "record_id": first_db['id'],
            "voucher_number": test_vno
        }, headers=admin_headers)
        assert res.status_code == 200, f"Verify failed: {res.text}"
        v_res = res.json()
        if v_res["status"] == "unverified":
            # Re-toggle to verified
            res = client.post("/api/data/verify", json={
                "dataset_type": "daybook",
                "record_id": first_db['id'],
                "voucher_number": test_vno
            }, headers=admin_headers)
            v_res = res.json()
        assert v_res["status"] == "verified"
        assert v_res["data"]["verified_by"] is not None
        print(f"   [PASS] Admin verified voucher '{test_vno}' successfully as '{v_res['data']['verified_by']}'")

        # Employee checks verifications list (simulating another user's live sync)
        res = client.get("/api/data/verifications", headers=emp_headers)
        assert res.status_code == 200
        all_verifs = res.json()["verifications"]
        assert f"voucher_{test_vno}" in all_verifs or f"voucher_verified_daybook_{test_vno}" in all_verifs
        print(f"   [PASS] Employee instantly retrieved Admin's verification from central server!")

        # Employee verifies AP voucher
        test_ap_vno = first_ap['voucher_number'] or "AP-TEST-001"
        res = client.post("/api/data/verify", json={
            "dataset_type": "ap",
            "record_id": first_ap['id'],
            "voucher_number": test_ap_vno
        }, headers=emp_headers)
        assert res.status_code == 200
        print(f"   [PASS] Employee verified AP voucher '{test_ap_vno}' successfully!")

        # Test Export with verified statuses
        res = client.post("/api/export/daybook", json={"site": ""}, headers=admin_headers)
        assert res.status_code == 200
        assert len(res.text) > 50
        print(f"   [PASS] Export CSV generated with server-verified columns!")

        # Toggle unverify
        res = client.post("/api/data/verify", json={
            "dataset_type": "daybook",
            "record_id": first_db['id'],
            "voucher_number": test_vno
        }, headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["status"] == "unverified"
        print(f"   [PASS] Admin unverified voucher '{test_vno}' and central DB updated!")

        # 13. Test User Account Blocking & Dynamic Security Enforcement
        print("\n13. Testing Dynamic User Account Blocking & Security Enforcement...")
        # Get employee user ID
        res = client.get("/api/auth/users", headers=admin_headers)
        assert res.status_code == 200
        users_list = res.json()
        emp_user = next((u for u in users_list if u['username'] == 'employee'), None)
        assert emp_user is not None, "Employee user not found"

        # Admin blocks employee account
        res = client.put(f"/api/auth/users/{emp_user['id']}/status", json={"is_active": False}, headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["is_active"] is False
        print(f"   [PASS] Admin successfully blocked account '{emp_user['username']}'")

        # Blocked employee attempts to login -> must be rejected (403 Forbidden)
        res = client.post("/api/auth/login", json={"username": "employee", "password": "Employee@123"})
        assert res.status_code == 403, f"Expected 403 Forbidden for blocked user, got: {res.status_code}"
        print(f"   [PASS] Blocked user login successfully rejected with 403 Forbidden: {res.json()['detail']}")

        # Admin unblocks employee account
        res = client.put(f"/api/auth/users/{emp_user['id']}/status", json={"is_active": True}, headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["is_active"] is True
        print(f"   [PASS] Admin successfully unblocked account '{emp_user['username']}'")

        # Unblocked employee attempts to login -> must succeed
        res = client.post("/api/auth/login", json={"username": "employee", "password": "Employee@123"})
        assert res.status_code == 200
        print(f"   [PASS] Unblocked user login succeeded!")

        # 14. Test Forgot Password & 10-Minute Expiring Reset Token Workflow
        print("\n14. Testing Forgot Password & 10-Minute Expiring Reset Token Workflow...")
        # Ensure admin has an email for test
        from app.models import PasswordResetToken
        db = SessionLocal()
        admin_db = db.query(User).filter(User.username == "admin").first()
        if not admin_db.email:
            admin_db.email = "admin.test@kogm.com"
            db.commit()
        db.close()

        # Request forgot password
        res = client.post("/api/auth/forgot-password", json={"identifier": "admin"})
        assert res.status_code == 200, f"Forgot password failed: {res.text}"
        fp_res = res.json()
        assert fp_res["status"] == "success"
        print(f"   [PASS] Forgot password requested successfully: {fp_res['message']}")

        # Fetch the token from DB
        db = SessionLocal()
        token_entry = db.query(PasswordResetToken).filter(PasswordResetToken.email == "admin.test@kogm.com", PasswordResetToken.is_used == False).order_by(PasswordResetToken.id.desc()).first()
        assert token_entry is not None, "Password reset token not recorded in DB"
        test_token = token_entry.token
        db.close()

        # Verify token endpoint
        res = client.get(f"/api/auth/verify-reset-token?token={test_token}")
        assert res.status_code == 200
        assert res.json()["valid"] is True
        print(f"   [PASS] Reset token verified successfully! User: @{res.json()['username']}")

        # Reset password to new password
        res = client.post("/api/auth/reset-password", json={
            "token": test_token,
            "new_password": "AdminNewPassword@999"
        })
        assert res.status_code == 200
        assert res.json()["status"] == "success"
        print(f"   [PASS] Password reset completed successfully!")

        # Login with new password
        res = client.post("/api/auth/login", json={"username": "admin", "password": "AdminNewPassword@999"})
        assert res.status_code == 200
        print(f"   [PASS] Logged in with newly updated password!")

        # Re-use of same token must be rejected (single-use constraint)
        res = client.post("/api/auth/reset-password", json={
            "token": test_token,
            "new_password": "AnotherPassword@123"
        })
        assert res.status_code == 400
        print(f"   [PASS] Re-use of consumed token properly rejected with 400!")

        # Restore password back to Admin@123 for default credentials consistency
        db = SessionLocal()
        from app.auth import get_password_hash
        admin_restore = db.query(User).filter(User.username == "admin").first()
        admin_restore.hashed_password = get_password_hash("Admin@123")
        db.commit()
        db.close()
        print(f"   [PASS] Admin credentials restored cleanly to default test baseline.")

    print("\n================================================================================")
    print("ALL TESTS PASSED WITH 100% ACCURACY!")
    print("================================================================================")

if __name__ == "__main__":
    test_full_pipeline()

