import traceback
import logging.config
from ast import literal_eval
from flask import Flask
from flask import render_template, request, redirect, url_for
from src.rds import Recipe, RecipeManager
from src.model import recommend
import pandas as pd
from config.flaskconfig import MODEL_DATA_PATH

from config.flaskconfig import LOGGING_CONFIG

# logging.config.fileConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

recipe_manager = RecipeManager(app)
model = pd.read_csv(MODEL_DATA_PATH)
logger.debug('Model loaded.')

@app.route('/', methods=['GET', 'POST'])
def index():
    """ Main view that allow for searching for a recipe that would like to find substitutes.

    Args: None

    Returns:
        rendered html template or redirect url

    """
    if request.method == 'GET':
        try:
            query = recipe_manager.session.query(Recipe.name).all()
            recipe_name = [row[0] for row in query]
            return render_template('index.html', recipe_name=recipe_name)
        except:
            traceback.print_exc()
            logger.warning("error encountered, error page returned.")
            return render_template('error.html')

    if request.method == 'POST':
        myRecipe = request.form.get('myRecipe')
        url_to_handle_request = url_for('recommendation', current_recipe=myRecipe)
        return redirect(url_to_handle_request)


@app.route('/rec-<current_recipe>')
def recommendation(current_recipe):
    """ List top 10 recommended substitutions.

    Args:
        current_recipe (str): recipe entered by user

    Returns:
        rendered html template

    """
    try:
        current_info = recipe_manager.session.query(Recipe).filter(Recipe.name == current_recipe).first()

        if current_info is None:
            logger.warning("recipe not found, not found page returned.")
            return render_template('not_found.html', user_input=current_recipe)
        else:
            # model

            _, recommended_recipes = recommend(model, name=current_recipe)
            print(recommended_recipes)
            return render_template('recommend.html', current_recipe=current_recipe,
                                   recommended_recipes=recommended_recipes)

    except:
        traceback.print_exc()
        logger.warning("error encountered, error page returned.")
        return render_template('error.html')


@app.route('/<myRecipe>')
def recipe_page(myRecipe):
    """ Show detailed of the recipe.

    Args:
        myRecipe (str): Recipe to be displayed

    Returns:
        rendered html template
    """
    try:
        result = recipe_manager.session.query(Recipe).filter(Recipe.name == myRecipe).first()

        if result is None:
            logger.warning("Recipe not found, not found page returned.")
            return render_template('not_found.html', user_input=myRecipe)
        else:
            steps = literal_eval(result.steps)
            logger.debug("Recipe page accessed")
            return render_template('recipe.html', recipe=result, steps=steps)
    except:
        traceback.print_exc()
        logger.warning("Error encountered, error page returned.")
        return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])
