from sklearn.feature_extraction.text import TfidfVectorizer


def aggregate_texts_by_account(data):
    account_texts = (
        data.groupby("account_id")["clean_text"]
        .apply(lambda texts: " ".join(texts))
        .reset_index()
    )

    return account_texts


def build_text_features(texts):
    vectorizer = TfidfVectorizer(
        max_features=1000,
        min_df=1,
        ngram_range=(1, 2)
    )

    features = vectorizer.fit_transform(texts)

    return features, vectorizer
