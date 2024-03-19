import os
import json
import boto3

from botocore.config import Config

from entities.Bucket import Bucket
from adapters.AdapterConfig import get_adapter

from utils.common import is_empty
from utils.logger import log_msg
from entities.Registry import Registry

CACHE_ADAPTER = get_adapter('cache')

def get_driver_access_key_id():
    access_key_id = os.getenv('AWS_DRIVER_ACCESS_KEY_ID')
    if is_empty(access_key_id):
        access_key_id = os.getenv('AWS_STRATEGY_ACCESS_KEY_ID')
    return access_key_id

def get_driver_secret_access_key():
    secret_access_key = os.getenv('AWS_DRIVER_SECRET_ACCESS_KEY')
    if is_empty(secret_access_key):
        secret_access_key = os.getenv('AWS_STRATEGY_SECRET_ACCESS_KEY')
    return secret_access_key

def update_aws_registry_credentials(rg_id, region, hashed_name):
    delete_old_reg_keys(rg_id, region, hashed_name)
    user_name = f'user-{hashed_name}'
    rslt = generate_aws_keys(username = user_name)
    aws_access_key_id = rslt['AccessKey']['AccessKeyId']
    aws_secret_access_key = rslt['AccessKey']['SecretAccessKey']
    return (aws_access_key_id, aws_secret_access_key)

def update_aws_bucket_credentials(bucket_id, region, hashed_bucket_name):
    delete_old_bucket_keys(hashed_bucket_name, region, bucket_id)
    user_name = f'user-{hashed_bucket_name}'
    rslt = generate_aws_keys(username = user_name)
    aws_access_key_id = rslt['AccessKey']['AccessKeyId']
    aws_secret_access_key = rslt['AccessKey']['SecretAccessKey']
    return (aws_access_key_id, aws_secret_access_key)

def create_aws_registry(hashed_name, region):
    access_key_id = get_driver_access_key_id()
    secret_access_key = get_driver_secret_access_key()
    iam = boto3.client('iam', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)
    user_name = f'user-{hashed_name}'
    iam.create_user(UserName = user_name)
    access_key = generate_aws_keys(username = user_name)
    aws_access_key_id = access_key['AccessKey']['AccessKeyId']
    aws_secret_access_key = access_key['AccessKey']['SecretAccessKey']
    iam.attach_user_policy(UserName = user_name, PolicyArn = create_aws_registry_policy(hashed_name, region))
    return (aws_access_key_id, aws_secret_access_key)

def generate_aws_keys(username):
    access_key_id = get_driver_access_key_id()
    secret_access_key = get_driver_secret_access_key()
    iam = boto3.client('iam', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)
    access_key = iam.create_access_key(UserName = username)
    return access_key

def create_aws_bucket(hashed_bucket_name, region):
    access_key_id = get_driver_access_key_id()
    secret_access_key = get_driver_secret_access_key()

    iam = boto3.client('iam', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)
    user_name = f'user-{hashed_bucket_name}'
    iam.create_user(UserName = user_name)
    access_key = generate_aws_keys(username = user_name)
    aws_access_key_id = access_key['AccessKey']['AccessKeyId']
    aws_secret_access_key = access_key['AccessKey']['SecretAccessKey']
    iam.attach_user_policy(UserName = user_name, PolicyArn = create_aws_bucket_policy(hashed_bucket_name, region))
    return (aws_access_key_id, aws_secret_access_key)

def get_aws_bucket_name(hashed_bucket_name, buckets_region):
    my_config = Config(region_name = buckets_region, signature_version = 'v4', retries = { 'max_attempts': 10, 'mode': 'standard'})
    client = boto3.client('s3', config = my_config, aws_access_key_id = get_driver_access_key_id(), aws_secret_access_key = get_driver_secret_access_key())
    buckets = client.list_buckets()['Buckets']
    for bucket in buckets:
        if bucket['Name'].startswith(hashed_bucket_name):
            return(bucket['Name'])

def get_aws_registry_name(hashed_name, region):
    my_config = Config(region_name = region, signature_version = 'v4', retries = { 'max_attempts': 10, 'mode': 'standard'})
    client = boto3.client('ecr', config = my_config, aws_access_key_id = get_driver_access_key_id(), aws_secret_access_key = get_driver_secret_access_key())
    buckets = client.describe_repositories()['repositories']
    for bucket in buckets:
        if bucket['repositoryName'].startswith(hashed_name):
            return(bucket['repositoryName'])

def create_aws_bucket_policy(hashed_bucket_name, region):
    bucket_name = get_aws_bucket_name(hashed_bucket_name, region)
    s3_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "s3:ListStorageLensConfigurations",
                    "s3:ListAccessPointsForObjectLambda",
                    "s3:GetAccessPoint",
                    "s3:PutAccountPublicAccessBlock",
                    "s3:GetAccountPublicAccessBlock",
                    "s3:ListAllMyBuckets",
                    "s3:ListAccessPoints",
                    "s3:PutAccessPointPublicAccessBlock",
                    "s3:ListJobs",
                    "s3:PutStorageLensConfiguration",
                    "s3:ListMultiRegionAccessPoints",
                    "s3:CreateJob" 
                ],
                "Resource": "*"
            },
            {
                "Sid": "VisualEditor1",
                "Effect": "Allow",
                "Action": "s3:*",
                "Resource": f"arn: aws:s3:::{bucket_name}/*"
            }
        ]
    }

    policy_json = json.dumps(s3_policy)
    access_key_id = get_driver_access_key_id()
    secret_access_key = get_driver_secret_access_key()
    iam = boto3.client('iam', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)

    response = iam.create_policy(PolicyName = bucket_name, PolicyDocument = policy_json)
    policy_arn = response['Policy']['Arn']
    return policy_arn

