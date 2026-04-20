#!/bin/bash
# Script para rodar o projeto completo localmente (sem Docker)

echo "=== Ballistic Trajectory Simulator - Modo Desenvolvimento ==="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar se ambiente virtual existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Criando ambiente virtual...${NC}"
    python3 -m venv venv
fi

# Ativar venv
source venv/bin/activate

# Instalar dependências se necessário
if [ ! -f "venv/.deps_installed" ]; then
    echo -e "${YELLOW}Instalando dependências...${NC}"
    pip install -r requirements.txt --quiet
    touch venv/.deps_installed
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js não encontrado. Instale o Node.js primeiro.${NC}"
    exit 1
fi

echo -e "${GREEN}Iniciando serviços...${NC}"
echo ""

# Função para limpar ao sair
cleanup() {
    echo -e "${YELLOW}Encerrando serviços...${NC}"
    kill $PID_BACKEND $PID_FRONTEND 2>/dev/null
    exit 0
}

trap cleanup EXIT INT TERM

# 1. Iniciar backend FastAPI em background
echo -e "${BLUE}[1/3] Iniciando FastAPI (Backend)...${NC}"
cd /home/kfrural/Documentos/github/ballistic_trajectory_simulator
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload &
PID_BACKEND=$!
echo "Backend rodando em http://localhost:8000"
echo "Docs em http://localhost:8000/docs"
echo ""

# 2. Iniciar frontend React
echo -e "${BLUE}[2/3] Iniciando Frontend (React)...${NC}"
cd /home/kfrural/Documentos/github/ballistic_trajectory_simulator/frontend
PORT=3000 npm start &
PID_FRONTEND=$!
echo "Frontend rodando em http://localhost:3000"
echo ""

# 3. Info do Airflow (manual)
echo -e "${BLUE}[3/3] Airflow instructions:${NC}"
echo "Para rodar Airflow单独的, use:"
echo "  airflow webserver -p 8080"
echo "  airflow scheduler"
echo ""
echo "Ou com Docker Compose completo:"
echo "  docker-compose -f docker-compose.yml up"
echo ""

# Esperar
echo -e "${GREEN}=== Todos os serviços iniciados! ===${NC}"
echo "Acesse:"
echo "  - Frontend: http://localhost:3000"
echo "  - API:      http://localhost:8000"
echo "  - Docs:     http://localhost:8000/docs"
echo ""
echo "Pressione Ctrl+C para encerrar"

wait