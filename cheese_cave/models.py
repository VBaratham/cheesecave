import os
import datetime

import boto3
import botocore.exceptions

# sdb model
#
# one domain for each type of data stored:
#   - temp/humidity readings
#   - changes of the set target
# item name = date/time of event

ISOFMT = "%Y-%m-%dT%H:%M:%S.%f"

sdb = boto3.client(
    'sdb',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
)

class CheeseCave(object):

    def __init__(self, env):
        env = env.lower() if env else 'dev'
        self.readings_domain = 'CheeseCave_readings_{env}'.format(env=env)
        self.settarget_domain = 'CheeseCave_settarget_{env}'.format(env=env)
        for domain in (self.readings_domain, self.settarget_domain):
            try:
                sdb.domain_metadata(DomainName=domain)
            except botocore.exceptions.ClientError:
                sdb.create_domain(DomainName=domain)
    
    def new_reading(self, temp, humidity):
        now = datetime.datetime.now()
        sdb.put_attributes(
            DomainName=self.readings_domain,
            ItemName=now.isoformat(),
            Attributes=[
                {
                    'Name': 'temp',
                    'Value': temp
                },
                {
                    'Name': 'humidity',
                    'Value': humidity
                }
            ]
        )

    @staticmethod
    def sdb_to_python(sdb_obj):
        attributes = {attr['Name']: attr['Value'] for attr in sdb_obj['Attributes']}
        date = datetime.datetime.strptime(sdb_obj['Name'], ISOFMT)
        return dict(attributes, date=date)        

    def get_latest_reading(self):
        query = "SELECT * FROM {domain} WHERE itemName() IS NOT NULL ORDER BY itemName() desc LIMIT 1".format(domain=self.readings_domain)
        latest_reading = sdb.select(SelectExpression=query)['Items'][0]
        return CheeseCave.sdb_to_python(latest_reading)

    def new_target(self, temp):
        now = datetime.datetime.now()
        sdb.put_attributes(
            DomainName=self.settarget_domain,
            ItemName=now.isoformat(),
            Attributes=[
                {
                    'Name': 'temp',
                    'Value': temp
                }
            ]
        )

    def get_current_target(self):
        query = "SELECT * FROM {domain} WHERE itemName() IS NOT NULL ORDER BY itemName() desc LIMIT 1".format(domain=self.settarget_domain)
        return CheeseCave.sdb_to_python(
            sdb.select(SelectExpression=query)['Items'][0]
        )
