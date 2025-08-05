# 🚀 SHADOOM - ESTRUTURA COMPLETA PARA GITHUB

## 📂 ESTRUTURA DE REPOSITÓRIOS RECOMENDADA

### 🎨 **REPOSITÓRIO 1: shadoom-frontend**
```
shadoom-frontend/
├── public/
│   ├── index.html              # HTML principal
│   ├── favicon.ico             # Ícone do site
│   └── manifest.json           # PWA manifest
├── src/
│   ├── App.js                  # ⭐ Componente principal (MODIFICAR CONFIG FIREBASE)
│   ├── App.css                 # Estilos customizados e mobile
│   ├── index.js                # Ponto de entrada React
│   └── index.css               # Estilos globais
├── package.json                # Dependências e scripts
├── tailwind.config.js          # Configuração Tailwind
├── postcss.config.js           # Configuração PostCSS
├── craco.config.js             # Configuração CRACO
├── .env                        # ⚠️ CONFIGURAR URL DO BACKEND
├── .env.example                # Exemplo de variáveis
├── .gitignore                  # Arquivos ignorados
├── README.md                   # Documentação
└── yarn.lock                   # Lock de dependências
```

### 🖥️ **REPOSITÓRIO 2: shadoom-backend**
```
shadoom-backend/
├── server.py                   # ⭐ API principal (MODIFICAR CREDENCIAIS ADMIN)
├── requirements.txt            # Dependências Python
├── .env                        # ⚠️ CONFIGURAR MONGO + GEMINI API
├── .env.example                # Exemplo de variáveis
├── Dockerfile                  # Container Docker
├── railway.json               # Configuração Railway (opcional)
├── .gitignore                 # Arquivos ignorados
└── README.md                  # Documentação API
```

---

## 🔧 ARQUIVOS QUE VOCÊ DEVE MODIFICAR

### 📱 **1. FRONTEND - src/App.js**

#### 🔥 **CONFIGURAÇÃO FIREBASE (LINHA ~13-21):**
```javascript
// ⚠️ SUBSTITUA PELA SUA CONFIGURAÇÃO FIREBASE
const firebaseConfig = {
  apiKey: "SUA-API-KEY-AQUI",                    // ✏️ MODIFICAR
  authDomain: "SEU-PROJECT.firebaseapp.com",    // ✏️ MODIFICAR  
  projectId: "SEU-PROJECT-ID",                   // ✏️ MODIFICAR
  storageBucket: "SEU-PROJECT.firebasestorage.app", // ✏️ MODIFICAR
  messagingSenderId: "123456789",                // ✏️ MODIFICAR
  appId: "1:123456789:web:abc123def456"         // ✏️ MODIFICAR
};
```

#### 🔍 **ONDE OBTER ESSAS INFORMAÇÕES:**
1. Acesse: https://console.firebase.google.com
2. Selecione seu projeto
3. ⚙️ Configurações do projeto
4. 📱 Seus apps → Configuração do SDK

---

### 🖥️ **2. BACKEND - server.py**

#### 🔐 **CREDENCIAIS ADMIN (LINHA ~35-36):**
```python
# ⚠️ SUBSTITUA PELAS SUAS CREDENCIAIS
ADMIN_EMAIL = "seu-email@dominio.com"          # ✏️ MODIFICAR
ADMIN_PASSWORD = "SuaSenhaSegura123!"          # ✏️ MODIFICAR
```

---

### 🔑 **3. FRONTEND - .env**
```bash
# ⚠️ URL DO SEU BACKEND DEPLOYADO
REACT_APP_BACKEND_URL=https://seu-backend.railway.app  # ✏️ MODIFICAR
```

### 🔑 **4. BACKEND - .env**
```bash
# ⚠️ CONFIGURAÇÕES DO SERVIDOR
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/shadoom_db  # ✏️ MODIFICAR
DB_NAME=shadoom_db
GEMINI_API_KEY=AIzaSyA7ognYgDQdfTDu1HCBxsmIIZyD0PAzi4w  # ✅ JÁ CONFIGURADA
```

---

## 📋 ARQUIVOS .env.example (PARA OUTROS DESENVOLVEDORES)

### 🎨 **FRONTEND - .env.example:**
```bash
# URL do backend da API
REACT_APP_BACKEND_URL=https://seu-backend.railway.app
```

