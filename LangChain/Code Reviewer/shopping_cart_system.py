# buggy_demo.py

inventory = {
    "apple": {"price": 1.50, "stock": 10},
    "banana": {"price": 0.75, "stock": 5},
    "milk": {"price": 2.00, "stock": 3},
    "bread": {"price": 1.80, "stock": 7},
}

cart = []
total = 0

# Bug 1: wrong key, KeyError crash
print("=== Available Items ===")
for item, details in inventory.items():
    print(f"{item}: ${details['cost']} (stock: {details['stock']})")  # 'cost' should be 'price'

# Bug 2: =+ instead of +=, total never accumulates
print("\n=== Adding Items to Cart ===")
cart.append({"item": "apple", "qty": 3})
cart.append({"item": "banana", "qty": 2})
cart.append({"item": "milk", "qty": 1})

for entry in cart:
    item_name = entry["item"]
    qty = entry["qty"]
    price = inventory[item_name]["price"]
    total =+ price * qty          # resets total every iteration
    print(f"Added {qty}x {item_name} @ ${price} each")

print(f"\nCart Total: ${total}")   # prints only last item's price

# Bug 3: stock never updated after adding to cart
print("\n=== Stock After Purchase ===")
for entry in cart:
    item_name = entry["item"]
    print(f"{item_name} remaining stock: {inventory[item_name]['stock']}")  # still shows original stock

# Bug 4: wrong comparison, discounts high prices instead of low
print("\n=== Applying Discount ===")
for entry in cart:
    item_name = entry["item"]
    price = inventory[item_name]["price"]
    if price >= 1.00:             # should be <= 1.00, discounts expensive items not cheap ones
        discounted = price * 0.9
        print(f"{item_name} discounted to ${discounted:.2f}")
    else:
        print(f"{item_name} no discount applied")

# Bug 5: string concatenation instead of addition
print("\n=== Receipt ===")
item_count = 0
for entry in cart:
    item_count = str(item_count) + str(entry["qty"])   # concatenates "0" + "3" + "2" + "1" = "0321"
print(f"Total items purchased: {item_count}")

# Bug 6: accessing index that doesn't exist
print("\n=== Most Expensive Item ===")
sorted_cart = sorted(cart, key=lambda x: inventory[x["item"]]["price"])
print(f"Most expensive: {sorted_cart[5]['item']}")   # cart only has 3 items, index 5 crashes