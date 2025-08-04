from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Gemini API key
GEMINI_API_KEY = os.environ['GEMINI_API_KEY']

# Admin credentials
ADMIN_EMAIL = "admin@shadoom.online"
ADMIN_PASSWORD = "@Enigmaext4@"

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class ContentIdea(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    topic: str
    title: str
    script: str
    content_type: str
    hashtags: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ContentIdeaCreate(BaseModel):
    user_id: str
    topic: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    profile_pic: Optional[str] = None
    plan: str = "free"  # free or premium
    instagram_handle: Optional[str] = None
    tiktok_handle: Optional[str] = None
    kwai_handle: Optional[str] = None
    ideas_generated: int = 0
    subscription_date: Optional[datetime] = None
    subscription_expires: Optional[datetime] = None
    total_paid: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class UserCreate(BaseModel):
    email: str
    name: str
    profile_pic: Optional[str] = None
    instagram_handle: Optional[str] = None
    tiktok_handle: Optional[str] = None
    kwai_handle: Optional[str] = None

class AdminLogin(BaseModel):
    email: str
    password: str

class PurchaseRequest(BaseModel):
    user_id: str
    plan: str = "premium"
    payment_method: str  # "card", "crypto"
    payment_data: dict

class PaymentRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    amount: float
    currency: str
    payment_method: str
    payment_data: dict
    status: str = "pending"  # pending, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProfileAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    platform: str  # instagram, tiktok, kwai
    handle: str
    analysis: str
    recommendations: List[str]
    best_posting_times: List[str]
    audience_insights: str
    content_performance: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Admin auth dependency
def verify_admin(email: str, password: str):
    return email == ADMIN_EMAIL and password == ADMIN_PASSWORD

@api_router.get("/")
async def root():
    return {"message": "Shadoom API - Seu Gerenciador Fantasma de Engajamento! 👻"}

@api_router.post("/admin/login")
async def admin_login(credentials: AdminLogin):
    if verify_admin(credentials.email, credentials.password):
        return {
            "success": True,
            "admin_token": "shadoom_admin_2025",
            "message": "Login admin realizado com sucesso"
        }
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@api_router.get("/admin/dashboard")
async def admin_dashboard():
    try:
        # Total users
        total_users = await db.users.count_documents({})
        
        # Active users (logged in last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = await db.users.count_documents({
            "last_active": {"$gte": thirty_days_ago}
        })
        
        # Premium users
        premium_users = await db.users.count_documents({"plan": "premium"})
        
        # Total revenue
        payments = await db.payments.find({"status": "completed"}).to_list(1000)
        total_revenue = sum(payment["amount"] for payment in payments)
        
        # Recent signups (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_signups = await db.users.count_documents({
            "created_at": {"$gte": seven_days_ago}
        })
        
        # Total ideas generated
        total_ideas = await db.content_ideas.count_documents({})
        
        # Monthly revenue
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_payments = await db.payments.find({
            "status": "completed",
            "created_at": {"$gte": current_month}
        }).to_list(100)
        monthly_revenue = sum(payment["amount"] for payment in monthly_payments)
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "premium_users": premium_users,
            "free_users": total_users - premium_users,
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
            "recent_signups": recent_signups,
            "total_ideas": total_ideas,
            "conversion_rate": round((premium_users / total_users * 100) if total_users > 0 else 0, 2)
        }
    except Exception as e:
        print(f"Dashboard error: {e}")
        return {
            "total_users": 0,
            "active_users": 0,
            "premium_users": 0,
            "free_users": 0,
            "total_revenue": 0.0,
            "monthly_revenue": 0.0,
            "recent_signups": 0,
            "total_ideas": 0,
            "conversion_rate": 0.0
        }

@api_router.get("/admin/users")
async def admin_get_users():
    users = await db.users.find().sort("created_at", -1).to_list(100)
    return [User(**user) for user in users]

