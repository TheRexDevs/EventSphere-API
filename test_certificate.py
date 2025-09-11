#!/usr/bin/env python3
"""
Test Certificate Generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.certificate_generator import certificate_generator
import uuid
from datetime import datetime

# Test data
certificate_id = uuid.uuid4()
event_data = {
    'title': 'Tech Workshop 2024',
    'date': '2024-09-15',
    'organizer': {'username': 'Tech Club'}
}

student_data = {
    'username': 'john_doe',
    'full_name': 'John Doe'
}

issued_date = datetime.now()

print("Generating test certificate...")
try:
    certificate_url = certificate_generator.generate_certificate(
        certificate_id=certificate_id,
        event_data=event_data,
        student_data=student_data,
        issued_date=issued_date
    )
    print(f"✅ Certificate generated successfully: {certificate_url}")
    print(f"Certificate ID: {certificate_id}")
except Exception as e:
    print(f"❌ Error generating certificate: {e}")
