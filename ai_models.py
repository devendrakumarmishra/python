# ============================================================
# AI MODELS MODULE — All AI/ML logic in one place
# ============================================================
# This file contains all the AI models used in our Flask app.
# We keep them separate from app.py to keep code organized.
#
# Libraries used:
# - numpy: For working with numbers and arrays (the "math" library of AI)
# - scikit-learn: The most popular ML library for beginners
# - textblob: Simple library for text analysis (sentiment, etc.)
# ============================================================

import numpy as np
# numpy (Numerical Python) — handles arrays and math operations
# AI models work with numbers, not text. numpy helps us organize those numbers.
# Example: np.array([1, 2, 3]) creates a number array

from sklearn.linear_model import LinearRegression, LogisticRegression
# LinearRegression — predicts a NUMBER (price, marks, temperature)
#   "Linear" means it draws a straight line through data points
#   Example: More hours studied → Higher marks (a line going up)
#
# LogisticRegression — predicts a CATEGORY (yes/no, spam/not spam)
#   Despite the name "regression", it's used for classification
#   Example: Is this email spam? YES or NO

from textblob import TextBlob
# TextBlob — makes text analysis super easy
# It can detect sentiment (positive/negative), correct spelling, etc.
# Behind the scenes, it uses NLP (Natural Language Processing)


# ============================================================
# MODEL 1: SENTIMENT ANALYSIS
# ============================================================
# What is Sentiment Analysis?
# It reads text and determines if it's POSITIVE, NEGATIVE, or NEUTRAL.
# Used by companies to analyze customer reviews, social media, etc.
#
# How TextBlob does it:
# - It has a dictionary of words with pre-assigned sentiment scores
# - "love" = +1.0 (very positive), "hate" = -1.0 (very negative)
# - It averages the scores of all words in your text
# ============================================================

def analyze_sentiment(text):
    """
    Takes a text string and returns sentiment analysis results.

    Returns a dictionary with:
    - polarity: -1.0 (very negative) to +1.0 (very positive)
    - subjectivity: 0.0 (factual) to 1.0 (opinion-based)
    - sentiment: 'Positive', 'Negative', or 'Neutral' (human-readable label)

    Example:
        analyze_sentiment("I love this product!")
        → {'polarity': 0.5, 'subjectivity': 0.6, 'sentiment': 'Positive'}
    """
    # Create a TextBlob object — this processes the text internally
    blob = TextBlob(text)

    # .sentiment returns two values:
    # polarity = how positive or negative (-1 to +1)
    # subjectivity = how opinion-based (0 = fact, 1 = opinion)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    # Convert the number to a human-readable label
    if polarity > 0.1:
        sentiment = 'Positive 😊'
    elif polarity < -0.1:
        sentiment = 'Negative 😞'
    else:
        sentiment = 'Neutral 😐'

    return {
        'polarity': round(polarity, 2),         # Round to 2 decimal places
        'subjectivity': round(subjectivity, 2),
        'sentiment': sentiment
    }


# ============================================================
# MODEL 2: TEXT SUMMARIZER
# ============================================================
# What is Text Summarization?
# It takes a long text and gives you a shorter version with key points.
#
# Our approach: EXTRACTIVE summarization (simple but effective)
# - Split text into sentences
# - Score each sentence based on important words
# - Pick the top-scoring sentences
#
# There's also ABSTRACTIVE summarization (used by ChatGPT) which
# generates NEW sentences, but that requires deep learning models.
# ============================================================

