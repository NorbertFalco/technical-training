from odoo import fields, models, api
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Propietats immobiliàries'

    # Informació bàsica
    name = fields.Char('Propietat Immobiliària', required=True)
    description = fields.Text('Descripció')
    postcode = fields.Char('Codi Postal')

    # Disponibilitat
    date_availability = fields.Date('Data de disponibilitat',copy=False)

    # Preus
    selling_price = fields.Float('Preu de venda')
    expected_selling_price = fields.Float('Preu de venda esperat')
    avg_price = fields.Float('Preu per m2', compute='_calcular_preu_per_metre', store=True)

    # Property Details
    bedrooms = fields.Integer('Nombre d\'habitacions', required=True)
    property_type = fields.Selection([
        ('house', 'Casa'),
        ('apartment', 'Pis'),
        # Afegir mes tipus de propietats
    ], string='Tipus')
    
    tag_ids = fields.Many2many('estate.property.tag', string='Etiquetes', help='Etiquetes relacionades amb la propietat' )
    offer_ids = fields.One2many('estate.property.offer','property_id', string='Ofertes')
    elevator = fields.Boolean('Ascensor', default=False)
    parking = fields.Boolean('Parking', default=False)
    renovated = fields.Boolean('Renovat', default=False)
    bathrooms = fields.Integer('Banys')
    area = fields.Float('Superficie', required=True)
    construction_year = fields.Integer('Any de construcció')
    energy_certificate = fields.Char('Certificat energètic')
    best_offer = fields.Many2one('estate.property.offer', string='Millor Oferta', compute='_compute_best_offer')

    # Status
    state = fields.Selection([
        ('New', 'Nova'),
        ('Offer Recieved', 'Oferta Rebuda'),
        ('Offer Accepted', 'Oferta Acceptada'),
        ('Sold', 'Venuda'),
        ('Canceled', 'Cancel·lada'),
    ], default='New', copy=False, required=True)

    # Informació adicional   
    # active = fields.Boolean('Actiu', default=True)
    buyer = fields.Many2one('res.partner', string='Comprador', compute='_compute_buyer', store=True)
    salesperson = fields.Many2one('res.users', string='Comercial', default=lambda self: self.env.user)

    @api.depends('offer_ids', 'offer_ids.price')
    def _compute_best_offer(self):
        for property_record in self:
            if property_record.offer_ids:
                best_offer = property_record.offer_ids.sorted(key=lambda r: r.price, reverse=True)
                property_record.best_offer = best_offer[0] if best_offer else False
            else:
                property_record.best_offer = False


    @api.depends('expected_selling_price','area')
    def _calcular_preu_per_metre(self):
        for record in self:
            if record.area > 0 :
                record.avg_price = record.expected_selling_price/record.area
            else:
                record.avg_price = None

    def cancellarPropietat(self):
        for record in self:
            if not record.state == 'Sold':
                record.state = 'Canceled'
            else:
                raise UserError('No es pot cancel·lar una propietat venuda')
        return True

    @api.depends('offer_ids', 'offer_ids.status', 'offer_ids.buyer', 'offer_ids.buyer.name', 'state')
    def _compute_buyer(self):
        for record in self:
            if record.state in ['Sold', 'Venuda']:
                accepted_offer = record.offer_ids.filtered(lambda offer: offer.status == 'accepted')
                print(f"Property {record.name} - Accepted Offer: {accepted_offer}")
                record.buyer = accepted_offer.buyer.name if accepted_offer else False
                print(f"Property {record.name} - Buyer: {record.buyer}")
            else:
                record.buyer = False

