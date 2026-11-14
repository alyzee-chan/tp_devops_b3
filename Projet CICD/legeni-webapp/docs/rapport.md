# Rapport Final DevOps – Chaîne CI/CD Complète « Du Commit à la Production »

**Formation :** B3 DevOps – Cours B3COM0105  
**Auteur :** Alyzée Aurore (`alyzeeaurore` / `alyzee-chan`)  
**Application :** Legeni WebApp (Flask + Redis)  
**Dépôt GitHub :** `https://github.com/alyzeeaurore/legeni-webapp.git`  
**Registre Docker Hub :** `https://hub.docker.com/r/alyzeeaurore/legeni-webapp`  

---

## 1. Vue d'ensemble de l'Architecture

La chaîne CI/CD implémente un pipeline continu sans couture :

---

## 2. Détail des Lots Réalisés

### Lot 0 – Organisation Git
- **Branche principale `main` protégée** : déploiement en production uniquement via commits validés.
- **Workflow de branches** : `feature/*` pour les développements sans déploiement en prod.
- **Gestion des tags** : Versionnage sémantique strict `v<VERSION>` (ex : `v1.0.0` appliqué au commit `0e85711`).
- Alias de log lisible configuré : `git log --graph --oneline --decorate`.

### Lot 1 – Conteneurisation Multi-stage & Sécurité
- **Dockerfile multi-stage** (`Dockerfile`) :
  - Étape `test` intermédiaire avec dépendances de développement (`pytest`, `flake8`, `coverage`).
  - Étape `runtime` finale basée sur `python:3.11-alpine` minimale.
- **Sécurité & bonnes pratiques** :
  - Utilisateur non-root dédié (`appuser:10001`).
  - `HEALTHCHECK` configuré interrogeant `/ready` toutes les 30s.
  - Forme `CMD ["python", "app.py"]` (exec form pour propagation propre des signaux SIGTERM).
  - Version injectée dynamiquement via `--build-arg APP_VERSION=1.0.0`.
  - Scan de vulnérabilité Trivy validé sans failles critiques bloquantes.

### Lot 2 – Infrastructure as Code (Ansible)
- **Playbook de provisioning** (`ansible/provision.yml`) :
  - Détection et initialisation de Docker Engine.
  - Déploiement automatique du serveur Jenkins personnalisé (`jenkins-custom:latest`).
  - Démarrage et configuration de Minikube (driver `docker`, k8s `v1.30.0`).
  - Activation déclarative des addons `metrics-server` et `ingress`.
- **Secrets sécurisés** :
  - Mot de passe Redis et secrets chiffrés sous **Ansible Vault** (`vars/vault.yml`).
  - Fichier de clé `.vault_pass` protégé (permissions `600`).
  - Idempotence prouvée : deuxième exécution `changed=0`.

### Lot 3 – Orchestration Kubernetes & Résilience
- **Séparation Staging / Prod** :
  - Namespace `legeni-staging` (1 à 2 réplicas, env staging).
  - Namespace `legeni-prod` (3 réplicas, env prod, haute disponibilité).
- **Persistance** :
  - Base Redis déployée en **StatefulSet** avec `PersistentVolumeClaim` (volume persistant 1Gi) et mot de passe injecté via `Secret`.
- **Haute disponibilité & Zéro Downtime** :
  - Déploiement avec stratégie `RollingUpdate` : `maxSurge: 1`, `maxUnavailable: 0`.
  - Probes configurées : `readinessProbe` sur `/ready` (période 5s) et `livenessProbe` sur `/health`.
  - Gestion des ressources : `requests: cpu 50m, memory 64Mi` / `limits: cpu 200m, memory 128Mi`.
- **Automatisation & Rollback automatique** :
  - Playbook Ansible `deploy.yml` utilisant `kubernetes.core.k8s`.
  - Attente du rollout effectif avec timeout.
  - Bloc `rescue` : en cas d'image défectueuse ou d'échec du healthcheck, déclenchement immédiat de `kubectl rollout undo` automatique avec conservation de l'ancienne version saine.

### Lot 4 – Intégration Continue (Jenkins)
- **Pipeline as Code** (`Jenkinsfile`) :
  - Pipeline déclaratif avec options `ansiColor('xterm')` et `timeout(time: 30, unit: 'MINUTES')`.
  - Exécution en parallèle des tests unitaires et linters pour minimiser le cycle de feedback.
  - Publication automatisée des rapports de tests JUnit (`results.xml`) et de couverture (`coverage.xml`).
  - Gestion des identifiants via le credential store Jenkins (`docker-hub-credentials`, `vault-password`).

### Lot 5 – Déploiement Continu & Validation
- Déploiement en `staging` dès que les tests et scans sont verts.
- **Porte de validation humaine (`input`)** demandant l'approbation explicite d'un opérateur avant promotion en production.
- Déploiement en `prod` via Ansible, suivi d'un smoke-test in-cluster vérifiant l'endpoint `/api/info`.
- Preuve de rollback testée avec succès (tentative de déploiement d'une version inexistante `9.9.9` conduisant au rollback automatique et préservation de la version `1.0.0`).

---

## 3. Synthèse de Conformité et Validation

| Lot | Exigence | Statut | Preuve / Validation |
|---|---|---|---|
| **Lot 0** | Git conventionnel & branches | **Conforme** | Tag `v1.0.0` posé, branche `main` synchronisée |
| **Lot 1** | Docker multi-stage & non-root | **Conforme** | Image `alyzeeaurore/legeni-webapp:1.0.0` sur Docker Hub |
| **Lot 2** | Ansible provisioning & Vault | **Conforme** | Playbooks `provision.yml` et `site.yml` testés |
| **Lot 3** | K8s staging/prod, StatefulSet & Rollback | **Conforme** | Namespaces actifs, rollback automatique validé |
| **Lot 4** | Jenkins CI parallèle & Trivy | **Conforme** | Pipeline Jenkinsfile testé avec rapports JUnit |
| **Lot 5** | CD avec gate & zéro downtime | **Conforme** | Staging et Prod validés via smoke-tests curl |

