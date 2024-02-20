from odoo import fields, models, api
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Model for Estate Property Offers"

    # Camps del model
    price = fields.Float(string="Preu", required=True)
    status = fields.Selection(
        [('pending', 'En tractament'), ('accepted', 'Acceptada'), ('rejected', 'Rebutjada')],
        string="Estat", default="pending", required=True
    )
    buyer = fields.Many2one("res.partner", string="Comprador")
    property_id = fields.Many2one("estate.property", string="Propietat", ondelete="cascade")
    comments = fields.Text(string="Comentaris")

    # Mètodes per gestionar la presentació dels registres
    @api.model
    def name_get(self):
        result = []
        for record in self:
            # Defineix la representació del nom que es mostrarà als usuaris (en aquest cas, utilitza el camp 'price')
            name = "{}".format(record.price)
            result.append((record.id, name))
        return result


    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        # Defineix el domini per la cerca del nom (en aquest cas, cerca pel nom del comprador)
        domain = [('partner_id.name', operator, name)]
        # Realitza la cerca dels registres amb el domini i altres condicions especificades
        record_ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
        # Retorna els noms dels registres que coincideixen amb la cerca
        return self.browse(record_ids).name_get()



    @api.model
    def accept_offer(self, property_id):
        for record in self:
            if record.state == 'Offer Recieved':
                accepted_offer = record.offer_ids.filtered(lambda offer: offer.status == 'accepted')
                if accepted_offer:
                    record.buyer = accepted_offer.buyer.id
                    record.selling_price = accepted_offer.price
                    accepted_offer.write({'status': 'accepted', 'property_state': 'Offer Accepted'})
                    record.state = 'Offer Accepted'
                else:
                    raise UserError('No s\'ha trobat cap oferta acceptada per a aquesta propietat.')
            else:
                raise UserError('Només es pot acceptar una oferta quan l\'estat de la propietat és "Offer Recieved".')



