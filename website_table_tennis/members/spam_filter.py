import joblib
import re

model = joblib.load('naive_bayes_model.pkl')
vectorizer = joblib.load('count_vectorizer.pkl')

def is_spam_naive_bayes(message):
    """
    Fungsi untuk mendeteksi spam menggunakan model Naive Bayes.
    """
    # Cek apakah jumlah kata lebih dari 200
    if len(message) > 200:
        return True  

    message_features = vectorizer.transform([message])

    prediction = model.predict(message_features)

    # 1 berarti spam, 0 berarti bukan spam
    return prediction[0] == 1
