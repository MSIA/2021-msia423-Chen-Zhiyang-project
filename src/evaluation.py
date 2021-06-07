import logging.config
import pandas as pd
import numpy as np
from ast import literal_eval
import src.model as model

logger = logging.getLogger(__name__)


def __get_dcg(row, rating_col, rank_col):
    """ Helper function that calculate DCG for one row.

    Args:
        row (list): row of dataframe
        rating_col (str): name of rating column
        rank_col (str): name of ranking column

    Returns: resulting float of DCG
    """
    return row[rating_col] / np.log2(row[rank_col] if row[rank_col] > 2 else 2)


def __get_idcg(eval_data, rating_col, rank_col, top_n):
    """Calculate IDCG for the given data.

    Args:
        eval_data (:obj:`pandas.DataFrame`): data frame of rating infomation
        rating_col (str): name of rating column
        rank_col (str); name of rank column
        top_n (int): number of recommendations

    Returns:
        idcg (float): calculated IDCG

    """
    ratelist = eval_data.sort_values(rating_col, ascending=False).head(top_n)
    idcglist = ratelist.apply(lambda x: __get_dcg(x, rating_col, rank_col), axis=1)
    idcg = sum(idcglist)
    return idcg


def __get_info(row_list, all_data, id_col):
    """ Get rating information of a given user.

    Args:
        row_list (list): list of recipe, rating pairs
        all_data (:obj:`pandas.DataFrame`): model information
        id_col (str): name of recipe id column

    Returns:
        recipe_id (int): id of the tested recipe
        cluster_data (:obj:`pandas.DataFrame`): dataset of information of all recipes
        info_df (:obj:`pandas.DataFrame`): information of id, rating and rank of recipes

    """
    clust_id_list = [item[0] for item in row_list]
    rating = [item[1] for item in row_list]
    rank = [sorted(rating, reverse=True).index(x) + 1 for x in rating]
    info_df = pd.DataFrame(zip(clust_id_list, rating, rank), columns=['id', 'rating', 'rank'])
    cluster_data = all_data[all_data[id_col].isin(clust_id_list)]
    recipe_id = cluster_data[id_col].iloc[0]
    return recipe_id, cluster_data, info_df


def evaluation(interactions, all_data, clust_col='cluster', list_col='list', rating_col='rating', rank_col='rank',
               id_col="id", top_n=10):
    """ Evaluate model using nDCG

    Args:
        interactions (:obj:`pandas.DataFrame`): cleaned interaction data set
        all_data (:obj:`pandas.DataFrame`): model data
        clust_col (str): name of cluster column. default = 'cluster'
        list_col (str): name of list column. default = 'list'
        rating_col (str): name of rating column. default = 'rating'
        rank_col (str): name of rank column. default = 'rank'
        id_col (str): name of id column. default = 'id'
        top_n (int): recommend top n recipes

    Returns:
        avg_ndcg (float): average nDCG calculated.

    """
    # get recipe info of all users ratings
    interactions[list_col] = interactions[list_col].apply(literal_eval)
    result = interactions[list_col].apply(lambda x: __get_info(x, all_data, id_col))

    # loop to get ndcg for all users
    ndcg_list = []
    for recipe_id, clust_data, info_df in result:
        if len(clust_data) > top_n:
            idxlist, namelist = model.recommend(clust_data, idx=recipe_id, id_col=id_col, clust_col=clust_col,
                                                top_n=top_n)

            # dataset to evaluate
            eval_data = info_df[info_df[id_col] != recipe_id]
            # idcg
            idcg = __get_idcg(eval_data, rating_col, rank_col, top_n)
            # dcg
            resultlist = eval_data[eval_data[id_col].isin(idxlist)]
            dcglist = resultlist.apply(lambda x: __get_dcg(x, rating_col, rank_col), axis=1)
            dcg = sum(dcglist)
            if idcg == 0:
                ndcg = 1
            else:
                ndcg = dcg / idcg
            ndcg_list.append(ndcg)

    # calculate average ndcg
    avg_ndcg = sum(ndcg_list) / len(ndcg_list)
    return avg_ndcg