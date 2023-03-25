from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

PEARLS = 'PEARLS'
BANANAS = 'BANANAS'
COCONUTS = 'COCONUTS'
PINA_COLADAS = 'PINA_COLADAS'
DIVING_GEAR = 'DIVING_GEAR'
BERRIES = 'BERRIES'

SINGLE_TRADE_SIZE = 5
LIMITS = {'PEARLS': 20, 'BANANAS': 20, 'COCONUTS': 600, 'PINA_COLADAS': 300, 'DIVING_GEAR': 50, 'BERRIES': 250}
PRICES = {'PEARLS': 10000, 'BANANAS': 5000, 'COCONUTS': 8000, 'PINA_COLADAS': 15000}

class Trader:
    def __init__(self):
        self.profit = 0

    def get_best_ask(self, order_depth: OrderDepth) -> int:
        if len(order_depth.sell_orders) > 0:
            return min(order_depth.sell_orders.keys())
        else:
            return -1

    def get_best_bid(self, order_depth: OrderDepth) -> int:
        if len(order_depth.buy_orders) > 0:
            return max(order_depth.buy_orders.keys())
        else:
            return -1

    def get_volume(self, product: str, is_buy: bool, position) -> int:
        limit = LIMITS[product]
        current_position = position[product]
        if is_buy:
            if current_position >= limit:
                return 0
            else:
                return limit - current_position
        else:
            if current_position <= -limit:
                return 0
            else:
                return current_position + limit

    def buy_product(self, product: str, price: int, volume: int) -> Order:
        return Order(product, price, volume)

    def sell_product(self, product: str, price: int, volume: int) -> Order:
        return Order(product, price, -volume)

    def market_making(self, product: str, order_depth: OrderDepth, position) -> list[Order]:
        orders: list[Order] = []

        best_ask = self.get_best_ask(order_depth)
        best_bid = self.get_best_bid(order_depth)
        if best_ask == -1 or best_bid == -1:
            return orders

        if best_bid + 1 < best_ask - 1:
            if position.keys().__contains__(product):
                volume = min(self.get_volume(product, True, position), self.get_volume(product, False, position))
            else:
                volume = SINGLE_TRADE_SIZE
            if volume > 0:
                buy_order = self.buy_product(product, best_bid + 1, volume)
                sell_order = self.sell_product(product, best_ask - 1, volume)
                orders.append(buy_order)
                orders.append(sell_order)
                print("-----market making: ", product, "-----")
        return orders

    def long_short_position(self, product: str, order_depth: OrderDepth, position) -> list[Order]:
        orders: list[Order] = []

        best_ask = self.get_best_ask(order_depth)
        if best_ask == -1:
            return orders
        else:
            if position.keys().__contains__(product):
                volume = min(order_depth.sell_orders[best_ask], self.get_volume(product, True, position))
            else:
                volume = SINGLE_TRADE_SIZE
            if best_ask < PRICES[product]:
                buy_order = self.buy_product(product, best_ask, volume)
                orders.append(buy_order)
                print("-----buy: ", product, "-----")

        best_bid = self.get_best_bid(order_depth)
        if best_bid == -1:
            return orders
        else:
            if position.keys().__contains__(product):
                volume = min(order_depth.buy_orders[best_bid], self.get_volume(product, False, position))
            else:
                volume = SINGLE_TRADE_SIZE
            if best_bid > PRICES[product]:
                sell_order = self.sell_product(product, best_bid, volume)
                orders.append(sell_order)
                print("-----sell: ", product, "-----")

        return orders

    """product price * factor = hedge product price"""
    def pair_trading(self, product: str, hedge_product: str, order_depths, factor: float, position) -> Dict[str, List[Order]]:
        product_order_depth = order_depths[product]
        hedge_product_order_depth = order_depths[hedge_product]

        results = {}
        product_orders = []
        hedge_orders = []

        product_best_ask = self.get_best_ask(product_order_depth)
        product_best_bid = self.get_best_bid(product_order_depth)
        hedge_best_ask = self.get_best_ask(hedge_product_order_depth)
        hedge_best_bid = self.get_best_bid(hedge_product_order_depth)

        if product_best_ask * factor < hedge_best_bid:
            if position.keys().__contains__(product):
                volume = min(product_order_depth.sell_orders[product_best_ask], self.get_volume(product, True, position))
            elif position.keys().__contains__(hedge_product):
                volume = min(hedge_product_order_depth.buy_orders[hedge_best_bid], self.get_volume(hedge_product, False, position))
            else:
                volume = SINGLE_TRADE_SIZE
            # buy product and sell hedge product
            buy_product = self.buy_product(product, product_best_ask, volume)
            sell_hedge_product = self.sell_product(hedge_product, hedge_best_bid, volume)
            product_orders.append(buy_product)
            hedge_orders.append(sell_hedge_product)
        elif hedge_best_ask < product_best_bid * factor:
            if position.keys().__contains__(product):
                volume = min(product_order_depth.buy_orders[product_best_bid], self.get_volume(product, False, position))
            elif position.keys().__contains__(hedge_product):
                volume = min(hedge_product_order_depth.sell_orders[hedge_best_ask], self.get_volume(hedge_product, True, position))
            else:
                volume = SINGLE_TRADE_SIZE
            # sell product and buy hedge product
            sell_product = self.sell_product(product, product_best_bid, volume)
            buy_hedge_product = self.buy_product(hedge_product, hedge_best_ask, volume)
            product_orders.append(sell_product)
            hedge_orders.append(buy_hedge_product)

        results[product] = product_orders
        results[hedge_product] = hedge_orders
        return results

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        result = {}

        position = state.position
        order_depths = state.order_depths

        # pearls: market making and long short positioning
        pearls_order_depth = order_depths[PEARLS]
        pearl_orders = self.market_making(PEARLS, pearls_order_depth, position)
        pearl_orders += self.long_short_position(PEARLS, pearls_order_depth, position)
        result[PEARLS] = pearl_orders

        # bananas: market making
        bananas_order_depth = order_depths[BANANAS]
        bananas_orders = self.market_making(BANANAS, bananas_order_depth, position)
        result[BANANAS] = bananas_orders

        # coconuts and pina coladas: pair trading
        factor = PRICES[PINA_COLADAS] / PRICES[COCONUTS]
        subset_of_results = self.pair_trading(COCONUTS, PINA_COLADAS, order_depths, factor, position)
        for product in subset_of_results.keys():
            if result.__contains__(product):
                result[product] += subset_of_results[product]
            else:
                result[product] = subset_of_results[product]

        # berries: market making
        berries_order_depth = order_depths[BERRIES]
        berries_orders = self.market_making(BERRIES, berries_order_depth, position)
        result[BERRIES] = berries_orders

        return result
