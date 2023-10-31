import numpy as np
from sentence_transformers import SentenceTransformer, util

t_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


def compare_two(article_array):
    embedding_a1 = t_model.encode(article_array[0], convert_to_tensor=True)
    embedding_a2 = t_model.encode(article_array[1], convert_to_tensor=True)
    return str(util.pytorch_cos_sim(embedding_a1, embedding_a2).numpy()[0][0])


def compare_relative(article_array):
    embeddings = [t_model.encode(a, convert_to_tensor=True) for a in article_array]
    embedding_array = [np.array(e) for e in embeddings]
    return np.corrcoef(embedding_array)


def compare_with_target(article_target, compare_array):
    embedding_target = t_model.encode(article_target, convert_to_tensor=True)
    embeddings_compare = [t_model.encode(a, convert_to_tensor=True) for a in compare_array]
    result = [util.pytorch_cos_sim(embedding_target, compare).numpy()[0][0] for compare in embeddings_compare]
    return str(result)
