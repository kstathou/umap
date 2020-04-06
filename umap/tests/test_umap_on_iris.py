from umap import UMAP
from sklearn.manifold import trustworthiness
from nose.tools import assert_greater_equal
from scipy import sparse
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score


# ===================================================
#  UMAP Test cases on IRIS Dataset
# ===================================================

# UMAP Trustworthiness on iris
# ----------------------------
def test_umap_trustworthiness_on_iris(iris, iris_model):
    embedding = iris_model.embedding_
    trust = trustworthiness(iris.data, embedding, 10)
    assert_greater_equal(
        trust,
        0.97,
        "Insufficiently trustworthy embedding for" "iris dataset: {}".format(trust),
    )


def test_initialized_umap_trustworthiness_on_iris(iris):
    data = iris.data
    embedding = UMAP(
        n_neighbors=10, min_dist=0.01, init=data[:, 2:], n_epochs=200, random_state=42
    ).fit_transform(data)
    trust = trustworthiness(iris.data, embedding, 10)
    assert_greater_equal(
        trust,
        0.97,
        "Insufficiently trustworthy embedding for" "iris dataset: {}".format(trust),
    )


def test_umap_trustworthiness_on_sphere_iris(iris, ):
    data = iris.data
    embedding = UMAP(
        n_neighbors=10,
        min_dist=0.01,
        n_epochs=200,
        random_state=42,
        output_metric="haversine",
    ).fit_transform(data)
    # Since trustworthiness doesn't support haversine, project onto
    # a 3D embedding of the sphere and use cosine distance
    r = 3
    projected_embedding = np.vstack(
        [
            r * np.sin(embedding[:, 0]) * np.cos(embedding[:, 1]),
            r * np.sin(embedding[:, 0]) * np.sin(embedding[:, 1]),
            r * np.cos(embedding[:, 0]),
        ]
    ).T
    trust = trustworthiness(iris.data, projected_embedding, 10, metric="cosine")
    assert_greater_equal(
        trust,
        0.80,
        "Insufficiently trustworthy spherical embedding for iris dataset: {}".format(
            trust
        ),
    )


# UMAP Transform on iris
# ----------------------
def test_umap_transform_on_iris(iris, iris_selection):
    data = iris.data[iris_selection]
    fitter = UMAP(n_neighbors=10, min_dist=0.01, n_epochs=200, random_state=42).fit(
        data
    )

    new_data = iris.data[~iris_selection]
    embedding = fitter.transform(new_data)

    trust = trustworthiness(new_data, embedding, 10)
    assert_greater_equal(
        trust,
        0.85,
        "Insufficiently trustworthy transform for" "iris dataset: {}".format(trust),
    )


def test_umap_transform_on_iris_modified_dtype(iris, iris_selection):
    data = iris.data[iris_selection]
    fitter = UMAP(n_neighbors=10, min_dist=0.01, random_state=42).fit(data)
    fitter.embedding_ = fitter.embedding_.astype(np.float64)

    new_data = iris.data[~iris_selection]
    embedding = fitter.transform(new_data)

    trust = trustworthiness(new_data, embedding, 10)
    assert_greater_equal(
        trust,
        0.89,
        "Insufficiently trustworthy transform for" "iris dataset: {}".format(trust),
    )


def test_umap_sparse_transform_on_iris(iris, iris_selection):
    data = sparse.csr_matrix(iris.data[iris_selection])
    assert sparse.issparse(data)
    fitter = UMAP(
        n_neighbors=10,
        min_dist=0.01,
        random_state=42,
        n_epochs=100,
        force_approximation_algorithm=True,
    ).fit(data)

    new_data = sparse.csr_matrix(iris.data[~iris_selection])
    assert sparse.issparse(new_data)
    embedding = fitter.transform(new_data)

    trust = trustworthiness(new_data, embedding, 10)
    assert_greater_equal(
        trust,
        0.80,
        "Insufficiently trustworthy transform for" "iris dataset: {}".format(trust),
    )


# UMAP Clusterability on Iris
# ---------------------------
def test_umap_clusterability_on_supervised_iris(supervised_iris_model, iris):
    embedding = supervised_iris_model.embedding_
    clusters = KMeans(3).fit_predict(embedding)
    assert_greater_equal(adjusted_rand_score(clusters, iris.target), 0.95)
