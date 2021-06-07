import logging.config
from ast import literal_eval

import pandas as pd

logger = logging.getLogger(__name__)


def __clean_up(row, inglist, similarlist):
    """ Clean up recipe ingredients using given lists of info.

    Args:
        row (list): row of dataframe
        inglist (list): list of food to generalize
        similarlist (dict): dictionary of food to replace

    Returns:
        row (list): cleaned up row
    """
    for i, item in enumerate(row):
        for gen in inglist:
            if gen in item:
                row[i] = gen
        item = row[i]
        for sim in similarlist:
            if sim in item:
                row[i] = similarlist[sim]
    return row


def __prep_ingredient(data, similarlist, inglist, ing_col='ingredients'):
    """ Prepare ingredient columns for recipe data

    Args:
        data (:obj:`pandas.DataFrame`): recipe raw data
        similarlist (dict): dictionary of food to replace
        inglist (list): list of food to be kept
        ing_col (str): name of the ingredient column. Default = 'ingredients'

    Returns:
        recipes (:obj:`pandas.DataFrame`): recipe data with added ingredient columns
    """
    recipes = data.copy()
    recipes[ing_col] = data[ing_col].apply(literal_eval)
    ingred = recipes[ing_col].apply(lambda x: __clean_up(x, inglist, similarlist))

    # add ingredient columns
    for ing in inglist:
        recipes[ing] = ingred.apply(lambda x: 1 if ing in x else 0)
    return recipes


def __prep_tag(data, taglist, tag_col='tags'):
    """ Prepare tag columns for recipe data.

    Args:
        data (:obj:`pandas.DataFrame`): recipe raw data
        taglist (list): list of tags to be kept
        tag_col (str): name of the tag column. Default = 'tags'

    Returns:
        recipes (:obj:`pandas.DataFrame`): recipe data with added tags columns
    """
    recipes = data.copy()
    recipes[tag_col] = data[tag_col].apply(literal_eval)

    # add tags columns
    for tag in taglist:
        recipes[tag] = recipes[tag_col].apply(lambda x: 1 if tag in x else 0)
    return recipes


def __prep_nutrition(data, nutritionlist, nutr_col='nutrition'):
    """ Add nutrition columns to the data.

    Args:
        data (:obj:`pandas.DataFrame`): recipe raw data
        nutritionlist (list): list of nutrition
        nutr_col (str): name of the nutrition column. Default = 'nutrition'

    Returns:
        recipes (:obj:`pandas.DataFrame`): recipe data with added nutrition columns
    """
    recipes = data.copy()
    recipes[nutr_col] = data[nutr_col].apply(literal_eval)

    # add nutrition columns
    for i, nutr in enumerate(nutritionlist):
        recipes[nutr] = recipes[nutr_col].apply(lambda x: x[i])
    return recipes


def prepare_recipe(data, config):
    """ Pipeline to prepare recipe data for modelling.

    Args:
        data (:obj:`pandas.DataFrame`): recipe raw data
        config (dict): configuration dictionary

    Returns:
        recipes (:obj:`pandas.DataFrame`): cleaned recipe data

    """
    recipes = data.dropna()
    recipes = __prep_ingredient(recipes, **config['prep_ingredient'])
    logging.debug("ingredient columns prepared.")
    recipes = __prep_tag(recipes, **config['prep_tag'])
    logging.debug("tag columns prepared.")
    recipes = __prep_nutrition(recipes, **config['prep_nutrition'])
    logging.debug("nutrition columns prepared.")

    recipes[config['step_col']] = recipes[config['step_col']].apply(literal_eval)
    for col in config['strlist']:
        recipes[col] = recipes[col].apply(lambda x: ', '.join(x))
    logging.debug("list columns changed to string.")
    recipes = recipes.dropna()
    return recipes


def get_recipe(prepared_recipe, droplist):
    """ Get reciple data ready for model

    Args:
        prepared_recipe (:obj:`pandas.DataFrame`): cleaned recipe data
        droplist (list): list of columns to drop

    Returns:
        final_data (:obj:`pandas.DataFrame`): recipe data ready for model

    """
    final_data = prepared_recipe.drop(droplist, axis=1)
    return final_data


def get_rds(prepared_recipe, collist):
    """ Prepare data to be put into rds.

    Args:
        prepared_recipe (:obj:`pandas.DataFrame`): cleaned recipe data
        collist (list): list of columns to keep
        strlist (list): list of columns to change to string
        step_col (str): name of step column to be clean. default = 'steps'

    Returns:
        data (:obj:`pandas.DataFrame`): data ready to be put into rds

    """
    data = prepared_recipe[[col for col in collist]]
    return data


def prepare_interactions(rawdata, uid_col='user_id', rid_col='recipe_id', rating_col='rating', list_col='list',
                         count_col='count', top_n=10):
    """ clean up interaction data for evaluation

    Args:
        rawdata (:obj:`pandas.DataFrame`): raw interaction data
        uid_col (str): name of user id column. default = user_id
        rid_col (str): name of recipe id column. default = recipe_id
        rating_col (str): name of rating column. default = rating
        list_col (str): name of list of ratings column. default = list
        count_col (str): name of count column. default = count
        top_n (int): keep active users with more than n ratings

    Returns:
        ratinglist (:obj:`pandas.DataFrame`): cleaned interaction data

    """
    interactions = rawdata[[uid_col, rid_col, rating_col]]
    ratinglist = pd.DataFrame(interactions.groupby(uid_col)[[rid_col, rating_col]]
                              .apply(lambda x: sorted(list(x.values.tolist()), key=lambda y: y[1], reverse=True)),
                              columns=[list_col])
    ratinglist[count_col] = ratinglist.apply(lambda x: len(x[list_col]), axis=1)
    ratinglist = ratinglist[ratinglist[count_col] > top_n].sort_values('count', ascending=False)

    return ratinglist
