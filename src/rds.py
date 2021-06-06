import logging.config
import sqlalchemy
import pandas as pd

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class Recipe(Base):

    """Create a data model for the database to be set up for capturing recipes.

    Args:
        Base (:obj:`sqlalchemy.ext.declarative.api.DeclarativeMeta`): declared base

    Returns: None
    """

    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=False, nullable=False)
    description = Column(String(6500), unique=False, nullable=True)
    minutes = Column(Integer, unique=False, nullable=True)
    tags = Column(String(1000), unique=False, nullable=True)
    calories = Column(Numeric, unique=False, nullable=True)
    total_fat = Column(Numeric, unique=False, nullable=True)
    sugar = Column(Numeric, unique=False, nullable=True)
    sodium = Column(Numeric, unique=False, nullable=True)
    protein = Column(Numeric, unique=False, nullable=True)
    saturated_fat = Column(Numeric, unique=False, nullable=True)
    carbs = Column(Numeric, unique=False, nullable=True)
    n_ingredients = Column(Integer, unique=False, nullable=True)
    ingredients = Column(String(1000), unique=False, nullable=False)
    n_steps = Column(Integer, unique=False, nullable=True)
    steps = Column(String(12000), unique=False, nullable=False)

    def __repr__(self):
        """printed output."""
        return '<Recipe %r, id %r>' % (self.name, self.id)


def create_db(engine_string: str) -> None:
    """Create database from provided engine string

    Args:
        engine_string: str - Engine string

    Returns: None

    """
    engine = sqlalchemy.create_engine(engine_string)

    Base.metadata.create_all(engine)
    logger.info("Database created.")


class RecipeManager:

    def __init__(self, app=None, engine_string=None):
        """
        Args:
            app: Flask - Flask app
            engine_string: str - Engine string

        Returns: None
        """
        if app:
            self.db = SQLAlchemy(app)
            self.session = self.db.session
        elif engine_string:
            self.engine = sqlalchemy.create_engine(engine_string)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        else:
            raise ValueError("Need either an engine string or a Flask app to initialize")

    def close(self) -> None:
        """Closes session

        Args: None

        Returns: None
        """
        self.session.close()

    def print_table(self) -> None:
        """print table recipes."""
        query = "SELECT * FROM recipes"
        df = pd.read_sql(query, con=self.engine)
        print(df)

    def add_recipe(self, id: int, name: str, description: str, minutes: int, tags: str,
                   calories: float, total_fat: float, sugar: float, sodium: float,
                   protein: float, saturated_fat: float, carbs: float,
                   n_ingredients: int, ingredients: str, n_steps: int, steps: str) -> None:
        """Seeds an existing database with additional recipes.

        Args:
            id (int): recipe id
            name (str): recipe name
            description (str): recipe description
            minutes (int): recipe cook time
            tags (str): tags for the recipe
            calories (float): calories in the recipe
            total_fat (float): total amount of fat in the recipe
            sugar (float): amount of sugar in the recipe
            sodium (float): amount of sodium in the recipe
            protein (float): amount of protein in the recipe
            saturated_fat (float): amount of saturated fat in the recipe
            carbs (float): amount of carbs in the recipe
            n_ingredients (int): number of ingredients for the recipe
            ingredients (str): ingredients description
            n_steps (int): number of steps in the recipe
            steps (str): steps description

        Returns: None
        """

        session = self.session
        recipe = Recipe(id=id, name=name, description=description, minutes=minutes, tags=tags,
                        calories=calories, total_fat=total_fat, sugar=sugar, sodium=sodium,
                        protein=protein, saturated_fat=saturated_fat, carbs=carbs,
                        n_ingredients=n_ingredients,
                        ingredients=ingredients, n_steps=n_steps, steps=steps)
        session.add(recipe)
        session.commit()
        logger.info("recipe %s of id %s, added to database", name, id)

    def add_recipe_df(self, df_loc) -> None:
        """Seeds an existing database with additional recipes.

        Args:
            df_loc (str): recipe data (csv) location

        Returns: None
        """

        session = self.session
        data = pd.read_csv(df_loc).fillna('').to_dict(orient='records')
        add_list = [Recipe(**rec) for rec in data]
        session.add_all(add_list)
        session.commit()
        logger.info(f'{len(data)} recipes added to database.')
