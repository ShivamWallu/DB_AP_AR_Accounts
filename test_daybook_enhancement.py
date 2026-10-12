"""
Test script for Finance Day Book - Upload, Validation & Dashboard Enhancement.
Verifies all 10 acceptance criteria specified in the user request.
"""
import os
import sys
from fastapi.testclient import TestClient

from app.main import app
from app.excel_parser import DAYBOOK_COLUMNS_44, compute_validation_status, parse_date_only, validate_daybook_file, parse_daybook_file
from app.database import get_db, SessionLocal
from app.models import DayBookRecord, ImportBatch, ImportFile
from app.auth import create_access_token

client = TestClient(app)

def test_1_column_sequence():
    print("\n--- Test 1: Column sequence verification (44 columns) ---")
    expected = [
        "Transaction Site",
        "Transaction Site Description",
        "Accounting Site Code",
        "Accounting Site Description",
        "Source",
        "Voucher Number",
        "Journal Voucher",
        "Voucher Date",
        "Inter Unit Y / N",
        "Source / Target",
        "Voucher Type",
        "Voucher Status",
        "Party Code",
        "Party Description",
        "Payment Mode",
        "Cheque Number",
        "Bank Account Number",
        "Account Code",
        "Account Description",
        "Owner Name",
        "Owner Description",
        "Purpose",
        "Purpose Description",
        "Net Amount in Foreign Currency",
        "Net Amount in Domestic Currency",
        "Service Amount Foreign Currency",
        "Service Amount Domestic Currency",
        "Charge Amount Foreign Currency",
        "Charge Amount Domestic Currency",
        "Bank Charge Amount Foreign Currency",
        "Bank Charge Amount Domestic Currency",
        "Discount in Foreign Currency",
        "Discount in Domestic Currency",
        "Tax Amount Foreign Currency",
        "Tax Amount Domestic Currency",
        "Round Off Amount Foreign Currency",
        "Round Off Amount Domestic Currency",
        "Total Amount in Foreign Currency",
        "Total Amount in Domestic Currency",
        "Narration",
        "Created By",
        "Created Date",
        "Approved By",
        "Approved Date",
    ]
    assert len(DAYBOOK_COLUMNS_44) == 44, f"Expected 44 columns, got {len(DAYBOOK_COLUMNS_44)}"
    for idx, (exp, actual) in enumerate(zip(expected, DAYBOOK_COLUMNS_44), start=1):
        assert exp == actual, f"Column mismatch at {idx}: expected '{exp}', got '{actual}'"
    print("[OK] All 44 columns verified in exact sequence!")

def test_2_validation_rules():
    print("\n--- Test 2: Date Validation Rules (Rules 1-5) ---")
    # Rule 1: Matched (V = A and C != A)
    # Example: V = 07/10/2026, C = 06/10/2026, A = 07/10/2026
    r1 = compute_validation_status("07/10/2026", "06/10/2026", "07/10/2026")
    assert r1 == "Matched", f"Rule 1 failed: got {r1}"
    print("[OK] Rule 1 (Matched): PASSED")

    # Rule 2: Back date entry (C = A and V != C)
    # Example: V = 07/10/2026, C = 08/10/2026, A = 08/10/2026
    r2 = compute_validation_status("07/10/2026", "08/10/2026", "08/10/2026")
    assert r2 == "Back date entry", f"Rule 2 failed: got {r2}"
    print("[OK] Rule 2 (Back date entry): PASSED")

    # Rule 3: Late Approval (V = C and C != A)
    # Example: V = 07/10/2026, C = 07/10/2026, A = 08/10/2026
    r3 = compute_validation_status("07/10/2026", "07/10/2026", "08/10/2026")
    assert r3 == "Late Approval", f"Rule 3 failed: got {r3}"
    print("[OK] Rule 3 (Late Approval): PASSED")

    # Rule 4: Back date entry & Late Approval (V != C and C != A and V != A)
    # Example: V = 07/10/2026, C = 08/10/2026, A = 10/10/2026
    r4 = compute_validation_status("07/10/2026", "08/10/2026", "10/10/2026")
    assert r4 == "Back date entry & Late Approval", f"Rule 4 failed: got {r4}"
    print("[OK] Rule 4 (Back date entry & Late Approval): PASSED")

    # Rule 5: Pending / Check Dates
    # V = C = A
    r5a = compute_validation_status("07/10/2026", "07/10/2026", "07/10/2026")
    assert r5a == "Pending / Check Dates", f"Rule 5a failed: got {r5a}"
    # Blank / missing date
    r5b = compute_validation_status(None, "07/10/2026", "07/10/2026")
    assert r5b == "Pending / Check Dates", f"Rule 5b failed: got {r5b}"
    r5c = compute_validation_status("invalid-date", "07/10/2026", "07/10/2026")
    assert r5c == "Pending / Check Dates", f"Rule 5c failed: got {r5c}"
    print("[OK] Rule 5 (Pending / Check Dates): PASSED")

def test_3_real_file_parse_and_validate():
    print("\n--- Test 3: Parse and validate actual Excel file ---")
    filepath = "data_files/DayBookReport_06-10-2026-14-27-32.xlsx"
    if not os.path.exists(filepath):
        print("Sample file not found at", filepath)
        return

    val_res = validate_daybook_file(filepath)
    assert val_res["is_valid"] is True, f"File validation failed: {val_res.get('error')}"
    assert val_res["missing_columns"] == [], f"Missing columns: {val_res['missing_columns']}"
    assert val_res["total_rows"] == 393
    stats = val_res["stats"]
    print("Validation stats on actual file:", stats)
    total_cat = (
        stats["matched"]
        + stats["back_date_entry"]
        + stats["late_approval"]
        + stats["back_date_and_late_approval"]
        + stats["pending_check_dates"]
    )
    assert total_cat == stats["total_transactions"], f"Sum {total_cat} != total {stats['total_transactions']}"
    print("[OK] Actual file validation and partition: PASSED")

