image:
	docker build -t recipe .

data/raw/RAW_recipes.csv data/raw/RAW_interactions.csv: config/config.yaml
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY \
	--mount type=bind,source="$(shell pwd)",target=/app/ recipe run_model.py acquire

acquire: data/raw/RAW_recipes.csv data/raw/RAW_interactions.csv

data/clean/recipes.csv, data/clean/rds.csv: data/raw/RAW_recipes.csv config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ recipe run_model.py clean

clean: data/clean/recipes.csv, data/clean/rds.csv

model/kmeans.csv: data/clean/recipes.csv config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ recipe run_model.py model
model: model/kmeans.csv

data/recipe.db:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ recipe run.py \
	create_db --engine_string=sqlite:///data/recipe.db

create_local_db: data/recipe.db

create_s3_db:
	docker run -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_PORT -e DATABASE_NAME -e MYSQL_HOST \
	--mount type=bind,source="$(shell pwd)",target=/app/ recipe run.py create_db

ingest_local: data/clean/rds.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ recipe run.py ingest \
	--data_path=data/clean/rds.csv --engine_string=sqlite:///data/recipe.db

tests:
	docker run recipe -m pytest test/*

clean_all:
	rm data/raw/*
	rm data/clean/*
	rm data/recipe.db
	rm model/*

model_pipline: acquire clean model

.PHONY: image acquire clean model create_local_db create_s3_db tests all