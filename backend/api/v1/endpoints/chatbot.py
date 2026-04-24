from fastapi import APIRouter, Depends, HTTPException
from core.neo4j import get_driver
from core.deps import get_current_user
from models.user import User
from schemas.chatbot import MentorRequest, MentorResponse
import google.generativeai as genai
import os

# Configurar Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter()

@router.post("/mentor", response_model=MentorResponse)
def socratic_mentor(
    request: MentorRequest,
    current_user: User = Depends(get_current_user)
):
    driver = get_driver()
    with driver.session() as session:
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
        """, id=request.question_id).single()

        if not result:
            raise HTTPException(status_code=404, detail="Questão não encontrada")

        # Mapeamento de opções
        options = {
            1: result["opt_a"], 2: result["opt_b"], 3: result["opt_c"],
            4: result["opt_d"], 5: result["opt_e"]
        }
        option_map = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
        
        user_letter = option_map.get(request.selected_option_id)
        is_correct = user_letter == result["correct_answer"]
        
        # 2. Configurar o Prompt Socrático
        skills_context = ", ".join([f"{code}: {desc}" for code, desc in zip(result["skill_codes"], result["skill_descriptions"])])
        
        system_instruction = f"""
        Você é um assistente pedagógico especializado no ENEM.
        Seu objetivo é auxiliar o estudante no processo de resolução de questões, utilizando o método socrático para guiá-lo ao raciocínio correto sem fornecer a resposta diretamente.
        
        CONTEXTO DA QUESTÃO:
        Texto: {result["text"]}
        Opção Correta: {result["correct_answer"]}
        Explicação Técnica: {result["explanation"]}
        Habilidades Relacionadas: {skills_context}
        
        RESPOSTA DO ESTUDANTE:
        O estudante selecionou a opção {user_letter}: "{options.get(request.selected_option_id)}"
        Status: {'Correto' if is_correct else 'Incorreto'}
        
        DIRETRIZES DE RESPOSTA:
        1. OBJETIVIDADE: Limite sua resposta a no máximo 3 frases curtas e diretas.
        2. FOCO PEDAGÓGICO: 
           - Se o estudante acertou: Valide brevemente o conhecimento e faça uma pergunta técnica de confirmação.
           - Se o estudante errou: Não revele a alternativa correta. Identifique a falha na aplicação da Habilidade ENEM e faça uma pergunta que direcione o foco do estudante para o conceito-chave.
        3. TOM: Profissional, neutro e técnico. Evite qualquer tipo de saudação metafórica ou tratamento informal.
        """

        # 3. Chamar o Gemini
        model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.0-flash"), system_instruction=system_instruction)
        
        # Converter histórico para o formato do Gemini
        history = []
        for msg in request.chat_history:
            history.append({"role": "user" if msg.role == "user" else "model", "parts": [msg.content]})
            
        chat = model.start_chat(history=history)
        
        # Criar a mensagem de entrada baseada no contexto atual se for o início
        input_text = f"O aluno acabou de responder a questão {request.question_id} e {'acertou' if is_correct else 'errou'}. Inicie a orientação."
        if request.chat_history:
            input_text = request.chat_history[-1].content

        response = chat.send_message(input_text)
        
        return {
            "response": response.text,
            "skill_targeted": result["skill_codes"][0] if result["skill_codes"] else None,
            "is_correct": is_correct
        }
