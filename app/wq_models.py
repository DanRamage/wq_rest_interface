from app import db


class Site_Type(db.Model):
  __tablename__ = 'site_type'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100))


# Create user model.
class WQ_Area(db.Model):
  __tablename__ = 'wq_area'
  id = db.Column(db.Integer, primary_key=True)
  area_name = db.Column(db.String(100))
  display_name =  db.Column(db.String(100))
  #bounding_box = db.Column(Geometry(geometry_type='POLYGON', srid=4326))
  bounding_box = db.Column(db.Text)
  #area_message = db.relationship('WQ_Site_Message', backref='wq_area', uselist=False)

  site_type_id = db.Column(db.Integer, db.ForeignKey('site_type.id'))
  site_type = db.relationship('Site_Type', backref='wq_area')

  column_filters = ('area_name', 'display_name', 'bounding_box', 'site_type')
  #Use the __str__ for the foreign key relationships.
  def __str__(self):
    return self.area_name

class WQ_Site_Message(db.Model):
  __tablename__ = 'wq_site_message'
  id = db.Column(db.Integer, primary_key=True)
  site_id = db.Column(db.Integer, db.ForeignKey('wq_area.id'))
  site = db.relationship('WQ_Area', backref='wq_site_message')
  message = db.Column(db.String(256))

  def __str__(self):
    return self.message