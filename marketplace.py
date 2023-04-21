"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock, currentThread
import unittest
import logging
from logging.handlers import RotatingFileHandler

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        # Initialize the Marketplace
        self.queue_size_per_producer = queue_size_per_producer

        # Initialize the producers list
        self.producers = []

        # Initialize the total number of elements a producer published
        self.total_producers_elements = []

        # Initialize the costumer's cart list
        self.consumers_carts = []

        # Initialize the lock for the producers list
        self.producers_lock = Lock()

        # Initialize the lock for the total number of elements a producer published
        self.total_producers_elements_lock = Lock()

        # Initialize the lock for the costumer's cart list
        self.consumers_carts_lock = Lock()

        # Initialize print lock
        self.print_lock = Lock()

        # Initialize the logger
        self.logger = logging.getLogger('marketplace')
        handler = RotatingFileHandler('marketplace.log')

        # Set the logger format
        formatter = logging.Formatter('%(asctime)s UTC/GMT - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(handler)

        # Set the logger level
        self.logger.setLevel(logging.INFO)

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        # Log the call
        self.logger.info("register_producer() called by %s", currentThread().getName())

        # Acquire the lock for the producers list
        self.producers_lock.acquire()

        # Add a new producer in the producers list
        self.producers.append([])

        # Add a new producer in the total number of elements a producer published list
        self.total_producers_elements.append(0)

        # Get the length of the producers list
        producer_id = len(self.producers) - 1

        # Release the lock for the producers list
        self.producers_lock.release()

        # Log the exit
        self.logger.info("register_producer() exited by %s", currentThread().getName())

        # Return the index of the new producer in the producers list
        return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        # Log the call with the parameters
        self.logger.info("publish() called by %s with parameters: %s, %s",
                         currentThread().getName(), str(producer_id), str(product))

        # Check if producer_id is valid
        if producer_id < 0 or producer_id >= len(self.producers):
            return False

        # Check if the producer's queue is full
        if self.total_producers_elements[producer_id] >= self.queue_size_per_producer:
            return False

        # Acquire the lock for the producers list
        self.producers_lock.acquire()

        # Check if the product is already in the producer's queue
        for i in range(len(self.producers[producer_id])):
            if self.producers[producer_id][i][0] == product:
                # Increase the quantity of the product in the producer's queue
                self.producers[producer_id][i][1] += 1

                # Acquire the lock for the total number of elements a producer published
                self.total_producers_elements_lock.acquire()
                self.total_producers_elements[producer_id] += 1
                self.total_producers_elements_lock.release()

                # Release the lock for the producers list
                self.producers_lock.release()
                return True

        # If the product is not in the producer's queue, add it
        self.producers[producer_id].append([product, 1])
        self.total_producers_elements_lock.acquire()
        self.total_producers_elements[producer_id] += 1
        self.total_producers_elements_lock.release()

        # Release the lock for the producers list
        self.producers_lock.release()

        # Log the exit
        self.logger.info("publish() exited by %s", currentThread().getName())

        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        # Log the call
        self.logger.info("new_cart() called by %s", currentThread().getName())

        # Acquire the lock for the costumer's cart list
        self.consumers_carts_lock.acquire()

        # Add a new cart in the costumer's cart list
        self.consumers_carts.append([])

        # Get the length of the costumer's cart list
        cart_id = len(self.consumers_carts) - 1

        # Release the lock for the costumer's cart list
        self.consumers_carts_lock.release()

        # Log the exit
        self.logger.info("new_cart() exited by %s", currentThread().getName())

        # Return the index of the new cart in the costumer's cart list
        return cart_id


    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        # Log the call with the parameters
        self.logger.info("add_to_cart() called by %s with parameters: %s, %s",
                         currentThread().getName(), str(cart_id), str(product))

        # Check if the cart_id is valid
        if cart_id < 0 or cart_id >= len(self.consumers_carts):
            return False

        # Acquire the lock for the producers list
        self.producers_lock.acquire()

        # Remember the index of the producer that has the product
        producer_index = -1
        product_index = -1

        # Check if the product is in the producers list
        for i in range(len(self.producers)):
            for j in range(len(self.producers[i])):
                if self.producers[i][j][0] == product and self.producers[i][j][1] > 0:
                    # The product is in the producers list
                    producer_index = i
                    product_index = j
                    break

        # Check if the product is in the producers list
        if producer_index == -1:
            # The product is not in the producers list
            self.producers_lock.release()
            return False

        # Acquire the lock for the cart
        self.consumers_carts_lock.acquire()

        # Add it to cart
        self.consumers_carts[cart_id].append([product, producer_index])

        # Remove the product from the producer's queue
        self.producers[producer_index][product_index][1] -= 1

        # Acquire the lock for the total number of elements a producer published
        self.total_producers_elements_lock.acquire()
        self.total_producers_elements[producer_index] -= 1
        self.total_producers_elements_lock.release()

        # Release the lock for the cart
        self.consumers_carts_lock.release()

        # Release the lock for the producers list
        self.producers_lock.release()

        # Log the exit
        self.logger.info("add_to_cart() exited by %s", currentThread().getName())

        return True

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        # Log the call with the parameters
        self.logger.info("remove_from_cart() called by %s with parameters: %s, %s",
                         currentThread().getName(), str(cart_id), str(product))

        if cart_id < 0 or cart_id >= len(self.consumers_carts):
            return

        # Acquire the lock for the cart
        self.consumers_carts_lock.acquire()

        # Remember the index of the producer that has the product
        producer_index = -1

        # Remember index to delete from cart
        remove_product_idx = -1

        # Find the product in the cart
        for i in range(len(self.consumers_carts[cart_id])):
            if self.consumers_carts[cart_id][i][0] == product:
                # The product is in the cart
                producer_index = self.consumers_carts[cart_id][i][1]
                remove_product_idx = i
                break

        # Acquire the lock for the producers list
        self.producers_lock.acquire()

        # Add the product to the producer's queue
        for i in range(len(self.producers[producer_index])):
            if self.producers[producer_index][i][0] == product:
                self.producers[producer_index][i][1] += 1
                break

        # Acquire the lock for the total number of elements a producer published
        self.total_producers_elements_lock.acquire()
        self.total_producers_elements[producer_index] += 1
        self.total_producers_elements_lock.release()

        # Remove the product from the cart
        del self.consumers_carts[cart_id][remove_product_idx]

        # Release the lock for the producers list
        self.producers_lock.release()

        # Release the lock for the cart
        self.consumers_carts_lock.release()

        # Log the exit
        self.logger.info("remove_from_cart() exited by %s", currentThread().getName())

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        # Log the call with the parameters
        self.logger.info("place_order() called by %s with parameters: %s",
                         currentThread().getName(), str(cart_id))

        # Check if the cart_id is valid
        if cart_id < 0 or cart_id >= len(self.consumers_carts):
            return False

        # Acquire the lock for the cart
        self.consumers_carts_lock.acquire()

        # Get the cart
        cart = self.consumers_carts[cart_id]

        # Print the cart
        for element in cart:
            # Acquire print mutex
            self.print_lock.acquire()

            print("{} bought {}".format(currentThread().getName(), element[0]))

            # Release print mutex
            self.print_lock.release()

        # Empty the cart
        self.consumers_carts[cart_id] = []

        # Release the lock for the cart
        self.consumers_carts_lock.release()

        # Log the exit
        self.logger.info("place_order() exited by %s", currentThread().getName())

        # Return the cart
        return cart


class TestProduct:
    """
    Class that represents a product.
    """
    def __init__(self, name, price):
        """
        Constructor

        :type name: str
        :param name: the name of the product

        :type price: float
        :param price: the price of the product
        """
        self.name = name
        self.price = price

    def __eq__(self, other):
        """
        Overwrite the equal operator.

        :type other: TestProduct
        :param other: the other product to compare with

        :rtype: bool
        :return: True if the products are equal, False otherwise
        """
        return self.name == other.name and self.price == other.price

class TestMarketplace(unittest.TestCase):
    """
    Test class for the Marketplace class.
    """
    def setUp(self):
        """
        Setup the test.
        """
        self.marketplace = Marketplace(queue_size_per_producer=5)

    def test_register_producer(self):
        """
        Tests the register_producer() method.
        """
        market = Marketplace(10)
        producer_id1 = market.register_producer()
        producer_id2 = market.register_producer()

        self.assertEqual(producer_id1, 0)
        self.assertEqual(producer_id2, 1)

    def test_registered_correctly(self):
        """
        Tests if the producer was registered correctly.
        """
        market = Marketplace(10)
        producer_id = market.register_producer()
        product = TestProduct("product1", 10)
        market.publish(producer_id, product)
        cart_id = market.new_cart()

        # Add the product to the cart and verify that the product was added successfully
        result = market.add_to_cart(cart_id, product)
        self.assertTrue(result)

    def test_publish(self):
        """
        Tests the publish() method.
        """
        market = Marketplace(10)
        producer_id = market.register_producer()
        product = TestProduct("product1", 10)
        market.publish(producer_id, product)

        # Verify that the product was published successfully
        self.assertEqual(market.producers[producer_id][0][0], product)

    def test_publish_max_queue_size(self):
        """
        Tests publishing the max queue size.
        """
        market = Marketplace(3)

        producer_id = market.register_producer()
        product = TestProduct("product1", 10)
        ret = market.publish(producer_id, product)
        self.assertTrue(ret)

        product = TestProduct("product2", 10)
        ret = market.publish(producer_id, product)
        self.assertTrue(ret)

        product = TestProduct("product3", 10)
        ret = market.publish(producer_id, product)
        self.assertTrue(ret)

        product = TestProduct("product4", 10)
        ret = market.publish(producer_id, product)
        self.assertFalse(ret)

    def test_new_cart(self):
        """
        Tests the new_cart() method.
        """
        market = Marketplace(10)
        cart_id = market.new_cart()

        # Verify that the cart was created successfully
        self.assertEqual(market.consumers_carts[cart_id], [])

    def test_multiple_new_carts(self):
        """
        Tests creating multiple carts.
        """
        market = Marketplace(10)
        cart_id1 = market.new_cart()
        cart_id2 = market.new_cart()

        # Verify that the carts were created successfully
        self.assertEqual(market.consumers_carts[cart_id1], [])
        self.assertEqual(market.consumers_carts[cart_id2], [])

    def test_add_to_cart(self):
        """
        Tests the add_to_cart() method.
        """
        market = Marketplace(10)

        # Add the product to market.producers
        producer_id = market.register_producer()
        product = TestProduct("product1", 10)
        market.publish(producer_id, product)

        cart_id = market.new_cart()
        result = market.add_to_cart(cart_id, product)

        # Verify that the product was added successfully
        self.assertTrue(result)

    def test_add_to_cart_invalid_cart(self):
        """
        Tests adding a product to an invalid cart.
        """
        market = Marketplace(10)
        product = TestProduct("product1", 10)
        result = market.add_to_cart(-1, product)

        # Verify that the product was not added successfully
        self.assertFalse(result)

    def test_add_to_cart_invalid_product(self):
        """
        Tests adding an invalid product to a cart.
        """
        market = Marketplace(10)
        cart_id = market.new_cart()
        product = TestProduct("product1", 10)
        result = market.add_to_cart(cart_id, product)

        # Verify that the product was not added successfully
        self.assertFalse(result)

    def test_remove_from_cart(self):
        """
        Tests the remove_from_cart() method.
        """
        market = Marketplace(10)

        # Add the product to market.producers
        producer_id = market.register_producer()
        product = TestProduct("product1", 10)
        market.publish(producer_id, product)

        cart_id = market.new_cart()
        market.add_to_cart(cart_id, product)
        market.remove_from_cart(cart_id, product)

        # Verify that the product is now in the market.producers
        self.assertEqual(market.producers[producer_id][0][0], product)

    def test_remove_from_cart_invalid_cart(self):
        """
        Tests removing a product from an invalid cart.
        """
        market = Marketplace(10)

        # Add the product to market.producers
        producer_id = market.register_producer()
        product = TestProduct("product1", 10)
        market.publish(producer_id, product)

        cart_id = market.new_cart()
        market.add_to_cart(cart_id, product)
        market.remove_from_cart(-1, product)

        # Verify that the product is stil in the cart
        self.assertNotEqual(market.consumers_carts[cart_id], [])

    def test_place_order(self):
        """
        Tests the place_order() method.
        """
        market = Marketplace(10)

        # Add the product to market.producers
        producer_id = market.register_producer()
        product = TestProduct("product1", 10)
        market.publish(producer_id, product)

        cart_id = market.new_cart()
        market.add_to_cart(cart_id, product)
        products = market.consumers_carts[cart_id]

        test_products = market.place_order(cart_id)

        # Verify that the order was placed successfully
        self.assertEqual(test_products, products)

if __name__ == '__main__':
    unittest.main()
