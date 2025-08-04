# 🚀 SHADOOM - GUIA COMPLETO DE DEPLOY/PUBLICAÇÃO

## 🎯 OPÇÕES DE PUBLICAÇÃO DO SEU SITE:

---

## 🌟 **OPÇÃO 1: VERCEL + RAILWAY (RECOMENDADO - FÁCIL E GRATUITO)**

### 🎨 **FRONTEND (Vercel - Grátis)**

#### **1️⃣ Preparar arquivos:**
```bash
# Criar repositório Git com apenas o frontend:
mkdir shadoom-frontend
cp -r /app/frontend/* shadoom-frontend/
cd shadoom-frontend

# Inicializar Git
git init
git add .
git commit -m "Shadoom frontend inicial"
```

#### **2️⃣ Configurar build:**
```json
// package.json - adicionar scripts:
{
  "scripts": {
    "build": "react-scripts build",
    "start": "react-scripts start"
  }
}
```

#### **3️⃣ Deploy na Vercel:**
- Acesse: https://vercel.com
- Conecte seu GitHub
- Import Project → shadoom-frontend
- Deploy automático! 🎉

### 🖥️ **BACKEND (Railway - Grátis)**

#### **1️⃣ Preparar backend:**
```bash
# Criar repositório Git com backend:
mkdir shadoom-backend
cp -r /app/backend/* shadoom-backend/
cd shadoom-backend

# Criar Dockerfile
touch Dockerfile
```

#### **2️⃣ Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

#### **3️⃣ Deploy no Railway:**
- Acesse: https://railway.app
- New Project → Deploy from GitHub
- Conectar repositório shadoom-backend
- Adicionar variáveis de ambiente:
  ```
  GEMINI_API_KEY=AIzaSyA7ognYgDQdfTDu1HCBxsmIIZyD0PAzi4w
  MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/shadoom
  DB_NAME=shadoom_db
  ```

#### **4️⃣ MongoDB Atlas (Grátis):**
- Acesse: https://cloud.mongodb.com
- Create Free Cluster
- Copie a connection string
- Use no MONGO_URL do Railway

---

## 🌟 **OPÇÃO 2: NETLIFY + HEROKU (ALTERNATIVA)**

### 🎨 **FRONTEND (Netlify):**
- Drag & drop da pasta `build/` no Netlify
- Ou conectar GitHub automaticamente

### 🖥️ **BACKEND (Heroku):**
- `heroku create shadoom-api`
- `git push heroku main`
- Configurar env vars no dashboard

---

## 🌟 **OPÇÃO 3: VPS PRÓPRIO (AVANÇADO)**

### 🖥️ **Requisitos do Servidor:**
```bash
# Mínimo recomendado:
- 2 GB RAM
- 20 GB Storage  
- Ubuntu 20.04+
- Python 3.8+
- Node.js 16+
- MongoDB
```

### 🔧 **Setup completo:**
```bash
# 1. Instalar dependências
sudo apt update
sudo apt install python3 python3-pip nodejs npm mongodb

# 2. Clonar projeto
git clone seu-repositorio
cd shadoom

# 3. Backend
cd backend
pip3 install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000

# 4. Frontend  
cd ../frontend
npm install
npm run build
npm install -g serve
serve -s build -p 3000

# 5. Nginx (proxy reverso)
sudo apt install nginx
# Configurar nginx para servir frontend e proxy para backend
```

---

## 🌐 **CONFIGURAÇÕES DE DOMÍNIO:**

### 📋 **Atualizar URLs:**

#### **1️⃣ Frontend (.env):**
```bash
# Substituir por sua URL real:
REACT_APP_BACKEND_URL=https://shadoom-api.railway.app
```

#### **2️⃣ Firebase (console):**
```javascript
// Authorized domains:
- seu-dominio.vercel.app
- seu-dominio-personalizado.com

// Authorized JavaScript origins:
- https://seu-dominio.vercel.app
- https://seu-dominio-personalizado.com
```

#### **3️⃣ CORS Backend:**
```python
# server.py - atualizar origins:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://seu-dominio.vercel.app",
        "https://seu-dominio-personalizado.com"
    ]
)
```

---

## 🔒 **VARIÁVEIS DE AMBIENTE NECESSÁRIAS:**

### 🖥️ **BACKEND:**
```bash
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/shadoom_db
DB_NAME=shadoom_db
GEMINI_API_KEY=AIzaSyA7ognYgDQdfTDu1HCBxsmIIZyD0PAzi4w
```

### 🎨 **FRONTEND:**
```bash
REACT_APP_BACKEND_URL=https://sua-api-url.railway.app
```

---

## 📊 **MONITORAMENTO PÓS-DEPLOY:**

### ✅ **Checklist final:**
- [ ] Site carregando corretamente
- [ ] Cadastro de usuários funcionando
- [ ] Login com email/senha OK
- [ ] Login com Google OK (se configurado)
- [ ] Geração de ideias com IA funcionando
- [ ] Upgrade Premium funcionando
- [ ] Painel admin acessível via URL secreta
- [ ] Pagamentos processando (teste)
- [ ] Análise de perfil Premium OK

### 📈 **Ferramentas de Analytics:**
```javascript
// Adicionar ao frontend:
- Google Analytics
- Hotjar (heatmaps)
- LogRocket (session replay)
```

---

## 💡 **DICAS DE OTIMIZAÇÃO:**

### ⚡ **Performance:**
```javascript
// React optimizations:
- Lazy loading de componentes
- Image optimization
- Code splitting
- Service workers (PWA)
```

### 🔍 **SEO:**
```html
<!-- Adicionar ao public/index.html: -->
<title>Shadoom - Gerenciador Fantasma de Engajamento</title>
<meta name="description" content="Banco secreto de ideas com IA para influenciadores">
<meta property="og:title" content="Shadoom">
<meta property="og:description" content="Gere ideias criativas ilimitadas">
```

---

## 🆘 **TROUBLESHOOTING COMUM:**

### ❌ **Problemas e Soluções:**

#### **CORS Error:**
```python
# server.py - verificar origins
allow_origins=["https://seu-dominio-real.com"]
```

#### **MongoDB Connection:**
```python
# Verificar connection string
# Whitelist IP no MongoDB Atlas
```

#### **Firebase Auth:**
```javascript
// Verificar domínios autorizados
// Verificar chaves de API
```

#### **Build Errors:**
```bash
# Limpar cache
npm ci
rm -rf node_modules package-lock.json
npm install
```

---

## 🎉 **RESULTADO FINAL:**

Após seguir este guia, você terá:

✅ **Site profissional** no ar
✅ **Backend robusto** funcionando
✅ **Banco de dados** configurado
✅ **Pagamentos** processando
✅ **Painel admin** exclusivo
✅ **IA Gemini** gerando ideias
✅ **Sistema completo** operacional

**🚀 SHADOOM PRONTO PARA RECEBER SEUS PRIMEIROS CLIENTES! 💰**

---

## 📞 **SUPORTE PÓS-DEPLOY:**

Em caso de problemas no deploy:
1. Verifique logs do servidor
2. Teste todas as funcionalidades
3. Monitore métricas de erro
4. Configure backups automáticos

**BOA SORTE COM SEU LANÇAMENTO! 🎊**