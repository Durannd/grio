from fastapi import APIRouter, Depends, HTTPException, Request
from core.neo4j import get_driver
from core.deps import get_current_user
from core.rate_limit import limiter, get_rate_limit
from models.user import User
from schemas.chatbot import MentorRequest, MentorResponse
from google import genai
from google.genai import types
import os
from core.translator import get_friendly_name

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
    
    # Suportar assistência genérica ou específica por questão
    if mentor_request.question_id == "general":
        # Modo de assistência geral
        system_instruction = """
        Você é um Mentor Educacional do Griô, especializado em preparação para o ENEM.
        Seu objetivo é ajudar o estudante com dúvidas sobre conceitos, estratégias de estudo e resolução de problemas.
        Seja encorajador, motivacional e focado no aprendizado.
        
        DIRETRIZES:
        1. TOM: Profissional, amigável e motivacional.
        2. MÉTODO: Explique conceitos de forma clara, usando exemplos quando possível.
        3. LINGUAGEM: PROIBIÇÃO EXTREMA DO USO DE EMOJIS. Não use gírias ou jargões técnicos sem explicar.
        4. CONCISÃO: Respostas claras e diretas, máximo 4 frases.
        """
        
        client = genai.Client()
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
                    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
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
                        detail="O servidor de Inteligência Artificial está com alta demanda. Tente novamente em alguns momentos."
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
        
        # 2. Configurar o Prompt Socrático
        skills_context = ", ".join([f"{get_friendly_name(code)}: {desc}" for code, desc in zip(result["skill_codes"], result["skill_descriptions"])])
        
        system_instruction = f"""
        Você é um Mentor Socrático especializado no ENEM.
        Seu objetivo é auxiliar o estudante na resolução de questões, utilizando o método socrático para guiá-lo ao raciocínio correto sem fornecer a resposta diretamente. Seja sempre encorajador, motivacional e focado no crescimento do aluno.
        
        CONTEXTO DA QUESTÃO:
        Texto: {result["text"]}
        Opção Correta: {result["correct_answer"]}
        Explicação Técnica: {result["explanation"]}
        Habilidades Relacionadas: {skills_context}
        
        RESPOSTA DO ESTUDANTE:
        O estudante selecionou a opção {user_letter}: "{options.get(mentor_request.selected_option_id)}"
        Status: {'Correto' if is_correct else 'Incorreto'}
        
        DIRETRIZES DE RESPOSTA:
        1. TOM: Profissional, encorajador e motivacional (focado no progresso).
        2. MÉTODO: Não forneça a alternativa correta. Utilize perguntas direcionadas para que o estudante identifique o erro ou confirme a lógica do acerto.
        3. LINGUAGEM: PROIBIÇÃO EXTREMA DO USO DE EMOJIS. Não atue como um personagem ou entidade (NÃO incorpore o Mestre Griô). Não use gírias.
        4. CONCISÃO: Limite a resposta a no máximo 3 frases curtas.
        5. FOCO: Relacione o feedback com a Habilidade ENEM associada à questão de forma clara e amigável.
        """

        # 3. Chamar o Gemini
        client = genai.Client()
        
        history = []
        for msg in mentor_request.chat_history:
            history.append({"role": "user" if msg.role == "user" else "model", "parts": [{"text": msg.content}]})
            
        if not history:
            input_text = f"O aluno acabou de responder a questão {mentor_request.question_id} e {'acertou' if is_correct else 'errou'}. Inicie a orientação."
            history.append({"role": "user", "parts": [{"text": input_text}]})

        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
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
                        detail="O servidor de Inteligência Artificial está com alta demanda. Tente novamente em alguns momentos."
                    )
