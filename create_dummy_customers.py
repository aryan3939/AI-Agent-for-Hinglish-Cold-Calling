import pandas as pd
import random

# Generate dummy customer data
customers = []
for i in range(1, 101):
    order_id = f"ORD{i:04d}"  # Format as ORD0001, ORD0002, etc.
    name = f"Customer {i}"
    
    # Randomly decide if the order is Paid or Pending
    status = random.choice(["Paid", "Pending"])
    
    # If status is "Paid", amount due is 0, otherwise assign a random amount
    amount_due = 0 if status == "Paid" else random.choice([500, 1000, 2000, 5000, 10000])
    
    email = f"customer{i}@example.com"

    customers.append([order_id, name, amount_due, status, email])

# Create DataFrame
df = pd.DataFrame(customers, columns=["Order ID", "Customer Name", "Amount Due", "Status", "Email"])

# Save to CSV
df.to_csv("customer_orders.csv", index=False)

print(" Dummy customer orders data generated successfully: customer_orders.csv")
