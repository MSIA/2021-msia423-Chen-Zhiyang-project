import logging.config
import sys

from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import linear_kernel

logger = logging.getLogger(__name__)


def kmeans_model(data, droplist, clust_col='cluster', n_cluster=20, seed=423):
    """ Standardize the data and train kmeans model.

    Args:
        data (:obj:`pandas.DataFrame`): recipe clean data
        droplist (list): list of columns to drop
        clust_col (str): output cluster string name
        n_cluster (int): number of clusters to create, default = 20
        seed (int): random state of kmeans model

    Returns:
        data (:obj:`pandas.DataFrame`): standardized data with cluster info
    """
    # standardize data
    prep_data = data.drop(droplist, axis=1)
    train_data = preprocessing.StandardScaler().fit(prep_data).transform(prep_data)
    data[prep_data.columns] = train_data
    logger.debug("data standardized.")

    # train kmeans model
    kmeans = KMeans(n_clusters=n_cluster, random_state=seed).fit(train_data)
    data[clust_col] = kmeans.predict(train_data)
    logger.debug("kmeans model trained and data predicted.")
    return data


def recommend(cluster_data, name=None, idx=None, id_col='id', name_col='name', clust_col='cluster', top_n=10):
    """ get top n recommendations.

    Args:
        cluster_data (:obj:`pandas.DataFrame`): data with kmeans result
        name (str): name of the recipe. default = none
        idx (int): index of the recipe. default = none
        id_col (str): name of the recipe id column. default = 'id'
        name_col (str): name of the recipe name column. default = 'name'
        clust_col (str): cluster string name
        top_n (int): number of top recipes to return. default = 10

    Returns:
        items_ids (list): list of ids of the returned recipes
        items_names (list): list of names of the returned recipes
    """
    # data preparation
    if name:
        target = cluster_data[cluster_data[name_col] == name]
        idx = target.index[0]
    elif idx:
        target = cluster_data[cluster_data[id_col] == idx]
    else:
        logger.error('need either name or index of the recipe.')
        sys.exit(1)

    drop_list = [id_col, name_col, clust_col]
    all_data = cluster_data.drop(drop_list, axis=1)
    target = target.drop(drop_list, axis=1)

    # calculate distance
    cosine_sim = linear_kernel(target, all_data)

    # get result
    idx_list = cosine_sim.argsort()[0]
    index = idx_list[idx_list != idx][-top_n:][::-1]
    item_info = cluster_data.iloc[index]
    item_names = list(item_info[name_col])
    item_ids = list(item_info[id_col])

    return item_ids, item_names
