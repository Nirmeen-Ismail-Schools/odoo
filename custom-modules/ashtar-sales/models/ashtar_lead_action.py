from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class ActionLead(models.Model):
    _name = "ashtar.lead.action"
    _description = "Lead action"
    _order = "id desc"

    lead_id = fields.Many2one("ashtar.lead", string="Lead")
    # make a field action_type with selection: meeting, call, whatsapp, mail, other and default value = call
    action_type = fields.Selection(
        string="Action Type",
        selection=[("meeting", "Meeting"), ("call", "Call"), ("whatsapp", "Whatsapp"), ("mail", "Mail"), ("other", "Other")],
        default="call",
        copy=False,
    )
    duedate = fields.Date(required=True, default=fields.Date.today())
    assignee = fields.Many2one("res.users", string="Assignee", default=lambda self: self.env.user)
    status = fields.Selection(
        string="Status",
        selection=[("new", "New"), 
            ("in_progress", "In Progress"),
            ("done", "Done")],
        default="new",
        copy=False,
        compute="_compute_status",
        store=True,
    )
    result = fields.Selection(
        string="Result",
        selection=[("no_answer", "No Answer"),
            ("interrested", "interested"), 
            ("not_interrested", "Not interested"), 
            ("follow_up", "Follow up"), 
            ("meeting", "Meeting"), 
            ("signed", "Signed"),
            ("canceled", "Canceled")],
        default=False,
        copy=False,
    )
    # make a field comments one to many relation to ashtar.lead.action.comment
    comments = fields.One2many("ashtar.lead.action.comment", "action_id", string="Comments")
    name = fields.Char(required=True)
    is_current = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if len(self.lead_id.actions) > 0:
            self.lead_id.actions[0].is_current = False
        return super().create(vals)

    def _handle_automation(self, vals):
        res = super().create(vals)
        if self.status == "done" and self.action_type == "call":
            self.lead_id.last_followup_date = self.create_date if self.create_date else fields.Date.today()
            # get current user_id and put into variable
            #self.result = "followup" if self.result != "signed" and self.result != "canceled" else self.result
            print (self.result)
            self.lead_id.is_meeting_scheduled = self.result == "meeting_scheduled"
            #calculate followup_incremental to be the days between next_call_at and last_followup_date
            self.lead_id.followup_incremental = False if not self.next_call_at else (self.next_call_at - (self.last_followup_date if self.last_followup_date else fields.Date.today())).days
            print (self.result != "canceled")
            print (self.result)
            self.lead_id.active = self.result != "canceled"
            duedate = self._compute_duedate(self)
            if duedate:
                self.actions = [duedate]
        return res

    @api.depends("result")
    def _compute_status(self):
        for rec in self:
            rec.status = "done" if rec.result else "new"