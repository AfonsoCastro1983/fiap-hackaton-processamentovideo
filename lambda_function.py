import boto3
import os

ses_client = boto3.client('ses', region_name='us-east-2')
dynamodb_client = boto3.resource('dynamodb')

def retornar_email(videoId):
    table = dynamodb_client.Table("VideosTable")
    # Query para buscar vídeos do usuário
    response = table.query(
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
        videoId = file_key.split('/')[1]
        file_name = file_key.split('/')[2]
        # Busca os dados do DynamoDB
        email = retornar_email(videoId)
        if email=="":
            continue
        # Processa o vídeo
        
        # Mensagem Email
        message = f"Olá, seu vídeo '{file_name}' foi processado e está disponível para download aqui ou através do site."
        subject = "Video Frame Upload - Notificação de processamento de vídeo"
        
        enviar_email(email, subject, message)
    
    return {"statusCode": 200, "body": "Notification sent successfully."}