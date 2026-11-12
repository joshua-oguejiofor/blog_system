from models.auditlog import AuditLog
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository

"""This tell type checkers at base repo the this repo is for AuditLogs
This method specify the actual model in the repository when communicating to base repo"""

class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(AuditLog, db)
        
       