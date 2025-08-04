from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
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
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    name: str
    profile_pic: Optional[str] = None
    instagram_handle: Optional[str] = None
    tiktok_handle: Optional[str] = None
    kwai_handle: Optional[str] = None

class PlanUpgrade(BaseModel):
    user_id: str
    plan: str  # "premium"

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

@api_router.get("/")
async def root():
    return {"message": "Shadoom API - Seu Gerenciador Fantasma de Engajamento! 👻"}

@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
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
    return User(**user)

@api_router.post("/upgrade-plan")
async def upgrade_plan(request: PlanUpgrade):
    # Update user plan
    result = await db.users.update_one(
        {"id": request.user_id},
        {"$set": {"plan": request.plan}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Plan upgraded successfully"}

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
            fallback_ideas = [
                {
                    "title": f"🔥 {request.topic}: O Segredo que MUDOU Minha Vida!",
                    "script": f"1. 'Eu costumava ter ZERO resultados com {request.topic}...'\n2. O momento que tudo mudou para mim\n3. A estratégia simples que NINGUÉM conta\n4. 'Se você chegou até aqui, comenta AI que eu compartilho mais!'",
                    "content_type": "Reels",
                    "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#segredo", "#viral", "#resultados", "#mudanca", "#dica"]
                },
                {
                    "title": f"⚠️ PARE TUDO! Você está fazendo {request.topic} ERRADO",
                    "script": f"1. 'Se você faz {request.topic} assim, PARE AGORA!'\n2. Os 3 erros que TODOS cometem\n3. A forma CORRETA (que poucos sabem)\n4. 'Salva este post e me agradece depois ❤️'",
                    "content_type": "Post",
                    "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#erro", "#alerta", "#dicavaliosa", "#salvavidas", "#importante"]
                },
                {
                    "title": f"✨ Como {request.topic} me fez ganhar R$ 10.000/mês",
                    "script": f"1. Minha vida ANTES de descobrir {request.topic}\n2. O que mudou quando apliquei isso\n3. Resultados em 30, 60 e 90 dias\n4. 'Quer saber como? Me chama no direct!'",
                    "content_type": "Stories",
                    "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#renda", "#transformacao", "#resultados", "#sucesso", "#dinheiro"]
                },
                {
                    "title": f"🎯 {request.topic} em 60 Segundos - MÉTODO RÁPIDO",
                    "script": f"1. 'Você tem 1 minuto? Vou te ensinar {request.topic}'\n2. Passo 1: O básico que você DEVE saber\n3. Passo 2: O truque que acelera tudo\n4. 'Funcionou? Conta aqui nos comentários!'",
                    "content_type": "Reels",
                    "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#rapidinha", "#metodo", "#pratico", "#funciona", "#testado"]
                },
                {
                    "title": f"💰 ANTES vs DEPOIS: Minha jornada com {request.topic}",
                    "script": f"1. ANTES: Minha situação era essa...\n2. DURANTE: O processo que segui\n3. DEPOIS: Onde estou hoje graças a {request.topic}\n4. 'Qual parte da sua jornada você está?'",
                    "content_type": "Post",
                    "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#antesedepois", "#jornada", "#evolucao", "#inspiracao", "#motivacao"]
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
        # Create AI chat for profile analysis
        chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id=f"analysis_{user_id}_{uuid.uuid4()}",
            system_message=f"""Você é um especialista em análise de perfis de redes sociais e estratégia de conteúdo.
            
            Baseado no handle @{handle} da plataforma {platform}, forneça uma análise detalhada no formato JSON:
            
            {{
                "analysis": "Análise geral do perfil e estratégia de conteúdo",
                "recommendations": ["Recomendação 1", "Recomendação 2", "Recomendação 3"],
                "best_posting_times": ["08:00", "12:00", "19:00"],
                "audience_insights": "Insights sobre a audiência e engajamento",
                "content_performance": "Análise de performance do conteúdo"
            }}
            
            RESPONDA APENAS O JSON VÁLIDO."""
        ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(3000)

        user_message = UserMessage(
            text=f"Analise o perfil @{handle} do {platform} e forneça insights completos para otimização de engajamento e crescimento."
        )
        
        response = await chat.send_message(user_message)
        
        # Parse response
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
                analysis=analysis_data.get("analysis", "Análise em desenvolvimento..."),
                recommendations=analysis_data.get("recommendations", ["Mantenha regularidade", "Use hashtags relevantes", "Interaja com seguidores"]),
                best_posting_times=analysis_data.get("best_posting_times", ["09:00", "15:00", "20:00"]),
                audience_insights=analysis_data.get("audience_insights", "Audiência engajada e ativa"),
                content_performance=analysis_data.get("content_performance", "Performance em análise")
            )
            
            # Save analysis
            await db.profile_analyses.insert_one(profile_analysis.dict())
            return profile_analysis
            
        except (json.JSONDecodeError, KeyError):
            # Fallback analysis
            profile_analysis = ProfileAnalysis(
                user_id=user_id,
                platform=platform,
                handle=handle,
                analysis=f"Perfil @{handle} no {platform} analisado. Recomenda-se foco em conteúdo de qualidade e consistência.",
                recommendations=[
                    "Poste conteúdo regularmente (3-5x por semana)",
                    "Use hashtags relevantes ao seu nicho",
                    "Interaja ativamente com seus seguidores",
                    "Analise métricas para otimizar horários",
                    "Crie conteúdo que gere discussão"
                ],
                best_posting_times=["08:30", "12:00", "19:30"],
                audience_insights="Audiência ativa principalmente em horários comerciais. Engajamento maior em conteúdos práticos e inspiracionais.",
                content_performance="Conteúdos com call-to-action tendem a ter melhor performance. Stories interativos aumentam engajamento."
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