import boto3
import os

ses_client = boto3.client('ses', region_name='us-east-2')
s3_client = boto3.client('s3', region_name='us-east-2')
mediaconvert = boto3.client('mediaconvert', region_name='us-east-2')
dynamodb_client = boto3.resource('dynamodb')

def retornar_email(videoId):
    table = dynamodb_client.Table("VideosTable")
    # Query para buscar vídeos do usuário
    response = table.query(
        IndexName="videoId-index",
        KeyConditionExpression="videoId = :videoId",
        ExpressionAttributeValues={
            ":videoId": videoId
        }
    )
    if len(response['Items'])==0:
        return ""
    else:
        try:
            return response['Items'][0]['user_data']['email']
        except:
            return ""

def enviar_email(to, subject, message):
    # Publicar no SES
    try:
        response = ses_client.send_email (
            Source=os.getenv('email_sender'),
            Destination={
                'ToAddresses': [to]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': message,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
    except Exception as e:
        print('Erro ao enviar e-mail para',email,'Erro:',e)

def lambda_handler(event, context):
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        file_key = record['s3']['object']['key']
        if 'trt_video' in file_key:
            continue
        videoId = file_key.split('/')[1]
        file_name = file_key.split('/')[2]
        # Busca os dados do DynamoDB
        email = retornar_email(videoId)
        if email=="":
            continue
        # Cria pastas de extração
        dir_frame = os.path.dirname(file_key)+'/frames/'
        dir_video = os.path.dirname(file_key)+'/trt_video/'
        s3_client.put_object(Bucket=bucket_name,Key=dir_frame)
        s3_client.put_object(Bucket=bucket_name,Key=dir_video)
        # Gera o job para extração do vídeo
        job_settings = {
            "Inputs": [{
                "FileInput": f's3://{bucket_name}/{file_key}',
                "TimecodeSource": "ZEROBASED"
            }],
            "OutputGroups": [
                {
                    "Name": "Frame Extraction",
                    "OutputGroupSettings": {
                        "Type": "FILE_GROUP_SETTINGS",
                        "FileGroupSettings": {
                            "Destination": f's3://{bucket_name}/{dir_frame}'
                        }
                },
                "Outputs": [{
                    "ContainerSettings": {"Container": "RAW"},
                    "VideoDescription": {
                        "CodecSettings": {
                            "Codec": "FRAME_CAPTURE",
                            "FrameCaptureSettings": {
                                "FramerateNumerator": 1,
                                "FramerateDenominator": 5,
                                "MaxCaptures": 100,
                                "Quality": 80
                            }
                        }
                    }
                }]
            },
            {
                "Name": "MP4 Output",
                "OutputGroupSettings": {
                    "Type": "FILE_GROUP_SETTINGS",
                    "FileGroupSettings": {
                        "Destination": f's3://{bucket_name}/{dir_video}/'
                    }
                },
                "Outputs": [{
                    "VideoDescription": {
                        "CodecSettings": {
                            "Codec": "H_264",
                            "H264Settings": {
                                "RateControlMode": "QVBR",
                                "QvbrSettings": {
                                    "QvbrQualityLevel": 8
                                },
                                "MaxBitrate": 5000000
                            }
                        }
                    },
                    
                    "ContainerSettings": {
                        "Container": "MP4",
                        "Mp4Settings": {}
                    }
                }]
            }
        ]}

        response = mediaconvert.create_job(
            Role='arn:aws:iam::992382363343:role/service-role/MediaConvert_Default_Role',
            Settings=job_settings
        )
        
        # Mensagem Email
        message = f"Olá, seu vídeo '{file_name}' foi iniciou o processo de extração, você será avisado quando este processo terminar."
        subject = "Video Frame Upload - Notificação de processamento de vídeo"
        
        enviar_email(email, subject, message)
    
    return {"statusCode": 200, "body": "Notificações enviadas com sucesso!"}