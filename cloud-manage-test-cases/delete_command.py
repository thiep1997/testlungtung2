from boto3_function import Ec2Checks, IamChecks, CloudformationChecks


ec2= Ec2Checks(region="ap-southeast-1", project_name="cloud-manage-test-cases")

print(ec2.terminate_instance())


iam= IamChecks(region="ap-southeast-1", project_name='cloud-manage-test-cases')

print(iam.delete_group())
print(iam.delete_user())
print(iam.delete_role())
print(iam.delete_policy())


CF = CloudformationChecks(region="ap-southeast-1", project_name="cloud-manage-test-cases")

print(CF.delete_stack())
