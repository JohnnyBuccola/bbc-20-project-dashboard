from app import db

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float)
    long = db.Column(db.Float)
    city = db.Column(db.String)
    state = db.Column(db.String)
    address = db.Column(db.String)
    sqft = db.Column(db.Integer)
    prototype_prefix = db.Column(db.String)
    prototype_suffix = db.Column(db.String)
    region = db.Column(db.String)
    wall_panels_cost = db.Column(db.Float)
    buyout_total = db.Column(db.Integer)
    panels_onsite_date = db.Column(db.Date)
    sales_order_date = db.Column(db.Date)
    panel_vendor = db.Column(db.String)
    n_wall_panels_ext = db.Column(db.Integer)
    n_wall_panels_int = db.Column(db.Integer)
    sqft_wall_panels_ext = db.Column(db.Float)
    sqft_wall_panels_int = db.Column(db.Float)
    project_status = db.Column(db.String)

    def __init__(self, id, lat, long, city, state, address, sqft, \
                prototype_prefix, prototype_suffix, region, \
                wall_panels_cost, buyout_total, panels_onsite_date, \
                sales_order_date, panel_vendor, 
                n_wall_panels_ext, n_wall_panels_int, sqft_wall_panels_ext, sqft_wall_panels_int, project_status):
        self.id = id
        self.lat = lat
        self.long = long
        self.city = city
        self.state = state
        self.address = address
        self.sqft = sqft
        self.prototype_prefix = prototype_prefix
        self.prototype_suffix = prototype_suffix
        self.region = region
        self.wall_panels_cost = wall_panels_cost
        self.buyout_total = buyout_total
        self.panels_onsite_date = panels_onsite_date
        self.sales_order_date = sales_order_date
        self.panel_vendor = panel_vendor
        self.n_wall_panels_ext = n_wall_panels_ext
        self.n_wall_panels_int = n_wall_panels_int
        self.sqft_wall_panels_ext = sqft_wall_panels_ext
        self.sqft_wall_panels_int = sqft_wall_panels_int
        self.project_status = project_status
        
    def __repr__(self):
        return '<project id {}>'.format(self.id)
    
    # def serialize(self):
    #     return {
    #         'id': self.id, 
    #         'location': self.location,
    #         'sqft': self.sqft,
    #         'region':self.region,
    #         'budget_structwood':self.budget_structwood,
    #         'buyout_structwood':self.buyout_structwood,
    #         'buyout_total':self.buyout_total,
    #         'panels_onsite_date': self.panels_onsite_date
    #     }

class Lumber_Price(db.Model):
    __tablename__ = 'lumber_prices'

    date = db.Column(db.Date, primary_key=True)
    ticker = db.Column(db.String)
    open = db.Column(db.Float)
    close = db.Column(db.Float)
    change = db.Column(db.Float)

    def __init__(self, ticker, date, open, close, change):
        self.ticker = ticker
        self.date = date
        self.open = open
        self.close = close
        self.change = change

    def __repr__(self):
        return '<id {0} - {1}>'.format(self.date, self.ticker)
    
    # def serialize(self):
    #     return {
    #         'id': self.id 

    #     }
