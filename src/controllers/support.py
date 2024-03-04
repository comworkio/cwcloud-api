from datetime import datetime
import json

from urllib.error import HTTPError
from fastapi.responses import JSONResponse

from entities.SupportTicket import SupportTicket

from utils.logger import log_msg
from utils.common import is_not_numeric
from utils.encoder import AlchemyEncoder
from utils.gitlab import add_gitlab_issue, add_gitlab_issue_comment

def get_support_tickets(current_user, db):
    from entities.SupportTicket import SupportTicket
    supportTickets = SupportTicket.getUserSupportTickets(current_user.id, db)
    supportTicketsJson = json.loads(json.dumps(supportTickets, cls = AlchemyEncoder))
    return JSONResponse(content = supportTicketsJson, status_code = 200)

def get_support_ticket(current_user, ticket_id, db):
    if is_not_numeric(ticket_id):
        return JSONResponse(content = {"error": "Invalid ticket id", "i18n_code": "400"}, status_code = 400)

    from entities.SupportTicket import SupportTicket
    supportTicket = SupportTicket.getUserSupportTicket(current_user.id, ticket_id, db)
    if not supportTicket:
        return JSONResponse(content = {"error": "ticket not found"}, status_code = 404)
    from entities.SupportTicketLog import SupportTicketLog
    ticket_replies = SupportTicketLog.getTicketLogs(ticket_id, db)
    supportTicketsJson = json.loads(json.dumps(supportTicket, cls = AlchemyEncoder))
    userSupportTicketJson = json.loads(json.dumps(supportTicket.user, cls = AlchemyEncoder))
    supportTicketsResult = {**supportTicketsJson, "user": userSupportTicketJson}

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
            return JSONResponse(content = {"error": "severity needs to be low, medium or high"}, status_code = 400)

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
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)

def reply_support_ticket(current_user, payload, ticket_id, db):
    try:
        if is_not_numeric(ticket_id):
            return JSONResponse(content = {"error": "Invalid ticket id", "i18n_code": "400"}, status_code = 400)
        from entities.SupportTicket import SupportTicket
        from entities.SupportTicketLog import SupportTicketLog
        ticket = SupportTicket.getUserSupportTicket(current_user.id, ticket_id, db)
        if not ticket:
            return JSONResponse(content = {"error": "ticket not found"}, status_code = 404)

        new_reply = SupportTicketLog(**payload.dict())
        new_reply.user_id = current_user.id
        new_reply.ticket_id = ticket.id
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
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)
