from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class FollowupLead(models.Model):
    _name = "ashtar.lead.followup"
    _description = "Lead Followup"
    _order = "id desc"

    lead_id = fields.Many2one("ashtar.lead", string="Lead")
    status = fields.Selection(
        string="Status",
        selection=[("no_answer", "No Answer"), 
            ("meeting_scheduled", "Meeting Scheduled"), 
            ("not_interrested", "Not Interrested"), 
            ("signed", "Signed"),
            ("canceled", "Canceled")],
        default="no_answer",
        copy=False,
    )
    # add next_call_at field to be computed based on status
    next_call_at = fields.Date(compute="_compute_next_call_at", inverse="_inverse", store=True)
    notes = fields.Text()

    @api.depends("status")
    def _compute_next_call_at(self):
        for rec in self:
            if rec.status == "no_answer" and rec.lead_id.is_meeting_scheduled:
                # get today date and put into variable
                rec.next_call_at = (rec.create_date if rec.create_date else fields.Date.today()) + relativedelta(days=1)
            elif rec.status == "no_answer":
                days=(7 if rec.lead_id.followup_incremental < 7 else rec.lead_id.followup_incremental*2)
                print("===================================== no_answer")
                print(days)
                rec.next_call_at = (rec.create_date if rec.create_date else fields.Date.today()) + relativedelta(days=days)
            elif rec.status == "not_interrested":
                days=(60 if rec.lead_id.followup_incremental < 60 or rec.lead_id.followup_incremental%7 == 0 else rec.lead_id.followup_incremental*2)
                print("===================================== not_interrested")
                print(days)
                rec.next_call_at = (rec.create_date if rec.create_date else fields.Date.today()) + relativedelta(days=days)
            else:
                rec.next_call_at = False

    def _inverse(self):
        return True

    # set sql constraint to make sure that next_call_at is required when status is not signed
    _sql_constraints = [
        ('next_call_at_required', 'CHECK(next_call_at IS NOT NULL OR status = \'signed\' OR status = \'canceled\')', "Next Call At is required when status is not signed!"),
    ]