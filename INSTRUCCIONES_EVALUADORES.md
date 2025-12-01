# Banco Pichincha - Instrucciones para Evaluadores

## ✅ Requisitos Cumplidos

### 📋 Requisitos Obligatorios

| Requisito | Estado | Ubicación |
|-----------|--------|-----------|
| **Microservicio REST con /DevOps** | ✅ | `app/main.py` |
| **POST con JSON específico** | ✅ | `app/models.py`, `app/main.py` línea 98-114 |
| **Respuesta JSON dinámica** | ✅ | `app/main.py` línea 88-94 |
| **Otros métodos retornan "ERROR"** | ✅ | `app/main.py` línea 166-176 |
| **Seguridad con API Key** | ✅ | `app/main.py` línea 65-71 |
| **Validación de JWT (único)** | ✅ | `app/jwt_manager.py`, `app/main.py` línea 77-79 |
| **Microservicio containerizado** | ✅ | `app/Dockerfile` |
| **Load Balancer con 2+ nodos** | ✅ | `k8s/service.yaml`, `k8s/deployment.yaml` (replicas: 2) |
| **IaC versionado** | ✅ | `infra/main.tf` (Terraform para AKS) |
| **Pipeline como código** | ✅ | `.github/workflows/ci-cd.yml` |
| **Dependency Management** | ✅ | `app/requirements.txt`, pip |
| **Stages: build y test** | ✅ | `.github/workflows/ci-cd.yml` líneas 18-75 |
| **Auto en cualquier branch** | ✅ | `.github/workflows/ci-cd.yml` líneas 3-7 |
| **Deploy master a producción** | ✅ | `.github/workflows/ci-cd.yml` línea 80 |
| **Ejecución manual** | ✅ | `.github/workflows/ci-cd.yml` línea 6 |
| **Tests automáticos** | ✅ | `app/test_main.py` (19 tests, 86.67% coverage) |
| **Static code revision** | ✅ | `.github/workflows/ci-cd.yml` línea 36-38 (Pylint) |
| **Dynamic grow (HPA)** | ✅ | `k8s/hpa.yaml` (2-10 réplicas) |
| **API Manager para JWT** | ✅ | `app/jwt_manager.py`, `/api/generate-token` |

### 🎯 Requisitos Adicionales Implementados

- ✅ **JWT único por transacción:** Sistema de cache en memoria que previene reutilización
- ✅ **Test Coverage:** 86.67% con reportes en CI/CD
- ✅ **Clean Code:** Funciones pequeñas, nombres descriptivos, docstrings completos
- ✅ **TDD:** Tests escritos primero, 19 tests cubriendo todos los casos
- ✅ **Azure Container Registry (ACR):** Integración con AKS
- ✅ **Metrics Server:** Para HPA funcional
- ✅ **Security Scan:** Trivy vulnerability scanner en pipeline
- ✅ **Zero Downtime Deployments:** Rolling updates

## 🧪 Comandos de Prueba

### 1. Generar JWT Token

```bash
# Reemplaza <EXTERNAL_IP> con la IP pública del LoadBalancer
curl -X POST \
  -H "X-Parse-REST-API-Key: 2f5ae96c-b558-4c7b-a590-a501ae1c3f6c" \
  http://<EXTERNAL_IP>/api/generate-token
```

**Respuesta esperada:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "type": "Bearer",
  "expires_in": 300,
  "usage": "Include in X-JWT-KWY header for /DevOps endpoint"
}
```

### 2. Usar Token en Request (Comando Oficial)

```bash
# Guardar token en variable
JWT_TOKEN="<token-generado-arriba>"

# Ejecutar request oficial
curl -X POST \
  -H "X-Parse-REST-API-Key: 2f5ae96c-b558-4c7b-a590-a501ae1c3f6c" \
  -H "X-JWT-KWY: ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "This is a test",
    "to": "Juan Perez",
    "from": "Rita Asturia",
    "timeToLifeSec": 45
  }' \
  http://<EXTERNAL_IP>/DevOps
```

**Respuesta esperada:**
```json
{
  "message": "Hello Juan Perez your message will be send"
}
```

### 3. Verificar JWT Único (Solo una vez)

```bash
# Intentar reusar el mismo token (debe fallar)
curl -X POST \
  -H "X-Parse-REST-API-Key: 2f5ae96c-b558-4c7b-a590-a501ae1c3f6c" \
  -H "X-JWT-KWY: ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message":"test","to":"Juan","from":"Rita","timeToLifeSec":45}' \
  http://<EXTERNAL_IP>/DevOps
