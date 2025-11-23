#!/bin/bash
# Script para desplegar en EC2

set -e

echo "🚀 Desplegando aplicación en EC2..."

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -d "server" ] || [ ! -d "client" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

echo -e "${YELLOW}📦 Paso 1: Instalando dependencias del servidor...${NC}"
cd server
pip install -r requirements.txt

echo -e "${YELLOW}📦 Paso 2: Instalando dependencias del cliente...${NC}"
cd ../client
npm install

echo -e "${GREEN}✅ Dependencias instaladas${NC}"

echo ""
echo "Para iniciar los servidores en EC2, ejecuta:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    cd server && python app.py"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd client && npm run dev"
echo ""
echo "La aplicación estará disponible en:"
echo "  http://ec2-3-85-134-16.compute-1.amazonaws.com:5173"
echo ""
