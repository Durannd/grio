from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.question import get_assessment_questions
from schemas.question import Assessment, Question
from schemas.assessment import AssessmentSubmission
from crud.assessment import process_assessment_submission
from core.neo4j import get_driver

router = APIRouter()

from schemas.question import Assessment, Question
from core.deps import get_current_user
from models.user import User

@router.get("/", response_model=Assessment)
def read_assessment(
    current_user: User = Depends(get_current_user)
):
    driver = get_driver()
    with driver.session() as session:
        # Algoritmo de seleção por competência para garantir abrangência (Breadth-First)
        # 1. Tenta pegar 1 questão de cada competência aleatória
        # 2. Remove restrição de ano (is_diagnostic) para evitar o erro de 2009
        result = session.run("""
            MATCH (c:Competence)
            WITH c, rand() as r ORDER BY r
            MATCH (q:Question)-[:EVALUATES]->(:Skill)-[:PART_OF]->(c)
            WHERE NOT (:User {id: $user_id})-[:ANSWERED]->(q)
            WITH c, q, rand() as rq ORDER BY rq
            WITH c, head(collect(q)) as chosen_q
            WITH chosen_q WHERE chosen_q IS NOT NULL
            RETURN chosen_q.id as id, chosen_q.text as text, chosen_q.difficulty as difficulty, 
                   chosen_q.answer as correct_answer,
                   chosen_q.option_a as option_a, chosen_q.option_b as option_b, chosen_q.option_c as option_c,
                   chosen_q.option_d as option_d, chosen_q.option_e as option_e
            LIMIT 15
            
            UNION
            
            // Fallback: se não completou 15 por competência, pega aleatórias restantes
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

@router.post("/submit")
def submit_assessment(
    submission: AssessmentSubmission, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Overwrite the user_id from the token to ensure security
    submission.user_id = current_user.id
    return process_assessment_submission(db, submission)
