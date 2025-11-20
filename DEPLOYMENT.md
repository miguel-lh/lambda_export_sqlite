# Guía de Despliegue Automático con GitHub Actions

Este documento explica cómo configurar el despliegue automático a AWS Lambda usando GitHub Actions.

## Requisitos Previos

1. **Cuenta de AWS** con permisos para:
   - AWS Lambda
   - API Gateway
   - CloudFormation
   - S3
   - IAM
   - CloudWatch Logs

2. **Bucket S3** para almacenar artefactos de SAM
   - Puedes crear uno con: `aws s3 mb s3://mi-bucket-sam-artifacts --region us-west-2`

## Configuración de GitHub Secrets

Ve a tu repositorio en GitHub → Settings → Secrets and variables → Actions → New repository secret

Debes crear los siguientes secrets:

### Secrets de AWS (Requeridos)

| Secret Name | Descripción | Ejemplo |
|-------------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | Access Key ID de tu usuario IAM | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | Secret Access Key de tu usuario IAM | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | Región de AWS donde desplegar | `us-west-2` |
| `STACK_NAME` | Nombre del stack de CloudFormation | `export-sqlite-stack` |
| `SAM_ARTIFACTS_BUCKET` | Bucket S3 para artefactos de SAM | `mi-bucket-sam-artifacts` |

### Secrets de PostgreSQL (Requeridos)

| Secret Name | Descripción | Valor Actual |
|-------------|-------------|--------------|
| `POSTGRES_HOST` | Host de PostgreSQL | `snapshots081020232.crgij3iw0xe0.us-west-2.rds.amazonaws.com` |
| `POSTGRES_PORT` | Puerto de PostgreSQL | `5432` |
| `POSTGRES_DATABASE` | Nombre de la base de datos | `production` |
| `POSTGRES_USER` | Usuario de PostgreSQL | `af_master` |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL | `af_master9021A` |

## Crear Usuario IAM para GitHub Actions

```bash
# 1. Crear usuario IAM
aws iam create-user --user-name github-actions-deployer

# 2. Crear y adjuntar política con permisos necesarios
cat > deploy-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "s3:*",
        "lambda:*",
        "apigateway:*",
        "iam:GetRole",
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:PutRolePolicy",
        "iam:AttachRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PassRole",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-user-policy \
  --user-name github-actions-deployer \
  --policy-name DeployPolicy \
  --policy-document file://deploy-policy.json

# 3. Crear access keys
aws iam create-access-key --user-name github-actions-deployer
```

Guarda el `AccessKeyId` y `SecretAccessKey` que te devuelve este comando - los necesitarás para los secrets de GitHub.

## Flujo de Despliegue

Cuando hagas push a la rama `main`:

1. GitHub Actions detecta el push
2. Checkout del código
3. Configura Python 3.11
4. Instala AWS SAM CLI
5. Configura credenciales de AWS
6. Ejecuta `sam build --use-container` (construye en contenedor Docker para compatibilidad)
7. Ejecuta `sam deploy` con los parámetros de los secrets
8. Muestra el endpoint de la API

## Despliegue Manual (Opcional)

Si quieres desplegar manualmente desde tu máquina local:

```bash
# 1. Configurar AWS CLI
aws configure

# 2. Build
sam build

# 3. Deploy (primera vez - crea samconfig.toml)
sam deploy --guided

# 4. Deploy (subsecuentes)
sam deploy
```

## Verificar el Despliegue

Después de que termine el workflow:

1. Ve a Actions → Deploy to AWS Lambda → Ver el último run
2. En el último step verás el URL del API endpoint
3. Prueba el endpoint:

```bash
curl "https://XXXXXX.execute-api.us-west-2.amazonaws.com/dev/export/64127" \
  --output tenant_64127.sqlite
```

## Monitoreo

Ver logs en tiempo real:

```bash
# Listar funciones
aws lambda list-functions

# Ver logs
sam logs -n dev-export-to-sqlite --stack-name export-sqlite-stack --tail
```

Ver en AWS Console:
- CloudWatch Logs: `/aws/lambda/dev-export-to-sqlite`
- Lambda: Buscar función `dev-export-to-sqlite`
- API Gateway: Buscar API `dev-export-api`

## Troubleshooting

### Error: "Bucket does not exist"
Crea el bucket S3 para artefactos:
```bash
aws s3 mb s3://mi-bucket-sam-artifacts --region us-west-2
```

### Error: "User is not authorized to perform: cloudformation:CreateStack"
El usuario IAM necesita más permisos. Revisa la política adjunta arriba.

### Error: "Stack already exists"
Si quieres recrear el stack:
```bash
aws cloudformation delete-stack --stack-name export-sqlite-stack
# Espera a que termine
aws cloudformation wait stack-delete-complete --stack-name export-sqlite-stack
# Haz push de nuevo
```

### La Lambda se queda sin memoria o timeout
Ajusta en `template.yaml`:
- `Timeout: 300` (aumenta si necesitas más tiempo)
- `MemorySize: 1024` (aumenta si necesitas más memoria)

## Estructura de Branches

- `main` → Despliega automáticamente a AWS
- Otras branches → No despliegan automáticamente (crea PRs para hacer merge a main)

Si quieres desplegar desde otra branch, modifica `.github/workflows/deploy.yml`:
```yaml
on:
  push:
    branches:
      - main
      - develop  # Agrega más branches aquí
```
