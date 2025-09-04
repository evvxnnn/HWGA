#!/usr/bin/env python3
"""
Quick test script to check if the UI modules work
"""

import sys
from PyQt6.QtWidgets import QApplication

def test_module(module_name, class_name):
    try:
        print(f"Testing {module_name}...")
        exec(f"from ui.{module_name} import {class_name}")
        print(f"✓ {class_name} imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error with {class_name}: {e}")
        return False

def main():
    print("UI Module Test Report")
    print("=" * 50)
    
    modules = [
        ("email_ui", "EmailPanel"),
        ("phone_ui", "PhonePanel"), 
        ("radio_ui", "RadioPanel"),
        ("everbridge_ui", "EverbridgePanel")
    ]
    
    results = []
    for module, class_name in modules:
        success = test_module(module, class_name)
        results.append((module, success))
    
    print("\nSummary:")
    print("-" * 30)
    for module, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{module:20} {status}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + ("All modules passed!" if all_passed else "Some modules failed."))
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())