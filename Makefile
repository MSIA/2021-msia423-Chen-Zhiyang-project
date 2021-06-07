image:
	docker build -t recipe .

#app_image:
#	docker build --platform linux/x86_64 -f app/Dockerfile -t recipe .

#model pipeline
data/raw/RAW_recipes.csv data/raw/RAW_interactions.csv: config/config.yaml
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY \
	--mount type=bind,source="$(shell pwd)",target=/app/ recipe run_model.py acquire

acquire: data/raw/RAW_recipes.csv data/raw/RAW_interactions.csv

data/clean/recipes.csv, data/clean/rds.csv, data/clean/interactions.csv: data/raw/RAW_recipes.csv config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ recipe run_model.py clean

clean: data/clean/recipes.csv, data/clean/rds.csv data/clean/interactions.csv

model/kmeans.csv: data/clean/recipes.csv config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ recipe run_model.py model
model: model/kmeans.csv

model/result.txt: model/kmeans.csv config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ recipe run_model.py evaluate
evaluation: model/result.txt

model_pipeline: acquire clean model evaluation

# database related
upload_s3:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY recipe run.py s3

data/recipe.db:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ recipe run.py \
	create_db --engine_string=sqlite:///data/recipe.db
create_local_db: data/recipe.db

create_rds_db:
	docker run -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_PORT -e DATABASE_NAME -e MYSQL_HOST recipe run.py create_db

ingest_local: data/clean/rds.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ recipe run.py ingest \
	--data_path=data/clean/rds.csv --engine_string=sqlite:///data/recipe.db

ingest_rds: data/clean/rds.csv
	docker run -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_PORT -e DATABASE_NAME -e MYSQL_HOST \
	recipe run.py ingest --data_path=data/clean/rds.csv

local_app:
	docker run -p 5000:5000 recipe app.py

rds_app:
	docker run -it -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e MYSQL_HOST -e MYSQL_PORT -e MYSQL_USER -e MYSQL_PASSWORD -e DATABASE_NAME -p 5000:5000 recipe app.py

run_local_app: model_pipeline create_local_db ingest_local local_app
run_rds_app: model_pipeline create_rds_db ingest_rds rds_app

tests:
	docker run recipe -m pytest test/*

clean_all:
	rm data/raw/*
	rm data/clean/*
	rm data/recipe.db
	rm model/*

.PHONY: image acquire clean model evaluation create_local_db create_rds_db tests ingest_local ingest_rds clean_all model_pipeline