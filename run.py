import argparse

import logging.config
from config.flaskconfig import LOGGING_CONFIG

from src.rds import RecipeManager, create_db
from src.s3 import upload_file_to_s3, download_file_from_s3
from config.flaskconfig import SQLALCHEMY_DATABASE_URI, RDS_DATA_PATH, S3_PATHS, LOCAL_RAW_PATHS

logging.config.fileConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)



if __name__ == '__main__':
    # Add parsers for
    # 1. uploading to or downloading from s3
    # 2. creating a database
    # 3. adding all recipes to the database
    # 4. adding one recipe to the database
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for interacting with s3
    sb_s3 = subparsers.add_parser("s3", description="Interacting with s3")
    sb_s3.add_argument('--download', default=False, action='store_true',
                       help="If true, will download from s3.")
    sb_s3.add_argument('--s3path', nargs='+', default=S3_PATHS,
                       help="One or more locations (files) in s3.")
    sb_s3.add_argument('--local_path', nargs='+', default=LOCAL_RAW_PATHS,
                       help="One or more local locations (files).")

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create database")
    sb_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # Sub-parser for ingesting new data
    sb_ingest = subparsers.add_parser("ingest", description="Add data to database")
    sb_ingest.add_argument("-p", "--print", action='store_true', default=False,
                           help="If given, will print the updated table.")
    sb_ingest.add_argument("--data_path", default=RDS_DATA_PATH, help='path of the rds cleaned data')
    sb_ingest.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # Sub-parser for adding one data point
    sb_ingest = subparsers.add_parser("add_one", description="Add one data point to database")
    sb_ingest.add_argument("-p", "--print", action='store_true', default=False,
                           help="If given, will print the updated table.")
    sb_ingest.add_argument("--id", default="123456789", help="Id of the recipe")
    sb_ingest.add_argument("--name", default="super mysterious unknown recipe", help="Name of the recipe")
    sb_ingest.add_argument("--description", default="A mysterious recipe!", help="Short Description of the Recipe")
    sb_ingest.add_argument("--minutes", default="1000", help="How long it takes to cook the recipe")
    sb_ingest.add_argument("--tags", default="[mysterious, unknown]", help="most important tags of the recipe")
    sb_ingest.add_argument("--calories", default="0.0", help="calories in the recipe")
    sb_ingest.add_argument("--total_fat", default="0.0", help="total amount of fat in the recipe")
    sb_ingest.add_argument("--sugar", default="0.0", help="amount of sugar in the recipe")
    sb_ingest.add_argument("--sodium", default="0.0", help="amount of sodium in the recipe")
    sb_ingest.add_argument("--protein", default="0.0", help="amount of protein in the recipe")
    sb_ingest.add_argument("--saturated_fat", default="0.0", help="amount of saturated fat in the recipe")
    sb_ingest.add_argument("--carbs", default="0.0", help="amount of carbohydrates in the recipe")
    sb_ingest.add_argument("--n_ingredients", default="0", help="number of ingredients of the recipe.")
    sb_ingest.add_argument("--ingredients", default="[food, recipe, hope]", help="ingredients of the recipe.")
    sb_ingest.add_argument("--n_steps", default="1", help="number of steps in the recipe")
    sb_ingest.add_argument("--steps", default="1. cook your meals!", help="the steps of the recipe")
    sb_ingest.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == 's3':
        if len(args.s3path) != len(args.local_path):
            logger.error("Number of s3 paths (" + str(len(args.s3path)) + ") and local paths ("
                         + str(len(args.local_path)) + ") mismatch.")
        else:
            if args.download:
                download_file_from_s3(args.local_path, args.s3path)
            else:
                upload_file_to_s3(args.local_path, args.s3path)
    elif sp_used == 'create_db':
        logger.info("DB URI used: " + args.engine_string)
        create_db(engine_string=args.engine_string)
    elif sp_used == 'ingest':
        logger.info("DB URI used: " + args.engine_string)
        rm = RecipeManager(engine_string=args.engine_string)
        rm.add_recipe_df(args.data_path)
        if args.print:
            rm.print_table()
        rm.close()
    elif sp_used == 'add_one':
        logger.info("DB URI used: " + args.engine_string)
        rm = RecipeManager(engine_string=args.engine_string)
        rm.add_recipe(id=args.id, name=args.name, description=args.description, minutes=args.minutes,
                      tags=args.tags, calories=args.calories, total_fat=args.total_fat, sugar=args.sugar,
                      sodium=args.sodium, protein=args.protein, saturated_fat=args.saturated_fat, carbs=args.carbs,
                      n_ingredients=args.n_ingredients, ingredients=args.ingredients,
                      n_steps=args.n_steps, steps=args.steps)
        if args.print:
            rm.print_table()
        rm.close()
    else:
        parser.print_help()
