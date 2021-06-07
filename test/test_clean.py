import pandas as pd
import pytest

import src.clean as clean


# __clean_up
def test_clean_up_happy():
    list_in = ['hard-cooked eggs', 'mayonnaise', 'dijon mustard', 'salt-free cajun seasoning',
               'tabasco sauce', 'salt', 'black pepper', 'fresh italian parsley']

    list_true = ['egg', 'mayonnaise', 'dijon mustard', 'salt-free cajun seasoning', 'tabasco sauce',
                 'salt', 'pepper', 'parsley']

    # Compute test output
    inglist = ['pepper', 'onion', 'cheese', 'garlic', 'egg', 'butter', 'flour', 'lemon', 'chicken', 'milk', 'tomato',
               'cream', 'baking', 'vanilla', 'cinnamon', 'parsley', 'apple', 'beef', 'potato', 'chili']
    similarlist = {'lime': 'lemon', 'cheddar': 'cheese', 'mozzarella': 'cheese'}
    list_test = clean.__clean_up(list_in, inglist=inglist, similarlist=similarlist)

    assert list_true == list_test


def test_clean_up_unhappy():
    list_in = pd.DataFrame(['hard-cooked eggs', 'mayonnaise', 'dijon mustard', 'salt-free cajun seasoning',
                            'tabasco sauce', 'salt', 'black pepper', 'fresh italian parsley'], columns=['ingredient'])
    with pytest.raises(KeyError):
        inglist = ['pepper', 'onion', 'cheese', 'garlic', 'egg', 'butter', 'flour', 'lemon', 'chicken', 'milk',
                   'tomato',
                   'cream', 'baking', 'vanilla', 'cinnamon', 'parsley', 'apple', 'beef', 'potato', 'chili']
        similarlist = {'lime': 'lemon', 'cheddar': 'cheese', 'mozzarella': 'cheese'}
        clean.__clean_up(list_in, inglist=inglist, similarlist=similarlist)


