from fastapi import APIRouter, Depends, HTTPException, Request
from core.neo4j import get_driver
from core.deps import get_current_user
from core.rate_limit import limiter, get_rate_limit
from models.user import User
from schemas.chatbot import MentorRequest, MentorResponse
from core.genai import get_genai_client
from google.genai import types
import os

router = APIRouter()

@router.post("/mentor", response_model=MentorResponse)
@limiter.limit(get_rate_limit("mentor"))
def socratic_mentor(
    request: Request,
    mentor_request: MentorRequest,
    current_user: User = Depends(get_current_user)
):
    from core.logger import logger
    import logging
    
    # Configurar logger
    if not logger:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
    
    driver = get_driver()
    client = get_genai_client()
    
    if not client:
        raise HTTPException(status_code=500, detail="Serviço de IA não configurado.")

    # Suportar assistência genérica ou específica por questão
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    if mentor_request.question_id == "general":
        # Modo de assistência geral (Vertex AI Optimized)
        system_instruction = """
        Você é o Mentor Educacional Griô, uma inteligência pedagógica de alta performance especializada no ENEM.
        Sua missão é guiar o estudante através de conceitos complexos, estratégias de estudo e resolução de problemas.
        
        DIRETRIZES TÉCNICAS (Maximizar potencial Vertex AI):
        1. TOM: Profissional, encorajador e focado em maturidade cognitiva.
        2. MÉTODO: Utilize analogias claras e exemplos práticos para desmistificar temas áridos.
        3. LINGUAGEM: PROIBIÇÃO ABSOLUTA DE EMOJIS. Use Markdown para estruturação.
        4. CONCISÃO: Máximo 4 frases por resposta. Vá direto ao ponto pedagógico.
        """
        
        history = []
        
        for msg in mentor_request.chat_history:
            history.append({
                "role": "user" if msg.role == "user" else "model",
                "parts": [{"text": msg.content}]
            })
        
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=history,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )
                
                return {
                    "response": response.text,
                    "skill_targeted": None,
                    "is_correct": False
                }
            except Exception as e:
                logger.warning(f"Gemini API error in general chat (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    import time
                    import random
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
                else:
                    logger.error(f"Gemini API completely failed in general chat: {str(e)}")
                    raise HTTPException(
                        status_code=503,
                        detail="O Mentor Griô via Vertex AI está temporariamente indisponível. Tente novamente em instantes."
                    )
    
    # Modo específico por questão
    with driver.session() as session:
        # Validar question_id
        if not mentor_request.question_id or not isinstance(mentor_request.question_id, str):
            raise HTTPException(
                status_code=400,
                detail="question_id inválido"
            )
        
        # 1. Buscar contexto completo da questão no Neo4j
        result = session.run("""
            MATCH (q:Question {id: $id})
            OPTIONAL MATCH (q)-[:EVALUATES]->(s:Skill)
            RETURN q.text as text, 
                   q.answer as correct_answer, 
                   q.explanation as explanation,
                   q.option_a as opt_a, q.option_b as opt_b, q.option_c as opt_c, 
                   q.option_d as opt_d, q.option_e as opt_e,
                   collect(s.description) as skill_descriptions,
                   collect(s.code) as skill_codes
        """, id=mentor_request.question_id).single()

        if not result:
            raise HTTPException(status_code=404, detail="Questão não encontrada")

        # Validar selected_option_id
        if not (1 <= mentor_request.selected_option_id <= 5):
            raise HTTPException(
                status_code=400,
                detail="selected_option_id deve estar entre 1 e 5"
            )

        # Mapeamento de opções
        options = {
            1: result["opt_a"], 2: result["opt_b"], 3: result["opt_c"],
            4: result["opt_d"], 5: result["opt_e"]
        }
        option_map = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
        
        user_letter = option_map.get(mentor_request.selected_option_id)
        is_correct = user_letter == result["correct_answer"]
        
        # 2. Configurar o Prompt Socrático (Vertex AI Optimized)
        skills_context = ", ".join([f"{code}: {desc}" for code, desc in zip(result["skill_codes"], result["skill_descriptions"])])
        
        system_instruction = f"""
        Você é o Mentor Socrático Griô de Alta Performance.
        Seu objetivo é guiar o estudante pelo labirinto cognitivo do ENEM, utilizando o método socrático para que ele descubra o caminho correto por conta própria.
        
        CONTEXTO TÉCNICO DA QUESTÃO:
        Texto: {result["text"]}
        Gabarito: {result["correct_answer"]}
        Análise Pedagógica: {result["explanation"]}
        Habilidades Matriz ENEM: {skills_context}
        
        RESPOSTA DO ESTUDANTE:
        Opção {user_letter}: "{options.get(mentor_request.selected_option_id)}"
        Status: {'Correto (Validar Raciocínio)' if is_correct else 'Incorreto (Redirecionar Cognição)'}
        
        DIRETRIZES DE TUTORIA (Maximizar potencial Vertex AI):
        1. MÉTODO SOCRÁTICO: NUNCA revele a alternativa correta. Faça perguntas que exponham a contradição no erro ou reforcem a lógica do acerto.
        2. RIGOR E ESTÍMULO: Seja técnico, profissional e motivacional. PROIBIÇÃO ABSOLUTA DE EMOJIS.
        3. CONCISÃO EXTREMA: Máximo 3 frases. Foque na Habilidade ENEM associada.
        """
        
        history = []
        for msg in mentor_request.chat_history:
            history.append({"role": "user" if msg.role == "user" else "model", "parts": [{"text": msg.content}]})
            
        if not history:
            input_text = f"O aluno acabou de responder a questão {mentor_request.question_id} e {'acertou' if is_correct else 'errou'}. Inicie a orientação técnica."
            history.append({"role": "user", "parts": [{"text": input_text}]})

        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=history,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )

                return {
                    "response": response.text,
                    "skill_targeted": result["skill_codes"][0] if result["skill_codes"] else None,
                    "is_correct": is_correct
                }
            except Exception as e:
                logger.warning(f"Gemini API error in specific question chat (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    import time
                    import random
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
                else:
                    logger.error(f"Gemini API completely failed in specific question chat: {str(e)}")
                    raise HTTPException(
                        status_code=503,
                        detail="O Mentor Griô via Vertex AI está processando muitas dúvidas no momento. Tente novamente em instantes."
                    )
