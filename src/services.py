import logging
import time
from typing import List, Dict, Any

import boto3
from botocore.exceptions import ClientError

dynamo_client = boto3.resource('dynamodb')

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def reset_dynamo_table(table_name: str, default_values_mapping: Dict):
    LOGGER.info(f'Going to reset {table_name} table with default values {default_values_mapping}')
    # Scan all table
    table_records = get_all_data_from_table(table_name)

    # Apply reset based on mapping on each record
    default_values = process_default_values(default_values_mapping)
    reset_values = []
    for record in table_records:
        reset_values.append({
            **record,
            **default_values
        })

    # Save the record to dynamo again
    save_records(reset_values, table_name)


def get_all_data_from_table(table_name: Any) -> List[Dict]:
    table = dynamo_client.Table(table_name)
    scan_attributes = {}
    done = False
    start_key = None
    returned_data = []
    while not done:
        if start_key:
            scan_attributes['ExclusiveStartKey'] = start_key
        response = exponential_back_off(table.scan, **scan_attributes)
        if len(returned_data) == 0:
            returned_data = response.get('Items', [])
        else:
            returned_data.extend(response.get('Items', []))
        start_key = response.get('LastEvaluatedKey', None)
        done = start_key is None

    return returned_data


def process_default_values(default_values_mapping: Dict):
    result = {}
    for key, val in default_values_mapping.items():
        if val['Type'] == 'Double':
            value = float(val['Value'])
        if val['Type'] == 'Boolean':
            value = eval(val['Value'])
        if val['Type'] == 'Number':
            value = int(val['Value'])
        else:
            value = val['Value']
        result[key] = value

    return result


def exponential_back_off(resource_client_function: Any, **kwargs) -> Dict:
    response = None
    success = False
    retries = 0
    while not success:

        try:
            response = resource_client_function(**kwargs)
            success = True
        except Exception as e:

            if 9 < retries:
                raise e

            sleep_time = (2 ** retries) * 1 / 10
            time.sleep(sleep_time)
            retries = retries + 1

    return response


def save_records(records: List[dict], table_name: str) -> None:
    table = dynamo_client.Table(table_name)
    for record in records:
        LOGGER.info(f'writing {record} to dynamo db')
        try:
            table.put_item(Item=record)
        except ClientError as e:
            LOGGER.error(f'Error writing to dynamo db {e.with_traceback(e.__traceback__)}')
            raise e
