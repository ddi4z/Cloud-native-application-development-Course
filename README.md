# Grupo 19

[![Evaluador Implementación Entrega 1](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_entrega1_k8s.yml/badge.svg)](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_entrega1_k8s.yml)

[![Evaluador Documentación Entrega 1](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_entrega1_docs.yml/badge.svg)](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_entrega1_docs.yml)

[![Evaluador Pruebas Unitarias](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_unit.yml/badge.svg)](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo19/actions/workflows/ci_evaluador_unit.yml)

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
├── offers_app              # Api de ofertas
├── posts_app               # Api de publicaciones
├── routes_app              # Api de rutas
├── users_app               # Api de usuarios
├── vale.ini                # Configuración para Vale. NO MODIFICAR
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

Para desplegar las aplicaciones en Minikube, siga estos pasos:

0. Cargar las imágenes de Docker en Minikube:
   ```bash
   minikube image load <nombre-imagen>
   ```

1. Iniciar Minikube:
   ```bash
   minikube start
   ```

2. Aplicar los archivos de configuración de Kubernetes:
   ```bash
   kubectl apply -f k8s
   ```

3. Exponer el servicio deseado:
   ```bash
   minikube service <NombreServicio>
   ```

4. Acceder a la aplicación a través de la URL generada por Minikube.
