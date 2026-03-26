#!/usr/bin/env python
"""
Simple example: Run MockDetector manually

This script demonstrates how to:
1. Create a DetectionRequest with sample fields
2. Instantiate MockDetector
3. Call detect() to get results
4. Print the DetectionResponse

Usage:
    python examples/run_mock_detector.py
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


from signature_detection.models import DetectionRequest, PDFDocument, PDFPage
from signature_detection.detectors.mock import MockDetector



# Add src to path so we can import signature_detection



def main():
    print("=" * 70)
    print("MockDetector Example - Manual Run")
    print("=" * 70)

    # Step 1: Create a sample PDF document
    print("\n1. Creating sample PDF document...")
    doc = PDFDocument(
        pages=[
            PDFPage(number=1, width=800, height=600, objects=[]),
            PDFPage(number=2, width=800, height=600, objects=[])
        ],
        metadata={"filename": "sample.pdf", "author": "Example"}
    )
    print(f"   ✓ Document created with {len(doc.pages)} pages")

    # Step 2: Create a detection request with multiple field types
    print("\n2. Creating DetectionRequest with fields to detect...")
    fields = [
        "signature_field_1",      # Should detect as present (0.90-1.0)
        "signature_field_2",      # Should detect as present (0.90-1.0)
        "signature_void",         # Should detect as absent (0.93-1.0)
        "initials",               # Should detect as present (0.80-0.90)
        "initials_authorized",    # Should detect as present (0.80-0.90)
        "unknown_field",          # Should detect as uncertain (0.45-0.55)
        "random_data"             # Should detect as uncertain (0.45-0.55)
    ]

    request = DetectionRequest(document=doc, fields=fields)
    print(f"   ✓ Request created with {len(fields)} fields to detect")
    print(f"   Fields: {', '.join(fields)}")

    # Step 3: Create detector and run detection
    print("\n3. Running MockDetector.detect()...")
    detector = MockDetector()
    response = detector.detect(request)
    print(f"   ✓ Detection complete in {response.processing_time_ms}ms")

    # Step 4: Display results
    print("\n4. Detection Results:")
    print("-" * 70)
    print(f"{'Field Name':<25} {'Status':<12} {'Confidence':<12} {'Pattern':<15}")
    print("-" * 70)

    for result in response.results:
        pattern = result.metadata.get("pattern", "unknown")
        print(
            f"{result.field_name:<25} "
            f"{result.status:<12} "
            f"{result.confidence:<12.2f} "
            f"{pattern:<15}"
        )

    # Step 5: Summary statistics
    print("-" * 70)
    print(f"\nSummary:")
    print(f"  Total results: {len(response.results)}")

    present_count = sum(1 for r in response.results if r.status == "present")
    absent_count = sum(1 for r in response.results if r.status == "absent")
    uncertain_count = sum(
        1 for r in response.results if r.status == "uncertain")

    print(f"  Present:    {present_count}")
    print(f"  Absent:     {absent_count}")
    print(f"  Uncertain:  {uncertain_count}")

    avg_confidence = sum(
        r.confidence for r in response.results) / len(response.results)
    print(f"  Avg Confidence: {avg_confidence:.2f}")

    print("\n" + "=" * 70)
    print("✅ Example complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
