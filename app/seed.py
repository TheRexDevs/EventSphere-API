from flask import Flask, current_app, url_for
from slugify import slugify
from sqlalchemy import inspect

from .extensions import db
from .models.user import AppUser, Profile, Address
from .models.wallet import Wallet
from .models.role import Role, UserRole
from .models.event import Event, EventCategory
from .models.registration import Registration
from .models.attendance import Attendance
from .logging import log_event
from .utils.date_time import DateTimeUtils

from .enums.auth import RoleNames

def seed_admin_user(clear: bool = False) -> None:
    """
    Seed the database with default Admin User.
    Args:
        clear (bool): If True, Clear existing admin before seeding.
    """
    
    if inspect(db.engine).has_table("role"):
        admin_role = Role.query.filter_by(name=RoleNames.ADMIN).first()
        if not admin_role:
            admin_role = Role()
            admin_role.name = RoleNames.ADMIN
            admin_role.slug = slugify(RoleNames.ADMIN.value)
            db.session.add(admin_role)
            db.session.commit()
    
    if inspect(db.engine).has_table("app_user"):
        admin = (
            AppUser.query
            .join(UserRole, AppUser.id == UserRole.app_user_id)
            .join(Role, UserRole.role_id == Role.id)
            .filter(Role.name == RoleNames.ADMIN)
            .first()
        )

        if clear and admin:
            admin.delete()
            db.session.close()
            log_event("Admin deleted successfully")
            return

        if not admin:
            admin_user = AppUser()
            admin_user.username = current_app.config["DEFAULT_ADMIN_USERNAME"]
            admin_user.email = "admin@admin.com"
            admin_user.password = current_app.config["DEFAULT_ADMIN_PASSWORD"]

            db.session.add(admin_user)
            db.session.flush()  # ensure admin_user.id

            admin_user_profile = Profile()
            admin_user_profile.firstname = "admin"
            admin_user_profile.user_id = admin_user.id

            admin_user_address = Address()
            admin_user_address.user_id = admin_user.id

            admin_user_wallet = Wallet()
            admin_user_wallet.user_id = admin_user.id

            db.session.add_all([admin_user_profile, admin_user_address, admin_user_wallet])
            db.session.commit()

            UserRole.assign_role(admin_user, admin_role)
            log_event("Admin user created with default credentials", event_type="seeding")
        else:
            log_event("Admin user already exists", event_type="seeding")


def seed_roles(clear: bool = False) -> None:
    """Seed database with default roles if the "role" table doesn't exist.

    Args:
        clear (bool, optional): If True, clears all existing roles before seeding. (Defaults to False).
    """
    if inspect(db.engine).has_table("role"):
        if clear:
            # Clear existing roles before creating new ones
            Role.query.delete()
            db.session.commit()
        
        for role_name in RoleNames:
            if not Role.query.filter_by(name=role_name).first():
                new_role = Role()
                new_role.name = role_name
                new_role.slug = slugify(role_name.value)
                db.session.add(new_role)
        db.session.commit()


def seed_event_categories(clear: bool = False) -> None:
    """Seed database with default event categories.

    Args:
        clear (bool, optional): If True, clears all existing categories before seeding. (Defaults to False).
    """
    if inspect(db.engine).has_table("event_category"):
        if clear:
            # Clear existing categories before creating new ones
            EventCategory.query.delete()
            db.session.commit()

        default_categories = [
            {"name": "Technical", "description": "Technical workshops, hackathons, and coding events"},
            {"name": "Cultural", "description": "Cultural festivals, music, dance, and art events"},
            {"name": "Sports", "description": "Sports competitions and athletic events"},
            {"name": "Academic", "description": "Academic seminars, conferences, and educational events"},
            {"name": "Entertainment", "description": "Entertainment shows, concerts, and recreational events"},
            {"name": "Workshop", "description": "Hands-on workshops and training sessions"},
            {"name": "Seminar", "description": "Educational seminars and lectures"},
            {"name": "Competition", "description": "Competitions and contests"}
        ]

        for category_data in default_categories:
            if not EventCategory.query.filter_by(name=category_data["name"]).first():
                category = EventCategory()
                category.name = category_data["name"]
                category.description = category_data["description"]
                
                db.session.add(category)

        db.session.commit()
        log_event("Event categories seeded successfully", event_type="seeding")


