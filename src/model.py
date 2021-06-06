from sklearn import preprocessing
from sklearn.metrics.pairwise import linear_kernel
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


def kmeans_model(data, droplist, clust_col='cluster', n_cluster=20, seed=423):
    # standardize data
    prep_data = data.drop(droplist, axis=1)
    train_data = preprocessing.StandardScaler().fit(prep_data).transform(prep_data)
    data[prep_data.columns] = train_data

    # train kmeans model
    kmeans = KMeans(n_clusters=n_cluster, random_state=seed).fit(train_data)
    data[clust_col] = kmeans.predict(train_data)
    return data


def get_item(name, cluster_data, id_col = 'id', name_col = 'name'):
    target = cluster_data[cluster_data[name_col] == name]
    idx = target.index[0]
    drop_list = [id_col, name_col]
    all_data = cluster_data.drop(drop_list, axis=1)
    target = target.drop(drop_list, axis=1)
    cosine_sim = linear_kernel(target, all_data)
    idx_list = cosine_sim.argsort()[0]
    index = idx_list[idx_list != idx][-10:-1]
    item_info = cluster_data.iloc[index]
    item_names = list(item_info[name_col])
    return item_info, item_names
