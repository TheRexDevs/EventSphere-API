from enum import Enum


class RoleNames(Enum):
    """ENUMS for the name filed in Role Model"""
    ADMIN = "Admin"
    MANAGER = "Manager"
    CREATOR = "Creator"
    CUSTOMER = "Customer"
    
    @classmethod
    def get_member_by_value(cls, value):
        return next((member for name, member in cls.__members__.items() if member.value == value), None)