```

**Respuesta esperada (401):**
```json
{
  "detail": "JWT token already used"
}
```

### 4. Verificar Métodos No Permitidos

```bash
# GET debe retornar "ERROR"
curl -X GET http://<EXTERNAL_IP>/DevOps

# PUT debe retornar "ERROR"
curl -X PUT http://<EXTERNAL_IP>/DevOps

# DELETE debe retornar "ERROR"
curl -X DELETE http://<EXTERNAL_IP>/DevOps
```

**Respuesta esperada:**
```
ERROR
```

## 🏗️ Arquitectura Desplegada

```
┌─────────────────────────────────────────────────────┐
│  Azure Resource Group: rg-banking-devops            │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  AKS Cluster: aks-banking-cluster              │ │
│  │  ├─ Node 1 (Standard_B2s)                      │ │
│  │  │  └─ Pod: banking-devops-api-xxx (replica 1) │ │
│  │  │     └─ Container: FastAPI App               │ │
│  │  │                                              │ │
│  │  ├─ Node 2 (Standard_B2s)                      │ │
│  │  │  └─ Pod: banking-devops-api-yyy (replica 2) │ │
│  │  │     └─ Container: FastAPI App               │ │
│  │  │                                              │ │
│  │  └─ Load Balancer Service                      │ │
│  │     └─ External IP: <PUBLIC_IP>                │ │
│  │                                                 │ │
│  │  ┌──────────────────────────────────┐          │ │
│  │  │  HPA (Horizontal Pod Autoscaler) │          │ │
│  │  │  Min: 2, Max: 10                 │          │ │
│  │  │  Target: CPU 70%, Memory 80%     │          │ │
│  │  └──────────────────────────────────┘          │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  ACR: acrbankingdevops.azurecr.io              │ │
│  │  └─ Image: banking-devops-api:latest           │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  Log Analytics Workspace                       │ │
│  │  └─ Container Insights (Monitoring)            │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## 📊 Evidencias de Calidad

### Tests y Coverage

```bash
# Ejecutar tests localmente
cd app
pytest test_main.py -v --cov=. --cov-report=term-missing

# Resultado:
# 19 passed
# Coverage: 86.67%
```

**Tests incluidos:**
- ✅ Happy path con credenciales válidas
- ✅ Mensaje dinámico (usa nombre del campo "to")
- ✅ API Key inválida (401)
- ✅ API Key faltante (401)
- ✅ JWT faltante (401)
- ✅ Ambos headers faltantes (401)
- ✅ **JWT ya usado (401)** ⭐
- ✅ **Generación de JWT** ⭐
- ✅ **Estadísticas de tokens** ⭐
- ✅ GET retorna "ERROR"
- ✅ PUT retorna "ERROR"
- ✅ DELETE retorna "ERROR"
- ✅ PATCH retorna "ERROR"
- ✅ Ruta inválida retorna "ERROR"
- ✅ Root path retorna "ERROR"
- ✅ Campo faltante (422)
- ✅ Valor inválido (422)
- ✅ Health check
- ✅ Nombre dinámico en respuesta

### Static Code Analysis

```bash
# Ejecutar linter
cd app
pylint *.py --disable=C0114,C0115,C0116 --max-line-length=120

# Score mínimo requerido: 8.0/10
# El pipeline falla si el score es < 8.0
```

### Infraestructura como Código

```bash
# Ver plan de Terraform
cd infra
terraform plan

# Recursos:
# + azurerm_resource_group.rg
# + azurerm_kubernetes_cluster.aks (2 nodos)
# + azurerm_container_registry.acr
# + azurerm_log_analytics_workspace.law
# + azurerm_role_assignment.aks_acr_pull
```

## 🔄 Pipeline CI/CD

El pipeline se ejecuta automáticamente en:
- ✅ Push a cualquier rama
- ✅ Pull request
- ✅ Ejecución manual

### Stages:

1. **Build & Test** (Todas las branches)
   - Checkout código
   - Setup Python 3.9
   - Install dependencies
   - Run Pylint (calificación mínima 8.0)
   - Run Pytest con coverage (mínimo 80%)
   - Build Docker image
   - Push a ACR

