#!/bin/bash
# Script para iniciar ambos servidores en EC2 usando tmux

set -e

echo "🚀 Iniciando servidores..."

# Verificar que tmux está instalado
if ! command -v tmux &> /dev/null; then
    echo "⚠️  tmux no está instalado. Instalando..."
    sudo apt-get update && sudo apt-get install -y tmux
fi

# Crear sesión tmux si no existe
SESSION_NAME="hackeps"

if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "⚠️  La sesión $SESSION_NAME ya existe. Cerrándola..."
    tmux kill-session -t $SESSION_NAME
fi

echo "📡 Creando sesión tmux: $SESSION_NAME"
tmux new-session -d -s $SESSION_NAME

# Ventana 1: Backend (Flask)
echo "🐍 Iniciando servidor Flask en puerto 5000..."
tmux rename-window -t $SESSION_NAME:0 'Backend'
tmux send-keys -t $SESSION_NAME:0 "cd $(pwd)/server && python app.py" C-m

# Ventana 2: Frontend (Vite)
echo "⚡ Iniciando servidor Vite en puerto 5173..."
tmux new-window -t $SESSION_NAME:1 -n 'Frontend'
tmux send-keys -t $SESSION_NAME:1 "cd $(pwd)/client && npm run dev" C-m

echo ""
echo "✅ Servidores iniciados en tmux!"
echo ""
echo "📋 Comandos útiles:"
echo "  - Ver los servidores: tmux attach -t $SESSION_NAME"
echo "  - Cambiar entre ventanas: Ctrl+B y luego 0 (backend) o 1 (frontend)"
echo "  - Salir sin cerrar: Ctrl+B y luego D"
echo "  - Cerrar todo: tmux kill-session -t $SESSION_NAME"
echo ""
echo "🌐 La aplicación estará disponible en:"
echo "   http://$(curl -s ifconfig.me):5173"
echo ""