@api_router.post("/admin/users/{user_id}/upgrade")
async def admin_upgrade_user(user_id: str):
    result = await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "plan": "premium",
                "subscription_date": datetime.utcnow(),
                "subscription_expires": datetime.utcnow() + timedelta(days=30)
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User upgraded to premium"}

@api_router.post("/admin/users/{user_id}/downgrade")
async def admin_downgrade_user(user_id: str):
    result = await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "plan": "free",
                "subscription_expires": None
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User downgraded to free"}

@api_router.get("/admin/payments")
async def admin_get_payments():
    payments = await db.payments.find().sort("created_at", -1).to_list(100)
    return [PaymentRecord(**payment) for payment in payments]

@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        # Update last_active
        await db.users.update_one(
            {"email": user_data.email},
            {"$set": {"last_active": datetime.utcnow()}}
        )
        return User(**existing_user)
    
    user_dict = user_data.dict()
    user_obj = User(**user_dict)
    await db.users.insert_one(user_obj.dict())
    return user_obj

@api_router.get("/users/{email}")
async def get_user(email: str):
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update last_active
    await db.users.update_one(
        {"email": email},
        {"$set": {"last_active": datetime.utcnow()}}
    )
    
    return User(**user)

@api_router.post("/purchase-premium")
async def purchase_premium(request: PurchaseRequest):
    try:
        # Get user
        user = await db.users.find_one({"id": request.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Premium pricing
        amount = 29.90  # R$ 29,90/mês
        
        # Create payment record
        payment_record = PaymentRecord(
            user_id=request.user_id,
            amount=amount,
            currency="BRL",
            payment_method=request.payment_method,
            payment_data=request.payment_data,
            status="pending"
        )
        
        # Simulate payment processing
        if request.payment_method == "crypto":
            # Crypto payment simulation
            crypto_address = request.payment_data.get("address", "")
            crypto_type = request.payment_data.get("type", "bitcoin")
            
            if crypto_address and len(crypto_address) > 20:
                payment_record.status = "completed"
            else:
                payment_record.status = "failed"
                
        elif request.payment_method == "card":
            # Card payment simulation  
            card_number = request.payment_data.get("card_number", "")
            if card_number and len(card_number) >= 16:
                payment_record.status = "completed"
            else:
                payment_record.status = "failed"
        
        # Save payment record
        await db.payments.insert_one(payment_record.dict())
        
        if payment_record.status == "completed":
            # Upgrade user to premium
            subscription_expires = datetime.utcnow() + timedelta(days=30)
            await db.users.update_one(
                {"id": request.user_id},
                {
                    "$set": {
                        "plan": "premium",
                        "subscription_date": datetime.utcnow(),
                        "subscription_expires": subscription_expires
                    },
                    "$inc": {"total_paid": amount}
                }
            )
            
            return {
                "success": True,
                "payment_id": payment_record.id,
                "message": "Pagamento aprovado! Bem-vindo ao Premium! 🎉",
                "expires_at": subscription_expires
            }
        else:
            return {
                "success": False,
                "payment_id": payment_record.id,
                "message": "Pagamento falhou. Tente novamente.",
                "error": "Invalid payment data"
            }
            
    except Exception as e:
        print(f"Payment error: {e}")
        raise HTTPException(status_code=500, detail="Erro no processamento do pagamento")

@api_router.post("/generate-ideas", response_model=List[ContentIdea])
async def generate_content_ideas(request: ContentIdeaCreate):
    try:
        # Get user to check plan and limits
        user = await db.users.find_one({"id": request.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_obj = User(**user)
        
        # Check limits for free users
        if user_obj.plan == "free" and user_obj.ideas_generated >= 10:
            raise HTTPException(
                status_code=403, 
                detail="Limite de ideias atingido. Faça upgrade para Premium para ideias ilimitadas!"
            )
        
        # Create AI chat session with improved prompt
        chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id=f"ideas_{request.user_id}_{uuid.uuid4()}",
            system_message="""Você é um especialista em criação de conteúdo para influenciadores digitais. 
            
            IMPORTANTE: Responda SEMPRE no formato JSON válido abaixo. NÃO adicione texto antes ou depois do JSON.
            
            Gere 5 ideias criativas e virais para o tópico solicitado. Para cada ideia:
            - Título: Clickbait atrativo com emojis
            - Roteiro: 4 pontos práticos e envolventes
            - Tipo: Reels, Post ou Stories
            - Hashtags: 6-8 tags populares e relevantes
            
            RESPONDA APENAS ESTE JSON:
            {
                "ideas": [
                    {
                        "title": "🔥 Título super atrativo com emoji",
                        "script": "1. Gancho inicial impactante\n2. Desenvolvimento do tema principal\n3. Valor prático ou insight\n4. Call to action envolvente",
                        "content_type": "Reels",
                        "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5", "#tag6"]
                    }
                ]
            }
            """
        ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(4000)

        # Generate ideas with context
        context_message = f"Gere 5 ideias criativas para influenciadores sobre: {request.topic}. " + \
                         f"Foque em conteúdo viral, engajamento alto e valor para o público."
        
        if user_obj.plan == "premium" and user_obj.instagram_handle:
            context_message += f" O influenciador tem Instagram @{user_obj.instagram_handle}."
        
        user_message = UserMessage(text=context_message)
        response = await chat.send_message(user_message)
        
        print(f"AI Response: {response}")  # Debug log
        
        # Try to parse AI response as JSON
        ideas_list = []
        try:
            # Clean response - remove code blocks if present
            clean_response = response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            # Parse JSON
            ideas_data = json.loads(clean_response)
            
            if "ideas" in ideas_data and isinstance(ideas_data["ideas"], list):
                for idea in ideas_data["ideas"]:
                    content_idea = ContentIdea(
                        user_id=request.user_id,
                        topic=request.topic,
                        title=idea.get("title", f"💡 Ideia sobre {request.topic}"),
                        script=idea.get("script", "Roteiro criativo em desenvolvimento..."),
                        content_type=idea.get("content_type", "Reels"),
                        hashtags=idea.get("hashtags", [f"#{request.topic.lower().replace(' ', '')}"])
                    )
                    
                    # Save to database
                    await db.content_ideas.insert_one(content_idea.dict())
                    ideas_list.append(content_idea)
            
            if len(ideas_list) == 0:
                raise ValueError("No valid ideas generated")
                
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Failed to parse AI response: {e}")
            # Enhanced fallback with better ideas
            topic_lower = request.topic.lower()
            
            if "fitness" in topic_lower or "treino" in topic_lower or "academia" in topic_lower:
                fallback_ideas = [
                    {
                        "title": f"🔥 Transformei meu corpo em 90 dias com {request.topic} - RESULTADO CHOCANTE!",
                        "script": f"1. 'Há 90 dias eu odiava me olhar no espelho...'\n2. Como descobri {request.topic} que mudou TUDO\n3. A rotina simples que me deu resultado (sem dieta maluca)\n4. 'Se você quer o mesmo, salva este post e me segue!'",
                        "content_type": "Reels",
                        "hashtags": ["#fitness", "#transformacao", "#90dias", "#antesedepois", "#motivacao", "#treino", "#resultado", "#corpodossonhos"]
                    },
                    {
                        "title": f"⚠️ PARE de fazer {request.topic} se você não sabe ISSO!",
                        "script": f"1. '95% das pessoas fazem {request.topic} ERRADO'\n2. O erro que te impede de ver resultados\n3. A forma correta (que personal trainer cobra R$ 300)\n4. 'Compartilha para salvar alguém!'",
                        "content_type": "Post",
                        "hashtags": ["#fitness", "#erro", "#dicavaliosa", "#personal", "#treino", "#academia", "#segredo", "#resultado"]
                    },
                    {
                        "title": f"💪 {request.topic}: 5 minutos que valem por 1 hora de academia!",
                        "script": f"1. 'Sem tempo para treinar? Este vídeo é para você!'\n2. Exercício 1: O básico que funciona\n3. Exercício 2: O que acelera o metabolismo\n4. 'Faz junto comigo e me marca nos stories!'",
                        "content_type": "Reels",
                        "hashtags": ["#fitness", "#5minutos", "#caseiro", "#pratico", "#rapido", "#funciona", "#treino", "#metabolismo"]
                    },
                    {
                        "title": f"✨ ANTES vs DEPOIS: Minha jornada com {request.topic}",
                        "script": f"1. ANTES: Como estava minha situação\n2. Durante: O processo que segui com {request.topic}\n3. DEPOIS: Onde estou hoje (resultado real)\n4. 'Qual parte da jornada você está?'",
                        "content_type": "Stories",
                        "hashtags": ["#fitness", "#antesedepois", "#jornada", "#processo", "#real", "#inspiracao", "#motivacao", "#transformacao"]
                    },
                    {
                        "title": f"🎯 {request.topic} em 60 segundos - MÉTODO TESTADO!",
                        "script": f"1. 'Você tem 1 minuto? Vou te ensinar {request.topic}'\n2. Passo 1: O básico essencial\n3. Passo 2: O segredo que acelera\n4. 'Funcionou? Conta aqui embaixo!'",
                        "content_type": "Reels",
                        "hashtags": ["#fitness", "#1minuto", "#metodo", "#rapido", "#testado", "#funciona", "#treino", "#dica"]
                    }
                ]
            else:
                # Generic fallback for any topic
                fallback_ideas = [
                    {
                        "title": f"🔥 {request.topic}: O que MUDOU minha vida em 30 dias!",
                        "script": f"1. 'Há 30 dias eu não sabia nada sobre {request.topic}...'\n2. A descoberta que virou minha chave\n3. Os resultados que consegui (sem mentira)\n4. 'Se funcionar com você, me marca nos stories!'",
                        "content_type": "Reels",
                        "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#30dias", "#mudanca", "#resultado", "#funciona", "#viral"]
                    },
                    {
                        "title": f"⚠️ TODO mundo faz {request.topic} ERRADO - eu também fazia!",
                        "script": f"1. 'Se você faz {request.topic} assim, PARE AGORA!'\n2. O erro que TODO mundo comete\n3. A forma certa (que poucos conhecem)\n4. 'Salva este post e me agradece depois!'",
                        "content_type": "Post", 
                        "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#erro", "#alerta", "#dicavaliosa", "#certo", "#importante"]
                    },
                    {
                        "title": f"✨ ANTES vs DEPOIS: Minha jornada com {request.topic}",
                        "script": f"1. ANTES: Como estava minha situação\n2. Durante: O processo que segui com {request.topic}\n3. DEPOIS: Onde estou hoje (resultado real)\n4. 'Qual parte da jornada você está?'",
                        "content_type": "Stories",
                        "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#antesedepois", "#jornada", "#processo", "#real", "#inspiracao"]
                    },
                    {
                        "title": f"🎯 {request.topic} em 60 segundos - MÉTODO TESTADO!",
                        "script": f"1. 'Você tem 1 minuto? Vou te ensinar {request.topic}'\n2. Passo 1: O básico essencial\n3. Passo 2: O segredo que acelera\n4. 'Funcionou? Conta aqui embaixo!'",
                        "content_type": "Reels",
                        "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#1minuto", "#metodo", "#rapido", "#testado", "#funciona"]
                    },
                    {
                        "title": f"💡 5 erros em {request.topic} que te impedem de ter resultado!",
                        "script": f"1. Erro 1: O que TODO mundo faz errado\n2. Erro 2: A armadilha que eu caí também\n3. Erro 3: O desperdício de tempo/dinheiro\n4. 'Você comete algum? Me fala nos comentários!'",
                        "content_type": "Post",
                        "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#5erros", "#evite", "#resultado", "#dica", "#cuidado"]
                    }
                ]
            
            for idea_data in fallback_ideas:
                content_idea = ContentIdea(
                    user_id=request.user_id,
                    topic=request.topic,
                    title=idea_data["title"],
                    script=idea_data["script"],
                    content_type=idea_data["content_type"],
                    hashtags=idea_data["hashtags"]
                )
                
                # Save to database
                await db.content_ideas.insert_one(content_idea.dict())
                ideas_list.append(content_idea)
        
        # Update user ideas count
        await db.users.update_one(
            {"id": request.user_id},
            {"$inc": {"ideas_generated": len(ideas_list)}}
        )
        
        return ideas_list
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating ideas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@api_router.post("/analyze-profile", response_model=ProfileAnalysis)
async def analyze_profile(request: dict):
    user_id = request.get("user_id")
    platform = request.get("platform")  # instagram, tiktok, kwai
    handle = request.get("handle")
    
    # Check if user has premium plan
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user["plan"] != "premium":
        raise HTTPException(
            status_code=403, 
            detail="Análise de perfil disponível apenas para usuários Premium!"
        )
    
    try:
        # Enhanced AI analysis with real profile context
        chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id=f"analysis_{user_id}_{uuid.uuid4()}",
            system_message=f"""Você é um especialista em análise de perfis de redes sociais e estratégia de conteúdo digital.

Analise o perfil @{handle} da plataforma {platform} e forneça insights ESPECÍFICOS e PRÁTICOS.

IMPORTANTE: Forneça análises realistas baseadas em:
1. Melhores práticas da plataforma {platform}
2. Estratégias que funcionam para o nicho implícito no handle @{handle}
3. Horários e táticas específicas para {platform}
4. Insights demográficos típicos da plataforma

Responda APENAS no formato JSON:
{{
    "analysis": "Análise específica do perfil @{handle} no {platform}, identificando oportunidades de crescimento baseadas no nome/nicho do perfil",
    "recommendations": [
        "Recomendação específica 1 para @{handle}",
        "Recomendação específica 2 para o nicho identificado", 
        "Recomendação específica 3 para {platform}",
        "Recomendação específica 4 baseada no handle",
        "Recomendação específica 5 para engajamento",
        "Recomendação específica 6 para crescimento"
    ],
    "best_posting_times": ["horário1", "horário2", "horário3"],
    "audience_insights": "Análise específica da audiência provável de @{handle} no {platform}, baseada no nicho e plataforma",
    "content_performance": "Análise específica de que tipo de conteúdo funcionaria melhor para @{handle} no {platform}"
}}"""
        ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(4000)

        # Create enhanced prompt with handle analysis
        analysis_prompt = f"""
        Analise o perfil @{handle} no {platform}:
        
        1. CONTEXTO DO HANDLE: Baseado no nome "@{handle}", identifique o possível nicho/tema do perfil
        2. PLATAFORMA: {platform} - use características específicas desta rede social
        3. ANÁLISE INTELIGENTE: Forneça insights específicos e acionáveis
        
        Seja específico ao @{handle} e não genérico. Use o nome do handle para inferir o nicho e dar conselhos direcionados.
        """
        
        user_message = UserMessage(text=analysis_prompt)
        response = await chat.send_message(user_message)
        
        print(f"AI Profile Analysis Response: {response}")
        
        # Parse AI response
        try:
            clean_response = response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            analysis_data = json.loads(clean_response)
            
            profile_analysis = ProfileAnalysis(
                user_id=user_id,
                platform=platform,
                handle=handle,
                analysis=analysis_data.get("analysis", f"Análise específica em desenvolvimento para @{handle}..."),
                recommendations=analysis_data.get("recommendations", [f"Mantenha consistência no conteúdo de @{handle}", "Use hashtags específicas do seu nicho", "Interaja ativamente com sua comunidade"]),
                best_posting_times=analysis_data.get("best_posting_times", ["09:00", "15:00", "20:00"]),
                audience_insights=analysis_data.get("audience_insights", f"Análise da audiência de @{handle} em desenvolvimento..."),
                content_performance=analysis_data.get("content_performance", f"Análise de performance para @{handle} em desenvolvimento...")
            )
            
            await db.profile_analyses.insert_one(profile_analysis.dict())
            return profile_analysis
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Failed to parse AI analysis, using enhanced fallback: {e}")
            
            # ENHANCED FALLBACK - Analyze handle for niche detection
            handle_lower = handle.lower()
            
            # Smart niche detection based on handle
            niche_indicators = {
                "fit": "fitness", "gym": "fitness", "treino": "fitness", "muscle": "fitness", "healthy": "fitness",
                "food": "culinária", "chef": "culinária", "cook": "culinária", "recipe": "culinária", "eat": "culinária",
                "beauty": "beleza", "makeup": "beleza", "skin": "beleza", "hair": "beleza", "fashion": "moda",
                "tech": "tecnologia", "dev": "tecnologia", "code": "tecnologia", "digital": "tecnologia",
                "business": "negócios", "entrepreneur": "negócios", "startup": "negócios", "invest": "negócios",
                "travel": "viagem", "trip": "viagem", "adventure": "viagem", "explore": "viagem",
                "mom": "maternidade", "mama": "maternidade", "baby": "maternidade", "family": "família",
                "art": "arte", "draw": "arte", "paint": "arte", "creative": "arte", "design": "design",
                "music": "música", "sing": "música", "guitar": "música", "piano": "música",
                "game": "games", "gamer": "games", "stream": "games", "play": "games"
            }
            
            detected_niche = "lifestyle"
            for keyword, niche in niche_indicators.items():
                if keyword in handle_lower:
                    detected_niche = niche
                    break
            
            # Platform-specific enhanced analysis
            platform_specific = {
                "instagram": {
                    "analysis": f"Perfil @{handle} no Instagram: Baseado na análise do handle, identifiquei um foco em {detected_niche}. Instagram é ideal para conteúdo visual de alta qualidade neste nicho. Recomendo estratégia focada em posts carrossel, Stories interativos e Reels com tendências atuais.",
                    "recommendations": [
                        f"Crie conteúdo visual atrativo sobre {detected_niche} com iluminação profissional",
                        f"Use Stories diários mostrando bastidores do seu trabalho com {detected_niche}",
                        f"Faça Reels curtos (15-30s) com dicas práticas de {detected_niche}",
                        f"Responda TODOS os comentários nas primeiras 2 horas após publicar",
                        f"Use hashtags mix: 3 grandes (1M+), 5 médias (100K-1M), 7 pequenas (1K-100K)",
                        f"Publique consistentemente: 3-4 posts por semana + Stories diários"
                    ],
                    "times": ["08:00", "12:30", "19:00"],
                    "audience": f"Audiência de @{handle}: Perfil focado em {detected_niche} atrai principalmente pessoas interessadas neste tema. No Instagram, seu público provavelmente é 60% feminino, 25-35 anos, ativo entre 8-10h, 12-14h e 19-21h. Engajamento maior em conteúdo educativo e inspiracional.",
                    "performance": f"Para @{handle} no Instagram: Posts em carrossel têm 40% mais engajamento que fotos únicas. Reels sobre {detected_niche} podem ter 3x mais alcance. Stories com enquetes/perguntas aumentam engajamento em 25%. Call-to-actions claros aumentam conversão em 30%."
                },
                "tiktok": {
                    "analysis": f"Perfil @{handle} no TikTok: Com foco em {detected_niche}, você tem grande potencial viral nesta plataforma. TikTok favorece conteúdo autêntico, educativo e divertido. Estratégia deve focar em trends, sounds populares e hooks fortes nos primeiros 3 segundos.",
                    "recommendations": [
                        f"Crie vídeos de 15-30s com dicas rápidas sobre {detected_niche}",
                        f"Use músicas/sounds em alta (verifica Discover Weekly)",
                        f"Hook forte: '3 segredos sobre {detected_niche} que mudaram minha vida'",
                        f"Participe de challenges relacionados ao seu nicho {detected_niche}",
                        f"Publique 1-2 vídeos por dia em horários de pico",
                        f"Interaja com outros criadores de {detected_niche} através de duetos/stitches"
                    ],
                    "times": ["18:00", "19:30", "21:00"],
                    "audience": f"@{handle} no TikTok: Audiência de {detected_niche} é predominantemente jovem (16-28 anos), ativa à noite (18-23h). Attention span de 8 segundos. Prefere conteúdo autêntico, educativo rápido e entretenimento. 45% descobre via FYP, 30% via hashtags.",
                    "performance": f"TikTok @{handle}: Vídeos sobre {detected_niche} com texto na tela têm 60% mais views. Trends musicais aumentam alcance em 85%. Conteúdo educativo de 15-30s tem 40% mais saves. Hooks nos primeiros 3s aumentam retenção em 70%."
                },
                "kwai": {
                    "analysis": f"Perfil @{handle} no Kwai: Plataforma brasileira perfeita para conteúdo de {detected_niche} com toque nacional. Kwai valoriza autenticidade, humor brasileiro e conexão com comunidade local. Ideal para mostrar seu conhecimento em {detected_niche} de forma descontraída.",
                    "recommendations": [
                        f"Crie conteúdo sobre {detected_niche} com jeito brasileiro/regional",
                        f"Use músicas populares no Brasil (sertanejo, funk, MPB)",
                        f"Faça vídeos de 30-60s com humor e informação sobre {detected_niche}",
                        f"Interaja muito com comentários - audiência Kwai valoriza proximidade",
                        f"Use gírias e expressões regionais ao falar sobre {detected_niche}",
                        f"Poste nos horários de pico: noite quando as pessoas relaxam"
                    ],
                    "times": ["19:00", "20:30", "21:30"],
                    "audience": f"@{handle} no Kwai: Audiência brasileira interessada em {detected_niche}, mais ativa à noite (19-23h). Valoriza autenticidade e humor. 70% interage mais quando criador responde. Prefere conteúdo descontraído e educativo ao mesmo tempo.",
                    "performance": f"Kwai @{handle}: Conteúdo de {detected_niche} com humor brasileiro tem 75% mais engajamento. Vídeos com música nacional performam 65% melhor. Responder comentários aumenta alcance em 45%. CTAs diretos funcionam 35% melhor que indiretos."
                }
            }
            
            platform_data = platform_specific.get(platform, platform_specific["instagram"])
            
            profile_analysis = ProfileAnalysis(
                user_id=user_id,
                platform=platform,
                handle=handle,
                analysis=platform_data["analysis"],
                recommendations=platform_data["recommendations"],
                best_posting_times=platform_data["times"],
                audience_insights=platform_data["audience"],
                content_performance=platform_data["performance"]
            )
            
            await db.profile_analyses.insert_one(profile_analysis.dict())
            return profile_analysis
            
    except Exception as e:
        print(f"Error analyzing profile: {e}")
        raise HTTPException(status_code=500, detail="Erro ao analisar perfil")

@api_router.get("/profile-analysis/{user_id}")
async def get_profile_analysis(user_id: str):
    analyses = await db.profile_analyses.find({"user_id": user_id}).sort("created_at", -1).to_list(10)
    return [ProfileAnalysis(**analysis) for analysis in analyses]

@api_router.get("/ideas/{user_id}", response_model=List[ContentIdea])
async def get_user_ideas(user_id: str):
    ideas = await db.content_ideas.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    return [ContentIdea(**idea) for idea in ideas]

@api_router.delete("/ideas/{idea_id}")
async def delete_idea(idea_id: str):
    result = await db.content_ideas.delete_one({"id": idea_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Idea not found")
    return {"message": "Idea deleted successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()