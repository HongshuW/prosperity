LOWEST_CRATE_PRICE = 9000
HIGHEST_CRATE_PRICE = 11000

CRATES_COUNT = 300
CRATE_SIZE = 4

PINEAPPLE_SINGLE_PRICE = 2500

"""Set a price per crate for your stock of 300 crates of Pineapples that is within the 50% lowest offers 
of our archipelago, but above the average price of those offerings."""
def main():
    reference_price = PINEAPPLE_SINGLE_PRICE * CRATE_SIZE
    median_price = (LOWEST_CRATE_PRICE + HIGHEST_CRATE_PRICE) / 2
    print("reference price: ", reference_price)
    print("median price: ", median_price)

    max_profit = -11000
    best_price = 0

    for price in range(9000, 11000):
        expected = 0
        for average_price in range(9000, 11001):
            difference = abs(average_price - reference_price)
            if difference == 0:
                weight = 2
            else:
                weight = 1 / difference
            pol = price - average_price
            expected += pol * weight

        difference = price - LOWEST_CRATE_PRICE
        if difference == 0:
            weight = 2
        else:
            weight = 1 / difference
        expected *= weight

        if expected > max_profit:
            max_profit = expected
            best_price = price

    print("price: ", best_price)
    print("profit: ", max_profit)

if __name__ == "__main__":
    main()