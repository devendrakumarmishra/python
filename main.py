from sklearn.linear_model import LinearRegression
import numpy as np

# Training data
size = np.array([500, 700, 900, 1100]).reshape(-1, 1)
price = np.array([150000, 200000, 250000, 300000])

# Create model
model = LinearRegression()

# Train the model
model.fit(size, price)

# Predict price of a 400 sqft house
prediction = model.predict([[400]])
print("Predicted price:", prediction[0])
