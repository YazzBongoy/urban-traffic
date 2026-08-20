# Deployment Guide

## Production Deployment

### Prerequisites
- Kubernetes cluster (EKS/GKE/AKS)
- Terraform 1.5+
- Helm 3.x
- kubectl

### Infrastructure Setup

```bash
cd infra/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file=production.tfvars

# Apply infrastructure
terraform apply -var-file=production.tfvars
```

### Kubernetes Deployment

```bash
cd infra/kubernetes

# Apply namespaces
kubectl apply -f namespaces.yaml

# Deploy services
kubectl apply -f backend/
kubectl apply -f frontend/
kubectl apply -f database/
```

### Environment Configuration

Create secrets:
```bash
kubectl create secret generic traffic-secrets \
  --from-literal=database-url='postgresql://...' \
  --from-literal=redis-url='redis://...' \
  --from-literal=secret-key='...'
```

## Docker Build

```bash
# Build backend
docker build -t urban-traffic-backend:latest ./backend

# Build frontend
docker build -t urban-traffic-frontend:latest ./frontend

# Tag for registry
docker tag urban-traffic-backend:latest registry.example.com/urban-traffic-backend:latest
docker tag urban-traffic-frontend:latest registry.example.com/urban-traffic-frontend:latest

# Push to registry
docker push registry.example.com/urban-traffic-backend:latest
docker push registry.example.com/urban-traffic-frontend:latest
```

## Monitoring

### Prometheus + Grafana
- Access Grafana: http://grafana.example.com
- Default credentials: admin/admin

### Health Checks
- Backend: http://api.example.com/health
- Frontend: http://frontend.example.com

## Backup

### Database Backup
```bash
# Manual backup
docker-compose exec db pg_dump -U postgres urban_traffic > backup.sql

# Automated (cron)
0 2 * * * docker-compose exec db pg_dump -U postgres urban_traffic | gzip > /backups/urban_traffic_$(date +\%Y\%m\%d).sql.gz
```

## Scaling

### Horizontal Pod Autoscaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Security Checklist

- [ ] TLS certificates configured
- [ ] Secrets encrypted at rest
- [ ] Network policies applied
- [ ] RBAC configured
- [ ] Audit logging enabled
- [ ] Vulnerability scanning enabled