def seed_organizer_user(clear: bool = False) -> None:
    """
    Seed the database with a default Organizer User.

    Args:
        clear (bool): If True, clear existing organizer before seeding.
    """
    if inspect(db.engine).has_table("role"):
        organizer_role = Role.query.filter_by(name=RoleNames.ORGANIZER).first()
        if not organizer_role:
            organizer_role = Role()
            organizer_role.name = RoleNames.ORGANIZER
            organizer_role.slug = slugify(RoleNames.ORGANIZER.value)
            db.session.add(organizer_role)
            db.session.commit()

    if inspect(db.engine).has_table("app_user"):
        organizer = (
            AppUser.query
            .join(UserRole, AppUser.id == UserRole.app_user_id)
            .join(Role, UserRole.role_id == Role.id)
            .filter(Role.name == RoleNames.ORGANIZER)
            .first()
        )

        if clear and organizer:
            organizer.delete()
            db.session.close()
            log_event("Organizer deleted successfully")
            return

        if not organizer:
            organizer_user = AppUser()
            organizer_user.username = "eventorganizer"
            organizer_user.email = "organizer@example.com"
            organizer_user.password = "organizer123"

            db.session.add(organizer_user)
            db.session.flush()  # ensure organizer_user.id

            organizer_profile = Profile()
            organizer_profile.firstname = "John"
            organizer_profile.lastname = "Doe"
            organizer_profile.user_id = organizer_user.id

            organizer_address = Address()
            organizer_address.state = "Event State"
            organizer_address.country = "Event Country"
            organizer_address.user_id = organizer_user.id

            organizer_wallet = Wallet()
            organizer_wallet.user_id = organizer_user.id

            db.session.add_all([organizer_profile, organizer_address, organizer_wallet])
            db.session.commit()

            UserRole.assign_role(organizer_user, organizer_role)
            log_event("Organizer user created with default credentials", event_type="seeding")
        else:
            log_event("Organizer user already exists", event_type="seeding")


def seed_sample_events(clear: bool = False) -> None:
    """
    Seed the database with sample events.

    Args:
        clear (bool): If True, clear existing events before seeding.
    """
    if inspect(db.engine).has_table("event"):
        if clear:
            Event.query.delete()
            db.session.commit()

        # Get organizer user
        organizer = (
            AppUser.query
            .join(UserRole, AppUser.id == UserRole.app_user_id)
            .join(Role, UserRole.role_id == Role.id)
            .filter(Role.name == RoleNames.ORGANIZER)
            .first()
        )

        if not organizer:
            log_event("No organizer found, skipping event seeding", event_type="seeding")
            return

        # Get categories
        tech_category = EventCategory.query.filter_by(name="Technical").first()
        cultural_category = EventCategory.query.filter_by(name="Cultural").first()
        workshop_category = EventCategory.query.filter_by(name="Workshop").first()

        sample_events = [
            {
                "title": "Python Workshop 2024",
                "description": "Learn Python programming from basics to advanced concepts. Perfect for beginners and intermediate developers.",
                "date": "2024-10-15",
                "time": "10:00:00",
                "venue": "Tech Hub Conference Room",
                "capacity": 50,
                "max_participants": 45,
                "category": workshop_category,
                "status": "approved"
            },
            {
                "title": "AI & Machine Learning Conference",
                "description": "Explore the latest trends in Artificial Intelligence and Machine Learning. Featuring industry experts and hands-on demos.",
                "date": "2024-11-20",
                "time": "09:00:00",
                "venue": "Grand Convention Center",
                "capacity": 200,
                "max_participants": 180,
                "category": tech_category,
                "status": "approved"
            },
            {
                "title": "Cultural Festival 2024",
                "description": "Celebrate diversity with traditional music, dance performances, and cultural exhibitions from around the world.",
                "date": "2024-12-01",
                "time": "18:00:00",
                "venue": "City Cultural Center",
                "capacity": 300,
                "max_participants": 280,
                "category": cultural_category,
                "status": "pending"
            },
            {
                "title": "Web Development Bootcamp",
                "description": "Intensive 3-day bootcamp covering modern web development technologies including React, Node.js, and cloud deployment.",
                "date": "2024-09-25",
                "time": "09:00:00",
                "venue": "Digital Skills Academy",
                "capacity": 30,
                "max_participants": 28,
                "category": workshop_category,
                "status": "approved"
            }
        ]

        for event_data in sample_events:
            # Check if event already exists
            existing_event = Event.query.filter_by(
                title=event_data["title"],
                organizer_id=organizer.id
            ).first()

            if not existing_event:
                event = Event()
                event.title = event_data["title"]
                event.description = event_data["description"]
                event.date = event_data["date"]
                event.time = event_data["time"]
                event.venue = event_data["venue"]
                event.capacity = event_data["capacity"]
                event.max_participants = event_data["max_participants"]
                event.status = event_data["status"]
                event.organizer_id = organizer.id

                if event_data["category"]:
                    event.category_id = event_data["category"].id

                db.session.add(event)

        db.session.commit()
        log_event(f"Sample events seeded successfully: {len(sample_events)} events created", event_type="seeding")


