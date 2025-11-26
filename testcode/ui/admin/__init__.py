# Admin UI module
from . import manage_doctors
from . import manage_patients
from . import manage_appointments
from . import manage_medicines
from . import manage_users
from . import manage_invoices
from . import reports

__all__ = [
    'manage_doctors',
    'manage_patients', 
    'manage_appointments',
    'manage_medicines',
    'manage_users',
    'manage_invoices',
    'reports'
]
