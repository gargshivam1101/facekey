import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1')

dbTableName = 'fk-users'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
usersTable = dynamodb.Table(dbTableName)

def lambda_handler(event, context):
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key'] #image name, should be like Shivam_Garg_40258018.jpg    

    try:
        response = index_image(bucket, key) #indexes image via rekognition
        print(response)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            faceId = response['FaceRecords'][0]['Face']['FaceId'] #unique id
            personalDetails = key.split('.')[0].split('_')
            firstName = personalDetails[0]
            lastName = personalDetails[1]
            userUuid = personalDetails[2]
            registerUser(faceId, firstName, lastName, userUuid)
        return response
    except Exception as e:
        print(e)
        print('Error in registration while indexing image {} from bucket {}'.format(key, bucket))
        raise e

def index_image(bucket, key):
    response = rekognition.index_faces(
        Image = {
            'S3Object':
            {
                'Bucket': bucket,
                'Name': key
            }
        },
        CollectionId = 'userCollection'
    )
    return response

def registerUser(faceId, firstName, lastName, userUuid):
    usersTable.put_item(
        Item = {
            'id': faceId,
            'firstName': firstName,
            'lastName': lastName,
            'userUuid': userUuid,
        }
    )