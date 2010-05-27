# -*- coding: utf-8 -*-

from resarmll.resa.models import Article

CART_KEY = 'CART_KEY'

class CartItem:
    id = 0
    quantity = 0
    label = ""
    price = 0.0
    salt = ''
    sorting = 0

    def __init__(self, id=0, quantity=0, label="", price=0.0, sorting=0):
        self.id = id
        self.quantity = quantity
        self.label = label
        self.price = price
        self.sorting = sorting

    def total(self):
        return self.quantity*self.price

    def stock(self):
        product = Article.objects.get(id=self.id)
        return product.quantity()

class Cart:
    def __init__(self, request, salt=None):
        self.items = []
        self.salt = str(salt)
        data = request.session.get(self.get_salt())
        if data is not None:
            products = {}
            for t in data:
                i,d = t
                products[i] = d
            self.add_group(products)

    def __iter__(self):
        for item in self.items:
            yield item

    def get_salt(self):
        ret = CART_KEY
        if self.salt != '':
            ret = CART_KEY+'_'+self.salt
        return ret

    def add_group(self, products):
        prods = Article.objects.filter(id__in=products.keys()).order_by('order')
        for product in prods:
            self.items.append(CartItem(product.id, products[product.id],
                product.label(), product.price, product.order))

    def add(self, product_id, quantity, replace=False):
        ret = False
        for i,item in enumerate(self.items):
            if item.id == product_id:
                if replace:
                    self.items[i].quantity = quantity
                else:
                    self.items[i].quantity += quantity
                ret = True
                break
        if not ret:
            try:
                product = Article.objects.get(id=product_id)
                self.items.append(CartItem(product_id, quantity,
                    product.label(), product.price, product.order))
                ret = True
            except:
                pass
        # sorting
        self.items = sorted(self.items, key=lambda i: i.sorting)
        return ret

    def delete(self, product_id):
        ret = False
        for i,item in enumerate(self.items):
            if item.id == product_id:
                del self.items[i]
                ret = True
                break
        return ret

    def update(self, product_id, quantity):
        if quantity < 0:
            quantity = 0
        if quantity == 0:
            ret = self.delete(product_id)
        else:
            ret = self.add(product_id, quantity, True)
        return ret

    def empty(self):
        return len(self.items) == 0

    def total(self):
        ret = 0
        for item in self.items:
            ret += item.total()
        return ret

    def save(self, request):
        session_data = []
        for i,item in enumerate(self.items):
            session_data.append((item.id, item.quantity))
        request.session[self.get_salt()] = session_data

    def clear(self):
        self.items = []

    def is_valid(self):
        ret = True
        for i,item in enumerate(self.items):
            product = Article.objects.get(id=item.id)
            ret = ret and product.quantity() >= item.quantity
        return ret