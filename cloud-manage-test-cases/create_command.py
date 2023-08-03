from boto3_function import Ec2Checks, IamChecks, CloudformationChecks


ec2= Ec2Checks(region="ap-southeast-1", project_name="cloud-manage-test-cases")

print(ec2.create_instance())

iam= IamChecks(region="ap-southeast-1", project_name='cloud-manage-test-cases')
print(iam.create_group())
print(iam.create_user())
print(iam.create_role())
print(iam.create_policy())

CF = CloudformationChecks(region="ap-southeast-1", project_name="cloud-manage-test-cases")

print(CF.create_stack())

