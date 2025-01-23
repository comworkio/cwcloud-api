from datetime import datetime
import json
import os
from datetime import datetime
from urllib.error import HTTPError
from uuid import uuid4
from entities.SupportTicketAttachment import SupportTicketAttachment
from fastapi.responses import JSONResponse, FileResponse
from entities.SupportTicket import SupportTicket
from entities.SupportTicketLog import SupportTicketLog
from entities.User import User
from utils.bucket import delete_from_attachment_bucket, download_from_attachment_bucket, upload_to_attachment_bucket
from utils.logger import log_msg
from utils.common import get_env_int, is_false, is_not_numeric
from utils.encoder import AlchemyEncoder
from utils.gitlab import add_gitlab_issue, add_gitlab_issue_comment
from utils.observability.cid import get_current_cid

def get_support_tickets(current_user, db):
    supportTickets = SupportTicket.getUserSupportTickets(current_user.id, db)
    supportTicketsJson = json.loads(json.dumps(supportTickets, cls = AlchemyEncoder))
    return JSONResponse(content = supportTicketsJson, status_code = 200)

def get_support_ticket(current_user, ticket_id, db):
    if is_not_numeric(ticket_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error ': 'Invalid ticket id ', 
            'i18n_code ': 'invalid_ticket_id',
            'cid': get_current_cid()
        }, status_code = 400)

    supportTicket = SupportTicket.getUserSupportTicket(current_user.id, ticket_id, db)
    if not supportTicket:
        return JSONResponse(content = {
            'status': 'ko',
            'error ': 'ticket not found',
            'cid': get_current_cid()
        }, status_code = 404)

    ticket_replies = SupportTicketLog.getTicketLogs(ticket_id, db)
    attachments = [{
        "id": attachment.id,
        "name": attachment.name,
        "has_rights": current_user.is_admin or current_user.id == attachment.user_id
    } for attachment in SupportTicketAttachment.getAttachmentsByTicketId(ticket_id, db)]

    supportTicketsJson = json.loads(json.dumps(supportTicket, cls = AlchemyEncoder))
    userSupportTicketJson = json.loads(json.dumps(supportTicket.user, cls = AlchemyEncoder))
    supportTicketsResult = {
        **supportTicketsJson,
        "user": userSupportTicketJson,
        "attachments": attachments,
    }

    supportTicketRepliesJson = []
    for ticket in ticket_replies:
            ticketJson = json.loads(json.dumps(ticket, cls = AlchemyEncoder))
            userJson = json.loads(json.dumps(ticket.user, cls = AlchemyEncoder))
            supportTicketRepliesJson.append({**ticketJson, "user": userJson})
    supportTickerResponse = {**supportTicketsResult, "replies": supportTicketRepliesJson}
    return JSONResponse(content = supportTickerResponse, status_code = 200)

def add_support_ticket(current_user, payload, db):
    try:
        if payload.severity not in ["low", "medium", "high"]:
            return JSONResponse(content = {
                'status': 'ko',
                'error ': 'severity needs to be low, medium or high ',
                'cid': get_current_cid()
            }, status_code = 400)

        log_msg("INFO", "[Support] User {} has opened a new support ticket with severity {}".format(current_user.email, payload.severity))

        dticket = payload.dict()
        dticket['selected_product'] = payload.product
        del dticket['product']

        ticket = SupportTicket(**dticket)
        ticket.user_id = current_user.id
        ticket.gitlab_issue_id = None
        ticket.save(db)
        issue_id = add_gitlab_issue(ticket.id, current_user.email, payload.subject, payload.message, payload.severity, payload.product)
        SupportTicket.attach_gitlab_issue(ticket.id, issue_id, db)
        ticket.gitlab_issue_id = issue_id
        ticket.created_at = datetime.now().isoformat()
        ticket.last_update = datetime.now().isoformat()
        ticket.save(db)
        supportTicketJson = json.loads(json.dumps(ticket, cls = AlchemyEncoder))
        supportTicketJson["id"] = ticket.id

        return JSONResponse(content = supportTicketJson, status_code = 201)

    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error ': e.msg, 
            'i18n_code ': e.headers[ 'i18n_code '],
            'cid': get_current_cid()
        }, status_code = e.code)

