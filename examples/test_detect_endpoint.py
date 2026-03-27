"""
Test Script: POST /detect Endpoint

Run this to test the minimal POST /detect endpoint.
Shows JSON request/response format.
"""

import json
import subprocess
import time
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))  # Add project root


def test_endpoint_with_curl():
    """Test the endpoint using curl."""
    print("\n" + "=" * 70)
    print("POST /detect Endpoint Test")
    print("=" * 70)

    # Request payload
    payload = {
        "fields": ["signature_field_1", "signature_void", "initials"]
    }

    print("\nREQUEST:")
    print(f"   POST http://localhost:8000/api/v1/detect")
    print(f"   Content-Type: application/json")
    print(f"\n   Body:")
    print(f"   {json.dumps(payload, indent=6)}")

    # Note: This would require server running
    print("\n[NOTE] Server must be running:")
    print("   python api/main.py")
    print("\n   Or in another terminal:")
    print(f"   curl -X POST http://localhost:8000/api/v1/detect \\")
    print(f"        -H 'Content-Type: application/json' \\")
    print(f"        -d '{json.dumps(payload)}'")


def test_endpoint_direct():
    """Test the endpoint directly without HTTP (local testing)."""
    print("\n" + "=" * 70)
    print("Direct Endpoint Test (No Server)")
    print("=" * 70)

    try:
        # Import the handler
        from api.routes.detect import detect_signatures
        import asyncio

        # Test payload
        payload = {
            "fields": ["signature_field_1", "signature_void", "initials"]
        }

        print("\nREQUEST:")
        print(f"   Fields: {payload['fields']}")

        # Call endpoint directly
        print("\nCalling endpoint...")
        response = asyncio.run(detect_signatures(payload))

        # Show response
        print("\nRESPONSE (200 OK):")
        print(json.dumps(response, indent=2))

        # Parse results
        print("\nRESULTS SUMMARY:")
        print(f"   Total detections: {len(response['results'])}")
        print(f"   Processing time: {response['processing_time_ms']}ms")
        print()

        for result in response['results']:
            status_emoji = {
                "present": "[OK]",
                "absent": "[X]",
                "uncertain": "[?]"
            }.get(result['status'], "[?]")

            print(f"   {status_emoji} {result['field_name']:<20} | "
                  f"Status: {result['status']:<10} | "
                  f"Confidence: {result['confidence']:.2f}")

        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("MINIMAL POST /DETECT ENDPOINT - TEST GUIDE")
    print("=" * 70)

    # Show API documentation
    print("""
ENDPOINT DOCUMENTATION:

    URL:     POST /api/v1/detect
    Purpose: Detect signature fields in a document
    
    Request:
        {
            "fields": ["field_name_1", "field_name_2", ...]
        }
    
    Response:
        {
            "results": [
                {
                    "field_name": "field_name_1",
                    "status": "present|absent|uncertain",
                    "confidence": 0.0-1.0,
                    "metadata": {}
                }
            ],
            "processing_time_ms": 5
        }

    Field Name Patterns:
        - "signature_*" -> detected as present (0.90-1.0 confidence)
        - "signature_void" -> detected as absent (0.93-1.0 confidence)
        - "initials*" -> detected as present (0.80-0.90 confidence)
        - anything else -> detected as uncertain (0.45-0.55 confidence)
""")

    print("\nTEST OPTIONS:\n")

    print("Option 1: Direct Python (No Server)")
    print("-" * 70)
    if test_endpoint_direct():
        print("\n[OK] Direct test passed!")
    else:
        print("\n[FAIL] Direct test failed!")

    print("\n" + "=" * 70)
    print("\nOption 2: HTTP Server (With cURL)")
    print("-" * 70)
    test_endpoint_with_curl()

    print("\n" + "=" * 70)