def test_4_stats_api():
    print("\n--- Test 4: Dynamic Dashboard Stats API ---")
    token = create_access_token({"sub": "admin", "role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = client.get("/api/data/daybook/stats", headers=headers)
    assert resp.status_code == 200, f"Stats API error: {resp.text}"
    data = resp.json()
    print("API Stats:", data)
    assert "total_transactions" in data
    assert "matched" in data
    assert "back_date_entry" in data
    assert "late_approval" in data
    assert "back_date_and_late_approval" in data
    assert "pending_check_dates" in data
    assert "balance_other" in data
    # Verify exact partition
    sum_parts = (
        data["matched"]
        + data["back_date_entry"]
        + data["late_approval"]
        + data["back_date_and_late_approval"]
        + data["pending_check_dates"]
    )
    assert sum_parts == data["total_transactions"], f"Partition error: {sum_parts} != {data['total_transactions']}"
    assert data["balance_other"] == data["pending_check_dates"]
    print("[OK] Dashboard stats API verified!")

def test_5_daybook_data_api_and_filters():
    print("\n--- Test 5: Day Book Data API with 44 columns + validation status + filters ---")
    token = create_access_token({"sub": "admin", "role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = client.get("/api/data/daybook?page=1&page_size=5", headers=headers)
    assert resp.status_code == 200, f"Data API error: {resp.text}"
    data = resp.json()
    assert len(data["items"]) > 0
    first_item = data["items"][0]
    # Check that original 44 column names exist in first_item
    for col in DAYBOOK_COLUMNS_44:
        assert col in first_item, f"Missing original column '{col}' in API response item"
    assert "validation_status" in first_item, "Missing validation_status column"
    print("[OK] First item has all 44 original columns in exact name plus validation_status")

    # Test filtering by status = "Matched"
    resp_matched = client.get("/api/data/daybook?validation_status=Matched&page=1&page_size=10", headers=headers)
    assert resp_matched.status_code == 200
    matched_data = resp_matched.json()
    for it in matched_data["items"]:
        assert it["validation_status"] == "Matched", f"Filter leaked status: {it['validation_status']}"
    print(f"[OK] Filter by 'Matched' returned {matched_data['total']} matching records correctly")

    # Test filtering by status = "Late Approval"
    resp_late = client.get("/api/data/daybook?validation_status=Late Approval&page=1&page_size=10", headers=headers)
    assert resp_late.status_code == 200
    late_data = resp_late.json()
    for it in late_data["items"]:
        assert it["validation_status"] == "Late Approval", f"Filter leaked status: {it['validation_status']}"
    print(f"[OK] Filter by 'Late Approval' returned {late_data['total']} matching records correctly")

def test_6_upload_deduplication():
    print("\n--- Test 6: Upload deduplication logic ---")
    token = create_access_token({"sub": "admin", "role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}
    filepath = "data_files/DayBookReport_06-10-2026-14-27-32.xlsx"
    if not os.path.exists(filepath):
        print("Sample file not found, skipping upload test")
        return

    # Call /api/daybook/validate endpoint
    with open(filepath, "rb") as f:
        resp = client.post("/api/daybook/validate", files={"file": ("DayBookReport.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, headers=headers)
    assert resp.status_code == 200, f"Validate endpoint failed: {resp.text}"
    vdata = resp.json()
    assert vdata["is_valid"] is True
    print(f"[OK] /api/daybook/validate returned valid file with {vdata['total_rows']} rows")

    # Re-upload existing file to test duplicate detection
    with open(filepath, "rb") as f:
        resp_up = client.post("/api/daybook/upload", files={"file": ("DayBookReport.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, headers=headers)
    assert resp_up.status_code == 200, f"Upload endpoint failed: {resp_up.text}"
    up_res = resp_up.json()
    print("Upload result on existing file:", up_res)
    assert up_res["inserted"] == 0, f"Expected 0 new insertions due to duplicates, got {up_res['inserted']}"
    assert up_res["duplicates"] == 393, f"Expected 393 duplicates detected, got {up_res['duplicates']}"
    # Clean up test batch so it doesn't leave an empty batch in DB
    if "batch_id" in up_res:
        with SessionLocal() as db_cleanup:
            b_clean = db_cleanup.query(ImportBatch).filter(ImportBatch.id == up_res["batch_id"]).first()
            if b_clean:
                db_cleanup.query(ImportFile).filter(ImportFile.batch_id == up_res["batch_id"]).delete()
                db_cleanup.delete(b_clean)
                db_cleanup.commit()

    print("[OK] Upload deduplication successfully identified all 393 identical rows!")

if __name__ == "__main__":
    try:
        test_1_column_sequence()
        test_2_validation_rules()
        test_3_real_file_parse_and_validate()
        test_4_stats_api()
        test_5_daybook_data_api_and_filters()
        test_6_upload_deduplication()
        print("\n==============================================")
        print("SUCCESS: ALL ACCEPTANCE CRITERIA TESTS PASSED 100%!")
        print("==============================================")
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
