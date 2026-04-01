import numpy as np
from sklearn.linear_model import LinearRegression

# Training Data
# Hours studied
X = np.array([[1], [2], [3], [4], [5]])
# Marks scored
y = np.array([35, 50, 65, 70, 80])

# Create model
model = LinearRegression()

# Train model
model.fit(X, y)

# Predict for 6 hours
hours = np.array([[6]])
prediction = model.predict(hours)

print("Predicted Marks:", prediction[0])