acquire: config/config.yaml
	docker run --mount type=bind,source="`pwd`",target=/app/ cloud run.py acquire

clean: config/config.yaml data/clouds.data
	docker run --mount type=bind,source="`pwd`",target=/app/ cloud run.py clean --input ./data/clouds.data --output ./data/data_cleaned.csv

featurize: config/config.yaml data/data_cleaned.csv
	docker run --mount type=bind,source="`pwd`",target=/app/ cloud run.py featurize --input ./data/data_cleaned.csv --output ./data/data_featurized.csv

eda_plots: config/config.yaml data/data_featurized.csv
	docker run --mount type=bind,source="`pwd`",target=/app/ cloud run.py eda_plots --input ./data/data_featurized.csv

train: config/config.yaml data/data_featurized.csv
	docker run --mount type=bind,source="`pwd`",target=/app/ cloud run.py train --input ./data/data_featurized.csv

tests:
	docker run cloud -m pytest test/*

clean_repo:
	rm -rf model/*
	rm -rf data/*
	rm -rf plots/*

pipeline: acquire clean featurize eda_plots train

.PHONY: pipeline