# Commandes Docker pour DocQA-MS

## 📋 Vue d'ensemble

**Les projets Python sont exécutés automatiquement par les conteneurs Docker.** Vous n'avez pas besoin de les exécuter manuellement. Chaque service Python (FastAPI) est lancé via `uvicorn` dans son conteneur Docker.

## 🚀 Commandes principales

### 1. Démarrer tous les services (recommandé)

```bash
# Depuis le dossier DocQA-MS
./init_all.sh
```

Ou manuellement :

```bash
# Démarrer tous les services en arrière-plan
docker-compose up -d

# Démarrer tous les services avec logs visibles
docker-compose up
```

### 2. Démarrer des services spécifiques

```bash
# Démarrer uniquement les services de base (DB, Redis, RabbitMQ)
docker-compose up -d postgres rabbitmq redis

# Démarrer un service Python spécifique
docker-compose up -d doc-ingestor
docker-compose up -d llm-qa-module
docker-compose up -d indexeur-semantique
docker-compose up -d deid
docker-compose up -d synthese-comparative
docker-compose up -d audit-logger
```

### 3. Arrêter les services

```bash
# Arrêter tous les services
docker-compose down

# Arrêter tous les services et supprimer les volumes (⚠️ supprime les données)
docker-compose down -v

# Arrêter un service spécifique
docker-compose stop llm-qa-module
```

### 4. Redémarrer les services

```bash
# Redémarrer tous les services
docker-compose restart

# Redémarrer un service spécifique
docker-compose restart llm-qa-module
```

### 5. Vérifier l'état des services

```bash
# Voir le statut de tous les conteneurs
docker-compose ps

# Voir les logs d'un service
docker-compose logs llm-qa-module
docker-compose logs -f llm-qa-module  # Suivre les logs en temps réel
```

### 6. Reconstruire les images

```bash
# Reconstruire toutes les images
docker-compose build

# Reconstruire une image spécifique
docker-compose build llm-qa-module

# Reconstruire sans cache
docker-compose build --no-cache llm-qa-module
```

### 7. Voir les logs de tous les services

```bash
# Logs de tous les services
docker-compose logs

# Logs en temps réel (suivre)
docker-compose logs -f

# Logs des 100 dernières lignes
docker-compose logs --tail=100
```

## 🔧 Services Python disponibles

| Service | Port | Description |
|---------|------|-------------|
| `doc-ingestor` | 8001 | Service d'ingestion de documents |
| `deid` | 8002 | Service de dé-identification |
| `llm-qa-module` | 8003 | Module de questions-réponses avec LLM |
| `indexeur-semantique` | 8004 | Service d'indexation sémantique |
| `synthese-comparative` | 8005 | Service de synthèse comparative |
| `audit-logger` | 8006 | Service d'audit et logging |

## 🌐 Accès aux services

- **API Gateway (Nginx)**: http://localhost:80/api
- **Frontend**: http://localhost:3000 (ou 3001 en développement)
- **PostgreSQL**: localhost:5432
- **RabbitMQ Management**: http://localhost:15672
- **Redis**: localhost:6379

## 🔍 Commandes de débogage

```bash
# Entrer dans un conteneur
docker-compose exec llm-qa-module bash

# Exécuter une commande dans un conteneur
docker-compose exec llm-qa-module python -c "import sys; print(sys.path)"

# Voir les variables d'environnement d'un conteneur
docker-compose exec llm-qa-module env

# Tester une connexion à la base de données depuis un conteneur
docker-compose exec postgres psql -U docqa_user -d docqa_db
```

## ⚠️ Exécution manuelle (non recommandé)

**Vous ne devriez PAS exécuter les services Python manuellement** car ils dépendent de :
- PostgreSQL (dans Docker)
- Redis (dans Docker)
- RabbitMQ (dans Docker)
- Variables d'environnement configurées dans docker-compose.yml

Si vous voulez quand même tester localement (pour le développement), vous devrez :

1. Démarrer les services de base :
```bash
docker-compose up -d postgres rabbitmq redis
```

2. Configurer les variables d'environnement localement

3. Installer les dépendances Python :
```bash
cd DocQA-MS-Backend/llm-qa-module
pip install -r requirements.txt
```

4. Lancer le service :
```bash
cd src
uvicorn main:app --host 0.0.0.0 --port 8003
```

**Mais c'est beaucoup plus compliqué que d'utiliser Docker Compose !**

## 📝 Notes importantes

- Les services Python sont automatiquement démarrés par Docker Compose
- Chaque service utilise `uvicorn` pour lancer l'application FastAPI
- Les services communiquent entre eux via le réseau Docker `docqa-network`
- Les variables d'environnement sont définies dans `docker-compose.yml` et `.env`
- Les migrations de base de données sont exécutées automatiquement par le conteneur `db-migrations`

