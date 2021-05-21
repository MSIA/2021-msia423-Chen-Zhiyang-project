# MSiA423 Project: What to Cook Next?

Developer: Zhiyang (Iris) Chen

QA support: Allen Xu

## Project Charter

### Vision

Everybody enjoys food, and preparing delicious meals can be a rewarding relaxation after a busy day. Nevertheless, even an all-time favorite dish becomes less attractive if one cooks and eats the exactly same thing repeatedly. Yet, exploring new recipes that fit one's taste may not be easy, especially for busy people: it is usually a process of trial and error, taking time and effort. This application, therefore, helps people to find new recipes that match their taste and skillset, adding a twist to their daily meals.

### Mission

Users will enter the food they like (there may exist search suggestions to match a recipe that existed in the database), and there is also an option to enter what they want to use as ingredients. Then the app will recommend the top 10 recipes (made with the ingredients if provided) that are similar to the given dish and have the highest predicted scores.

For example, the user likes "Mac & Cheese" and the app will recommend things like "The Ultimate Spaghetti Carbonara Recipe" and will predict the user would score 4/5 for this recipe.

The dataset used is from [Food.com](https://www.kaggle.com/shuyangli94/food-com-recipes-and-user-interactions) in Kaggle. It includes both recipes and user interactions with the recipes. It has 180K+ recipes and 700K+ recipe reviews, covering 18 years of user interactions.


### Success Criteria

#### 1. Model Performance Metric:
The model will be tested on the Food.com users interaction dataset. For the recommender system, mAP and nDCG will be used. An ideal nDCG will be higher than 0.7. For the predicted score, the desired Cross-Validation R-squared prior to deployment is 0.7.

#### 2. Business Metrics:
Ideally, an A/B testing should be conducted. Two metrics should be considered: the amount of time spent to find out recipes and the ratings for the new recipe. We would compare between the group of users who select new recipe using the app and the group who do not.
Overall, the successful deployment of the app should increase users' satisfaction with the experience of searching and cooking, helping people to find recipes that fit their taste in a shorter amount of time.

## Data Acquisition

The dataset is available on Kaggle: [Food.com Recipes and Interactions](https://www.kaggle.com/shuyangli94/food-com-recipes-and-user-interactions), which is a crawled data from Food.com (GeniusKitchen) online recipe aggregator. 
The files used in this project are `RAW_interactions.csv` and `RAW_recipes.csv`. You can download these two datasets to the `\data` folder. 

Small samples of both of the datasets (`sample_RAW_interactions.csv` and `sample_RAW_recipes.csv`) are already included in `\data\sample` folder.

<!-- toc -->

- [Directory structure](#directory-structure)
- [Database Management Using Docker](#database-management-using-docker)
  * [1. Build the Image](#1-build-the-image)
  * [2. Interacting with S3 Bucket](#2-interacting-with-s3-bucket)
    + [1) Set up configuration for S3](#1-set-up-configuration-for-s3)
    + [2) Upload Raw_Datasets to S3 Bucket](#2-upload-raw-datasets-to-s3-bucket)
    + [3) Download Raw Datasets from S3 Bucket](#3-download-raw-datasets-from-s3-bucket)
  * [3. Create the Database](#3-create-the-database)
    + [1) Create RDS MySQL Database](#1-create-rds-mysql-database)
      - [a. Set up configuration for RDS MySQL](#a-set-up-configuration-for-rds-mysql)
      - [b. Create DataBase in RDS MySQL](#b-create-database-in-rds-mysql)
      - [c. Add a Recipe](#c-add-a-recipe)
      - [d. Connect to RDS MySQL Database](#d-connect-to-rds-mysql-database)
    + [2) Create Local SQLite Database](#2-create-local-sqlite-database)
     

<!-- tocstop -->

## Directory structure 

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── Dockerfile                    <- Dockerfile for building image to run app  
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project. 
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project 
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```

## Database Management Using Docker

There exist two sets of data for this project: one is the raw data stored in S3; 
the other is the recipe detailed information stored in RDS-hosted MySQL database, which 
will be displaced to the app user when providing recommendations to them.

### 1. Build the image 

The Dockerfile for accessing s3 bucket and building database is in the root. 
To build the image, run from this directory (the root of the repo): 

```bash
 docker build -t recipe .
```

This command builds the Docker image, with the tag `recipe`, based on the instructions in `Dockerfile` and the files existing in this directory.

The entry point is `python3`, and thus when you run the image as a container, the command python3 is run, followed by the arguments given in the docker run command after the image name.

### 2. Interacting with S3 Bucket

The S3 Bucket stores all the raw datasets of this project.

#### 1) Set up configuration for S3
For your convenience, you can first config your environment for the following.

```bash
export AWS_ACCESS_KEY_ID=<Your AWS Access Key ID>
export AWS_SECRET_ACCESS_KEY=<Your AWS Access Key>
```

#### 2) Upload Raw Datasets to S3 Bucket
To upload datasets, please run:

```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY recipe run.py s3 \
    --s3path <s3 directory path1> <s3 directory path2> \
    --local_path <local directory path1> <local directory path2>
```

The default `s3path` are <br>
`s3://2021-msia423-chen-zhiyang/raw_data/RAW_recipes.csv` and <br>
`s3://2021-msia423-chen-zhiyang/raw_data/RAW_interactions.csv`.

The default `local_path` are <br>
`data/sample/sample_RAW_recipes.csv` and <br>
`data/sample/sample_RAW_interactions.csv`.

#### 3) Download Raw Datasets from S3 Bucket
To download datasets, please run:

```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY recipe run.py s3 --download\
    --s3path <s3 directory path1> <s3 directory path2> \
    --local_path <local directory path1> <local directory path2>
```

The default `s3path` and `local_path` are the same as upload.

**Notes:**
1. You can also indicate only one s3 path and one local path, but remember that the number of s3 paths 
should match number of local paths.
2. There are also two small sample datasets for testing purpose in the s3 bucket. Their paths are:<br>
`s3://2021-msia423-chen-zhiyang/raw_data/sample_RAW_recipes.csv` and 
`s3://2021-msia423-chen-zhiyang/raw_data/sample_RAW_interactions.csv`.

### 3. Create the Database 

You can create the database in either the RDS MYSQL database or a local location.

#### 1) Create RDS MySQL Database

##### a. Set up configuration for RDS MySQL

For your convenience, you can first config your environment for the following.

```bash
export MYSQL_USER=<Your RDS MySQL User Name>
export MYSQL_PASSWORD=<Your RDS MySQL Password>
export MYSQL_HOST=nw-msia423-zcm9834.cgtjrvditdsm.us-east-1.rds.amazonaws.com
export MYSQL_PORT=3306
export DATABASE_NAME=msia423_db
```

##### b. Create DataBase in RDS MySQL

To create the database in RDS MySQL using docker, please first configure the above, then **connect to Northwestern VPN**, 
and then run:

```bash
docker run -e MYSQL_USER \
  -e MYSQL_PASSWORD \
  -e MYSQL_PORT \
  -e DATABASE_NAME \
  -e MYSQL_HOST \
recipe run.py create_db
```

##### c. Add a Recipe

A function is written so that you can manually add a recipe by running the code below:

```bash
docker run -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_PORT -e DATABASE_NAME -e MYSQL_HOST recipe run.py ingest \
  id=<recipe id> name=<recipe name> description=<recipe description> minutes=<cook minutes> \
  top_tags=<top tags> calories=<calories> total_fat=<total fat> sugar=<sugar> sodium=<sodium> \
  protein=<protein> saturated_fat=<saturated_fat> carbs=<carbs> num_of_ingredients=<number of ingredients> \
  all_ingredients=<ingredient list> num_of_steps=<number of cooking steps> steps=<detailed steps>
```
As you can see, this is really tedious! Thus, it is more for testing purpose.

##### d. Connect to RDS MySQL Database

You can also connect to the Database to see the table. With the configuration mentioned above is set up and on NU VPN, run:

```bash
docker run -it --rm \
    mysql:5.7.33 \
    mysql \
    -h$MYSQL_HOST \
    -u$MYSQL_USER \
    -p$MYSQL_PASSWORD
```

Then you can see the database using the command:

```SQL
USE msia423_db;
```
To show all the tables (which should only be one, `recipes`):

```SQL
SHOW tables;
```

Then you can see the sample of the table by running:

```SQL
SELECT * FROM recipes LIMIT 5;
```

**Note:**
1. Since the security group of the default HOST is set for Northwestern VPN `165.124.160.0/21` access, 
   please make sure that you are on Northwestern VPN before connecting to the database.

#### 2) Create Local SQLite Database

You can also create a local SQLite database. If no `MYSQL_HOST` provided, the `SQLALCHEMY_DATABASE_URI` 
will be set to a local SQLite database. 

```bash
docker run recipe run.py create_db --engine_string=<engine_string>
```

By default, the command creates a database at `sqlite:///data/recipe.db`. 
You can also configure your own local SQLite database by changing the `engine_string` 
or by modifying the configuration in `config/flaskconfig.py`.

**Note:**
1. Please notice that this database created by docker is WITHIN the container filesystem.
Thus, you may want to use [volumes](https://docs.docker.com/storage/volumes/), or just runing the code outside of docker container.

# BELOW IS NOT CHANGED


#### Defining your engine string 
A SQLAlchemy database connection is defined by a string with the following format:

`dialect+driver://username:password@host:port/database`

The `+dialect` is optional and if not provided, a default is used. For a more detailed description of what `dialect` and `driver` are and how a connection is made, you can see the documentation [here](https://docs.sqlalchemy.org/en/13/core/engines.html). We will cover SQLAlchemy and connection strings in the SQLAlchemy lab session on 
##### Local SQLite database 

A local SQLite database can be created for development and local testing. It does not require a username or password and replaces the host and port with the path to the database file: 

```python
engine_string='sqlite:///data/tracks.db'

```

The three `///` denote that it is a relative path to where the code is being run (which is from the root of this directory).

You can also define the absolute path with four `////`, for example:

```python
engine_string = 'sqlite://///Users/cmawer/Repos/2020-MSIA423-template-repository/data/tracks.db'
```


### 2. Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
DEBUG = True  # Keep True for debugging, change to False when moving to production 
LOGGING_CONFIG = "config/logging/local.conf"  # Path to file that configures Python logger
HOST = "0.0.0.0" # the host that is running the app. 0.0.0.0 when running locally 
PORT = 5000  # What port to expose app on. Must be the same as the port exposed in app/Dockerfile 
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/tracks.db'  # URI (engine string) for database that contains tracks
APP_NAME = "penny-lane"
SQLALCHEMY_TRACK_MODIFICATIONS = True 
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100 # Limits the number of rows returned from the database 
```

### 3. Run the Flask app 

To run the Flask app, run: 

```bash
python app.py
```

You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

# Testing

From within the Docker container, the following command should work to run unit tests when run from the root of the repository: 

```bash
python -m pytest
``` 

Using Docker, run the following, if the image has not been built yet:

```bash
 docker build -f app/Dockerfile_python -t pennylane .
```

To run the tests, run: 

```bash
 docker run penny -m pytest
```
 
