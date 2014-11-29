from flask import Markup, url_for
from sqlalchemy import Table, Column, Integer, Float, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from flask.ext.appbuilder.filemanager import ImageManager
from flask.ext.appbuilder.models.mixins import BaseMixin, ImageColumn
from flask.ext.appbuilder import Model
from flask_appbuilder.security.models import User

class ProductType(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Product(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    photo = Column(ImageColumn)
    description = Column(Text())
    product_type_id = Column(Integer, ForeignKey('product_type.id'), nullable=False)
    product_type = relationship("ProductType")

    def photo_img(self):
        im = ImageManager()
        if self.photo:
            return Markup('<a href="' + url_for('ProductPubView.show',
                                                pk=str(self.id)) + '" class="thumbnail"><img src="' +
                          im.get_url(self.photo) + '" alt="Photo" class="img-rounded img-responsive"></a>')
        else:
            return Markup('<a href="' + url_for('ProductPubView.show',
                                                pk=str(self.id)) + '" class="thumbnail"><img src="//:0" alt="Photo" class="img-responsive"></a>')

    def price_label(self):
        return Markup('Price:<strong> {} </strong>'.format(self.price))

    def __repr__(self):
        return self.name


class Client(User):
    extra = Column(String(50), unique=True, nullable=False)


class PurchaseOrder(Model):

    id = Column(Integer, primary_key=True)
    client_id=Column(Integer,ForeignKey('ab_user.id'))
    product_type_id = Column(Integer,ForeignKey('product_type.id'))
    product_id=Column(Integer,ForeignKey('product.id'))
    product = relationship("Product")
    product_type = relationship("ProductType")
    client = relationship("User")
    quantity = Column(Integer)

  



