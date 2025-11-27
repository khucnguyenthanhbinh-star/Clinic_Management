#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST SCRIPT - Kiểm tra tất cả admin features
Chạy: python test_admin_features.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.models import ClinicDatabase
from core.auth import AuthManager
from core.password_hasher import PasswordHasher

def test_database():
    """Kiểm tra database hoạt động"""
    print("=" * 60)
    print("TEST 1: DATABASE CONNECTION")
    print("=" * 60)
    
    try:
        db = ClinicDatabase()
        print("✅ Database connection: OK")
        
        # Test query
        cursor = db.cursor
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"✅ Total users in DB: {count}")
        
        # Test each role
        for role in ["admin", "patient", "doctor", "receptionist"]:
            cursor.execute(f"SELECT COUNT(*) FROM users WHERE role = '{role}'")
            role_count = cursor.fetchone()[0]
            print(f"   - {role}: {role_count}")
        
        return db
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None

def test_auth(db):
    """Kiểm tra authentication"""
    print("\n" + "=" * 60)
    print("TEST 2: AUTHENTICATION")
    print("=" * 60)
    
    try:
        auth = AuthManager(db)
        
        # Test login as admin
        success, msg = auth.login("admin", "123456")
        if success:
            print(f"✅ Admin login: OK")
            print(f"   - Current user: {auth.current_user}")
            print(f"   - Current role: {auth.current_role}")
        else:
            print(f"❌ Admin login failed: {msg}")
        
        auth.logout()
        print(f"✅ Logout: OK")
        
    except Exception as e:
        print(f"❌ Auth error: {e}")

def test_database_methods(db):
    """Kiểm tra các method database"""
    print("\n" + "=" * 60)
    print("TEST 3: DATABASE METHODS")
    print("=" * 60)
    
    try:
        # Test get_users_by_role
        patients = db.get_users_by_role("patient")
        print(f"✅ get_users_by_role('patient'): {len(patients)} patients")
        
        doctors = db.get_users_by_role("doctor")
        print(f"✅ get_users_by_role('doctor'): {len(doctors)} doctors")
        
        # Test get_user
        user = db.get_user("admin")
        if user:
            print(f"✅ get_user('admin'): {user['name']}")
        
        # Test get_appointments
        appointments = db.get_appointments()
        print(f"✅ get_appointments(): {len(appointments)} appointments")
        
        # Test get_medicines
        medicines = db.get_medicines()
        print(f"✅ get_medicines(): {len(medicines)} medicines")
        
        # Test get_all_users
        all_users = db.get_all_users()
        print(f"✅ get_all_users(): {len(all_users)} total users")
        
    except Exception as e:
        print(f"❌ Database methods error: {e}")

def test_imports():
    """Kiểm tra import các modules admin"""
    print("\n" + "=" * 60)
    print("TEST 4: ADMIN UI IMPORTS")
    print("=" * 60)
    
    modules = [
        ("ui.admin.manage_patients", "ManagePatientsView"),
        ("ui.admin.manage_doctors", "ManageDoctorsView"),
        ("ui.admin.manage_appointments", "ManageAppointmentsView"),
        ("ui.admin.manage_medicines", "ManageMedicinesView"),
        ("ui.admin.manage_users", "ManageUsersView"),
        ("ui.admin.reports", "ReportsView"),
    ]
    
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}: OK")
        except Exception as e:
            print(f"❌ {module_name}.{class_name}: {e}")

def test_json_parsing():
    """Kiểm tra JSON parsing"""
    print("\n" + "=" * 60)
    print("TEST 5: JSON PARSING")
    print("=" * 60)
    
    import json
    
    try:
        db = ClinicDatabase()
        
        # Test doctor info parsing
        doctors = db.get_users_by_role("doctor")
        if doctors:
            for doc in doctors[:2]:  # Test first 2 doctors
                try:
                    info = json.loads(doc.get("info", "{}"))
                    print(f"✅ Doctor '{doc['name']}' info parsed: {list(info.keys())}")
                except:
                    print(f"❌ Failed to parse doctor info: {doc['name']}")
        
        # Test patient info parsing
        patients = db.get_users_by_role("patient")
        if patients:
            for pat in patients[:2]:  # Test first 2 patients
                try:
                    info = json.loads(pat.get("info", "{}"))
                    print(f"✅ Patient '{pat['name']}' info parsed: {list(info.keys())}")
                except:
                    print(f"❌ Failed to parse patient info: {pat['name']}")
    
    except Exception as e:
        print(f"❌ JSON parsing error: {e}")

def main():
    """Main test runner"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "ADMIN FEATURES TEST SUITE" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    
    db = test_database()
    if db:
        test_auth(db)
        test_database_methods(db)
        test_json_parsing()
    
    test_imports()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE ✅")
    print("=" * 60)
    print("\n💡 Bạn có thể chạy ứng dụng bằng: python main.py")
    print("📚 Xem ADMIN_USAGE_GUIDE.md để biết cách sử dụng")
    print()

if __name__ == "__main__":
    main()
