#!/usr/bin/env python3
"""
Test script to verify PDF Downloader setup
"""

import sys
import os
import importlib

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    required_modules = [
        'flask',
        'selenium',
        'requests',
        'fake_useragent',
        'webdriver_manager',
        'python-dotenv'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            if module == 'python-dotenv':
                importlib.import_module('dotenv')
            else:
                importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n⚠️ Failed imports: {failed_imports}")
        print("Please install missing packages: pip install -r requirements.txt")
        return False
    
    print("✅ All imports successful!")
    return True


def test_config():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import Config
        config = Config()
        
        print(f"✅ Config loaded successfully")
        print(f"   Max PDFs per keyword: {config.MAX_PDF_PER_KEYWORD}")
        print(f"   Headless mode: {config.HEADLESS_MODE}")
        print(f"   Download directory: {config.get_download_path()}")
        
        fields = config.get_fields_keywords()
        print(f"   Available fields: {len(fields)}")
        
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False


def test_pdf_downloader():
    """Test PDF downloader initialization"""
    print("\n📄 Testing PDF downloader...")
    
    try:
        from src.pdf_downloader import PDFDownloader
        from config import Config
        
        config = Config()
        downloader = PDFDownloader(config)
        
        print("✅ PDF downloader initialized successfully")
        print(f"   Download path: {downloader.download_path}")
        
        return True
    except Exception as e:
        print(f"❌ PDF downloader error: {e}")
        return False


def test_flask_app():
    """Test Flask app initialization"""
    print("\n🌐 Testing Flask app...")
    
    try:
        from app import app
        
        print("✅ Flask app initialized successfully")
        
        # Test basic routes
        with app.test_client() as client:
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ Health check endpoint working")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        return False


def test_directory_structure():
    """Test if all required directories exist"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        'src',
        'templates',
        'downloads'
    ]
    
    missing_dirs = []
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ (missing)")
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"\n⚠️ Missing directories: {missing_dirs}")
        return False
    
    return True


def test_files():
    """Test if all required files exist"""
    print("\n📄 Testing required files...")
    
    required_files = [
        'app.py',
        'config.py',
        'requirements.txt',
        'README.md',
        'src/__init__.py',
        'src/pdf_downloader.py',
        'templates/index.html'
    ]
    
    missing_files = []
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} (missing)")
            missing_files.append(file_name)
    
    if missing_files:
        print(f"\n⚠️ Missing files: {missing_files}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("🧪 PDF Downloader Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_pdf_downloader,
        test_flask_app,
        test_directory_structure,
        test_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 To start the application:")
        print("   python app.py")
        print("\n💻 To use the CLI:")
        print("   python cli.py --list-fields")
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == '__main__':
    main() 