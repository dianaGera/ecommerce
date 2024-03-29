from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey
from ..extentions import db



promotions = db.Table('promotions', db.Model.metadata,
    Column('promotion_id', Integer, ForeignKey('promotion.id'), primary_key=True),
    Column('seller_id', Integer, ForeignKey('seller.id'), primary_key=True)
)

active_codes_for_custmr = db.Table('active_codes_for_custmr', db.Model.metadata,
    Column('coupon_id', Integer, ForeignKey('coupon.id'), primary_key=True),
    Column('customer_id', Integer, ForeignKey('customer.id'), primary_key=True)
)

active_codes_for_sel = db.Table('active_codes_for_sel', db.Model.metadata,
    Column('coupon_id', Integer, ForeignKey('coupon.id'), primary_key=True),
    Column('seller_id', Integer, ForeignKey('seller.id'), primary_key=True)
)


class User(UserMixin):
    __abstract__ = True
    R_CUSTOMER = 0
    R_SELLER = 1
    STATUS = 'Active'
    id = Column(Integer(), primary_key=True)
    email = Column(String(125), unique=True, nullable=False)
    password = Column(String(125), nullable=False)
    role = Column(Integer, nullable=False, default=R_CUSTOMER)
    status = Column(String(50), nullable=False, default=STATUS)


    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()


class Customer(User, db.Model):
    username = Column(String(50), nullable=False)
    description = Column(String(1000), nullable=True)
    img = Column(Integer, ForeignKey('customer_avatar.id'))
    cart_id = Column(Integer, nullable=True)
    # coupons = relationship(
    #     Coupon, secondary=active_codes_for_custmr,
    #     lazy='subquery', backref=db.backref('customer', lazy=True)
    # )

    def __repr__(self):
        return f'{self.username}'

    # def save_product(self, id):
    #     product = Product.query.get(id)
    #     if product not in self.saved:
    #         self.saved.extend([product])
    #         product.like += 1
    #     else:
    #         self.saved.remove(product)
    #         product.like -= 1
    #     db.session.add(product)
    #     db.session.commit()


class Seller(User, db.Model):
    company_name = Column(String(125), nullable=True)
    country = Column(String(125), nullable=True)
    img = Column(Integer, ForeignKey('company_logo.id'), nullable=True)
    # promotion = relationship(
    #     Promotion, secondary=promotions, lazy='subquery',
    #     backref=db.backref('seller', lazy=True)
    # )
    # coupons = relationship(
    #     Coupon, secondary=active_codes_for_sel, lazy='subquery',
    #     backref=db.backref('seller', lazy=True)
    # )

    def __repr__(self):
        return f'{self.company_name}'


class CustomerAvatar(db.Model):
    id = Column(Integer(), primary_key=True)
    path = Column(String(125), nullable=False)


class CompanyLogo(db.Model):
    id = Column(Integer, primary_key=True)
    path = Column(String(125), nullable=False)


