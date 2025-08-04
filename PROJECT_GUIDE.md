# 📚 SHADOOM - DOCUMENTAÇÃO COMPLETA DO PROJETO

## 🏗️ ARQUITETURA DO SISTEMA

```
📁 /app/
├── 🖥️ BACKEND (FastAPI + Python)
│   ├── server.py              # Servidor principal da API
│   ├── requirements.txt       # Dependências Python
│   └── .env                  # Variáveis de ambiente do backend
│
├── 🎨 FRONTEND (React + JavaScript)  
│   ├── src/
│   │   ├── App.js            # Componente principal do React
│   │   ├── App.css           # Estilos customizados
│   │   └── index.js          # Ponto de entrada do React
│   ├── public/               # Arquivos estáticos
│   ├── package.json          # Dependências Node.js
│   ├── tailwind.config.js    # Configuração do Tailwind CSS
│   ├── postcss.config.js     # Configuração do PostCSS
│   └── .env                  # Variáveis de ambiente do frontend
│
└── 📋 DOCUMENTAÇÃO
    ├── PROJECT_GUIDE.md       # Este arquivo (guia completo)
    ├── ADMIN_ACCESS.md        # Instruções do painel admin
    └── README.md             # Documentação geral
```

---

## 📄 FUNÇÃO DE CADA ARQUIVO PRINCIPAL:

### 🖥️ **BACKEND FILES:**

#### `server.py` (Coração do Sistema)
```python
# O QUE FAZ:
- 🔌 API REST completa com FastAPI
- 🤖 Integração com IA Gemini para geração de ideias
- 💾 Conexão com MongoDB para dados
- 👥 Sistema de usuários (Free/Premium)
- 💳 Processamento de pagamentos (Cartão + Crypto)
- 🔍 Análise premium de perfis das redes sociais
- 🔐 Painel administrativo com dashboard
- 📊 Métricas e relatórios em tempo real

# PRINCIPAIS ENDPOINTS:
- POST /api/users                 # Criar/buscar usuário
- POST /api/generate-ideas        # Gerar ideias com IA
- POST /api/analyze-profile       # Análise premium de perfil
- POST /api/purchase-premium      # Comprar plano Premium
- GET /api/admin/dashboard        # Dashboard administrativo
```

#### `requirements.txt` (Dependências Python)
```python
# O QUE CONTÉM:
- fastapi                 # Framework web
- motor                   # Driver MongoDB assíncrono
- python-dotenv          # Gerenciamento de variáveis de ambiente
- emergentintegrations   # Biblioteca IA Gemini customizada
- pydantic               # Validação de dados
```

#### `.env` (Configurações Backend)
```bash
# VARIÁVEIS CRÍTICAS:
MONGO_URL="mongodb://localhost:27017"      # Conexão MongoDB
DB_NAME="shadoom_db"                       # Nome do banco
GEMINI_API_KEY="sua-api-key-aqui"         # Chave da IA Gemini
```

---

### 🎨 **FRONTEND FILES:**

#### `App.js` (Interface Principal)
```javascript
// O QUE FAZ:
🔐 Sistema de autenticação (Firebase + Email/Senha + Google)
👤 Gestão de perfis de usuário
🧠 Interface para geração de ideias com IA
📱 Cadastro com redes sociais (@instagram, @tiktok, @kwai)
💎 Sistema de planos (Free/Premium)
💳 Modal de pagamentos (Cartão + Criptomoedas)
🔍 Interface de análise premium de perfis
📚 Histórico de ideias geradas
🔐 Painel administrativo completo (URL secreta)

// COMPONENTES PRINCIPAIS:
- AdminPanel()           # Painel de administração
- PremiumModal()         # Modal de upgrade Premium
- Landing Page           # Página inicial e cadastro
- Dashboard Principal    # Área logada do usuário
```

#### `App.css` (Estilos Visuais)
```css
/* O QUE DEFINE: */
🎨 Design moderno com gradientes purple/pink
✨ Efeitos glass morphism e blur
📱 Responsividade para mobile/tablet/desktop
🖱️ Animações e transições suaves
🌈 Paleta de cores profissional
```

#### `package.json` (Configuração React)
```json
// DEPENDÊNCIAS PRINCIPAIS:
- react                  # Framework frontend
- firebase              # Autenticação e backend
- axios                 # Requisições HTTP
- tailwindcss          # Framework CSS
```

#### `.env` (Configurações Frontend)
```bash
# URL DO BACKEND:
REACT_APP_BACKEND_URL=https://sua-url-backend.com
```

---

## 🔧 CONFIGURAÇÕES IMPORTANTES:

### 🔑 **Firebase (Autenticação)**
```javascript
// firebaseConfig em App.js:
- apiKey: Chave pública do Firebase
- authDomain: Domínio de autenticação
- projectId: ID do projeto Firebase
```

### 🔐 **Admin Credentials (server.py)**
```python
ADMIN_EMAIL = "admin@shadoom.online"
ADMIN_PASSWORD = "@Enigmaext4@"
```

### 🤖 **IA Gemini Integration**
```python
# Usa biblioteca emergentintegrations
- Geração de ideias contextualizadas
- Análise de perfis das redes sociais
- Sistema de fallback robusto
```

---

## 📊 FUNCIONALIDADES IMPLEMENTADAS:

### ✅ **SISTEMA COMPLETO:**
- 👤 Cadastro/Login (Email + Google)
- 🧠 Geração de ideias com IA Gemini
- 💎 Planos Free (10 ideias/mês) / Premium (ilimitado)
- 💳 Pagamentos: Cartão de crédito + Criptomoedas
- 🔍 Análise premium de perfil (@instagram, @tiktok, @kwai)
- 📚 Histórico completo de ideias
- 🔐 Painel admin com métricas em tempo real
- 📱 Interface responsiva e moderna

### ✅ **PAINEL ADMINISTRATIVO:**
- 📊 Dashboard com métricas de negócio
- 👥 Gestão de usuários (upgrade/downgrade)
- 💰 Histórico de pagamentos
- 📈 Relatórios de crescimento
- 🔒 Acesso via URL secreta

---

## 💾 BANCO DE DADOS (MongoDB):

### 📋 **COLEÇÕES:**
```javascript
users {
  id, email, name, plan, instagram_handle, 
  tiktok_handle, kwai_handle, ideas_generated,
  subscription_date, total_paid, created_at
}

content_ideas {
  id, user_id, topic, title, script, 
  content_type, hashtags, created_at
}

payments {
  id, user_id, amount, currency, payment_method,
  status, payment_data, created_at
}

profile_analyses {
  id, user_id, platform, handle, analysis,
  recommendations, best_posting_times, created_at
}
```

---

## 🚀 TECNOLOGIAS UTILIZADAS:

### 🖥️ **BACKEND:**
- FastAPI (Python web framework)
- MongoDB (banco NoSQL)
- Gemini AI (geração de conteúdo)
- emergentintegrations (biblioteca IA customizada)

### 🎨 **FRONTEND:**
- React (biblioteca JavaScript)
- Firebase (autenticação)
- Tailwind CSS (framework CSS)
- Axios (cliente HTTP)

### ☁️ **INFRAESTRUTURA:**
- Kubernetes (container orchestration)
- Docker (containerização)
- MongoDB (database)
- Supervisor (gerenciamento de processos)

---

Este é um projeto full-stack completo e profissional, pronto para produção e comercialização imediata! 🎉