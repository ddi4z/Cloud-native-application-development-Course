# Grupo 19

## Estado Github Actions

### Entrega 1 

[![Evaluador Implementación Entrega 1](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_entrega1_k8s.yml/badge.svg)](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_entrega1_k8s.yml)

[![Evaluador Documentación Entrega 1](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_entrega1_docs.yml/badge.svg)](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_entrega1_docs.yml)

[![Evaluador Pruebas Unitarias](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_unit.yml/badge.svg)](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_unit.yml)

### Entrega 2

[![Evaluador Implementación Entrega 2](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_entrega2.yml/badge.svg)](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_entrega2.yml)

### Entrega 3
[![Evaluador Implementación Entrega 3](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_entrega3.yml/badge.svg)](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_entrega3.yml)

[![Evaluador Implementación Entrega 3 con Email](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_entrega3_email.yml/badge.svg)](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_entrega3_email.yml)

---

## Tabla de contenido

- [proyecto-base](#proyecto-base)
  - [Tabla de contenido](#tabla-de-contenido)
  - [Estructura del Proyecto](#estructura-del-proyecto)
  - [Archivo de configuración](#archivo-de-configuración)
  - [Estructura de cada aplicación](#estructura-de-cada-aplicación)

## Estructura del Proyecto

```
.
├── github/
│   └── workflows/          # Pipelines del repositorio
├── k8s/                    # Archivos para despliegue en k8s
├── docs/                   # Archivos de documentación técnica
├── rf003_app               # Api de creación de publicaciones
├── rf004_app               # Api de ofertar sobre publicaciones
├── rf005_app               # Api de consultar publicaciones y ordenarlas por score, descendiente
├── offers_app              # Api de ofertas
├── posts_app               # Api de publicaciones
├── routes_app              # Api de rutas
├── users_app               # Api de usuarios
├── vale.ini                # Configuración para Vale. NO MODIFICAR
├── build-all.ps1           # Script automatizacón compilación apps
├── deploy.ps1              # Script automatización despliegue apps
├── config.yaml             # Configuración del repositorio. 
├── Makefile                # Scripts para evaluación. 
└── README.md               # Este archivo
```

## Estructura de cada aplicación

Todas las aplicaciones fueron desarrolladas utilizando las tecnologías: **Python**, **Poetry**, **FastAPI** y **Pytest**, tomando como base la arquitectura de `pets_app`.  
Cada aplicación incluye un `Dockerfile` y un archivo `README.md` con sus instrucciones de ejecución.

- [offers_app](./offers_app/README.md)  
- [posts_app](./posts_app/README.md)  
- [routes_app](./routes_app/README.md)  
- [users_app](./users_app/README.md)  

## Ejecución en Minikube

Para desplegar las aplicaciones, siga estos pasos:
---

### 0) Prerrequisitos
- AWS CLI configurado (`aws configure`), `kubectl`, `docker`, y (opcional) `eksctl`, `helm`.
- Cuenta/rol con permisos para EKS, ECR, RDS, IAM.
- Variables que usarás durante los pasos:
```bash
export AWS_REGION=<tu-region>          # ej: us-east-1
export AWS_ACCOUNT_ID=<tu-account-id>
export ECR="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
export NAMESPACE=platform              # o el que uses en tus manifests
```

### 1) Crear cluster (si no existe)
```bash
eksctl create cluster --name platform-cluster \
  --version 1.29 --region $AWS_REGION \
  --nodegroup-name ng-ondemand --nodes 2 --nodes-min 2 --nodes-max 4
kubectl config use-context arn:aws:eks:$AWS_REGION:$AWS_ACCOUNT_ID:cluster/platform-cluster
kubectl create namespace $NAMESPACE
```

### 2) Crear repos en ECR y autenticar Docker
```bash
aws ecr get-login-password --region $AWS_REGION \
 | docker login --username AWS --password-stdin $ECR

for repo in users_app routes_app posts_app offers_app scores_app rf003_app rf004_app rf005_app; do
  aws ecr create-repository --repository-name $repo --region $AWS_REGION >/dev/null 2>&1 || true
done

```

### 3) Construir y publicar imágenes en ECR
```bash
# ejemplo para posts_app (repite para cada app)
docker build -t posts_app:1.0.0 ./posts_app
docker tag posts_app:1.0.0 $ECR/posts_app:1.0.0
docker push $ECR/posts_app:1.0.0

```
* Asegurarse de actualizar la imagen en los manifests de k8s al URI de ECR correspondiente (ej.: $ECR/posts_app:1.0.0).

### 4) Provisionar RDS PostgreSQL
```bash
kubectl -n $NAMESPACE create secret generic platform-db \
  --from-literal=DATABASE_URL="postgresql://<user>:<pass>@<endpoint-rds>:5432/<dbname>"

```

### 5) Instalar el Ingress Controler (Ngix)
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace

```


### 6) Aplicar manifiestos de K8s
```bash
kubectl apply -n $NAMESPACE -f k8s/
# Si tienes una carpeta específica para cloud:
# kubectl apply -n $NAMESPACE -f k8s/cloud/
```

### 7) Verificar despliegue
```bash
kubectl get pods,svc,ingress -n $NAMESPACE
```

### 8) Actualizar imágenes en despliegues (si cambia de versión)
```bash
kubectl -n $NAMESPACE set image deployment/posts-app posts-app-container=$ECR/posts_app:1.0.1
# Repite por servicio; observa rolling update:
kubectl rollout status deployment/posts-app -n $NAMESPACE

```
### 9) Limpieza (Opcional)
```bash
kubectl delete ns $NAMESPACE
eksctl delete cluster --name platform-cluster --region $AWS_REGION

```

