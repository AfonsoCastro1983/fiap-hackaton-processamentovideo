# README - Lambda para Processamento de Vídeos e Notificação via AWS

## Introdução

Este projeto implementa uma função AWS Lambda que processa vídeos enviados para um bucket S3. A solução realiza extração de frames, conversão para MP4 e notifica o usuário por e-mail sobre o progresso do processamento.

O objetivo deste projeto é demonstrar o uso de serviços gerenciados da AWS para arquitetura serverless, integrando serviços como **AWS Lambda**, **Amazon S3**, **AWS Elemental MediaConvert**, **Amazon SES** e **Amazon DynamoDB**.

---

## Funcionalidades

1. **Monitoramento de bucket S3**:
   - Detecta novos vídeos enviados.
   - Ignora vídeos já processados.

2. **Extração de dados do DynamoDB**:
   - Obtém o e-mail associado ao vídeo usando o `videoId` como chave.

3. **Processamento de vídeos**:
   - Realiza extração de frames do vídeo.
   - Converte o vídeo para formato MP4.

4. **Envio de notificações por e-mail**:
   - Notifica o usuário sobre o início do processamento.

---

## Pré-requisitos

1. **Serviços AWS configurados**:
   - Bucket S3 para upload dos vídeos.
   - Tabela DynamoDB (`VideosTable`) com índice secundário `videoId-index`.
   - Configuração do AWS Elemental MediaConvert.
   - Domínio verificado no Amazon SES para envio de e-mails.

2. **Permissões IAM**:
   - Função IAM vinculada ao Lambda com permissões para:
     - Leitura e escrita no S3.
     - Acesso ao DynamoDB.
     - Uso do AWS MediaConvert.
     - Envio de e-mails via SES.

3. **Configuração de variáveis de ambiente**:
   - `email_sender`: Endereço de e-mail utilizado como remetente no Amazon SES.

---

## Estrutura do Código

### Principais Componentes

1. **`retornar_email(videoId)`**  
   Consulta a tabela DynamoDB para buscar o e-mail associado ao vídeo.

2. **`enviar_email(to, subject, message)`**  
   Envia e-mails para os usuários utilizando o Amazon SES.

3. **`lambda_handler(event, context)`**  
   Função principal que:
   - Processa os eventos do S3.
   - Inicia jobs no AWS MediaConvert.
   - Envia notificações por e-mail.

---

## Configuração e Deploy

### 1. **Configuração do AWS Lambda**
- Crie uma nova função Lambda no console AWS.
- Faça o upload do código acima como arquivo `.zip` ou utilizando um IDE compatível (ex.: AWS Cloud9).
- Configure as variáveis de ambiente:
  ```plaintext
  email_sender=<seu-email-verificado-no-SES>
  ```
- Vincule uma função IAM com permissões adequadas.

### 2. **Configuração do S3**
- Configure um bucket para armazenar os vídeos e os resultados do processamento.
- Configure um evento S3 para invocar a função Lambda ao fazer upload.

### 3. **Configuração do DynamoDB**
- Crie uma tabela chamada `VideosTable` com os seguintes atributos:
  - **Partition Key:** `videoId` (String).
  - **Atributos adicionais:** `user_data` (contendo o e-mail do usuário).

### 4. **Configuração do MediaConvert**
- Configure o AWS Elemental MediaConvert:
  - Crie um Role IAM padrão para o MediaConvert.
  - Configure o endpoint padrão da região `us-east-2`.

---

## Fluxo de Funcionamento

1. **Upload de Vídeo**:
   - O usuário faz o upload de um vídeo para o bucket S3.

2. **Trigger da Lambda**:
   - A função Lambda é disparada pelo evento de upload no S3.

3. **Processamento**:
   - A Lambda consulta o DynamoDB para buscar o e-mail do usuário.
   - Cria jobs no AWS MediaConvert para extração de frames e conversão para MP4.

4. **Notificação por E-mail**:
   - Um e-mail é enviado ao usuário informando que o processamento começou.

---

## Exemplo de Resposta da Lambda

### Evento de Sucesso:
```json
{
  "statusCode": 200,
  "body": "Notificações enviadas com sucesso"
}
```

### Evento de Erro:
- Caso ocorra um erro ao enviar o e-mail, a exceção será registrada nos logs do CloudWatch.

---

## Diagrama da Arquitetura

```plaintext
[ Usuário ] -> [ S3 Bucket ] -> [ Lambda Function ]
                       ↸             ↶
                        [ DynamoDB ]  [ AWS MediaConvert ]
                                 ↸    ↶
                                 [ E-mail via SES ]
```

---

## Pontos de Aprendizado

- Arquitetura serverless para processamento de mídia.
- Integração de múltiplos serviços AWS.
- Uso de indexação no DynamoDB para consultas eficientes.
- Configuração e uso do Amazon SES para notificações transacionais.

---

**Apresentação prática:** Durante a demonstração, faremos o upload de um vídeo, acompanharemos seu processamento e exibiremos o e-mail recebido pelo usuário.

