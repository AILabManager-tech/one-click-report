#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# ONE-CLICK REPORT — DÉPLOIEMENT VPS AUTOMATISÉ
# ═══════════════════════════════════════════════════════════════════════
# Lit manifest.json → rsync vers VPS → docker-compose up → nginx config
# Usage: bash deploy.sh [--check | --build-only | --push-only | --ssl]
# ═══════════════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST="$SCRIPT_DIR/manifest.json"

# ─── Couleurs ────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()   { echo -e "${GREEN}  OK${NC}  $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }

# ─── Bannière ────────────────────────────────────────────────────────
echo -e "${CYAN}"
cat << 'BANNER'
  ╔══════════════════════════════════════════════════╗
  ║   ONE-CLICK REPORT — VPS Auto Deploy v3.1       ║
  ╚══════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

# ─── 1. Lecture du manifeste ─────────────────────────────────────────
[ -f "$MANIFEST" ] || fail "manifest.json introuvable"
command -v jq >/dev/null 2>&1 || fail "jq requis: sudo apt install jq"

PROJECT=$(jq -r '.project.name' "$MANIFEST")
VERSION=$(jq -r '.project.version' "$MANIFEST")
DOMAIN=$(jq -r '.project.domain' "$MANIFEST")
VPS_HOST=$(jq -r '.deployment.vps_host' "$MANIFEST")
VPS_USER=$(jq -r '.deployment.vps_user' "$MANIFEST")
REMOTE_DIR=$(jq -r '.deployment.remote_dir' "$MANIFEST")
FE_PORT=$(jq -r '.deployment.frontend_port' "$MANIFEST")
BE_PORT=$(jq -r '.deployment.backend_port' "$MANIFEST")

OPENAI_KEY=$(jq -r '.secrets.OPENAI_API_KEY // empty' "$MANIFEST")
SUPABASE_URL=$(jq -r '.secrets.SUPABASE_URL // empty' "$MANIFEST")

ok "Manifeste: ${BOLD}$PROJECT${NC} v$VERSION → ${CYAN}$VPS_HOST${NC}"

# ─── 2. Génération du .env pour docker-compose ──────────────────────
generate_env() {
    log "Génération de .env depuis manifest.json..."
    cat > "$SCRIPT_DIR/.env" << ENVEOF
OPENAI_API_KEY=${OPENAI_KEY}
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_SERVICE_KEY=$(jq -r '.secrets.SUPABASE_SERVICE_KEY // empty' "$MANIFEST")
ENVEOF
    ok ".env généré"
}

# ─── Mode --check ────────────────────────────────────────────────────
run_check() {
    echo ""
    echo -e "  ${BOLD}Projet${NC}:    ${CYAN}$PROJECT${NC} v$VERSION"
    echo -e "  ${BOLD}Domaine${NC}:   ${CYAN}https://$DOMAIN${NC}"
    echo -e "  ${BOLD}VPS${NC}:       ${CYAN}$VPS_USER@$VPS_HOST${NC}"
    echo -e "  ${BOLD}Remote${NC}:    ${CYAN}$REMOTE_DIR${NC}"
    echo -e "  ${BOLD}Ports${NC}:     frontend=$FE_PORT, backend=$BE_PORT"
    echo -e "  ${BOLD}Langues${NC}:   $(jq -r '.config.languages | join(", ")' "$MANIFEST")"
    echo -e "  ${BOLD}Features${NC}:  $(jq -r '.config.features | join(", ")' "$MANIFEST")"
    echo ""
    echo -e "  ${BOLD}Services (optionnels):${NC}"
    [ -n "$OPENAI_KEY" ] && echo -e "    OpenAI ......... ${GREEN}configuré${NC}" || echo -e "    OpenAI ......... ${YELLOW}absent (fallback stats)${NC}"
    [ -n "$SUPABASE_URL" ] && echo -e "    Supabase ....... ${GREEN}configuré${NC}" || echo -e "    Supabase ....... ${YELLOW}absent (auth désactivé)${NC}"
    echo ""

    log "Test SSH vers $VPS_HOST..."
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "$VPS_USER@$VPS_HOST" "echo ok" >/dev/null 2>&1; then
        ok "SSH connecté"
        ssh "$VPS_USER@$VPS_HOST" "docker --version 2>/dev/null && docker compose version 2>/dev/null" 2>/dev/null && ok "Docker disponible sur le VPS" || warn "Docker non détecté sur le VPS"
    else
        warn "SSH non accessible — vérifiez votre clé ed25519"
    fi
    echo ""
}

