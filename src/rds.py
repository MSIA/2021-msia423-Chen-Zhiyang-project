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
    """Create a data model for the database to be set up for capturing recipes
    """

    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=False, nullable=False)
    description = Column(String(6500), unique=False, nullable=False)
    minutes = Column(Integer, unique=False, nullable=False)
    top_tags = Column(String(100), unique=False, nullable=False)
    calories = Column(Numeric, unique=False, nullable=False)
    total_fat = Column(Numeric, unique=False, nullable=False)
    sugar = Column(Numeric, unique=False, nullable=False)
    sodium = Column(Numeric, unique=False, nullable=False)
    protein = Column(Numeric, unique=False, nullable=False)
    saturated_fat = Column(Numeric, unique=False, nullable=False)
    carbs = Column(Numeric, unique=False, nullable=False)
    num_of_ingredients = Column(Integer, unique=False, nullable=False)
    all_ingredients = Column(String(1000), unique=False, nullable=False)
    num_of_steps = Column(Integer, unique=False, nullable=False)
    steps = Column(String(12000), unique=False, nullable=False)

    def __repr__(self):
        """printed output."""
        return '<Recipe %r, id %r>' % self.name, self.id


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

        Returns: None
        """
        self.session.close()

    def print_table(self) -> None:
        """print table recipes."""
        query = "SELECT * FROM recipes"
        df = pd.read_sql(query, con=self.engine)
        print(df)

    def add_recipe(self, id: int, name: str, description: str, minutes: int, top_tags: str,
                   calories: float, total_fat: float, sugar: float, sodium: float,
                   protein: float, saturated_fat: float, carbs: float,
                   num_of_ingredients: int, all_ingredients: str, num_of_steps: int, steps: str) -> None:
        """Seeds an existing database with additional recipes.

        Args:
            id (int): recipe id
            name (str): recipe name
            description (str): recipe description
            minutes (int): recipe cook time
            top_tags (str): top tags for the recipe
            calories (float): calories in the recipe
            total_fat (float): total amount of fat in the recipe
            sugar (float): amount of sugar in the recipe
            sodium (float): amount of sodium in the recipe
            protein (float): amount of protein in the recipe
            saturated_fat (float): amount of saturated fat in the recipe
            carbs (float): amount of carbs in the recipe
            num_of_ingredients (int): number of ingredients for the recipe
            all_ingredients (str): ingredients description
            num_of_steps (int): number of steps in the recipe
            steps (str): steps description

        Returns:
            None
        """

        session = self.session
        recipe = Recipe(id=id, name=name, description=description, minutes=minutes, top_tags=top_tags,
                        calories=calories, total_fat=total_fat, sugar=sugar, sodium=sodium,
                        protein=protein, saturated_fat=saturated_fat, carbs=carbs,
                        num_of_ingredients=num_of_ingredients,
                        all_ingredients=all_ingredients, num_of_steps=num_of_steps, steps=steps)
        session.add(recipe)
        session.commit()
        logger.info("recipe %s of id %s, added to database", name, id)
