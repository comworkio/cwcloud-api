from datetime import datetime
from urllib.error import HTTPError
from entities.SupportTicket import SupportTicket
from entities.SupportTicketLog import SupportTicketLog
from entities.User import User
from utils.common import is_not_empty, is_not_numeric, is_numeric
from utils.gitlab import add_gitlab_issue, add_gitlab_issue_comment, close_gitlab_issue, reopen_gitlab_issue
from utils.encoder import AlchemyEncoder
import json
from fastapi.responses import JSONResponse
from utils.logger import log_msg
from utils.mail import send_reply_to_customer_email
from utils.observability.cid import get_current_cid

def get_support_tickets(current_user, db):
    from entities.SupportTicket import SupportTicket
    supportTickets = SupportTicket.getAllSupportTickets(db)
    supportTicketsJson = json.loads(json.dumps(supportTickets, cls = AlchemyEncoder))
    return JSONResponse(content = supportTicketsJson, status_code = 200)

def add_support_ticket(current_user, payload, db):
    try:
        user = User.getUserByEmail(payload.email, db)
        if not user:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'user not found',
                'i18n_code': 'user_not_found',
                'cid': get_current_cid()
            }, status_code = 404)

        if payload.severity not in ["low", "medium", "high"]:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'severity needs to be low, medium or high',
                'cid': get_current_cid()
            }, status_code = 400)

        log_msg("INFO", "[Admin Support] Admin {} has opened a new support ticket for User {} with severity {}".format(current_user.email, user.email, payload.severity))

        dticket = payload.dict()
        dticket.pop('email')
        dticket['selected_product'] = payload.product
        del dticket['product']

        ticket = SupportTicket(**dticket)
        ticket.user_id = user.id
        ticket.gitlab_issue_id = None
        ticket.created_at = datetime.now().isoformat()
        ticket.last_update = datetime.now().isoformat()
        ticket.save(db)
        issue_id = add_gitlab_issue(ticket.id, payload.email, payload.subject, payload.message, payload.severity, payload.product)
        SupportTicket.attach_gitlab_issue(ticket.id, issue_id, db)
        ticket.gitlab_issue_id = issue_id
        ticket.save(db)
        supportTicketJson = json.loads(json.dumps(ticket, cls = AlchemyEncoder))
        supportTicketJson["id"] = ticket.id
        return JSONResponse(content = supportTicketJson, status_code = 201)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg, 
            'i18n_code': e.headers['i18n_code'],
            'cid': get_current_cid()
        }, status_code = e.code)

def get_support_ticket(current_user, ticket_id, db):
    if not is_numeric(ticket_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid ticket id', 
            'i18n_code': 'invalid_payment_method_id',
            'cid': get_current_cid()
        }, status_code = 400)

    from entities.SupportTicket import SupportTicket
    supportTicket = SupportTicket.getSupportTicket(ticket_id, db)
    if not supportTicket:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'ticket not found',
            'cid': get_current_cid()
        }, status_code = 404)

    from entities.SupportTicketLog import SupportTicketLog
    ticket_replies = SupportTicketLog.getTicketLogs(ticket_id, db)
    supportTicketsJson = json.loads(json.dumps(supportTicket, cls = AlchemyEncoder))
    userSupportTicketJson = json.loads(json.dumps(supportTicket.user, cls = AlchemyEncoder))
    supportTicketsResult = {**supportTicketsJson, 'user':userSupportTicketJson}
    supportTicketRepliesJson = []
    for ticket in ticket_replies:
        ticketJson = json.loads(json.dumps(ticket, cls = AlchemyEncoder))
        userJson = json.loads(json.dumps(ticket.user, cls = AlchemyEncoder))
        supportTicketRepliesJson.append({**ticketJson, 'user':userJson})

    supportTickerResponse = {**supportTicketsResult, 'replies':supportTicketRepliesJson}
    return JSONResponse(content = supportTickerResponse, status_code = 200)

