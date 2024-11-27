from enum import Enum

class Department(str, Enum):
    CREW = "Crew"
    MAINTENANCE = "Maintenance"