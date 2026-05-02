from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from crud.question import get_assessment_questions
from schemas.question import Assessment, Question
from schemas.assessment import AssessmentSubmission
from crud.assessment import process_assessment_submission
from crud.user import update_user_streak
from core.neo4j import get_driver
from core.deps import get_current_user
from core.rate_limit import limiter, get_rate_limit
from models.user import User
from core.translator import get_friendly_name
import re

router = APIRouter()

# Security: Input validation patterns
SKILL_ID_PATTERN = re.compile(r'^[A-Z]{2,3}(-[0-9]+)?$')
VALID_AREAS = {"MT", "CN", "LC", "CH"}

@router.get("/", response_model=Assessment)
@limiter.limit(get_rate_limit("assessment"))
def read_assessment(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    driver = get_driver()
    with driver.session() as session:
        # Algoritmo de seleção Top-Down equilibrado por Área
        # 1. Tenta pegar até 4 questões distintas (de competências diferentes) para cada Área
        # 2. Mantém o fallback caso o banco não tenha questões suficientes em alguma área
        result = session.run("""
            // Busca equilibrada por Área -> Competência
            MATCH (a:Area)<-[:BELONGS_TO]-(c:Competence)<-[:PART_OF]-(:Skill)<-[:EVALUATES]-(q:Question)
            WHERE NOT (:User {id: $user_id})-[:ANSWERED]->(q)
            WITH a, c, q, rand() as rq ORDER BY rq
            WITH a, c, head(collect(q)) as chosen_q // 1 questão por competência
            WITH a, chosen_q, rand() as rc ORDER BY rc
            WITH a, collect(chosen_q)[..4] as area_questions // até 4 questões por área
            UNWIND area_questions as final_q
            RETURN final_q.id as id, final_q.text as text, final_q.difficulty as difficulty, 
                   final_q.answer as correct_answer,
                   final_q.option_a as option_a, final_q.option_b as option_b, final_q.option_c as option_c,
                   final_q.option_d as option_d, final_q.option_e as option_e
            LIMIT 15
            
            UNION
            
            // Fallback: se não completou 15, pega aleatórias restantes
            MATCH (q:Question)
            WHERE NOT (:User {id: $user_id})-[:ANSWERED]->(q)
            WITH q, rand() as r ORDER BY r
            RETURN q.id as id, q.text as text, q.difficulty as difficulty, 
                   q.answer as correct_answer,
                   q.option_a as option_a, q.option_b as option_b, q.option_c as option_c,
                   q.option_d as option_d, q.option_e as option_e
            LIMIT 15
        """, user_id=current_user.id)
        
        questions_map = {} # Usar mapa para evitar duplicatas do UNION
        for record in result:
            if record["id"] in questions_map: continue
            
            options = [
                {"id": 1, "text": record["option_a"] or ""},
                {"id": 2, "text": record["option_b"] or ""},
                {"id": 3, "text": record["option_c"] or ""},
                {"id": 4, "text": record["option_d"] or ""},
                {"id": 5, "text": record["option_e"] or ""},
            ]
            questions_map[record["id"]] = {
                "id": record["id"],
                "text": record["text"],
                "difficulty": record["difficulty"],
                "concept_name": "Diagnóstico", # Pode ser refinado
                "options": options
            }
            if len(questions_map) >= 15: break
            
        questions = list(questions_map.values())
            
    return {"questions": questions}

@router.get("/practice/{skill_id}", response_model=Assessment)
@limiter.limit(get_rate_limit("assessment"))
def read_practice_assessment(
    request: Request,
    skill_id: str,
    current_user: User = Depends(get_current_user)
):
    if not SKILL_ID_PATTERN.match(skill_id):
        raise HTTPException(
            status_code=400,
            detail=f"skill_id inválido: {skill_id}. Formato esperado: XX ou XXX-123"
        )
    friendly_name = get_friendly_name(skill_id)
    driver = get_driver()
    with driver.session() as session:
        # Busca questões vinculadas à Habilidade específica (Skill) que o usuário ainda não respondeu
        result = session.run("""
            MATCH (s:Skill {id: $skill_id})<-[:EVALUATES]-(q:Question)
            WHERE NOT (:User {id: $user_id})-[:ANSWERED]->(q)
            WITH q, rand() as r ORDER BY r
            RETURN q.id as id, q.text as text, q.difficulty as difficulty,
                   q.answer as correct_answer,
                   q.option_a as option_a, q.option_b as option_b, q.option_c as option_c,
                   q.option_d as option_d, q.option_e as option_e
            LIMIT 10
        """, skill_id=skill_id, user_id=current_user.id)

        questions = []
        for record in result:
            options = [
                {"id": 1, "text": record["option_a"] or ""},
                {"id": 2, "text": record["option_b"] or ""},
                {"id": 3, "text": record["option_c"] or ""},
                {"id": 4, "text": record["option_d"] or ""},
                {"id": 5, "text": record["option_e"] or ""},
            ]
            questions.append({
                "id": record["id"],
                "text": record["text"],
                "difficulty": record["difficulty"],
                "concept_name": f"Prática: {skill_id}",
                "options": options
            })

    return {"questions": questions, "friendly_name": friendly_name}

@router.get("/diagnostico/{area}", response_model=Assessment)
@limiter.limit(get_rate_limit("assessment"))
def read_diagnostic_assessment_by_area(
    request: Request,
    area: str,
    current_user: User = Depends(get_current_user)
):
    if area not in VALID_AREAS:
        raise HTTPException(
            status_code=400,
            detail=f"Área inválida: {area}. Valores aceitos: {', '.join(sorted(VALID_AREAS))}"
        )
    area_map = {"MT": "Matemática", "CN": "Natureza", "LC": "Linguagens", "CH": "Humanas"}
    mapped_area = area_map.get(area, area)
    
    driver = get_driver()
    with driver.session() as session:
        result = session.run("""
            MATCH (a:Area)<-[:BELONGS_TO]-(c:Competence)<-[:PART_OF]-(s:Skill)<-[:EVALUATES]-(q:Question)
            WHERE a.name CONTAINS $mapped_area AND NOT (:User {id: $user_id})-[:ANSWERED]->(q)
            WITH q, c
            ORDER BY c.weight DESC, rand()
            RETURN q.id as id, q.text as text, q.difficulty as difficulty, 
                   q.answer as correct_answer,
                   q.option_a as option_a, q.option_b as option_b, q.option_c as option_c,
                   q.option_d as option_d, q.option_e as option_e
            LIMIT 20
        """, mapped_area=mapped_area, user_id=current_user.id)
        
        questions = []
        for record in result:
            options = [
                {"id": 1, "text": record["option_a"] or ""},
                {"id": 2, "text": record["option_b"] or ""},
                {"id": 3, "text": record["option_c"] or ""},
                {"id": 4, "text": record["option_d"] or ""},
                {"id": 5, "text": record["option_e"] or ""},
            ]
            questions.append({
                "id": record["id"],
                "text": record["text"],
                "difficulty": record["difficulty"],
                "concept_name": f"Diagnóstico: {area}",
                "options": options
            })
            
    return {"questions": questions}

@router.post("/submit")
@limiter.limit(get_rate_limit("assessment"))
def submit_assessment(
    request: Request,
    submission: AssessmentSubmission, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.is_diagnostic_in_progress:
        raise HTTPException(
            status_code=429,
            detail="Diagnóstico em andamento. Aguarde a conclusão."
        )

    current_user.is_diagnostic_in_progress = True
    db.add(current_user)
    db.commit()

    try:
        # Overwrite the user_id from the token to ensure security
        submission.user_id = current_user.id
        update_user_streak(db, current_user)
        return process_assessment_submission(db, submission)
    finally:
        current_user.is_diagnostic_in_progress = False
        db.add(current_user)
        db.commit()

class AttemptSubmission(BaseModel):
    question_id: str
    is_correct: bool

@router.post("/students/{student_id}/attempts", status_code=202)
@limiter.limit(get_rate_limit("assessment"))
def submit_attempt(
    request: Request,
    student_id: str,
    attempt: AttemptSubmission,
    current_user: User = Depends(get_current_user)
):
    if str(current_user.id) != student_id:
        raise HTTPException(status_code=403, detail="Not authorized to submit attempts for this user")
        
    # Por enquanto, apenas um "pass" na lógica de cálculo, como requisitado para o MVP core.
    # A atualização no grafo seria feita via um job assíncrono ou chamada subsequente.
    return {"message": "Attempt registered", "student_id": student_id, "question_id": attempt.question_id, "is_correct": attempt.is_correct}
