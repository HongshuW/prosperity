from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


SINGLE_TRADE_SIZE = 5
LIMITS = {'PEARLS': 20, 'BANANAS': 20}
PRICES = {'PEARLS': 10000, 'BANANAS': 5000}

class Trader:
    def __init__(self):
        self.positions = dict()

    def market_making(self, product: str, order_depth: OrderDepth) -> list[Order]:
        # Initialize the list of Orders to be sent as an empty list
        orders: list[Order] = []
        # If statement checks if there are any SELL orders in the PEARLS market
        if len(order_depth.sell_orders) > 0:
            # Sort all the available sell orders by their price,
            # and select only the sell order with the lowest price
            best_ask = min(order_depth.sell_orders.keys())
            # best_ask_volume = order_depth.sell_orders[best_ask]
        else:
            return
        if len(order_depth.buy_orders) > 0:
            best_bid = max(order_depth.buy_orders.keys())
            # best_bid_volume = order_depth.buy_orders[best_bid]
        else:
            return
        volume = SINGLE_TRADE_SIZE
        if best_bid + 1 < best_ask - 1:
            orders.append(Order(product, best_bid + 1, volume))
            orders.append(Order(product, best_ask - 1, -volume))
            print("BUY", volume, "x", best_bid + 1)
            print("SELL", volume, "x", best_ask - 1)
        return orders

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        for product in state.position.keys():
            self.positions[product] = state.position[product]

        print(self.positions)

        # Iterate over all the keys (the available products) contained in the order dephts
        for product in state.order_depths.keys():
            # if abs(state.position[product]) + SINGLE_TRADE_SIZE <= LIMITS[product]:
            order_depth: OrderDepth = state.order_depths[product]
            orders = self.market_making(product, order_depth)
            result[product] = orders

        return result