def reply_support_ticket(current_user, payload, ticket_id, db):
    try:
        if is_not_numeric(ticket_id):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Invalid ticket id',
                'i18n_code': 'invalid_numeric_id',
                'cid': get_current_cid()
            }, status_code = 400)

        ticket = SupportTicket.getUserSupportTicket(current_user.id, ticket_id, db)
        if not ticket:
            return JSONResponse(content = {
                'status': 'ko',
                'error ':  'ticket not found ',
                'cid': get_current_cid()
            }, status_code = 404)

        new_reply = SupportTicketLog(**payload.dict())
        new_reply.user_id = current_user.id
        new_reply.ticket_id = ticket.id
        new_reply.creation_date = datetime.now().isoformat()
        new_reply.change_date = datetime.now().isoformat()
        new_reply.save(db)

        add_gitlab_issue_comment(ticket.gitlab_issue_id, current_user.email, payload.message)
        supportTicketReplyJson = json.loads(json.dumps(new_reply, cls = AlchemyEncoder))
        userJson = json.loads(json.dumps(new_reply.user, cls = AlchemyEncoder))
        supportTicketReply = {**supportTicketReplyJson, "user": userJson}
        SupportTicket.updateTicketStatus(ticket.id, "await agent", db)
        SupportTicket.updateTicketTime(ticket.id, db)
        log_msg("INFO", "[Support] User {} has replied to support ticket # {}".format(current_user.email, ticket.id))

        return JSONResponse(content = supportTicketReply, status_code = 200)

    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error ': e.msg, 
            'i18n_code ': e.headers[ 'i18n_code '],
            'cid': get_current_cid()
        }, status_code = e.code)
    
def update_reply_support_ticket(current_user, ticket_id, reply_id, payload, db):
    try:
        if is_not_numeric(ticket_id) or is_not_numeric(reply_id):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Invalid ticket id or reply id',
                'i18n_code': 'invalid_numeric_id',
                'cid': get_current_cid()
            }, status_code = 400)

        ticket = SupportTicket.getUserSupportTicket(current_user.id, ticket_id, db)
        if not ticket:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'ticket not found',
                'cid': get_current_cid()
            }, status_code = 404)

        reply = SupportTicketLog.getTicketLog(reply_id, db)
        if not reply:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'reply not found',
                'i18n_code': 'reply_not_found',
                'cid': get_current_cid()
            }, status_code = 404)

        if reply.user_id != current_user.id:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'You are not allowed to update this reply',
                'i18n_code': 'user_not_allowed_to_update_reply',
                'cid': get_current_cid()
            }, status_code = 403)

        SupportTicketLog.updateTicketLog(reply_id, payload.message, db)
        update_message = "_(updated message)_ {}: {}".format(current_user.email, payload.message)
        add_gitlab_issue_comment(ticket.gitlab_issue_id, current_user.email, update_message)
        log_msg("INFO", "[Support] User {} has updated support ticket reply #{}".format(current_user.email, reply.id))

        return JSONResponse(content = {
            'status': 'ok',
            'message': 'Support ticket reply updated successfully.',
            'i18n_code': 'support_ticket_updated_successfully'
        }, status_code = 200)

    except Exception as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Failed to update support ticket reply.',
            'message': str(e),
            'i18n_code': 'support_ticket_update_failed',
            'cid': get_current_cid()
        }, status_code = 500)
    
