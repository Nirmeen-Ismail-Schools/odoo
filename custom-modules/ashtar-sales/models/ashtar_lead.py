from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class Lead(models.Model):
    _name = "ashtar.lead"
    _description = "Lead"
    _order = "id desc"

    name = fields.Char(required=True, translate=True)
    picture = fields.Binary()
    active = fields.Boolean(default=True)
    state = fields.Selection(
        string="State",
        selection=[("new", "New"), ("followup", "Follow up"), ('answered', 'Answered'), ('met', 'Met'), ("signed", "Signed"), ("canceled", "Canceled")],
        default="new",
        copy=False,
        store=True,
        compute="_compute_state"
    )
    status = fields.Selection(
        string="Status",
        selection=[("new", "New"), ("won", "Won"), ("junk", "Junk"), ("lost", "Lost"), ("lost_to_competition", "Lost to competition")],
        default="new",
        copy=False,
        required=True
    )
    channel = fields.Selection(
        string="Channel",
        selection=[("marketing", "Marketing"), ("referral", "Referral")],
        default="marketing",
        copy=False,
        required=True
    )
    city = fields.Many2one("ashtar.city", string="City")
    city_manager_id = fields.Many2one("res.users", string="City Manager", related="city.manager_id")
    # make a field lead_actions with one to many relation to ashtar.lead.action
    #lead_actions = fields.One2many("ashtar.lead.action", "lead_id", string="Lead Actions")
    is_meeting_scheduled = fields.Boolean(default=False)
    is_met = fields.Boolean(default=False, string="Met")
    last_followup_date = fields.Date(copy=False, default=fields.Date.today())
    followup_incremental = fields.Integer(default=1, copy=False)
    phone = fields.Char()
    email = fields.Char()
    lead_owner = fields.Many2one("res.users", string="Lead Owner", copy=False)
    followup_history = fields.One2many("ashtar.lead.followup", "lead_id", string="Follow up history")
    # add next_call_at field with default value = today + 7 days
    next_call_at = fields.Date()
    actions = fields.One2many("ashtar.lead.action", "lead_id", string="Actions")
    subjects = fields.Many2many("ashtar.lead.subject", string="Subjects")
    subject = fields.Char(store=False, compute="_get_first_subject")
    edu_stage = fields.Many2one("ashtar.lead.stage", string="Educational Stage")
    num_of_students = fields.Char()
    facebook_page = fields.Char()
    notes = fields.Text()
    contract_value = fields.Float(default=0.0, required=True)
    whatsapp = fields.Char(store=False, compute="_compute_whats")

    # make a map between action result and lead state
    _action_result_state_map = {
        "no_answer": "followup",
        "meeting_scheduled": "followup",
        "not_interrested": "followup",
        "signed": "signed",
        "canceled": "canceled",
    }

    def _compute_whats(self):
        for rec in self:
            rec.whatsapp = "wa.me/" + rec.phone if rec.phone else ""

    def _get_first_subject(self):
        for rec in self:
            rec.subject = rec.subjects[0] if len(rec.subjects) > 0 else ""
    
    def _compute_duedate(rec, changed_action):
        duedate = fields.Date.today()
        actionType = "call"
        if changed_action.result == "no_answer" and rec.is_meeting_scheduled:
            # get today date and put into variable
            duedate = (rec.create_date if rec.create_date else fields.Date.today()) + relativedelta(days=1)
        elif changed_action.result == "no_answer":
            days=(7 if rec.followup_incremental < 7 else rec.followup_incremental*2)
            print("===================================== no_answer")
            print(days)
            duedate = (rec.create_date if rec.create_date else fields.Date.today()) + relativedelta(days=days)
        elif changed_action.result == "not_interrested":
            days=(60 if rec.followup_incremental < 60 or rec.followup_incremental%7 == 0 else rec.followup_incremental*2)
            print("===================================== not_interrested")
            print(days)
            duedate = (rec.create_date if rec.create_date else fields.Date.today()) + relativedelta(days=days)
        elif changed_action.result == "meeting_scheduled":
            duedate = fields.Date.today() + relativedelta(days=2)
            actionType = "meeting"
        else:
            duedate = False
        
        return (0, 0, {
                    "action_type": actionType,
                    "duedate": duedate,
                    "assignee": rec.lead_owner.id,
                    "name": "Call " + rec.name,
                })

    @api.depends("actions")
    def _compute_state(self):
        for rec in self:
            if len(rec.actions) == 0: continue
            print("Passed first filter")
            if rec.actions[0].status == "new": continue
            print("Passed second filter")
            rec.state = rec._action_result_state_map[rec.actions[0].result]

    # make an on change function that adds new action assigned to the lead owner once owner is changed
    @api.onchange("lead_owner")
    def _onchange_lead_owner(self):
        print ("===================================== _onchange_lead_owner")
        for rec in self:
            if rec.lead_owner:
                # create new action assigned to the lead owner
                if len(rec.actions) > 0 and rec.actions[0].status == "new": 
                    rec.actions[0].assignee = rec.lead_owner.id
                else:
                    rec.actions = [(0, 0, {
                        "action_type": "call",
                        "duedate": rec.next_call_at if rec.next_call_at else fields.Date.today() + relativedelta(days=2),
                        "assignee": rec.lead_owner.id,
                        "name": "Call " + rec.name,
                    })]


    @api.onchange("actions")
    def _onchange_actions(self):
        print ("===================================== _onchange_actions")
        for rec in self:
            if len(rec.actions) == 0: continue
            print("Passed first filter")
            if rec.actions[len(rec.actions)-1].create_date == False: 
                actionToFollow = rec.actions[len(rec.actions)-1]
            else:
                actionToFollow = rec.actions[0]
            print(actionToFollow.create_date)
            if actionToFollow.status == "new": continue
            print("Passed second filter")
            if actionToFollow.result:
                print("Passed third filter")
                if rec.is_meeting_scheduled and actionToFollow.result != "no_answer":
                    rec.is_met = True
                    rec.is_meeting_scheduled = actionToFollow.result == "meeting_scheduled"
                if actionToFollow.result == "meeting_scheduled":
                    rec.is_meeting_scheduled = True
                if actionToFollow.result != "signed" and actionToFollow.result != "canceled":
                    rec.actions = [rec._compute_duedate(actionToFollow)]