# __prep_ingredient
def test_prep_ingredient_happy():
    df_in_values = [['2 day herb marinated pimiento stuffed olives', 101260,
                     "['pimento stuffed olives', 'extra virgin olive oil', 'fresh thyme', 'fresh rosemary', 'garlic', "
                     "'chili flakes', 'fresh lemon juice']",
                     "['15-minutes-or-less', 'time-to-make', 'course', 'preparation', 'occasion', 'appetizers', "
                     "'condiments-etc', 'dinner-party', 'dietary', 'number-of-servings']",
                     '[495.0, 83.0, 2.0, 0.0, 1.0, 37.0, 1.0]'],
                    ['2 hour buns', 100340,
                     "['warm water', 'sugar', 'oil', 'salt', 'fast rising yeast', 'eggs', 'flour']",
                     "['time-to-make', 'course', 'preparation', 'healthy', 'breads', 'rolls-biscuits', 'dietary', "
                     "'low-sodium', 'low-saturated-fat', 'low-in-something', '4-hours-or-less']",
                     '[1127.8, 38.0, 103.0, 26.0, 56.0, 18.0, 64.0]']]
    df_in_columns = ['name', 'id', 'ingredients', 'tags', 'nutrition']

    df_in_index = [0, 1]

    df_in = pd.DataFrame(df_in_values, index=df_in_index, columns=df_in_columns)

    df_true = pd.DataFrame(
        [['2 day herb marinated pimiento stuffed olives', 101260,
          list(['pimento stuffed olives', 'extra virgin olive oil', 'fresh thyme', 'fresh rosemary', 'garlic', 'chili',
                'lemon']),
          "['15-minutes-or-less', 'time-to-make', 'course', 'preparation', 'occasion', 'appetizers', 'condiments-etc', "
          "'dinner-party', 'dietary', 'number-of-servings']",
          '[495.0, 83.0, 2.0, 0.0, 1.0, 37.0, 1.0]', 0, 0, 0, 1, 0, 0, 0,
          1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         ['2 hour buns', 100340,
          list(['warm water', 'sugar', 'oil', 'salt', 'fast rising yeast', 'egg', 'flour']),
          "['time-to-make', 'course', 'preparation', 'healthy', 'breads', 'rolls-biscuits', 'dietary', 'low-sodium', "
          "'low-saturated-fat', 'low-in-something', '4-hours-or-less']",
          '[1127.8, 38.0, 103.0, 26.0, 56.0, 18.0, 64.0]', 0, 0, 0, 0, 1,
          0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
        columns=['name', 'id', 'ingredients', 'tags', 'nutrition', 'pepper', 'onion',
                 'cheese', 'garlic', 'egg', 'butter', 'flour', 'lemon', 'chicken',
                 'milk', 'tomato', 'cream', 'baking', 'vanilla', 'cinnamon', 'parsley',
                 'apple', 'beef', 'potato', 'chili'], index=[0, 1])

    # Compute test output
    inglist = ['pepper', 'onion', 'cheese', 'garlic', 'egg', 'butter', 'flour', 'lemon', 'chicken', 'milk', 'tomato',
               'cream', 'baking', 'vanilla', 'cinnamon', 'parsley', 'apple', 'beef', 'potato', 'chili']
    similarlist = {'lime': 'lemon', 'cheddar': 'cheese', 'mozzarella': 'cheese'}
    df_test = clean.__prep_ingredient(df_in, inglist=inglist, similarlist=similarlist)
    pd.testing.assert_frame_equal(df_test, df_true)


def test_prep_ingredient_unhappy():
    df_in = "I'm not dataframe."
    with pytest.raises(AttributeError):
        inglist = ['pepper', 'onion', 'cheese', 'garlic', 'egg', 'butter', 'flour', 'lemon', 'chicken', 'milk',
                   'tomato',
                   'cream', 'baking', 'vanilla', 'cinnamon', 'parsley', 'apple', 'beef', 'potato', 'chili']
        similarlist = {'lime': 'lemon', 'cheddar': 'cheese', 'mozzarella': 'cheese'}
        df_test = clean.__prep_ingredient(df_in, inglist=inglist, similarlist=similarlist)


# __prep_ingredient
def test_prep_tag_happy():
    df_in_values = [['2 day herb marinated pimiento stuffed olives', 101260,
                     "['pimento stuffed olives', 'extra virgin olive oil', 'fresh thyme', 'fresh rosemary', 'garlic', "
                     "'chili flakes', 'fresh lemon juice']",
                     "['15-minutes-or-less', 'time-to-make', 'course', 'preparation', 'occasion', 'appetizers', "
                     "'condiments-etc', 'dinner-party', 'dietary', 'number-of-servings']",
                     '[495.0, 83.0, 2.0, 0.0, 1.0, 37.0, 1.0]'],
                    ['2 hour buns', 100340,
                     "['warm water', 'sugar', 'oil', 'salt', 'fast rising yeast', 'eggs', 'flour']",
                     "['time-to-make', 'course', 'preparation', 'healthy', 'breads', 'rolls-biscuits', 'dietary', "
                     "'low-sodium', 'low-saturated-fat', 'low-in-something', '4-hours-or-less']",
                     '[1127.8, 38.0, 103.0, 26.0, 56.0, 18.0, 64.0]']]
    df_in_columns = ['name', 'id', 'ingredients', 'tags', 'nutrition']

    df_in_index = [0, 1]

    df_in = pd.DataFrame(df_in_values, index=df_in_index, columns=df_in_columns)

    df_true = pd.DataFrame(
        [['2 day herb marinated pimiento stuffed olives', 101260,
          "['pimento stuffed olives', 'extra virgin olive oil', 'fresh thyme', 'fresh rosemary', 'garlic', "
          "'chili flakes', 'fresh lemon juice']",
          list(['15-minutes-or-less', 'time-to-make', 'course', 'preparation', 'occasion', 'appetizers',
                'condiments-etc', 'dinner-party', 'dietary', 'number-of-servings']),
          '[495.0, 83.0, 2.0, 0.0, 1.0, 37.0, 1.0]', 1, 0, 0, 0, 0, 0, 0,
          0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         ['2 hour buns', 100340,
          "['warm water', 'sugar', 'oil', 'salt', 'fast rising yeast', 'eggs', 'flour']",
          list(['time-to-make', 'course', 'preparation', 'healthy', 'breads', 'rolls-biscuits', 'dietary', 'low-sodium',
                'low-saturated-fat', 'low-in-something', '4-hours-or-less']),
          '[1127.8, 38.0, 103.0, 26.0, 56.0, 18.0, 64.0]', 1, 0, 1, 0, 0,
          0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
        columns=['name', 'id', 'ingredients', 'tags', 'nutrition', 'dietary', 'easy',
                 'low-in-something', 'main-dish', 'meat', 'vegetables', 'north-american',
                 'desserts', 'healthy', 'dinner-party', 'vegetarian', 'beginner-cook',
                 'inexpensive', 'fruit', 'oven', 'eggs-dairy', 'pasta-rice-and-grains',
                 'kid-friendly', 'comfort-food', 'european'], index=[0, 1])

    # Compute test output
    taglist = ['dietary', 'easy', 'low-in-something', 'main-dish', 'meat', 'vegetables', 'north-american', 'desserts',
               'healthy', 'dinner-party', 'vegetarian', 'beginner-cook', 'inexpensive', 'fruit', 'oven', 'eggs-dairy',
               'pasta-rice-and-grains', 'kid-friendly', 'comfort-food', 'european']
    df_test = clean.__prep_tag(df_in, taglist)
    pd.testing.assert_frame_equal(df_test, df_true)


def test_prep_tag_unhappy():
    df_in = "I'm not dataframe."
    with pytest.raises(AttributeError):
        taglist = ['dietary', 'easy', 'low-in-something', 'main-dish', 'meat', 'vegetables', 'north-american',
                   'desserts',
                   'healthy', 'dinner-party', 'vegetarian', 'beginner-cook', 'inexpensive', 'fruit', 'oven',
                   'eggs-dairy',
                   'pasta-rice-and-grains', 'kid-friendly', 'comfort-food', 'european']
        df_test = clean.__prep_tag(df_in, taglist)


# __prep_nutrition
def test_prep_nutrition_happy():
    df_in_values = [['2 day herb marinated pimiento stuffed olives', 101260,
                     "['pimento stuffed olives', 'extra virgin olive oil', 'fresh thyme', 'fresh rosemary', 'garlic', "
                     "'chili flakes', 'fresh lemon juice']",
                     "['15-minutes-or-less', 'time-to-make', 'course', 'preparation', 'occasion', 'appetizers', "
                     "'condiments-etc', 'dinner-party', 'dietary', 'number-of-servings']",
                     '[495.0, 83.0, 2.0, 0.0, 1.0, 37.0, 1.0]'],
                    ['2 hour buns', 100340,
                     "['warm water', 'sugar', 'oil', 'salt', 'fast rising yeast', 'eggs', 'flour']",
                     "['time-to-make', 'course', 'preparation', 'healthy', 'breads', 'rolls-biscuits', 'dietary', "
                     "'low-sodium', 'low-saturated-fat', 'low-in-something', '4-hours-or-less']",
                     '[1127.8, 38.0, 103.0, 26.0, 56.0, 18.0, 64.0]']]
    df_in_columns = ['name', 'id', 'ingredients', 'tags', 'nutrition']

    df_in_index = [0, 1]

    df_in = pd.DataFrame(df_in_values, index=df_in_index, columns=df_in_columns)

    df_true = pd.DataFrame(
        [['2 day herb marinated pimiento stuffed olives', 101260,
          "['pimento stuffed olives', 'extra virgin olive oil', 'fresh thyme', 'fresh rosemary', 'garlic', "
          "'chili flakes', 'fresh lemon juice']",
          "['15-minutes-or-less', 'time-to-make', 'course', 'preparation', 'occasion', 'appetizers', 'condiments-etc',"
          " 'dinner-party', 'dietary', 'number-of-servings']",
          list([495.0, 83.0, 2.0, 0.0, 1.0, 37.0, 1.0]), 495.0, 83.0, 2.0,
          0.0, 1.0, 37.0, 1.0],
         ['2 hour buns', 100340,
          "['warm water', 'sugar', 'oil', 'salt', 'fast rising yeast', 'eggs', 'flour']",
          "['time-to-make', 'course', 'preparation', 'healthy', 'breads', 'rolls-biscuits', 'dietary', 'low-sodium', "
          "'low-saturated-fat', 'low-in-something', '4-hours-or-less']",
          list([1127.8, 38.0, 103.0, 26.0, 56.0, 18.0, 64.0]), 1127.8,
          38.0, 103.0, 26.0, 56.0, 18.0, 64.0]],
        columns=['name', 'id', 'ingredients', 'tags', 'nutrition', 'calories',
       'total_fat', 'sugar', 'sodium', 'protein', 'saturated_fat', 'carbs'], index=[0, 1])

    # Compute test output
    nutritionlist = ['calories', 'total_fat', 'sugar', 'sodium', 'protein', 'saturated_fat', 'carbs']
    df_test = clean.__prep_nutrition(df_in, nutritionlist)
    pd.testing.assert_frame_equal(df_test, df_true)


def test_prep_nutrition_unhappy():
    df_in = "I'm not dataframe."
    with pytest.raises(AttributeError):
        nutritionlist = ['calories', 'total_fat', 'sugar', 'sodium', 'protein', 'saturated_fat', 'carbs']
        df_test = clean.__prep_nutrition(df_in, nutritionlist)
