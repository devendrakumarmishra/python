import numpy as np
from sklearn.linear_model import LinearRegression

# Training data
# [square_feet, bedrooms]
X = np.array([
    [1000, 2],
    [1500, 3],
    [2000, 3],
    [2500, 4],
    [3000, 5]
])

# prices
y = np.array([150000, 200000, 250000, 300000, 360000])

model = LinearRegression()
model.fit(X, y)

# predict for 2200 sq ft and 3 bedrooms
test = np.array([[2200, 3]])
prediction = model.predict(test)

print("Predicted House Price:", prediction[0])