"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time

class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.name = kwargs['name']
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time

    def run(self):
        # For each product in the cart
        for carts in self.carts:
            cart_id = self.marketplace.new_cart()

            for cart in carts:
                op_type = cart['type']
                product = cart['product']
                quantity = cart['quantity']

                while quantity > 0:
                    # If the type is add, add the product to the cart
                    if op_type == "add":
                        res = self.marketplace.add_to_cart(cart_id, product)
                        if res is False:
                            # Wait for the retry wait time
                            time.sleep(self.retry_wait_time)
                        else:
                            quantity -= 1
                    elif op_type == "remove":
                        # If the type is remove, remove the product from the cart
                        self.marketplace.remove_from_cart(cart_id, product)
                        quantity -= 1

            # Buy the cart
            product = self.marketplace.place_order(cart_id)
