# 🚀 Guía de Despliegue en EC2

## 📋 Requisitos Previos

1. Acceso SSH a tu instancia EC2
2. Python 3.8+ instalado
3. Node.js 16+ y npm instalados
4. Puertos 5173 abiertos en el Security Group de EC2

## 🔧 Configuración del Security Group

Asegúrate de que tu Security Group de EC2 tenga estas reglas de entrada:

| Tipo | Protocolo | Puerto | Origen |
|------|-----------|--------|--------|
| HTTP | TCP | 5173 | 0.0.0.0/0 |
| SSH | TCP | 22 | Tu IP |

## 📦 Instalación

### 1. Clonar el repositorio en EC2

```bash
ssh -i tu-clave.pem ubuntu@ec2-3-85-134-16.compute-1.amazonaws.com
git clone https://github.com/aleixJ/hackEPS_2025.git
cd hackEPS_2025
```

### 2. Configurar variables de entorno

```bash
cd server
cp .env.example .env  # Si existe
nano .env  # Edita y agrega tu GOOGLE_API_KEY
```

Contenido del `.env`:
```
GOOGLE_API_KEY=tu_clave_api_aqui
```

### 3. Instalar dependencias

```bash
# Desde el directorio raíz del proyecto
chmod +x deploy_ec2.sh
./deploy_ec2.sh
```

## 🎯 Iniciar los Servidores

### Opción 1: Usando el script automático (recomendado)

```bash
chmod +x start_servers.sh
./start_servers.sh
```

Esto iniciará ambos servidores en una sesión tmux. Para ver los logs:
```bash
tmux attach -t hackeps
```

### Opción 2: Manualmente en terminales separadas

**Terminal 1 - Backend:**
```bash
cd server
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd client
npm run dev
```

## 🌐 Acceder a la Aplicación

Una vez iniciados los servidores, accede a:
```
http://ec2-3-85-134-16.compute-1.amazonaws.com:5173
```

## 🔍 Verificar que funciona

```bash
# Verificar backend (desde EC2)
curl http://localhost:5000/api/health

# Verificar frontend (desde tu navegador)
# Abre: http://ec2-3-85-134-16.compute-1.amazonaws.com:5173
```

## 🛠️ Comandos Útiles

### Ver logs en tmux
```bash
tmux attach -t hackeps
# Cambiar entre ventanas: Ctrl+B luego 0 (backend) o 1 (frontend)
# Salir sin cerrar: Ctrl+B luego D
```

### Detener los servidores
```bash
tmux kill-session -t hackeps
```

### Reiniciar un servidor
```bash
tmux attach -t hackeps
# Ir a la ventana que quieras reiniciar (Ctrl+B luego 0 o 1)
# Ctrl+C para detener
# Flecha arriba para repetir el comando anterior
```

## 🐛 Solución de Problemas

### Puerto 5173 ya en uso
```bash
# Encontrar y matar el proceso
lsof -ti:5173 | xargs kill -9
```

### Permisos denegados
```bash
chmod +x deploy_ec2.sh start_servers.sh
```

### Error de módulo Python no encontrado
```bash
cd server
pip install -r requirements.txt
```

### Error de npm
```bash
cd client
rm -rf node_modules package-lock.json
npm install
```

## 📊 Monitoreo

Para ver el uso de recursos:
```bash
# CPU y memoria
htop

# Espacio en disco
df -h

# Logs del sistema
journalctl -f
```

## 🔐 Seguridad

**IMPORTANTE:** 
- No expongas el puerto 5000 (Flask) públicamente
- Flask corre en localhost:5000 solo accesible desde el EC2
- Vite hace proxy de las peticiones /api/* a localhost:5000
- Solo el puerto 5173 (Vite) debe estar abierto al público

## 🔄 Actualizar la Aplicación

```bash
cd hackEPS_2025
git pull
./deploy_ec2.sh
tmux kill-session -t hackeps
./start_servers.sh
```

## 📝 Arquitectura

```
Internet
   ↓
[Puerto 5173] → Vite Dev Server (0.0.0.0:5173)
                      ↓ (proxy /api/*)
                [localhost:5000] → Flask App
```

- **Cliente:** Vite escucha en 0.0.0.0:5173 (público)
- **Servidor:** Flask escucha en 127.0.0.1:5000 (solo local)
- **Proxy:** Vite redirige /api/* a localhost:5000
