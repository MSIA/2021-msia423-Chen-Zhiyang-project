image:
	docker build -t recipe_zcm9834 .

app_image:
	docker build --platform linux/x86_64 -f app/Dockerfile -t recipe_zcm9834 .

#model pipeline
data/raw/RAW_recipes.csv data/raw/RAW_interactions.csv: config/config.yaml
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY \
	--mount type=bind,source="$(shell pwd)",target=/app/ recipe_zcm9834 run_model.py acquire

acquire: data/raw/RAW_recipes.csv data/raw/RAW_interactions.csv

data/clean/recipes.csv, data/clean/rds.csv, data/clean/interactions.csv: data/raw/RAW_recipes.csv config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ recipe_zcm9834 run_model.py clean

clean: data/clean/recipes.csv, data/clean/rds.csv data/clean/interactions.csv

model/kmeans.csv: data/clean/recipes.csv config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ recipe_zcm9834 run_model.py model
model: model/kmeans.pkl

model/result.csv: data/clean/interactions.csv model/kmeans.pkl config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ recipe_zcm9834 run_model.py evaluate
evaluation: model/result.csv

model_pipeline: acquire clean model evaluation

# database related
data/recipe.db:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ recipe_zcm9834 run.py \
	create_db --engine_string=sqlite:///data/recipe.db
create_local_db: data/recipe.db

create_rds_db:
	docker run -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_PORT -e DATABASE_NAME -e MYSQL_HOST recipe_zcm9834 run.py create_db

ingest_local: data/clean/rds.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ recipe_zcm9834 run.py ingest \
	--data_path=data/clean/rds.csv --engine_string=sqlite:///data/recipe.db

ingest_rds: data/clean/rds.csv
	docker run -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_PORT -e DATABASE_NAME -e MYSQL_HOST \
	recipe_zcm9834 run.py ingest --data_path=data/clean/rds.csv

local_app: model/kmeans.pkl
	docker run -p 5000:5000 recipe_zcm9834 app.py

rds_app: model/kmeans.pkl
	docker run -it -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e MYSQL_HOST -e MYSQL_PORT -e MYSQL_USER -e MYSQL_PASSWORD -e DATABASE_NAME -p 5000:5000 recipe_zcm9834 app.py

run_local_app: model_pipeline create_local_db ingest_local local_app
run_rds_app: model_pipeline create_rds_db ingest_rds rds_app

tests:
	docker run recipe_zcm9834 -m pytest test/*

clean_all:
	rm data/raw/*
	rm data/clean/*
	rm data/recipe.db
	rm model/*

.PHONY: image acquire clean model evaluation create_local_db create_rds_db tests ingest_local ingest_rds clean_all model_pipeline