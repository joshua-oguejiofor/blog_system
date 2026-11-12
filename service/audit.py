import logging

from fastapi import HTTPException
from repositories.audit_repository import AuditRepository

logger= logging.getLogger(__name__)


"""dependency injection to audit_logs allowing the needed database to come from outside
This follows the open/close principle in SOLID(no need to modify the code when database change)
Because db will not be passed into this from route we don't need db
all passage to database by repository cn be gotten from the base
"""  

class AuditService:
    def __init__(self, audit_repo: AuditRepository):
        self.audit_repo = audit_repo
        
       
    async def create_auditlog(self, audit_log: dict):
        
        return await self.audit_repo.create_object(audit_log)
        
    
    async def get_all_auditlog(self, offset: int, limit: int):
        
        audit= await self.audit_repo.get_all(offset= offset, limit= limit)
        if not audit:
            return []
        return audit
     
     
    async def get_auditlog_by_id(self, audit_id: int):
        
        audit= await  self.audit_repo.get_by_model_id(audit_id)
        if not audit:
            raise HTTPException(status_code=404, detail="Audit log not found")
        return audit
     
     
    async def delete(self, audit_id: int):
        
        db_audit= await self.get_auditlog_by_id(audit_id)
        
        return await self.audit_repo.delete_object(db_audit)
        
        
        
    
     
     
     
     
        