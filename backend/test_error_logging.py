#!/usr/bin/env python3
"""
Simple test script to demonstrate error logging functionality.
"""
import requests
import json
from datetime import datetime


def test_error_logging():
    """Test the error logging functionality."""
    base_url = "http://localhost:3001"
    
    print("🧪 Testing Error Logging Functionality")
    print("=" * 50)
    
    # Test 1: Make some API calls to generate logs
    print("\n1. Making API calls to generate logs...")
    
    # Successful calls
    requests.get(f"{base_url}/api/health")
    requests.get(f"{base_url}/api/categories")
    requests.get(f"{base_url}/api/links")
    
    # Error calls
    requests.get(f"{base_url}/api/nonexistent")  # 404
    requests.post(f"{base_url}/api/categories", json={})  # 400
    requests.get(f"{base_url}/api/categories/99999")  # 404
    
    print("✅ API calls completed")
    
    # Test 2: View error logs
    print("\n2. Viewing error logs...")
    response = requests.get(f"{base_url}/api/errors")
    
    if response.status_code == 200:
        data = response.json()
        logs = data['data']['errors']
        total = data['data']['total']
        
        print(f"📊 Total logs: {total}")
        print(f"📄 Recent logs: {len(logs)}")
        
        for log in logs[:5]:  # Show first 5 logs
            print(f"  - {log['method']} {log['endpoint']} → {log['status_code']} ({log['duration_ms']}ms)")
    else:
        print(f"❌ Failed to get error logs: {response.status_code}")
    
    # Test 3: Get error statistics
    print("\n3. Getting error statistics...")
    response = requests.get(f"{base_url}/api/errors/statistics")
    
    if response.status_code == 200:
        data = response.json()
        stats = data['data']
        
        print(f"📈 Total requests: {stats['total_requests']}")
        print(f"📊 Status codes: {stats['status_code_counts']}")
        print(f"🔧 Methods: {stats['method_counts']}")
        print(f"⏱️  Avg response time: {stats['average_response_time_ms']:.2f}ms")
    else:
        print(f"❌ Failed to get statistics: {response.status_code}")
    
    # Test 4: Filter logs by status code
    print("\n4. Filtering logs by status code...")
    response = requests.get(f"{base_url}/api/errors?status_code=404")
    
    if response.status_code == 200:
        data = response.json()
        error_logs = data['data']['errors']
        print(f"🔍 Found {len(error_logs)} logs with status code 404")
        
        for log in error_logs:
            print(f"  - {log['method']} {log['endpoint']} → {log['error_message']}")
    else:
        print(f"❌ Failed to filter logs: {response.status_code}")
    
    # Test 5: Export logs
    print("\n5. Exporting logs...")
    response = requests.get(f"{base_url}/api/errors/export?limit=10")
    
    if response.status_code == 200:
        data = response.json()
        export_info = data['data']['export_info']
        logs = data['data']['errors']
        
        print(f"📤 Export info: {export_info['total_records']} records")
        print(f"📅 Export date: {export_info['export_date']}")
        print(f"📄 Exported {len(logs)} logs")
    else:
        print(f"❌ Failed to export logs: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 Error logging test completed!")


if __name__ == "__main__":
    test_error_logging() 