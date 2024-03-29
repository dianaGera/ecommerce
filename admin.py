from flask_admin.contrib.sqla import ModelView
from .products.models import Product
from .auth.models import Seller, Customer
from .checkout.models import Promotion


class CustomerAdminView(ModelView):
    can_view_details = True
    column_list = ['id', 'email', 'username', 'role', 'cart_id', 'currency', 'active_discount']

    def __init__(self, session, **kwargs):
        super(CustomerAdminView, self).__init__(Customer, session, **kwargs)


class SellerAdminView(ModelView):
    can_view_details = True
    column_exclude_list = ('password')

    def __init__(self, session, **kwargs):
        super(SellerAdminView, self).__init__(Seller, session, **kwargs)


class ProductAdminView(ModelView):
    can_view_details = True
    column_exclude_list = ('description')

    def __init__(self, session, **kwargs):
        super(ProductAdminView, self).__init__(Product, session, **kwargs)



class PromotionAdminView(ModelView):
    can_view_details = True
    # column_exclude_list = ('busines_type')

    def __init__(self, session, **kwargs):
        super(PromotionAdminView, self).__init__(Promotion, session, **kwargs)
        self.name = 'promotion'
