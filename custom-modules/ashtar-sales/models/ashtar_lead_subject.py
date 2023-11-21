from odoo import models, fields, api

class AshtarLeadSubject(models.Model):
    _name = "ashtar.lead.subject"
    _description = "Subject"
    _order = "id desc"

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    lead_ids = fields.Many2many("ashtar.lead", string="Leads")