def summarize_text(text, num_sentences=3):
    """
    Takes a long text and returns the most important sentences.

    How it works:
    1. Split text into sentences
    2. Split into words and count word frequency
    3. Score each sentence based on how many important words it has
    4. Return top N sentences as the summary

    Parameters:
    - text: The long text to summarize
    - num_sentences: How many sentences to include in summary (default: 3)
    """
    # Step 1: Use TextBlob to split text into sentences
    blob = TextBlob(text)
    sentences = blob.sentences
    # blob.sentences automatically detects sentence boundaries (., !, ?)

    # If text is already short, return it as-is
    if len(sentences) <= num_sentences:
        return text

    # Step 2: Count how often each word appears (word frequency)
    # Common words appear a lot, but "important" words appear in key sentences
    word_freq = {}
    for word in blob.words.lower():
        # blob.words splits text into individual words
        # .lower() converts to lowercase so "The" and "the" count together

        # Skip very short words (like "a", "is", "the" — not meaningful)
        if len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
            # .get(word, 0) returns current count or 0 if word is new
            # Then +1 adds one more occurrence

    # Step 3: Score each sentence
    # A sentence with more frequent/important words gets a higher score
    sentence_scores = {}
    for sentence in sentences:
        score = 0
        for word in sentence.words.lower():
            if word in word_freq:
                score += word_freq[word]
                # Add the word's frequency to the sentence's score
        sentence_scores[sentence] = score

    # Step 4: Get the top N sentences (sorted by score, highest first)
    ranked = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    # sorted() with key=sentence_scores.get sorts sentences by their scores
    # reverse=True = highest score first

    # Take only the top N sentences
    top_sentences = ranked[:num_sentences]

    # Re-order sentences by their original position (so summary reads naturally)
    top_sentences.sort(key=lambda s: sentences.index(s))
    # lambda s: sentences.index(s) = for each sentence, find its original position

    # Join sentences back into a paragraph
    summary = ' '.join(str(s) for s in top_sentences)
    return summary


# ============================================================
# MODEL 3: SPAM DETECTOR (Machine Learning)
# ============================================================
# What is a Spam Detector?
# It classifies text as SPAM or NOT SPAM using Logistic Regression.
#
# How Logistic Regression works:
# 1. We give it examples: "5 suspicious words → spam", "1 word → not spam"
# 2. It learns a DECISION BOUNDARY (a threshold)
# 3. For new text, it counts suspicious words and classifies
#
# This is SUPERVISED LEARNING — we provide labeled examples to train the model.
# "Supervised" because we supervise the training by giving correct answers.
# ============================================================