### 🖥️ **BACKEND - .env.example:**
```bash
# Conexão MongoDB (MongoDB Atlas recomendado)
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/database_name
DB_NAME=shadoom_db

# Chave da API Gemini (Google AI Studio)
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🐳 DOCKERFILE (PARA BACKEND)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta (Railway usa variável $PORT)
EXPOSE $PORT

# Comando de inicialização
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port $PORT"]
```

---

## 📦 PACKAGE.JSON OTIMIZADO

```json
{
  "name": "shadoom-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "firebase": "^10.7.1",
    "axios": "^1.6.2",
    "@tailwindcss/forms": "^0.5.7"
  },
  "scripts": {
    "start": "craco start",
    "build": "craco build",
    "test": "craco test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "devDependencies": {
    "@craco/craco": "^7.1.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6"
  }
}
```

---

## 🎯 RAILWAY.JSON (CONFIGURAÇÃO OPCIONAL)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## 📝 README.md TEMPLATES

### 🎨 **FRONTEND README:**
```markdown
# 👻 Shadoom Frontend

Interface React para o Shadoom - Gerenciador Fantasma de Engajamento.

## 🚀 Deploy Rápido

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/SEU-USUARIO/shadoom-frontend)

## ⚙️ Configuração

1. Clone o repositório
2. Copie `.env.example` para `.env`
3. Configure as variáveis de ambiente:
   - `REACT_APP_BACKEND_URL`: URL do seu backend

## 🔧 Desenvolvimento Local

```bash
yarn install
yarn start
```

## 📱 Recursos

- ✅ Autenticação Firebase
- ✅ Interface responsiva
- ✅ Sistema de pagamentos
- ✅ Design moderno
```

### 🖥️ **BACKEND README:**
```markdown
# 🖥️ Shadoom Backend

API FastAPI para o Shadoom com integração IA Gemini.

## 🚀 Deploy Rápido

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/TEMPLATE-ID)

## ⚙️ Configuração

1. Configure variáveis de ambiente:
   - `MONGO_URL`: String de conexão MongoDB
   - `GEMINI_API_KEY`: Chave da API Gemini

## 🔧 Desenvolvimento Local

```bash
pip install -r requirements.txt
uvicorn server:app --reload
```

## 📊 Recursos

- ✅ IA Gemini para geração de ideias
- ✅ Sistema de usuários e planos
- ✅ Painel administrativo
- ✅ Integração MongoDB
```

---

## 🔄 PROCESSO DE DEPLOY

### 📋 **CHECKLIST DE MODIFICAÇÕES:**

#### ✏️ **ANTES DE FAZER COMMIT:**

**FRONTEND:**
- [ ] Substituir `firebaseConfig` em `src/App.js`
- [ ] Configurar `REACT_APP_BACKEND_URL` em `.env`
- [ ] Verificar se todas as URLs estão corretas

**BACKEND:**
- [ ] Alterar `ADMIN_EMAIL` e `ADMIN_PASSWORD` em `server.py`
- [ ] Configurar `MONGO_URL` (MongoDB Atlas)
- [ ] Verificar `GEMINI_API_KEY`

**FIREBASE CONSOLE:**
- [ ] Adicionar domínio do frontend em "Authorized domains"
- [ ] Configurar "Authorized JavaScript origins"

---

## 🌐 URLs DE EXEMPLO PÓS-DEPLOY

```bash
# Frontend (Vercel)
https://shadoom-frontend.vercel.app

# Backend (Railway)  
https://shadoom-backend.railway.app

# Admin Panel
https://shadoom-frontend.vercel.app/?admin=shadoom_secret_2025
```

---

## 🔒 VARIÁVEIS SECRETAS (NÃO COMMITAR)

### ⚠️ **NUNCA COMMITE NO GIT:**
```bash
# .env files com valores reais
.env
.env.local
.env.production

# Credenciais
firebase-admin-key.json
```

### ✅ **SEMPRE COMMITA:**
```bash
# Exemplos de configuração
.env.example
.env.sample
README.md
```

---

## 📞 SUPORTE PÓS-DEPLOY

Após o deploy, teste:

1. ✅ Cadastro de usuários
2. ✅ Login com email/Google
3. ✅ Geração de ideias
4. ✅ Upgrade Premium
5. ✅ Painel admin via URL secreta

**🎉 SEU SHADOOM ESTÁ PRONTO PARA O MUNDO! 🚀**