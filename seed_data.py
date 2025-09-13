#!/usr/bin/env python3
"""
Manual database seeding script for EventSphere.

This script seeds the database with:
- Roles (Admin, Organizer, Participant, Visitor)
- Admin user (admin@admin.com / admin123)
- Event categories
- Organizer user (organizer@example.com / organizer123)
- Sample events

Usage:
    python seed_data.py
"""

from app import create_app
from app.seed import (
    seed_roles,
    seed_admin_user,
    seed_event_categories,
    seed_organizer_user,
    seed_sample_events
)
from app.logging import log_event

def main():
    """Main seeding function."""
    print("🚀 Starting EventSphere Database Seeding...")

    # Create Flask app
    app = create_app()

    with app.app_context():
        print("📋 Seeding roles...")
        seed_roles()

        print("👑 Seeding admin user...")
        seed_admin_user()

        print("📂 Seeding event categories...")
        seed_event_categories()

        print("🎭 Seeding organizer user...")
        seed_organizer_user()

        print("🎪 Seeding sample events...")
        seed_sample_events()

    print("✅ Database seeding completed successfully!")
    print("\n📝 Default Credentials:")
    print("   Admin: admin@admin.com / admin123")
    print("   Organizer: organizer@example.com / organizer123")
    print("\n🎯 Sample Events Created:")
    print("   - Python Workshop 2024")
    print("   - AI & Machine Learning Conference")
    print("   - Cultural Festival 2024")
    print("   - Web Development Bootcamp")

if __name__ == "__main__":
    main()

