from fastapi import APIRouter, Depends
from models.user import User
from schemas.auditlog import AduitResponse
from service.audit import AuditService
from utility.dependency import admin_required, get_audit_service

router= APIRouter()



@router.get('/', status_code= 200, response_model=AduitResponse)
async def view_all(
    offset: int= 0,
    limit: int= 20,
    current_user: User= Depends(admin_required),
    audit_service: AuditService= Depends(get_audit_service)
):
    return await audit_service.get_all_auditlog(offset= offset, limit= limit)


@router.get('/{audit_id}', status_code= 200, response_model=AduitResponse)
async def view_audit(
    audit_id: int,
    current_user: User= Depends(admin_required),
    audit_service: AuditService= Depends(get_audit_service)
):
    return await audit_service.get_auditlog_by_id(audit_id= audit_id)



@router.delete('/{audit_id}', status_code= 204)
async def delete_audit(
    audit_id: int,
    current_user: User= Depends(admin_required),
    audit_service: AuditService= Depends(get_audit_service)
):
    return await audit_service.delete(audit_id= audit_id)



    