def delete_support_ticket(current_user, ticket_id, db):
    if not is_numeric(ticket_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid ticket id', 
            'i18n_code': 'invalid_payment_method_id',
            'cid': get_current_cid()
        }, status_code = 400)

    from entities.SupportTicket import SupportTicket
    supportTicket = SupportTicket.getSupportTicket(ticket_id, db)
    if not supportTicket:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'ticket not found',
            'cid': get_current_cid()
        }, status_code = 404)
    close_gitlab_issue(supportTicket.gitlab_issue_id)
    SupportTicket.deleteOne(ticket_id, db)
    from entities.SupportTicketLog import SupportTicketLog
    SupportTicketLog.deleteTicketReplies(ticket_id, db)
    return JSONResponse(content = {
        'status': 'ok',
        'message': 'ticket successfully deleted'
    }, status_code = 200)

def reply_support_ticket(current_user, ticket_id, payload, db):
    try:
        message = payload.message
        status = payload.status
        if not is_numeric(ticket_id):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Invalid ticket id', 
                'i18n_code': 'invalid_payment_method_id',
                'cid': get_current_cid()
            }, status_code = 400)

        from entities.SupportTicket import SupportTicket
        from entities.SupportTicketLog import SupportTicketLog
        ticket = SupportTicket.getSupportTicket(ticket_id, db)
        if not ticket:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'ticket not found',
                'cid': get_current_cid()
            }, status_code = 404)

        if status == 'closed':
            close_gitlab_issue(ticket.gitlab_issue_id)
        else:
            if ticket.status == 'closed':
                reopen_gitlab_issue(ticket.gitlab_issue_id)
        SupportTicket.updateTicketStatus(ticket.id, status, db)
        if is_not_empty(message):
            new_reply = SupportTicketLog()
            new_reply.user_id = current_user.id
            new_reply.ticket_id = ticket.id
            new_reply.message = message
            new_reply.status = status
            new_reply.is_admin = True
            new_reply.creation_date = datetime.now().isoformat()
            new_reply.change_date = datetime.now().isoformat()
            new_reply.save(db)
            supportTicketReplyJson = json.loads(json.dumps(new_reply, cls = AlchemyEncoder))
            userJson = json.loads(json.dumps(new_reply.user, cls = AlchemyEncoder))
            supportTicketReply = {**supportTicketReplyJson, 'user':userJson}
            add_gitlab_issue_comment(ticket.gitlab_issue_id, current_user.email, message)
            SupportTicket.updateTicketTime(ticket.id, db)
            customer_email = User.getUserById(ticket.user_id, db).email
            send_reply_to_customer_email(customer_email, ticket.subject, new_reply.message)
            return JSONResponse(content = {"reply": supportTicketReply}, status_code = 200)
        return JSONResponse(content = {
            'status': 'ok',
            'message': 'successfully updated ticket status'
        }, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg, 
            'i18n_code': e.headers['i18n_code'],
            'cid': get_current_cid()
        }, status_code = e.code)
    
def update_reply_support_ticket(current_user, ticket_id, reply_id, payload, db):
    try:
        if is_not_numeric(ticket_id) or is_not_numeric(reply_id):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Invalid ticket id or reply id',
                'i18n_code': 'invalid_payment_method_id',
                'cid': get_current_cid()
            }, status_code = 400)

        ticket = SupportTicket.getSupportTicket(ticket_id, db)
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
        update_message = "\n__User:___{}\n__Updated message:__\n{}".format(current_user.email, payload.message)
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
                'i18n_code': 'invalid_payment_method_id',
                'cid': get_current_cid()
            }, status_code = 400)

        ticket = SupportTicket.getSupportTicket(ticket_id, db)
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
    
def update_support_ticket(current_user, ticket_id, payload, db):
    try:
        if is_not_numeric(ticket_id):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Invalid ticket id',
                'i18n_code': 'invalid_payment_method_id',
                'cid': get_current_cid()
            }, status_code = 400)

        ticket = SupportTicket.getSupportTicket(ticket_id, db)
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
        update_message = "\n__User:___{}\n__Updated description:__\n{}".format(current_user.email, payload.message)
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
