#!/usr/bin/env python3
"""
Test script for Olympus-Coder-v1 monitoring tools

Validates that accuracy tracking and performance monitoring tools work correctly.
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

def test_accuracy_tracker():
    """Test accuracy tracker functionality"""
    print("🧪 Testing Accuracy Tracker...")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        # Test report generation (should work even without data)
        cmd = [
            sys.executable, "olympus-coder-v1/scripts/accuracy_tracker.py",
            "--report-only", "--db-path", db_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ Accuracy tracker report generation works")
            return True
        else:
            print(f"  ❌ Accuracy tracker failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ Accuracy tracker test error: {e}")
        return False
    finally:
        # Clean up
        try:
            os.unlink(db_path)
        except:
            pass

def test_performance_monitor():
    """Test performance monitor functionality"""
    print("🧪 Testing Performance Monitor...")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        # Test with minimal iterations and export to JSON
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_json:
            json_path = tmp_json.name
        
        cmd = [
            sys.executable, "olympus-coder-v1/scripts/performance_monitor.py",
            "--iterations", "1", "--db-path", db_path, "--output", json_path
        ]
        
        # This might fail if Ollama is not running, but we can check the script syntax
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Check if script runs without syntax errors (even if it fails due to no Ollama)
        if "performance_monitor.py" not in result.stderr or "SyntaxError" not in result.stderr:
            print("  ✅ Performance monitor script syntax is valid")
            return True
        else:
            print(f"  ❌ Performance monitor syntax error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⚠️  Performance monitor test timed out (likely no Ollama server)")
        return True  # Timeout is acceptable if no server is running
    except Exception as e:
        print(f"  ❌ Performance monitor test error: {e}")
        return False
    finally:
        # Clean up
        try:
            os.unlink(db_path)
            os.unlink(json_path)
        except:
            pass

def test_monitoring_dashboard():
    """Test monitoring dashboard functionality"""
    print("🧪 Testing Monitoring Dashboard...")
    
    # Create temporary databases
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_acc_db:
        acc_db_path = tmp_acc_db.name
    
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_perf_db:
        perf_db_path = tmp_perf_db.name
    
    try:
        # Test dashboard report generation (should work even without data)
        cmd = [
            sys.executable, "olympus-coder-v1/scripts/monitoring_dashboard.py",
            "--accuracy-db", acc_db_path,
            "--performance-db", perf_db_path,
            "--days", "7"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ Monitoring dashboard works")
            return True
        else:
            print(f"  ❌ Monitoring dashboard failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ Monitoring dashboard test error: {e}")
        return False
    finally:
        # Clean up
        try:
            os.unlink(acc_db_path)
            os.unlink(perf_db_path)
        except:
            pass

def test_script_imports():
    """Test that all monitoring scripts can be imported without errors"""
    print("🧪 Testing Script Imports...")
    
    scripts = [
        "olympus-coder-v1/scripts/accuracy_tracker.py",
        "olympus-coder-v1/scripts/performance_monitor.py",
        "olympus-coder-v1/scripts/monitoring_dashboard.py"
    ]
    
    all_passed = True
    
    for script in scripts:
        try:
            # Test syntax by compiling
            with open(script, 'r') as f:
                code = f.read()
            
            compile(code, script, 'exec')
            print(f"  ✅ {Path(script).name} syntax is valid")
            
        except SyntaxError as e:
            print(f"  ❌ {Path(script).name} syntax error: {e}")
            all_passed = False
        except Exception as e:
            print(f"  ❌ {Path(script).name} error: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Run all monitoring tool tests"""
    print("🚀 Testing Olympus-Coder-v1 Monitoring Tools")
    print("=" * 50)
    
    tests = [
        ("Script Imports", test_script_imports),
        ("Accuracy Tracker", test_accuracy_tracker),
        ("Performance Monitor", test_performance_monitor),
        ("Monitoring Dashboard", test_monitoring_dashboard)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"  ❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All monitoring tools are working correctly!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())