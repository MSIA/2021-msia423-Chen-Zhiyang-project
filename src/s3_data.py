import argparse
import logging
import re

import boto3
import botocore

# Code modified from the one provided in class:
# https://github.com/MSIA/2021-msia423/blob/main/aws-s3/s3.py

logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', level=logging.DEBUG)
logging.getLogger("botocore").setLevel(logging.ERROR)
logging.getLogger("s3transfer").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("boto3").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("aiobotocore").setLevel(logging.ERROR)
logging.getLogger("s3fs").setLevel(logging.ERROR)

logger = logging.getLogger('s3')


def parse_s3(s3path):
    """Parse full s3 path to bucket name and path name.

    Args:
        s3path(str): string that is the full path to s3.
    Return:
        s3bucket(str): name of the s3bucket
        s3path(str): remaining of the s3 path
    """
    regex = r"s3://([\w._-]+)/([\w./_-]+)"

    m = re.match(regex, s3path)
    s3bucket = m.group(1)
    s3path = m.group(2)

    return s3bucket, s3path


def upload_file_to_s3(local_paths, s3paths):
    """Upload file from local path to the given s3 path.

    Args:
        local_paths(list): list of local location of the file to be uploads
        s3paths(list): list of the location in s3 to upload file
    """
    for local_path, s3path in zip(local_paths, s3paths):

        s3bucket, s3_just_path = parse_s3(s3path)

        s3 = boto3.resource("s3")
        bucket = s3.Bucket(s3bucket)

        try:
            bucket.upload_file(local_path, s3_just_path)
        except botocore.exceptions.NoCredentialsError:
            logger.error(
                'Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
        except Exception as e:
            logger.error(e)
        else:
            logger.info('Data uploaded from %s to %s', local_path, s3path)


def download_file_from_s3(local_paths, s3paths):
    """Download csv file from the given s3 path.

    Args:
        local_paths(list): list of local location of the file to be downloaded
        s3paths(list): list of the location in s3 to download file
    """
    for local_path, s3path in zip(local_paths, s3paths):
        s3bucket, s3_just_path = parse_s3(s3path)

        s3 = boto3.resource("s3")
        bucket = s3.Bucket(s3bucket)

        try:
            bucket.download_file(s3_just_path, local_path)
        except botocore.exceptions.NoCredentialsError:
            logger.error(
                'Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
        except Exception as e:
            logger.error(e)
        else:
            logger.info('Data downloaded from %s to %s', s3path, local_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', default=False, action='store_true',
                        help="If true, will download from s3.")
    parser.add_argument('--s3path', nargs='+', default=['s3://2021-msia423-chen-zhiyang/raw_data/RAW_recipes.csv',
                                                        's3://2021-msia423-chen-zhiyang/raw_data/RAW_interactions.csv'],
                        help="One or more locations (files) in s3.")
    parser.add_argument('--local_path', nargs='+', default=['data/RAW_recipes.csv', 'data/RAW_interaction.csv'],
                        help="One or more local locations (files).")
    args = parser.parse_args()

    if len(args.s3path) != len(args.local_path):
        logger.error("Number of s3 paths (" + str(len(args.s3path)) + ") and local paths ("
                     + str(len(args.local_path)) + ") mismatch.")
    else:
        if args.download:
            download_file_from_s3(args.local_path, args.s3path)
        else:
            upload_file_to_s3(args.local_path, args.s3path)
