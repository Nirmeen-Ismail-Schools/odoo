from odoo import models, fields, api

class AshtarLeadStage(models.Model):
    _name = "ashtar.lead.stage"
    _description = "Educational stage"
    _order = "id desc"

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    lead_ids = fields.One2many("ashtar.lead", "edu_stage", string="Leads")
    