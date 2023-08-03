import boto3
from botocore.config import Config
import json
from operator import itemgetter


def find_default_SG(client):
    SG_id = []
    response = client.describe_security_groups(GroupNames=["default"])
    for i in response.get("SecurityGroups"):
        SG_id.append(i.get("GroupId"))
    return SG_id


def find_default_image(client):
    response = client.describe_images(
        Filters=[
            {"Name": "name", "Values": ["Ubuntu Server 22.04 *"]},
            {"Name": "virtualization-type", "Values": ["hvm"]},
            {"Name": "architecture", "Values": ["x86_64"]},
        ]
    )
    image_details = sorted(response.get("Images"), key=itemgetter("CreationDate"))
    ami_id = image_details[0].get("ImageId")
    return ami_id


def find_default_subnet(client):
    response = client.describe_vpcs(
        Filters=[{"Name": "is-default", "Values": ["true"]}]
    )
    vpc_id = response.get("Vpcs")[0].get("VpcId")

    response2 = client.describe_subnets(
        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )
    subnet_id = (response2).get("Subnets")[0].get("SubnetId")
    return subnet_id


class Ec2Checks:

    instance_type = "t2.micro"

    def __init__(self, region, project_name):
        self.region = region
        self.project_name = project_name

    def create_instance(self, image_id=None, SG_id=None, subnet_id=None):
        client = boto3.client("ec2", region_name=self.region)

        if not image_id:
            image_id = self.__find_default_image(client=client)
        if not SG_id:
            SG_id = self.__find_default_SG(client=client)
        if not subnet_id:
            subnet_id = self.__find_default_subnet(client=client)

        response = client.run_instances(
            ImageId=image_id,
            InstanceType=self.instance_type,
            MaxCount=1,
            MinCount=1,
            SecurityGroupIds=SG_id,
            SubnetId=subnet_id,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "Name", "Value": self.project_name},
                        {"Key": "owner", "Value": "devops"},
                        {"Key": "app", "Value": self.project_name},
                    ],
                }
            ],
        )
        return response

    def terminate_instance(self):
        client = boto3.client("ec2", region_name=self.region)
        response = client.describe_instances(
            Filters=[
                {"Name": "tag:Name", "Values": [self.project_name]},
                {"Name": "instance-state-name", "Values": ["running"]},
            ]
        )
        if response.get("Reservations") != []:
            for instance in response.get("Reservations"):
                instance_id = instance.get("Instances")[0].get("InstanceId")
                terminate = (client.terminate_instances(InstanceIds=[instance_id]),)
                print(terminate)

    def __find_default_SG(self, client):
        SG_id = []
        response = client.describe_security_groups(GroupNames=["default"])
        for i in response.get("SecurityGroups"):
            SG_id.append(i.get("GroupId"))
        return SG_id

    def __find_default_image(self, client):
        response = client.describe_images(
            Filters=[
                {"Name": "name", "Values": ["Ubuntu Server 22.04 *"]},
                {"Name": "virtualization-type", "Values": ["hvm"]},
                {"Name": "architecture", "Values": ["x86_64"]},
            ]
        )
        image_details = sorted(response.get("Images"), key=itemgetter("CreationDate"))
        ami_id = image_details[0].get("ImageId")
        return ami_id

    def __find_default_subnet(self, client):
        response = client.describe_vpcs(
            Filters=[{"Name": "is-default", "Values": ["true"]}]
        )
        vpc_id = response.get("Vpcs")[0].get("VpcId")

        response2 = client.describe_subnets(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        subnet_id = (response2).get("Subnets")[0].get("SubnetId")
        return subnet_id


class IamChecks:
    def __init__(self, region, project_name="cloud-manage-test-cases"):
        self.region = region
        self.project_name = project_name

    def create_group(self):
        client = boto3.client("iam", region_name=self.region)
        response = client.create_group(GroupName=self.project_name)
        return response

    def create_user(self):
        client = boto3.client("iam", region_name=self.region)
        response = client.create_user(
            UserName=self.project_name,
            Tags=[
                {"Key": "owner", "Value": "devops"},
                {"Key": "app", "Value": self.project_name},
            ],
        )
        return response

    def create_policy(self):
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": "ec2:*",
                    "Resource": "*",
                }
            ],
        }

        client = boto3.client("iam", region_name=self.region)
        response = client.create_policy(
            PolicyName=self.project_name,
            PolicyDocument=json.dumps(policy_document),
            Description=self.project_name,
            Tags=[
                {"Key": "owner", "Value": "devops"},
                {"Key": "app", "Value": self.project_name},
            ],
        )
        return response

    def create_role(self):
        role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Principal": {"AWS": "693573057868"},
                    "Condition": {},
                }
            ],
        }

        client = boto3.client("iam", region_name=self.region)
        response = client.create_role(
            RoleName=self.project_name,
            AssumeRolePolicyDocument=json.dumps(role_policy),
            Description=self.project_name,
            Tags=[
                {"Key": "owner", "Value": "devops"},
                {"Key": "app", "Value": self.project_name},
            ],
        )
        return response

    def delete_group(self):
        client = boto3.client("iam", region_name=self.region)
        response = client.delete_group(GroupName=self.project_name)
        return response

    def delete_user(self):
        client = boto3.client("iam", region_name=self.region)
        response = client.delete_user(UserName=self.project_name)
        return response

    def delete_role(self):
        client = boto3.client("iam", region_name=self.region)
        response = client.delete_role(RoleName=self.project_name)
        return response

    def delete_policy(self):
        sts = boto3.client("sts", region_name=self.region)
        account = sts.get_caller_identity()
        account_id = account.get("Account")
        arn = f"arn:aws:iam::{account_id}:policy/{self.project_name}"
        client = boto3.client("iam", region_name=self.region)
        response = client.delete_policy(PolicyArn=arn)
        return response


class CloudformationChecks:
    def __init__(self, region, project_name="cloud-manage-test-cases"):
        self.region = region
        self.project_name = project_name

    def create_stack(self):
        body = """
        AWSTemplateFormatVersion: "2010-09-09"
        Parameters:
            Policyname:
              Type: String
        Resources: 
          CreateGroup:
            Type: "AWS::IAM::Group"
            Properties: 
              GroupName: !Join
                      - "-"
                      - - !Ref Policyname
                        - "Deny-Group"
          RolePolicies: 
            Type: "AWS::IAM::Policy"
            Properties: 
              Groups:
                - !Ref CreateGroup
              
              PolicyName: !Ref Policyname
              PolicyDocument: 
                Version: "2012-10-17"
                Statement: 
                  - Effect: "Deny"
                    Action: 
                    - ec2:Delete*
                    - cloudformation:Delete*
                    - iam:Delete*
                    - cognito-identity:Delete*
                    - cognito-sync:Delete*
                    - cognito-idp:Delete*
                    Resource: "*"
                    """
        client = boto3.client("cloudformation", region_name=self.region)
        response = client.create_stack(
            StackName=self.project_name,
            TemplateBody=body,
            Parameters=[
                {"ParameterKey": "Policyname", "ParameterValue": self.project_name}
            ],
            Tags=[
                {"Key": "owner", "Value": "devops"},
                {"Key": "app", "Value": self.project_name},
            ],
            Capabilities=["CAPABILITY_NAMED_IAM"],
        )
        return response

    def delete_stack(self):
        client = boto3.client("cloudformation", region_name=self.region)
        response = client.delete_stack(StackName=self.project_name)
        return response