# Training data for spam detection
# X = number of suspicious words in email
# y = 0 (not spam), 1 (spam)
_spam_X = np.array([[0], [1], [2], [3], [5], [7], [8], [10], [12], [15]])
_spam_y = np.array([0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
# Pattern: emails with 5+ suspicious words tend to be spam

# Train the model once when this file is loaded (not every request)
spam_model = LogisticRegression()
spam_model.fit(_spam_X, _spam_y)
# .fit() = "learn from this data"
# After this, the model has learned the pattern

# List of words commonly found in spam emails
SPAM_WORDS = [
    'free', 'win', 'winner', 'cash', 'prize', 'congratulations',
    'click', 'subscribe', 'offer', 'deal', 'discount', 'limited',
    'urgent', 'act now', 'buy now', 'order now', 'money', 'credit',
    'loan', 'earn', 'income', 'investment', 'bonus', 'guarantee',
    'no cost', 'risk free', 'cheap', 'bargain', 'lowest price'
]


def detect_spam(text):
    """
    Takes email/message text and predicts if it's spam.

    How it works:
    1. Count how many spam words appear in the text
    2. Feed that count to our trained Logistic Regression model
    3. Model returns: spam (1) or not spam (0)

    Also returns probability — model's confidence level.

    Example:
        detect_spam("Congratulations! You won free cash prize!")
        → {'is_spam': True, 'confidence': 0.95, 'spam_words_found': [...]}
    """
    text_lower = text.lower()

    # Count how many spam words are in the text
    found_words = [word for word in SPAM_WORDS if word in text_lower]
    # List comprehension: creates a list of spam words found in the text
    # This is the same as:
    # found_words = []
    # for word in SPAM_WORDS:
    #     if word in text_lower:
    #         found_words.append(word)

    spam_word_count = len(found_words)

    # Use the trained model to predict
    prediction = spam_model.predict(np.array([[spam_word_count]]))[0]
    # np.array([[spam_word_count]]) = model expects a 2D array
    # [0] gets the first (and only) prediction

    # Get probability (how confident the model is)
    probability = spam_model.predict_proba(np.array([[spam_word_count]]))[0]
    # predict_proba returns [prob_not_spam, prob_spam]
    # Example: [0.15, 0.85] means 85% chance it's spam

    return {
        'is_spam': bool(prediction == 1),
        'confidence': round(float(max(probability)) * 100, 1),
        # max(probability) = the higher probability (model's confidence)
        # * 100 converts 0.85 to 85.0 (percentage)
        'spam_words_found': found_words,
        'spam_word_count': spam_word_count
    }


# ============================================================
# MODEL 4: STUDENT MARKS PREDICTOR (Linear Regression)
# ============================================================
# What is Linear Regression?
# It finds a straight line that best fits the data points.
#
# Imagine plotting dots on a graph:
#   X-axis = hours studied
#   Y-axis = marks scored
# Linear Regression draws the BEST line through those dots.
# Then for a NEW X value, it follows the line to predict Y.
#
# The "line" equation: y = mx + b
#   m = slope (how steep the line is)
#   b = intercept (where the line crosses Y-axis)
# scikit-learn calculates m and b automatically from training data.
# ============================================================

# Training data
_marks_X = np.array([[1], [2], [3], [4], [5], [6], [7], [8]])
_marks_y = np.array([35, 50, 65, 70, 80, 85, 90, 95])
# Pattern: more hours → higher marks (positive correlation)

marks_model = LinearRegression()
marks_model.fit(_marks_X, _marks_y)


def predict_marks(hours):
    """
    Predicts student marks based on hours studied.

    Uses Linear Regression — draws a line through known data points
    and uses that line to predict marks for new hour values.

    Example:
        predict_marks(6)
        → {'hours': 6, 'predicted_marks': 84.5, 'grade': 'A'}
    """
    prediction = marks_model.predict(np.array([[hours]]))[0]
    # Model internally calculates: marks = slope * hours + intercept

    # Assign a grade based on predicted marks
    if prediction >= 90:
        grade = 'A+'
    elif prediction >= 80:
        grade = 'A'
    elif prediction >= 70:
        grade = 'B'
    elif prediction >= 60:
        grade = 'C'
    elif prediction >= 50:
        grade = 'D'
    else:
        grade = 'F'

    return {
        'hours': hours,
        'predicted_marks': round(prediction, 1),
        'grade': grade,
        # These show the line equation the model learned:
        'model_slope': round(marks_model.coef_[0], 2),
        # coef_ = the slope (m in y = mx + b)
        # "For every extra hour, marks increase by this much"
        'model_intercept': round(marks_model.intercept_, 2)
        # intercept_ = the starting point (b in y = mx + b)
        # "If you study 0 hours, you'd get approximately this many marks"
    }


# ============================================================
# MODEL 5: HOUSE PRICE PREDICTOR (Multiple Linear Regression)
# ============================================================
# What is Multiple Linear Regression?
# Same as Linear Regression but with MULTIPLE inputs (features).
#
# Simple Linear Regression: price = m * area + b         (1 input)
# Multiple Linear Regression: price = m1*area + m2*bedrooms + b  (2+ inputs)
#
# Each input (feature) gets its own slope/weight, showing how much
# it contributes to the final prediction.
# ============================================================

# Training data: [square_feet, bedrooms]
_house_X = np.array([
    [800, 1],
    [1000, 2],
    [1200, 2],
    [1500, 3],
    [1800, 3],
    [2000, 3],
    [2200, 4],
    [2500, 4],
    [3000, 5],
    [3500, 5]
])
_house_y = np.array([
    100000, 150000, 170000, 200000, 240000,
    280000, 310000, 350000, 420000, 480000
])

house_model = LinearRegression()
house_model.fit(_house_X, _house_y)


def predict_house_price(square_feet, bedrooms):
    """
    Predicts house price based on area and number of bedrooms.

    Uses Multiple Linear Regression — considers multiple factors
    to make a more accurate prediction.

    Example:
        predict_house_price(2000, 3)
        → {'square_feet': 2000, 'bedrooms': 3, 'predicted_price': 275000}
    """
    prediction = house_model.predict(np.array([[square_feet, bedrooms]]))[0]

    return {
        'square_feet': square_feet,
        'bedrooms': bedrooms,
        'predicted_price': round(prediction, 2),
        'price_formatted': f"${prediction:,.0f}",
        # :,.0f formats number with commas: 275000 → $275,000
        'feature_weights': {
            'per_sqft': round(house_model.coef_[0], 2),
            # "Each extra square foot adds this much to the price"
            'per_bedroom': round(house_model.coef_[1], 2)
            # "Each extra bedroom adds this much to the price"
        }
    }
