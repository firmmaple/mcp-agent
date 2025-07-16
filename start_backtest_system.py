#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Smart Investment Backtest System - Quick Start Script

This script automatically checks dependencies and starts the backtest system web interface
"""

import sys
import os
import subprocess
import importlib.util

def check_dependencies():
    """Check required packages"""
    print("🔍 Checking system dependencies...")
    
    required_packages = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('baostock', 'baostock')
    ]
    
    missing_packages = []
    
    for package_name, display_name in required_packages:
        if importlib.util.find_spec(package_name) is None:
            missing_packages.append(display_name)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("\n🔧 Auto-installing missing dependencies...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                'Flask==3.0.0', 'Flask-CORS==4.0.0'
            ])
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Auto-installation failed, please run manually:")
            print("pip install Flask==3.0.0 Flask-CORS==4.0.0")
            return False
    else:
        print("✅ All dependencies are ready!")
    
    return True

def check_files():
    """Check if required files exist"""
    print("📁 Checking required files...")
    
    required_files = [
        'backtest_api.py',
        'backtest_system.py',
        'multi_agent_workflow.py',
        'frontend/backtest.html',
        'frontend/backtest_style.css',
        'frontend/backtest_script.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files exist!")
    
    return True

def start_server():
    """Start Flask server"""
    print("\n🚀 Starting backtest system web server...")
    print("📱 Access URL: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Import and run API server
        import backtest_api
        backtest_api.app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🎯 Smart Investment Backtest System Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check files
    if not check_files():
        return
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 