def delete_reply_support_ticket(current_user, ticket_id, reply_id, db):
    try:
        if is_not_numeric(ticket_id) or is_not_numeric(reply_id):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Invalid ticket id or reply id',
                'i18n_code': 'invalid_numeric_id',
                'cid': get_current_cid()
            }, status_code = 400)

        ticket = SupportTicket.getUserSupportTicket(current_user.id, ticket_id, db)
        if not ticket:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'ticket not found',
                'cid': get_current_cid()
            }, status_code = 404)

        reply = SupportTicketLog.getTicketLog(reply_id, db)
        if not reply:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'reply not found',
                'cid': get_current_cid()
            }, status_code = 404)

        if reply.user_id != current_user.id:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'You are not allowed to delete this reply',
                'i18n_code': 'user_not_allowed_to_delete_reply',
                'cid': get_current_cid()
            }, status_code = 403)

        deleted_message = "\n__User:___{}\n__Deleted message:__\n{}".format(current_user.email, reply.message)
        add_gitlab_issue_comment(ticket.gitlab_issue_id, current_user.email, deleted_message)
        log_msg("INFO", "[Support] User {} has deleted support ticket reply #{}".format(current_user.email, reply.id))
        SupportTicketLog.deleteTicketLog(reply_id, db)

        return JSONResponse(content = {
            'status': 'ok',
            'message': 'Support ticket reply deleted successfully.',
            'i18n_code': 'support_ticket_reply_deleted_successfully'
        }, status_code = 200)

    except Exception as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Failed to delete support ticket reply.',
            'message': str(e),
            'i18n_code': 'support_ticket_reply_delete_failed',
            'cid': get_current_cid()
        }, status_code = 500)

def auto_close_tickets(current_user, db):
    try:
        threshold_days = get_env_int('DAYS_BEFORE_CLOSURE', 7)
        inactive_tickets = SupportTicket.getInactiveSupportTickets(threshold_days, db)
      
        for ticket in inactive_tickets:
            message = "This ticket is awaiting for a customer answer since {} days, it's closed automatically.\n Feel free to reopen-it if there's still an issue and adding more context to the ticket".format(threshold_days)
            new_reply = SupportTicketLog(
                is_admin=True,
                ticket_id=ticket.id,
                message=message,
                creation_date=datetime.now().isoformat(),
                change_date=datetime.now().isoformat(),
                user_id=current_user.id
            )
            new_reply.save(db)
            SupportTicket.updateTicketStatus(ticket.id, "closed", db)
            log_msg("INFO", "[Support] Ticket {} has been automatically closed due to inactivity.".format(ticket.id))
            
        return JSONResponse(content={
            'status': 'ok',
            'message': 'Auto-closed inactive tickets successfully.'
        }, status_code=200)

    except Exception as e:
        return JSONResponse(content={
            'status': 'ko', 
            'error': 'Failed to auto-close tickets.', 
            'message': str(e),
            'cid': get_current_cid()    
        }, status_code=500)
    
def update_support_ticket(current_user, ticket_id, payload, db):
    try:
        if is_not_numeric(ticket_id):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Invalid ticket id',
                'i18n_code': 'invalid_numeric_id',
                'cid': get_current_cid()
            }, status_code = 400)

        ticket = SupportTicket.getUserSupportTicket(current_user.id, ticket_id, db)
        if not ticket:
            return JSONResponse(content = {
                'status': 'ko',
                'error ':  'ticket not found ',
                'cid': get_current_cid()
            }, status_code = 404)

        if payload.severity not in ["low", "medium", "high"]:
            return JSONResponse(content = {
                'status': 'ko',
                'error ': 'severity needs to be low, medium or high ',
                'cid': get_current_cid()
            }, status_code = 400)

        SupportTicket.updateTicket(ticket.id, payload, db)
        update_message = "_(updated description)_ {}: {}".format(current_user.email, payload.message)
        add_gitlab_issue_comment(ticket.gitlab_issue_id, current_user.email, update_message)
        log_msg("INFO", "[Support] User {} has updated support ticket #{}".format(current_user.email, ticket.id))

        return JSONResponse(content = {
            'status': 'ok',
            'message': 'Support ticket updated successfully.',
            'i18n_code': 'support_ticket_updated_successfully'
        }, status_code = 200)

    except Exception as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Failed to update support ticket.',
            'message': str(e),
            'i18n_code': 'support_ticket_update_failed',
            'cid': get_current_cid()
        }, status_code = 500)

