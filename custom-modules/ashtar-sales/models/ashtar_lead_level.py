from odoo import models, fields, api

class AshtarLeadLevel(models.Model):
    _name = "ashtar.lead.level"
    _description = "Educational grade level"
    _order = "id desc"

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    lead_ids = fields.Many2many("ashtar.lead", string="Leads")
    