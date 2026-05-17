from sklearn.cluster import DBSCAN


def cluster_accounts(features, eps=0.75, min_samples=2):
    model = DBSCAN(
        eps=eps,
        min_samples=min_samples,
        metric="cosine"
    )

    labels = model.fit_predict(features)

    return labels
