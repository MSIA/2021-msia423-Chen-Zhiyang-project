import logging
import re
import boto3
import botocore

# Code modified from the one provided in class:
# https://github.com/MSIA/2021-msia423/blob/main/aws-s3/s3.py

logger = logging.getLogger(__name__)


def parse_s3(s3path):
    """Parse full s3 path to bucket name and path name.

    Args:
        s3path(str): string that is the full path to s3.
    Return:
        s3bucket(str): name of the s3bucket
        s3path(str): remaining of the s3 path
    """
    regex = r"s3://([\w._-]+)/([\w./_-]+)"

    try:
        m = re.match(regex, s3path)
        s3bucket = m.group(1)
        s3path = m.group(2)
    except Exception as e:
        logger.error(e)
        exit(1)

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
