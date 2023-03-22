from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


SINGLE_TRADE_SIZE = 5
LIMITS = {'PEARLS': 20, 'BANANAS': 20}
PRICES = {'PEARLS': 10000, 'BANANAS': 5000}

"""33,352,562"""
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

    def market_making(self, product: str, order_depth: OrderDepth) -> list[Order]:
        orders: list[Order] = []

        best_ask = self.get_best_ask(order_depth)
        best_bid = self.get_best_bid(order_depth)
        if best_ask == -1 or best_bid == -1:
            return orders

        volume = SINGLE_TRADE_SIZE
        if best_bid + 1 < best_ask - 1:
            orders.append(Order(product, best_bid + 1, volume))
            orders.append(Order(product, best_ask - 1, -volume))
            # print("BUY", volume, "x", best_bid + 1)
            # print("SELL", volume, "x", best_ask - 1)
            print("-----market making: ", product, "-----")
        return orders

    def long_short_position(self, product: str, order_depth: OrderDepth) -> list[Order]:
        orders: list[Order] = []

        best_ask = self.get_best_ask(order_depth)
        if best_ask == -1:
            return orders
        else:
            best_ask_volume = order_depth.sell_orders[best_ask]
            if best_ask < PRICES[product]:
                volume = min(best_ask_volume, SINGLE_TRADE_SIZE)
                orders.append(Order(product, best_ask, volume))
                print("-----buy: ", product, "-----")
                # print("BUY", volume, "x", best_ask)

        best_bid = self.get_best_bid(order_depth)
        if best_bid == -1:
            return orders
        else:
            best_bid_volume = order_depth.buy_orders[best_bid]
            if best_bid > PRICES[product]:
                volume = min(best_bid_volume, SINGLE_TRADE_SIZE)
                orders.append(Order(product, best_bid, -volume))
                print("-----sell: ", product, "-----")
                # print("SELL", volume, "x", best_bid)

        return orders

    def print_pol(self, own_trades, position, order_depths) -> None:
        if len(own_trades.keys()) == 0:
            print("\nprofit or loss: ", self.profit)
            return

        for product in own_trades.keys():
            trades = own_trades[product]
            for trade in trades:
                pol = trade.price * trade.quantity
                if trade.buyer == 'SUBMISSION':
                    # spent money
                    self.profit -= pol
                elif trade.seller == 'SUBMISSION':
                    # gained money
                    self.profit += pol

        for product in position.keys():
            pos = position[product]
            order_depth = order_depths[product]
            if pos > 0:
                # need to sell
                price = self.get_best_bid(order_depth)
                self.profit += price * pos
            elif pos < 0:
                # need to buy
                price = self.get_best_ask(order_depth)
                self.profit -= price * pos

        print("\nprofit or loss: ", self.profit)

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        result = {}

        position = state.position
        own_trades = state.own_trades
        order_depths = state.order_depths

        self.print_pol(own_trades, position, order_depths)
        print("\nposition: ", position)

        for product in order_depths.keys():
            if position.keys().__contains__(product):
                if abs(position[product]) + SINGLE_TRADE_SIZE <= LIMITS[product]:
                    order_depth: OrderDepth = order_depths[product]
                    orders = self.market_making(product, order_depth)
                    orders += self.long_short_position(product, order_depth)
                    result[product] = orders
            else:
                order_depth: OrderDepth = order_depths[product]
                orders = self.market_making(product, order_depth)
                orders += self.long_short_position(product, order_depth)
                result[product] = orders

        return result
