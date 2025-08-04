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
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    name: str
    profile_pic: Optional[str] = None

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

@api_router.post("/generate-ideas", response_model=List[ContentIdea])
async def generate_content_ideas(request: ContentIdeaCreate):
    try:
        # Create AI chat session
        chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id=f"ideas_{request.user_id}_{uuid.uuid4()}",
            system_message="""Você é um especialista em criação de conteúdo para influenciadores digitais. 
            Gere 5 ideias criativas e envolventes para o tópico solicitado. Para cada ideia, forneça:
            1. Um título atrativo e clickbait
            2. Um roteiro básico com 3-4 pontos principais
            3. Tipo de conteúdo (Reels, Post, Stories)
            4. 5-8 hashtags relevantes
            
            Formato de resposta (JSON):
            {
                "ideas": [
                    {
                        "title": "Título super atrativo",
                        "script": "1. Introdução chamativa\n2. Ponto principal 1\n3. Ponto principal 2\n4. Call to action",
                        "content_type": "Reels|Post|Stories",
                        "hashtags": ["#tag1", "#tag2", "#tag3"]
                    }
                ]
            }
            """
        ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(4000)

        # Generate ideas
        user_message = UserMessage(
            text=f"Gere 5 ideias criativas para conteúdo sobre: {request.topic}"
        )
        
        response = await chat.send_message(user_message)
        
        # Parse response (assuming it returns JSON format)
        import json
        try:
            ideas_data = json.loads(response)
            ideas_list = []
            
            for idea in ideas_data.get("ideas", []):
                content_idea = ContentIdea(
                    user_id=request.user_id,
                    topic=request.topic,
                    title=idea["title"],
                    script=idea["script"],
                    content_type=idea["content_type"],
                    hashtags=idea["hashtags"]
                )
                
                # Save to database
                await db.content_ideas.insert_one(content_idea.dict())
                ideas_list.append(content_idea)
            
            return ideas_list
            
        except json.JSONDecodeError:
            # If response is not JSON, create ideas from text
            ideas_list = []
            lines = response.split('\n')
            current_idea = {"title": "", "script": "", "content_type": "Reels", "hashtags": []}
            
            for i in range(5):  # Generate 5 ideas
                content_idea = ContentIdea(
                    user_id=request.user_id,
                    topic=request.topic,
                    title=f"💡 Ideia Criativa sobre {request.topic} #{i+1}",
                    script=f"1. Gancho inicial sobre {request.topic}\n2. Desenvolva o conceito principal\n3. Adicione valor para o público\n4. Chame para ação",
                    content_type=["Reels", "Post", "Stories"][i % 3],
                    hashtags=[f"#{request.topic.lower().replace(' ', '')}", "#conteudo", "#dica", "#influencer", "#viral"]
                )
                
                # Save to database
                await db.content_ideas.insert_one(content_idea.dict())
                ideas_list.append(content_idea)
            
            return ideas_list
            
    except Exception as e:
        # Fallback ideas if AI fails
        print(f"AI generation failed: {e}")
        ideas_list = []
        
        fallback_ideas = [
            {
                "title": f"🔥 {request.topic}: O Segredo que Ninguém Conta",
                "script": f"1. Gancho: 'Você sabia que sobre {request.topic}...'\n2. Revele 3 insights importantes\n3. Conte sua experiência pessoal\n4. Pergunte: 'E você, já passou por isso?'",
                "content_type": "Reels",
                "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#segredo", "#dicavaliosa", "#viral", "#contenudo"]
            },
            {
                "title": f"✨ Transformei minha vida com {request.topic}",
                "script": f"1. Antes vs Depois sobre {request.topic}\n2. Os 3 passos que me ajudaram\n3. Resultados que obtive\n4. 'Salva este post para aplicar!'",
                "content_type": "Post",
                "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#transformacao", "#motivacao", "#inspiracao", "#crescimento"]
            },
            {
                "title": f"🚨 ERRO Fatal que todos cometem com {request.topic}",
                "script": f"1. 'Pare tudo que você está fazendo!'\n2. O erro mais comum sobre {request.topic}\n3. Como eu descobri isso\n4. A forma correta de fazer",
                "content_type": "Stories",
                "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#erro", "#alerta", "#dica", "#cuidado"]
            },
            {
                "title": f"💰 Como {request.topic} mudou meu faturamento",
                "script": f"1. Números: antes e depois\n2. O que aprendi sobre {request.topic}\n3. Estratégias que funcionaram\n4. 'Comenta AI se quer saber mais'",
                "content_type": "Reels",
                "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#faturamento", "#negocio", "#empreender", "#resultados"]
            },
            {
                "title": f"🎯 {request.topic} em 60 segundos",
                "script": f"1. 'Você tem 1 minuto livre?'\n2. Resumo rápido sobre {request.topic}\n3. 3 pontos essenciais\n4. 'Seguir para mais dicas assim'",
                "content_type": "Reels",
                "hashtags": [f"#{request.topic.lower().replace(' ', '')}", "#rapidinha", "#resumo", "#pratico", "#follow"]
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
        
        return ideas_list

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