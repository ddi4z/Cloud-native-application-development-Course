# Vistas de arquitectura

## Vista de componentes
  
![Vista de componentes](./diagrams/components.png "Vista de componentes")

Arquitectura por servicios con propiedad de datos por dominio y acoplamiento bajo, enfocada en cubrir funcionalidades esenciales de la primera entrega.
- Actor: User interactúa con los servicios vía cliente/APIs (líneas punteadas).
- Servicios (cajas rosadas): users_app, posts_app, offers_app, routes_app; cada uno es desplegable de forma independiente y expone una API.
- Persistencia (cilindros azules): cada servicio posee su propia BD (users_db, posts_db, offers_db, routes_db); sin acceso cruzado; intercambio entre dominios vía APIs.
- Entorno (env): encapsula los procesos en un mismo stack/cluster; habilita escalado y despliegue independientes.


## Vista de despliegue

![Vista de despliegue](./diagrams/deployment.png "Vista de despliegue")

Despliegue local en un clúster k8s (p. ej., minikube/kind). 
- Acceso del usuario: el User consume las APIs vía HTTP a través de los Services de las apps.
- Patrón por dominio (users, posts, routes, offers):
  - App: contenedor Docker (*_app) ejecutado en k8s y expuesto por un Service.
  - Base de datos: contenedor (*_db) accesible mediante su Service interno.
  - Persistencia: volumen dedicado para la BD (PVC/PV) para evitar pérdida de datos al reiniciar pods.
- Comunicación: cada app se conecta solo a su BD vía el Service correspondiente (sin acceso cruzado).
- Operación: componentes aislados y escalables de forma independiente.

## Vista de redes

![Vista de redes](./diagrams/networks.png "Vista de redes")

K8s con cuatro dominios lógicos/“networks”: users, posts, routes, offers.
- Exposición externa: cada app se publica vía Service NodePort; el usuario accede por Internet → NodePort → *-app-service (HTTP :80) → pod *_app.
- Acceso a datos: la app se conecta a su propia BD vía ClusterIP *-db-service (:5432) → pod *_db. No hay acceso cruzado entre bases ni entre dominios.
- Aislamiento y escalabilidad: cada dominio puede escalarse y desplegarse de forma independiente manteniendo propiedad de datos por servicio.

## Vista de información

![Vista de información](./diagrams/entities.png "Vista de información")

Modelo lógico de datos para la primera iteración. Muestra entidades clave, atributos y relaciones.
