import argparse

import logging.config
from config.flaskconfig import LOGGING_CONFIG

import yaml
import pandas as pd

logging.config.fileConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

import src.s3 as s3
import src.clean as clean
import src.model as model
import src.evaluation as evaluation

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="")

    parser.add_argument('step', help='Which step to run',
                        choices=['acquire', 'clean', 'model', 'evaluate'])
    parser.add_argument('--config', default='config/config.yaml', help='Path to configuration file')

    args = parser.parse_args()

    # Load configuration file for parameters and tmo path
    with open(args.config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    logger.info("Configuration file loaded from %s" % args.config)

    if args.step == 'acquire':
        s3.download_file_from_s3(**config['s3']['download_file_from_s3'])

    elif args.step == 'clean':
        recipe = pd.read_csv(config['clean']['recipe_in_path'])
        interaction = pd.read_csv(config['clean']['interaction_in_path'])
        clean_recipe = clean.prepare_recipe(recipe, config['clean']['prepare_recipe'])
        logger.debug("recipe data cleaned.")
        prepared_recipe = clean.get_recipe(clean_recipe, **config['clean']['get_recipe'])
        logger.debug("prepared recipe data.")
        prepared_rds = clean.get_rds(clean_recipe, **config['clean']['get_rds'])
        logger.debug("prepared rds data.")
        prepared_interactions = clean.prepare_interactions(interaction, **config['clean']['prepare_interactions'])
        logger.debug("prepared interaction data.")

        # write data to folder
        prepared_recipe.to_csv(config['clean']['recipe_out_path'], index=False)
        prepared_rds.to_csv(config['clean']['rds_path'], index=False)
        prepared_interactions.to_csv(config['clean']['interaction_out_path'], index=False)
        logger.info("prepared recipe, interactions and rds data saved.")

    elif args.step == 'model':
        data = pd.read_csv(config['model']['clean_data_path'])
        model_data = model.kmeans_model(data, **config['model']['kmeans_model'])
        logger.info('kmean model finished.')

        model_data.to_pickle(config['model']['model_data_path'])
        logger.info("kmeans result saved.")

    elif args.step == 'evaluate':
        interaction = pd.read_csv(config['clean']['interaction_out_path'])
        model = pd.read_pickle(config['model']['model_data_path'])
        avg_ndcg = evaluation.evaluation(interaction, model, **config['evaluate']['evaluation'])
        result = pd.DataFrame({'Avg_nDCG': avg_ndcg}, index=[0])
        logger.info(f"Average nDCG for the model is {avg_ndcg}.")
        result.to_csv(config['evaluate']['result_path'], index=False)
        logger.info("Evaluation result exported.")
