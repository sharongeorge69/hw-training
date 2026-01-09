#create iventory with items and their prices

inventory = {
    "apple": 90.0,
    "milk": 32.0,
    "orange": 40.0
}
#create a list named cart with selected item names 

cart = ["apple","milk","banana"]

print("Data Types :")
print("Type of inventory:", type(inventory))
print("Type of one price value:", type(inventory["apple"]))
print("Type of cart:", type(cart))

total_bill =0
for item in cart:
    if item in inventory:
        price = inventory[item]
        total_bill+=price
    else:
        print(f"{item} is not in inventory")
print(f"Total Bill = {total_bill}")

# Convert cart list to set (unique items)
unique_cart_items = set(cart)

# Create product categories tuple
categories = ("fruits", "dairy", "bakery")

# Add an item with None price
inventory["salt"] = None
print(type(inventory["salt"]))


# Boolean variable for discount
is_discount_applied = False

#Apply discount condition
if total_bill > 100:
    is_discount_applied = True

# Formated bill
print()
print(f"Items in cart       : {cart}")
print(f"Total Bill Amount   : {total_bill}")
print(f"Discount Applied    : {is_discount_applied}")