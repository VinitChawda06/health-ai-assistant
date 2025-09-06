#!/usr/bin/env python3
"""
Universal Health AI Assistant - Verification Script
Tests all components to ensure cross-platform compatibility
"""

import sys
import os
import json
import importlib.util
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.11+")
        return False

def check_file_encoding():
    """Test file encoding handling"""
    try:
        data_dir = Path("data")
        
        if not data_dir.exists():
            print("⚠️  Data directory not found")
            return False
            
        videos_file = data_dir / "videos.json"
        merged_file = data_dir / "merged.json"
        
        files_ok = True
        
        # Test UTF-8 encoding
        for file_path in [videos_file, merged_file]:
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"✅ {file_path.name} - UTF-8 encoding OK")
                except UnicodeDecodeError:
                    print(f"⚠️  {file_path.name} - UTF-8 failed, trying fallback")
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            data = json.load(f)
                        print(f"✅ {file_path.name} - Fallback encoding OK")
                    except Exception as e:
                        print(f"❌ {file_path.name} - Encoding failed: {e}")
                        files_ok = False
                except json.JSONDecodeError as e:
                    print(f"❌ {file_path.name} - JSON parsing failed: {e}")
                    files_ok = False
                except Exception as e:
                    print(f"❌ {file_path.name} - Unexpected error: {e}")
                    files_ok = False
            else:
                print(f"⚠️  {file_path.name} - File not found")
                files_ok = False
                
        return files_ok
        
    except Exception as e:
        print(f"❌ File encoding check failed: {e}")
        return False

def check_dependencies():
    """Check critical dependencies"""
    required_packages = [
        ('fastapi', '0.104.1'),
        ('uvicorn', '0.24.0'),
        ('openai', '1.51.0'),
        ('httpx', '0.27.2'),
        ('sentence_transformers', '2.2.2'),
        ('faiss_cpu', '1.8.0'),
        ('torch', '2.5.1'),
        ('streamlit', '1.29.0'),
        ('numpy', '1.26.2'),
        ('pydantic', '2.5.0')
    ]
    
    all_ok = True
    
    for package, expected_version in required_packages:
        try:
            # Handle package name variations
            import_name = package
            if package == 'faiss_cpu':
                import_name = 'faiss'
            elif package == 'sentence_transformers':
                import_name = 'sentence_transformers'
                
            spec = importlib.util.find_spec(import_name)
            if spec is None:
                print(f"❌ {package} - Not installed")
                all_ok = False
                continue
                
            # Try to get version
            try:
                module = importlib.import_module(import_name)
                version = getattr(module, '__version__', 'unknown')
                if version == expected_version:
                    print(f"✅ {package} {version} - Correct version")
                else:
                    print(f"⚠️  {package} {version} - Expected {expected_version}")
            except Exception:
                print(f"✅ {package} - Installed (version check failed)")
                
        except Exception as e:
            print(f"❌ {package} - Import failed: {e}")
            all_ok = False
            
    return all_ok

def check_backend_import():
    """Test backend imports"""
    try:
        sys.path.append('backend')
        from main import app, health_assistant
        print("✅ Backend imports - OK")
        print(f"✅ Health assistant initialized - {len(health_assistant.videos_data)} videos loaded")
        return True
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False

def check_frontend_import():
    """Test frontend imports"""
    try:
        sys.path.append('frontend')
        import streamlit
        print("✅ Frontend imports - OK")
        return True
    except Exception as e:
        print(f"❌ Frontend import failed: {e}")
        return False

def main():
    """Run all verification checks"""
    print("🧪 Health AI Assistant - Universal Compatibility Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("File Encoding", check_file_encoding),
        ("Dependencies", check_dependencies),
        ("Backend Import", check_backend_import),
        ("Frontend Import", check_frontend_import)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        result = check_func()
        results.append((check_name, result))
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY:")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:20s}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! The system is ready for cross-platform deployment.")
        print("\n🚀 Next Steps:")
        print("1. Run backend: python backend/main.py")
        print("2. Run frontend: streamlit run frontend/app.py")
        print("3. Or use Docker: docker-compose up --build")
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -r backend/requirements.txt")
        print("2. Check data files are present in data/ directory")
        print("3. Verify Python 3.11+ is installed")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