def create_aws_registry_policy(hashed_name, region):
    registry_name = get_aws_registry_name(hashed_name, region)
    my_config = Config(region_name = region, signature_version = 'v4', retries = { 'max_attempts': 10, 'mode': 'standard'})
    sts_client = boto3.client('sts', config = my_config, aws_access_key_id = get_driver_access_key_id(), aws_secret_access_key = get_driver_secret_access_key())
    account_id = sts_client.get_caller_identity()['Account']

    reg_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "ecr: GetRegistryPolicy",
                    "ecr: CreateRepository",
                    "ecr: DescribeRegistry",
                    "ecr: DescribePullThroughCacheRules",
                    "ecr: GetAuthorizationToken",
                    "ecr: PutRegistryScanningConfiguration",
                    "ecr: CreatePullThroughCacheRule",
                    "ecr: DeletePullThroughCacheRule",
                    "ecr: PutRegistryPolicy",
                    "ecr: GetRegistryScanningConfiguration",
                    "ecr: BatchImportUpstreamImage",
                    "ecr: DeleteRegistryPolicy",
                    "ecr: PutReplicationConfiguration"
                ],
                "Resource": "*"
            },
            {
                "Sid": "VisualEditor1",
                "Effect": "Allow",
                "Action": "ecr:*",
                "Resource": f"arn: aws:ecr:{region}:{account_id}:repository/{registry_name}"
            }
        ]
    }

    policy_json = json.dumps(reg_policy)
    access_key_id = get_driver_access_key_id()
    secret_access_key = get_driver_secret_access_key()
    iam = boto3.client('iam', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)
    try:
        response = iam.create_policy(PolicyName = registry_name, PolicyDocument = policy_json)
        policy_arn = response['Policy']['Arn']
        return policy_arn
    except Exception as e:
        log_msg("ERROR", "[AwsDriver][create registry policy] unexpected exception: e = {}".format(e))

def delete_old_reg_keys(rg_id, region, hashed_name):
    access_key_id = get_driver_access_key_id()
    secret_access_key = get_driver_secret_access_key()
    iam = boto3.client('iam', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)
    username = f'user-{hashed_name}'
    access_key = Registry.getRegistryAccessKey('aws', region, rg_id)
    result = access_key.strip("(')").strip(", ").strip("'")
    iam.delete_access_key(AccessKeyId = result, UserName = username)

def delete_aws_user_registry(hashed_name, region, registry_id):
    access_key_id = get_driver_access_key_id()
    secret_access_key = get_driver_secret_access_key()
    my_config = Config(region_name = region, signature_version = 'v4', retries = { 'max_attempts': 10, 'mode': 'standard'})
    sts_client = boto3.client('sts', config = my_config, aws_access_key_id = get_driver_access_key_id(), aws_secret_access_key = get_driver_secret_access_key())
    account_id = sts_client.get_caller_identity()['Account']
    registry_name = CACHE_ADAPTER().get(f'aws_registry_name_{registry_id}')
    user = f'user-{hashed_name}'
    iam = boto3.client('iam', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)
    iam.detach_user_policy(UserName = user, PolicyArn = f"arn: aws:iam::{account_id}:policy/{registry_name}")
    delete_old_reg_keys(registry_id, region, hashed_name)
    iam.delete_user(UserName = user)

def delete_old_bucket_keys(hashed_bucket_name, region, bucket_id):
    access_key_id = get_driver_access_key_id()
    secret_access_key = get_driver_secret_access_key()
    iam = boto3.client('iam', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)
    username = f'user-{hashed_bucket_name}'
    access_key = Bucket.getBucketAccessKey('aws', region, bucket_id)
    result = access_key.strip("(')").strip(", ").strip("'")
    iam.delete_access_key(AccessKeyId = result, UserName = username)

def delete_aws_user_bucket(region, bucket_id, hashed_bucket_name):
    access_key_id = get_driver_access_key_id()
    secret_access_key = get_driver_secret_access_key()
    iam = boto3.client('iam', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)
    my_config = Config(region_name = region, signature_version = 'v4', retries = { 'max_attempts': 10, 'mode': 'standard'})
    sts_client = boto3.client('sts', config = my_config, aws_access_key_id = get_driver_access_key_id(), aws_secret_access_key = get_driver_secret_access_key())
    account_id = sts_client.get_caller_identity()['Account']
    bucket_name = CACHE_ADAPTER().get(f'aws_bucket_name_{bucket_id}')
    user = f'user-{hashed_bucket_name}'
    iam = boto3.client('iam', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)
    iam.detach_user_policy(UserName = user, PolicyArn = f"arn: aws:iam::{account_id}:policy/{bucket_name}" )
    delete_old_bucket_keys(hashed_bucket_name, region, bucket_id)
    iam.delete_user(UserName = user)
