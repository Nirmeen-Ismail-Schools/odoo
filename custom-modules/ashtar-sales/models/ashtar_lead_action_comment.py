from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class CommentAction(models.Model):
    _name = "ashtar.lead.action.comment"
    _description = "Lead action.comment"
    _order = "id desc"

    action_id = fields.Many2one("ashtar.lead.action", string="Action")
    comment = fields.Text()