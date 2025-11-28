# Banking DevOps API - Prueba Técnica

[![CI/CD Pipeline](https://github.com/yourusername/banco/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/yourusername/banco/actions/workflows/ci-cd.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Descripción

Microservicio REST seguro para operaciones bancarias, desarrollado siguiendo principios de **Clean Code**, **TDD (Test Driven Development)** e **Infraestructura como Código (IaC)**. Desplegado en Azure Kubernetes Service (AKS) con pipeline CI/CD completo.

## 🏗️ Arquitectura

```
├── app/                    # Código fuente de la aplicación
│   ├── main.py            # Endpoint principal de la API
│   ├── models.py          # Modelos de datos (Pydantic)
│   ├── test_main.py       # Suite de pruebas (TDD)
│   ├── requirements.txt   # Dependencias de Python
│   └── Dockerfile         # Imagen Docker optimizada
├── infra/                 # Infraestructura como Código (Terraform)
│   ├── main.tf           # Recursos de Azure (AKS, RG)
│   ├── variables.tf      # Variables de configuración
│   └── terraform.tfvars  # Valores de variables
├── k8s/                   # Manifiestos de Kubernetes
│   ├── deployment.yaml   # Deployment con 2 réplicas
│   ├── service.yaml      # LoadBalancer service
│   ├── hpa.yaml          # Horizontal Pod Autoscaler
│   └── namespace.yaml    # Namespace definition
└── .github/workflows/    # CI/CD Pipeline
    └── ci-cd.yml         # GitHub Actions workflow
```

## 🚀 Características

### Seguridad
- ✅ Validación de API Key (`X-Parse-REST-API-Key`)
- ✅ Validación de JWT Token (`X-JWT-KWY`)
- ✅ Autenticación HTTP 401 para credenciales inválidas
- ✅ Contenedor ejecutado con usuario no privilegiado

### Clean Code
- ✅ Separación de responsabilidades (models, main, tests)
- ✅ Nombres descriptivos y funciones pequeñas
- ✅ Documentación completa con docstrings
- ✅ Type hints en todas las funciones

### TDD (Test Driven Development)
- ✅ 15+ tests automatizados con `pytest`
- ✅ Cobertura de casos happy path y edge cases
- ✅ Tests de seguridad y validación
- ✅ Tests ejecutados en CI/CD

### Alta Disponibilidad
- ✅ 2 réplicas mínimas en Kubernetes
- ✅ 2 nodos mínimos en AKS
- ✅ Health checks (liveness/readiness probes)
- ✅ Horizontal Pod Autoscaler (HPA)
- ✅ Rolling updates sin downtime

## 🛠️ Tecnologías

| Categoría | Tecnología |
|-----------|-----------|
| **Backend** | Python 3.9+, FastAPI, Pydantic, Uvicorn |
| **Testing** | Pytest, TestClient |
| **Containerización** | Docker, Multi-stage builds |
| **Orquestación** | Kubernetes (AKS) |
| **Cloud** | Microsoft Azure |
| **IaC** | Terraform |
| **CI/CD** | GitHub Actions |
| **Linting** | Pylint |

## 📦 Instalación y Ejecución

### Prerequisitos
- Python 3.9+
- Docker
- Terraform
- Azure CLI
- kubectl
- Cuenta de Azure
- Cuenta de Docker Hub

### 1. Ejecución Local

```bash
# Clonar el repositorio
git clone https://github.com/yourusername/banco.git
cd banco/app

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# La API estará disponible en http://localhost:8000
```

### 2. Ejecutar Tests

```bash
cd app
pytest test_main.py -v
```

### 3. Ejecutar con Docker

```bash
cd app

# Construir imagen
docker build -t banking-devops-api .

# Ejecutar contenedor
docker run -d -p 8000:8000 --name banking-api banking-devops-api

# Ver logs
docker logs banking-api
```

### 4. Desplegar Infraestructura en Azure

#### 4.1. Login en Azure
```bash
# Login en Azure CLI
az login

# Verificar suscripción activa
az account show

# (Opcional) Cambiar suscripción
az account set --subscription "nombre-o-id-suscripcion"
```

#### 4.2. Desplegar con Terraform
```bash
cd infra

# Inicializar Terraform (descargar providers)
terraform init

# Validar sintaxis
terraform validate

# Ver plan de ejecución (sin aplicar cambios)
terraform plan

# Aplicar infraestructura (crea RG, AKS, Log Analytics)
terraform apply -auto-approve

# Guardar outputs importantes
terraform output
```

**Recursos que crea Terraform:**
- ✅ Resource Group: `rg-banking-devops`
- ✅ AKS Cluster: `aks-banking-cluster` (2 nodos)
- ✅ Log Analytics Workspace (para monitoreo)
- ✅ System-Assigned Managed Identity
- ✅ Azure CNI networking con Calico

**Costo estimado:** ~$6-8 USD/día

#### 4.3. Conectar a AKS
```bash
# Obtener credenciales de AKS
az aks get-credentials --resource-group rg-banking-devops --name aks-banking-cluster --overwrite-existing

# Verificar conexión
kubectl get nodes
kubectl cluster-info
```

### 5. Desplegar en Kubernetes

#### 5.1. Subir imagen a Docker Hub
```bash
cd app

# Build imagen
docker build -t tu-usuario/banking-devops-api:latest .

# Login en Docker Hub
docker login

# Push imagen
docker push tu-usuario/banking-devops-api:latest
```

#### 5.2. Actualizar deployment.yaml
```bash
# Editar k8s/deployment.yaml línea 28
# Cambiar: image: your-dockerhub-username/banking-devops-api:latest
# Por:     image: tu-usuario/banking-devops-api:latest
```

#### 5.3. Aplicar manifiestos
```bash
# Aplicar en orden
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Verificar deployment
kubectl get all -n default
kubectl get pods -n default -l app=banking-devops

# Ver estado del rollout
kubectl rollout status deployment/banking-devops-api -n default
```

#### 5.4. Obtener IP pública
```bash
# Esperar a que Azure asigne IP pública (puede tardar 2-3 minutos)
kubectl get service banking-devops-service -n default -w

# Obtener IP
EXTERNAL_IP=$(kubectl get service banking-devops-service -n default -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "API disponible en: http://$EXTERNAL_IP"
```

#### 5.5. Probar la API desplegada
```bash
# Test health check
curl http://$EXTERNAL_IP/health

# Test endpoint DevOps
curl -X POST \
  -H "X-Parse-REST-API-Key: 2f5ae96c-b558-4c7b-a590-a501ae1c3f6c" \
  -H "X-JWT-KWY: token" \
  -H "Content-Type: application/json" \
  -d '{"message":"test","to":"Juan Perez","from":"Rita","timeToLifeSec":45}' \
  http://$EXTERNAL_IP/DevOps
```

## 🧪 Pruebas de la API

### Comando oficial de prueba

Una vez desplegado, usa el siguiente comando `curl` para probar la API:

```bash
curl -X POST \
  -H "X-Parse-REST-API-Key: 2f5ae96c-b558-4c7b-a590-a501ae1c3f6c" \
  -H "X-JWT-KWY: un_token_valido" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "This is a test",
    "to": "Juan Perez",
    "from": "Rita Asturia",
    "timeToLifeSec": 45
  }' \
  http://localhost:80/DevOps
```

**Respuesta esperada:**
```json
{
  "message": "Hello Juan Perez your message will be send"
}
```

### Casos de prueba adicionales

#### 1. API Key inválida (debe retornar 401)
```bash
curl -X POST \
  -H "X-Parse-REST-API-Key: invalid-key" \
  -H "X-JWT-KWY: token" \
  -H "Content-Type: application/json" \
  -d '{"message":"test","to":"Juan","from":"Rita","timeToLifeSec":45}' \
  http://localhost:80/DevOps
```

#### 2. JWT faltante (debe retornar 401)
```bash
curl -X POST \
  -H "X-Parse-REST-API-Key: 2f5ae96c-b558-4c7b-a590-a501ae1c3f6c" \
  -H "Content-Type: application/json" \
  -d '{"message":"test","to":"Juan","from":"Rita","timeToLifeSec":45}' \
  http://localhost:80/DevOps
```

#### 3. Método GET (debe retornar "ERROR")
```bash
curl -X GET http://localhost:80/DevOps
```

#### 4. Health Check
```bash
curl http://localhost:80/health
```

## 🔄 CI/CD Pipeline

El pipeline de GitHub Actions se ejecuta automáticamente en:
- ✅ Push a cualquier rama (build + test + push imagen)
- ✅ Push a rama `master` (build + test + push + **deploy a AKS**)
- ✅ Ejecución manual (workflow_dispatch)

### Flujo Visual del Pipeline

```
┌─────────────────────────────────────────────────────────┐
│  PUSH a GitHub (cualquier branch)                       │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Job 1: Build & Test (Siempre se ejecuta)              │
│  ├─ Checkout código                                    │
│  ├─ Setup Python 3.9                                   │
│  ├─ Install dependencies                               │
│  ├─ Run Pylint                                         │
│  ├─ Run Pytest (15 tests)                              │
│  ├─ Setup Docker Buildx                                │
│  ├─ Login Docker Hub                                   │
│  ├─ Build imagen                                       │
│  └─ Push a Docker Hub ✅                               │
│     Tags: latest, branch-name, branch-sha              │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  ¿Branch = master?                                      │
│  NO  → Pipeline termina                                │
│  SÍ  → Continúa a Deploy                               │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Job 2: Deploy to AKS (Solo master)                    │
│  ├─ Azure Login (service principal)                    │
│  ├─ Set AKS context                                    │
│  ├─ Update deployment.yaml con nueva imagen           │
│  ├─ Deploy to Kubernetes                               │
│  │   ├─ namespace.yaml                                 │
│  │   ├─ deployment.yaml (Rolling Update) 🔄           │
│  │   ├─ service.yaml                                   │
│  │   └─ hpa.yaml                                       │
│  ├─ Verify deployment (rollout status)                │
│  ├─ Get LoadBalancer IP                                │
│  └─ Test /health endpoint ✅                           │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Job 3: Security Scan (Solo master, parallel)          │
│  ├─ Run Trivy vulnerability scanner                    │
│  └─ Upload results to GitHub Security tab ✅           │
└─────────────────────────────────────────────────────────┘
```

### Stages del Pipeline

#### Stage 1: Build & Test (Todas las ramas)
1. ✅ Checkout del código
2. ✅ Setup de Python 3.9 con cache de pip
3. ✅ Instalación de dependencias
4. ✅ **Linting** con Pylint (calidad de código)
5. ✅ **Tests** con Pytest (15 tests unitarios)
6. ✅ Setup Docker Buildx (multi-platform builds)
7. ✅ Login a Docker Hub
8. ✅ Extract metadata (tags automáticos)
9. ✅ Build de imagen Docker con cache
10. ✅ Push a Docker Hub con múltiples tags

**Tags de imagen generados:**
- `usuario/banking-devops-api:main`
- `usuario/banking-devops-api:main-a1b2c3d` (branch + commit)
- `usuario/banking-devops-api:latest` (solo en master)

#### Stage 2: Deploy to AKS (Solo master o manual)
1. ✅ Login a Azure con service principal
2. ✅ Configuración de contexto AKS
3. ✅ Actualización de deployment.yaml con imagen específica
4. ✅ Deploy de todos los manifiestos Kubernetes
5. ✅ Verificación de rollout exitoso
6. ✅ Obtención de IP pública del LoadBalancer
7. ✅ Test del servicio desplegado

**Estrategia de Deploy:**
- Rolling Update con `maxUnavailable: 0` (Zero Downtime)
- Espera hasta 5 minutos para rollout completo
- Verifica health check antes de confirmar éxito

#### Stage 3: Security Scan (Solo master)
1. ✅ Escaneo de vulnerabilidades con Trivy
2. ✅ Análisis de dependencias y CVEs
3. ✅ Upload de resultados a GitHub Security tab
4. ✅ Generación de SARIF report

### Configuración de Secrets en GitHub

Para que el pipeline funcione, configura los siguientes secrets:

**Ruta:** `Settings → Secrets and variables → Actions → New repository secret`

#### 1. Docker Hub Secrets
```bash
# Nombre: DOCKER_USERNAME
# Valor: tu-usuario-dockerhub

# Nombre: DOCKER_PASSWORD  
# Valor: tu-token-dockerhub (no uses tu password, crea un access token)
```

**Crear token en Docker Hub:**
1. Login en https://hub.docker.com
2. Account Settings → Security → New Access Token
3. Copia el token y úsalo como `DOCKER_PASSWORD`

#### 2. Azure Credentials
```bash
# Primero, obtén tu subscription ID
az account show --query id -o tsv

# Crea un Service Principal
az ad sp create-for-rbac \
  --name "github-actions-banking" \
  --role contributor \
  --scopes /subscriptions/{SUBSCRIPTION-ID}/resourceGroups/rg-banking-devops \
  --sdk-auth
```

**Output esperado:**
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  ...
}
```

**Copiar el JSON completo y crear secret:**
```bash
# Nombre: AZURE_CREDENTIALS
# Valor: {JSON completo del comando anterior}
```

#### 3. Verificar Secrets
Después de configurar, deberías ver:
- ✅ `DOCKER_USERNAME`
- ✅ `DOCKER_PASSWORD`
- ✅ `AZURE_CREDENTIALS`

### Ejecutar Pipeline Manualmente

1. Ve a tu repo en GitHub
2. Click en **Actions**
3. Selecciona **CI/CD Pipeline - Banking DevOps API**
4. Click en **Run workflow**
5. Selecciona branch (ejemplo: `master`)
6. Click en **Run workflow**

El pipeline se ejecutará completo y desplegará en AKS.

## 📊 Monitoreo y Logs

### Ver logs de pods
```bash
kubectl logs -l app=banking-devops -n default --tail=100 -f
```

### Ver métricas de recursos
```bash
kubectl top pods -n default
kubectl top nodes
```

### Verificar HPA
```bash
kubectl get hpa -n default
```

### Logs en Azure
Los logs están integrados con Azure Log Analytics. Accede desde el portal de Azure:
1. Navega a tu cluster AKS
2. Ve a "Insights" en el menú lateral
3. Explora logs y métricas

## 🔐 Seguridad

### API Key válida
```
2f5ae96c-b558-4c7b-a590-a501ae1c3f6c
```

### Headers requeridos
- `X-Parse-REST-API-Key`: API Key de autenticación
- `X-JWT-KWY`: Token JWT para autorización
- `Content-Type`: application/json

## 🐛 Troubleshooting

### 🔴 El pod no arranca

```bash
# Ver eventos del pod
kubectl describe pod <pod-name> -n default

# Ver logs del container
kubectl logs <pod-name> -n default

# Ver logs anteriores (si crasheó)
kubectl logs <pod-name> -n default --previous

# Ver todos los pods con problemas
kubectl get pods -n default --field-selector=status.phase!=Running
```

**Problemas comunes:**
- `ImagePullBackOff`: Imagen no existe en Docker Hub o es privada
- `CrashLoopBackOff`: La app falla al iniciar (revisar logs)
- `Pending`: No hay recursos suficientes en los nodos

### 🔴 El servicio no responde

```bash
# Verificar que el servicio tenga endpoints
kubectl get endpoints banking-devops-service -n default

# Si no tiene endpoints, revisar selector del service
kubectl describe service banking-devops-service -n default

# Port-forward para debug local
kubectl port-forward service/banking-devops-service 8080:80 -n default
curl http://localhost:8080/health

# Ver logs de todos los pods del servicio
kubectl logs -l app=banking-devops -n default --tail=50
```

### 🔴 LoadBalancer sin IP externa

```bash
# Ver estado del service
kubectl describe service banking-devops-service -n default

# Verificar eventos de Azure
kubectl get events -n default --sort-by='.lastTimestamp'

# Esperar unos minutos (Azure tarda 2-5 min en asignar IP)
kubectl get service banking-devops-service -n default -w
```

**Si después de 10 minutos no tiene IP:**
```bash
# Recrear el service
kubectl delete service banking-devops-service -n default
kubectl apply -f k8s/service.yaml
```

### 🔴 HPA no escala

```bash
# Verificar métricas disponibles
kubectl get hpa -n default
kubectl describe hpa banking-devops-hpa -n default

# Verificar metrics-server
kubectl get deployment metrics-server -n kube-system

# Si no hay métricas, instalar metrics-server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Generar carga para probar autoscaling
kubectl run -it --rm load-generator --image=busybox -- /bin/sh
# Dentro del pod:
while true; do wget -q -O- http://banking-devops-service; done
```

### 🔴 Terraform falla

```bash
# Ver logs detallados
TF_LOG=DEBUG terraform plan

# Ver plan guardado
terraform plan -out=tfplan
terraform show tfplan

# Validar sintaxis
terraform validate

# Formatear archivos
terraform fmt

# Refrescar estado
terraform refresh

# Destruir recursos específicos
terraform destroy -target=azurerm_kubernetes_cluster.aks

# Destruir todo
terraform destroy -auto-approve
```

**Errores comunes:**
- `Error: Duplicate resource`: Revisa que no haya recursos duplicados
- `Error: Insufficient quota`: Aumenta cuota en Azure o cambia región
- `Error: Provider authentication`: Ejecuta `az login`

### 🔴 Pipeline de GitHub Actions falla

```bash
# Ver logs detallados en GitHub
Actions → Seleccionar run → Click en step que falló

# Problemas comunes:
# - Secrets no configurados: Verifica DOCKER_USERNAME, DOCKER_PASSWORD, AZURE_CREDENTIALS
# - Tests fallan: Ejecuta tests localmente primero
# - Azure login falla: Verifica que el Service Principal tenga permisos
# - Deploy falla: Verifica que AKS exista y sea accesible
```

### 🔴 API retorna 401

```bash
# Verificar headers
curl -v -X POST \
  -H "X-Parse-REST-API-Key: 2f5ae96c-b558-4c7b-a590-a501ae1c3f6c" \
  -H "X-JWT-KWY: token" \
  http://$EXTERNAL_IP/DevOps

# Asegúrate de usar la API Key exacta:
# 2f5ae96c-b558-4c7b-a590-a501ae1c3f6c
```

### 🔴 Health check falla

```bash
# Verificar endpoint directamente en pod
kubectl exec -it <pod-name> -n default -- curl http://localhost:8000/health

# Debería retornar: {"status":"healthy"}
```

### 🔴 Limpiar todo y empezar de nuevo

```bash
# 1. Eliminar recursos de Kubernetes
kubectl delete -f k8s/

# 2. Destruir infraestructura de Azure
cd infra
terraform destroy -auto-approve

# 3. Limpiar imágenes Docker locales
docker system prune -a --volumes

# 4. Volver a desplegar desde cero
terraform apply -auto-approve
az aks get-credentials --resource-group rg-banking-devops --name aks-banking-cluster
kubectl apply -f k8s/
```

## 📝 Mejoras Futuras

- [ ] Implementar autenticación JWT real
- [ ] Agregar rate limiting
- [ ] Implementar circuit breaker pattern
- [ ] Añadir distributed tracing (OpenTelemetry)
- [ ] Métricas con Prometheus
- [ ] Dashboards con Grafana
- [ ] Implementar API Gateway (Azure API Management)
- [ ] Secrets management con Azure Key Vault
- [ ] Backup automatizado de configuraciones

## 👥 Autor

**Byron Realpe** - Senior DevOps Engineer & Backend Developer

## 📄 Licencia

Este proyecto es parte de una prueba técnica bancaria.

---

## 📞 Soporte

Para preguntas o soporte, contactar a través de los issues del repositorio.

**Versión:** 1.0.0  
**Última actualización:** Noviembre 2025
