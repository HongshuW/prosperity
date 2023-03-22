PIZZA = 'PIZZA'
WASABI = 'WASABI'
SNOWBALL = 'SNOWBALL'
SHELL = 'SHELL'

MAX_TRADES = 5

# key: from, value: dictionary of prices
PRICES = {PIZZA: {WASABI: 0.5, SNOWBALL: 1.45, SHELL: 0.75},
          WASABI: {PIZZA: 1.95, SNOWBALL: 3.1, SHELL: 1.49},
          SNOWBALL: {PIZZA: 0.67, WASABI: 0.31, SHELL: 0.48},
          SHELL: {PIZZA: 1.34, WASABI: 0.64, SNOWBALL: 1.98}}

CURRENCIES = [SHELL, WASABI, PIZZA, SNOWBALL]

class GNode:
    def __init__(self, currency: str):
        self.currency: str = currency
        self.value: float = 1
        self.depth: int = 0
        self.parent: GNode = None

    def get_neighbours(self) -> list:
        neighbours = list()
        # add neighbours
        edges = PRICES[self.currency]
        for neighbour_str in edges.keys():
            neighbour_node = GNode(neighbour_str)
            neighbour_node.value = self.value * edges[neighbour_str]
            neighbour_node.depth = self.depth + 1
            neighbour_node.parent = self
            neighbours.append(neighbour_node)
        return neighbours

def main():
    # initialise root
    root = GNode(SHELL)

    # search the path with the highest profit
    max_profit = 1
    best_node: GNode = root
    queue = list()
    queue.append(root)
    while len(queue) > 0:
        node = queue.pop(0)
        if node.depth == 5:
            if node.currency == SHELL:
                # record best node
                if node.value > max_profit:
                    best_node = node
                    max_profit = node.value
        else:
            if node.currency == SHELL:
                # record best node
                if node.value > max_profit:
                    best_node = node
                    max_profit = node.value
            # add neighbours to the queue
            queue = queue + node.get_neighbours()

    path = list()
    current_node = best_node
    while current_node:
        path.append(current_node.currency)
        current_node = current_node.parent
    path.reverse()
    print(path)
    print(max_profit)

if __name__ == "__main__":
    main()