2. **Deploy to AKS** (Solo master o manual)
   - Azure login
   - Set AKS context
   - Update deployment.yaml con imagen específica
   - Deploy manifiestos K8s
   - Verify rollout
   - Get LoadBalancer IP
   - Test service

3. **Security Scan** (Solo master)
   - Trivy vulnerability scan
   - Upload SARIF to GitHub Security

## 🎯 Puntos Destacados

### 1. JWT Único por Transacción ⭐

Implementamos un sistema completo de JWT management:
- Generación de tokens con identificador único (JTI)
- Validación de expiración (5 minutos)
- Cache en memoria con TTL
- Cleanup automático de tokens expirados
- Endpoint `/api/generate-token` para generar tokens
- Endpoint `/api/token-stats` para estadísticas

**Archivo:** `app/jwt_manager.py`

### 2. Clean Code ⭐

- Funciones pequeñas y con responsabilidad única
- Nombres descriptivos (validate_security_headers, build_success_message)
- Docstrings completos en todas las funciones
- Type hints en todos los parámetros
- Constantes definidas al inicio
- Logging estructurado

**Archivos:** `app/main.py`, `app/models.py`

### 3. TDD Real ⭐

- 19 tests automatizados
- 86.67% de cobertura de código
- Tests escritos antes de la implementación
- Cobertura de happy path, edge cases y security
- Tests ejecutados en CI/CD con umbral mínimo

**Archivo:** `app/test_main.py`

### 4. Cero Downtime ⭐

- Rolling updates con `maxUnavailable: 0`
- Health checks (liveness y readiness)
- 2 réplicas mínimas
- Pod anti-affinity para distribución en nodos
- HPA para escalar bajo carga

**Archivos:** `k8s/deployment.yaml`, `k8s/hpa.yaml`

## 📝 Información Adicional

### Costos (2 días)

- AKS (2 nodos Standard_B2s): ~$4.00 USD
- ACR Basic: ~$0.33 USD
- Log Analytics: ~$0.20 USD
- **Total:** ~$4.50 USD por 2 días

### Comandos Útiles

```bash
# Ver pods
kubectl get pods -n default

# Ver logs
kubectl logs -l app=banking-devops -n default

# Ver métricas
kubectl top pods -n default
kubectl top nodes

# Ver HPA
kubectl get hpa -n default

# Port-forward para debug
kubectl port-forward svc/banking-devops-service 8080:80 -n default

# Destruir infraestructura
cd infra
terraform destroy -auto-approve
```

## 🔗 URLs Importantes

- **GitHub Repository:** https://github.com/ByronAnto/repositorio_test_banco
- **API Endpoint:** `http://<EXTERNAL_IP>/DevOps`
- **Health Check:** `http://<EXTERNAL_IP>/health`
- **Generate Token:** `http://<EXTERNAL_IP>/api/generate-token`
- **Token Stats:** `http://<EXTERNAL_IP>/api/token-stats`

## ✅ Checklist Final

- [x] Microservicio REST con endpoint /DevOps
- [x] POST acepta JSON con campos específicos
- [x] Respuesta JSON dinámica con nombre del destinatario
- [x] Otros métodos HTTP retornan "ERROR"
- [x] Validación de API Key en header
- [x] Validación de JWT en header
- [x] **JWT único por transacción (no reutilizable)**
- [x] Containerización con Docker
- [x] Load Balancer con 2+ nodos
- [x] Infraestructura como código (Terraform)
- [x] Pipeline como código (GitHub Actions)
- [x] Dependency management
- [x] Stages: build, test, deploy
- [x] Automático en cualquier branch
- [x] Deploy a producción en master
- [x] Ejecución manual disponible
- [x] Tests automáticos (19 tests)
- [x] **Coverage 86.67%**
- [x] Static code analysis (Pylint)
- [x] **Dynamic grow con HPA**
- [x] **API Manager para JWT**
- [x] Clean Code
- [x] TDD
- [x] Zero Downtime Deployments
- [x] Monitoring con Log Analytics
- [x] Security Scan con Trivy

---

**Desarrollado por:** Byron Realpe  
**Fecha:** Noviembre 2025  
**Versión:** 1.0.0