def attach_file_to_ticket_by_id(current_user, ticket_id, files, db):
    if is_not_numeric(ticket_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid ticket id', 
            'i18n_code': 'invalid_ticket_id',
            'cid': get_current_cid()
        }, status_code = 400)
 
    if current_user.is_admin:
        ticket: SupportTicket = SupportTicket.getSupportTicket(ticket_id, db)
    else:
        ticket: SupportTicket = SupportTicket.getUserSupportTicket(current_user.id, ticket_id, db)
    if not ticket:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'ticket not found',
            'cid': get_current_cid()
        }, status_code = 404)

    if not files:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'No files attached', 
            'i18n_code': 'no_files_attached',
            'cid': get_current_cid()
        }, status_code = 400)

    for file in files:
        os.makedirs('uploaded_files', exist_ok=True)
        target_name = uuid4().__str__()
        path_file = os.path.join('uploaded_files', target_name)
        with open(path_file, "wb") as file_object:
            file_object.write(file.file.read())    
        result = upload_to_attachment_bucket(path_file, target_name)
        if is_false(result['status']):
            return JSONResponse(content = {
                'status': 'ko',
                'error': result['error'],
                'i18n_code': result['i18n_code'],
                'cid': result['cid']
            }, status_code = result['http_code'])

        SupportTicketAttachment(
            mime_type = file.content_type,
            storage_key = path_file,
            name = file.filename,
            support_ticket_id = ticket_id,
            user_id = current_user.id
        ).save(db)

    return JSONResponse(content = {
        'status': 'ok',
        'message': 'file successfully attached',
        'i18n_code': 'file_attached_successfully'
    }, status_code = 200)
    
def download_file_from_ticket_by_id(current_user, ticket_id, attachment_id, db):
    if is_not_numeric(ticket_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid ticket id', 
            'i18n_code': 'invalid_ticket_id',
            'cid': get_current_cid()
        }, status_code = 400)
    
    if current_user.is_admin:
        ticket: SupportTicket = SupportTicket.getSupportTicket(ticket_id, db)
    else:
        ticket: SupportTicket = SupportTicket.getUserSupportTicket(current_user.id, ticket_id, db)
    
    if not ticket:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'ticket not found',
            'cid': get_current_cid()
        }, status_code = 404)

    attachment: SupportTicketAttachment = SupportTicketAttachment.getAttachmentByTicketId(ticket_id, attachment_id, db)

    if not attachment:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Attachment not found',
            'i18n_code': 'attachment_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    
    target_name = attachment.name
    path_file = attachment.storage_key

    result = download_from_attachment_bucket(path_file, target_name)
    if is_false(result['status']):
        return JSONResponse(content = {
            'status': 'ko',
            'error': result['error'],
            'i18n_code': result['i18n_code'],
            'cid': result['cid']
        }, status_code = result['http_code'])

    return FileResponse(target_name, filename = target_name)

def delete_file_from_ticket_by_id(current_user: User, ticket_id, attachment_id, db):
    if is_not_numeric(ticket_id):
        return JSONResponse(content={
            'status': 'ko',
            'error': 'Invalid ticket id',
            'i18n_code': 'invalid_ticket_id',
            'cid': get_current_cid()
        }, status_code=400)

    attachment: SupportTicketAttachment = SupportTicketAttachment.getAttachmentByTicketId(ticket_id, attachment_id, db)
    if attachment is None:
        return JSONResponse(content={
            'status': 'ko',
            'error': 'Attachment not found',
            'i18n_code': 'attachment_not_found',
            'cid': get_current_cid()
        }, status_code=404)

    if not current_user.is_admin and attachment.user_id != current_user.id:
        return JSONResponse(content={
            'status': 'ko',
            'error': 'You are not allowed to delete this attachment',
            'i18n_code': 'no_privilege',
            'cid': get_current_cid()
        }, status_code=403)

    SupportTicketAttachment.deleteAttachmentById(attachment.id, db)
    result = delete_from_attachment_bucket(attachment.storage_key)
    if is_false(result['status']):
        return JSONResponse(content = {
            'status': 'ko',
            'error': result['error'],
            'i18n_code': result['i18n_code'],
            'cid': result['cid']
        }, status_code = result['http_code'])

    return JSONResponse(content={
        'status': 'ok',
        'message': 'file successfully deleted',
        'i18n_code': 'file_deleted_successfully'
    }, status_code=200)