def seed_participant_user(clear: bool = False) -> None:
    """
    Seed the database with a default Participant User.

    Args:
        clear (bool): If True, clear existing participant before seeding.
    """
    if inspect(db.engine).has_table("role"):
        participant_role = Role.query.filter_by(name=RoleNames.PARTICIPANT).first()
        if not participant_role:
            participant_role = Role()
            participant_role.name = RoleNames.PARTICIPANT
            participant_role.slug = slugify(RoleNames.PARTICIPANT.value)
            db.session.add(participant_role)
            db.session.commit()

    if inspect(db.engine).has_table("app_user"):
        participant = (
            AppUser.query
            .join(UserRole, AppUser.id == UserRole.app_user_id)
            .join(Role, UserRole.role_id == Role.id)
            .filter(Role.name == RoleNames.PARTICIPANT)
            .first()
        )

        if clear and participant:
            participant.delete()
            db.session.close()
            log_event("Participant deleted successfully")
            return

        if not participant:
            participant_user = AppUser()
            participant_user.username = "participant"
            participant_user.email = "participant@example.com"
            participant_user.password = "participant123"

            db.session.add(participant_user)
            db.session.flush()  # ensure participant_user.id

            participant_profile = Profile()
            participant_profile.firstname = "Jane"
            participant_profile.lastname = "Smith"
            participant_profile.user_id = participant_user.id

            participant_address = Address()
            participant_address.state = "Participant State"
            participant_address.country = "Participant Country"
            participant_address.user_id = participant_user.id

            participant_wallet = Wallet()
            participant_wallet.user_id = participant_user.id

            db.session.add_all([participant_profile, participant_address, participant_wallet])
            db.session.commit()

            UserRole.assign_role(participant_user, participant_role)
            log_event("Participant user created with default credentials", event_type="seeding")
        else:
            log_event("Participant user already exists", event_type="seeding")


def seed_sample_registrations(clear: bool = False) -> None:
    """
    Seed the database with sample registrations and attendance for the participant user.

    Args:
        clear (bool): If True, clear existing registrations and attendance before seeding.
    """
    if inspect(db.engine).has_table("registration") and inspect(db.engine).has_table("attendance"):
        if clear:
            Attendance.query.delete()
            Registration.query.delete()
            db.session.commit()

        # Get participant user
        participant = (
            AppUser.query
            .join(UserRole, AppUser.id == UserRole.app_user_id)
            .join(Role, UserRole.role_id == Role.id)
            .filter(Role.name == RoleNames.PARTICIPANT)
            .first()
        )

        if not participant:
            log_event("No participant found, skipping registration seeding", event_type="seeding")
            return

        # Get some sample events
        events = Event.query.limit(3).all()

        if not events:
            log_event("No events found, skipping registration seeding", event_type="seeding")
            return

        sample_registrations = [
            {
                "event": events[0],
                "status": "confirmed",
                "attended": True
            },
            {
                "event": events[1] if len(events) > 1 else events[0],
                "status": "confirmed",
                "attended": False
            },
            {
                "event": events[2] if len(events) > 2 else events[0],
                "status": "pending",
                "attended": False
            }
        ]

        for reg_data in sample_registrations:
            # Check if registration already exists
            existing_reg = Registration.query.filter_by(
                event_id=reg_data["event"].id,
                student_id=participant.id
            ).first()

            if not existing_reg:
                registration = Registration()
                registration.event_id = reg_data["event"].id
                registration.student_id = participant.id
                registration.status = reg_data["status"]
                registration.registered_on = DateTimeUtils.aware_utcnow()

                db.session.add(registration)
                db.session.flush()  # ensure registration.id

                # Create attendance record if attended
                if reg_data["attended"]:
                    attendance = Attendance()
                    attendance.event_id = reg_data["event"].id
                    attendance.student_id = participant.id
                    attendance.attended = True
                    attendance.marked_on = DateTimeUtils.aware_utcnow()

                    db.session.add(attendance)

        db.session.commit()
        log_event(f"Sample registrations and attendance seeded successfully for participant: {participant.username}", event_type="seeding")


def seed_database(app: Flask) -> None:
    with app.app_context():
        seed_roles()
        seed_admin_user()
        seed_event_categories()
        seed_organizer_user()
        seed_participant_user()
        seed_sample_events()
        seed_sample_registrations()