# ─── Déploiement complet ─────────────────────────────────────────────
deploy() {
    generate_env

    # Vérifier SSH
    log "Connexion SSH vers $VPS_USER@$VPS_HOST..."
    ssh -o ConnectTimeout=10 -o BatchMode=yes "$VPS_USER@$VPS_HOST" "echo connected" >/dev/null 2>&1 \
        || fail "Impossible de se connecter en SSH à $VPS_HOST. Vérifiez votre clé."
    ok "SSH OK"

    # Créer le dossier distant
    log "Préparation du serveur..."
    ssh "$VPS_USER@$VPS_HOST" "mkdir -p $REMOTE_DIR"

    # Sync le projet vers le VPS
    log "Transfert du projet vers $VPS_HOST:$REMOTE_DIR..."
    rsync -avz --delete \
        --exclude '.git' \
        --exclude 'node_modules' \
        --exclude '.next' \
        --exclude '__pycache__' \
        --exclude '.env.local' \
        "$SCRIPT_DIR/" "$VPS_USER@$VPS_HOST:$REMOTE_DIR/"
    ok "Fichiers synchronisés"

    # Build et démarrage sur le VPS
    log "Build et lancement des conteneurs Docker..."
    ssh "$VPS_USER@$VPS_HOST" << REMOTEOF
        set -e
        cd $REMOTE_DIR

        # Build
        echo "[VPS] Build Docker..."
        docker compose build --no-cache

        # Stop old containers
        docker compose down 2>/dev/null || true

        # Start
        echo "[VPS] Démarrage des services..."
        docker compose up -d

        # Vérification
        echo "[VPS] Attente du healthcheck..."
        sleep 5
        curl -sf http://127.0.0.1:$BE_PORT/health && echo " → Backend OK" || echo " → Backend en démarrage..."
        curl -sf http://127.0.0.1:$FE_PORT   && echo " → Frontend OK" || echo " → Frontend en démarrage..."

        # Nginx config
        echo "[VPS] Configuration nginx..."
        cp $REMOTE_DIR/nginx-report.conf /etc/nginx/sites-available/report.conf
        ln -sf /etc/nginx/sites-available/report.conf /etc/nginx/sites-enabled/report.conf
        nginx -t && systemctl reload nginx
        echo "[VPS] Nginx rechargé"
REMOTEOF

    ok "Conteneurs démarrés"

    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         DÉPLOIEMENT TERMINÉ AVEC SUCCÈS             ║${NC}"
    echo -e "${GREEN}╠══════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║${NC}  URL:      ${CYAN}https://$DOMAIN${NC}"
    echo -e "${GREEN}║${NC}  Backend:  ${CYAN}http://$VPS_HOST:$BE_PORT/health${NC}"
    echo -e "${GREEN}║${NC}  Frontend: ${CYAN}http://$VPS_HOST:$FE_PORT${NC}"
    echo -e "${GREEN}╠══════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║${NC}  Prochaine étape: ${YELLOW}bash deploy.sh --ssl${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
}

# ─── SSL via Certbot ─────────────────────────────────────────────────
setup_ssl() {
    log "Configuration SSL Let's Encrypt pour $DOMAIN..."
    ssh "$VPS_USER@$VPS_HOST" << SSLEOF
        set -e
        apt-get install -y certbot python3-certbot-nginx 2>/dev/null || true
        certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@marksystems.ca
        systemctl reload nginx
        echo "[VPS] SSL activé pour $DOMAIN"
SSLEOF
    ok "Certificat SSL installé: https://$DOMAIN"
}

# ─── Dispatch des arguments ──────────────────────────────────────────
MODE="${1:-deploy}"

case "$MODE" in
    --check)       run_check ;;
    --ssl)         setup_ssl ;;
    --push-only)
        generate_env
        rsync -avz --delete --exclude '.git' --exclude 'node_modules' --exclude '.next' --exclude '__pycache__' "$SCRIPT_DIR/" "$VPS_USER@$VPS_HOST:$REMOTE_DIR/"
        ok "Fichiers synchronisés (push-only)"
        ;;
    *)             deploy ;;
esac
