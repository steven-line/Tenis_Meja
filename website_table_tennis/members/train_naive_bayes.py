import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

X_train = [
    'Promo besar diskon 50% semua barang', 
    'Jadwal latihan ping pong minggu ini',
    'Dapatkan promo menarik hanya hari ini',
    'Latihan tenis meja setiap Senin dan Kamis',
    'Mau dapatkan uang gratis? Klik sekarang!',
    'Senin latihan ping pong di UWIKA',
]
y_train = [1, 0, 1, 0, 1, 0]  # 1: spam, 0: non-spam

vectorizer = CountVectorizer()
X_train_features = vectorizer.fit_transform(X_train)

model = MultinomialNB()
model.fit(X_train_features, y_train)

joblib.dump(model, 'naive_bayes_model.pkl')
joblib.dump(vectorizer, 'count_vectorizer.pkl')

print("Model Naive Bayes telah dilatih dan disimpan.")
