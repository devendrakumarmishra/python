import numpy as np
from sklearn.linear_model import LogisticRegression

# X = number of suspicious words
X = np.array([[1], [2], [4], [5], [10], [12]])
# y = 0 (not spam), 1 (spam)
y = np.array([0, 0, 0, 1, 1, 1])

model = LogisticRegression()
model.fit(X, y)

# Test email with 6 suspicious words
test = np.array([[6]])
prediction = model.predict(test)

print("Spam?" , "YES" if prediction[0] == 1 else "NO")