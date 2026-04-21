from sqlalchemy.orm import Session
from backend.models.question import Question, DifficultyEnum
from backend.schemas.question import QuestionCreate

def populate_questions(db: Session):
    if db.query(Question).count() == 0:
        questions = [
            # Facil
            QuestionCreate(text="Qual a capital da França?", difficulty=DifficultyEnum.facil, concept_name="Geografia"),
            QuestionCreate(text="Quanto é 2+2?", difficulty=DifficultyEnum.facil, concept_name="Matemática"),
            QuestionCreate(text="Qual a cor do céu?", difficulty=DifficultyEnum.facil, concept_name="Conhecimentos Gerais"),
            # Media
            QuestionCreate(text="Quem escreveu 'Dom Quixote'?", difficulty=DifficultyEnum.media, concept_name="Literatura"),
            QuestionCreate(text="Qual o ponto de ebulição da água em Celsius?", difficulty=DifficultyEnum.media, concept_name="Física"),
            QuestionCreate(text="Qual a maior cordilheira do mundo?", difficulty=DifficultyEnum.media, concept_name="Geografia"),
            # Dificil
            QuestionCreate(text="O que é a constante de Planck?", difficulty=DifficultyEnum.dificil, concept_name="Física Quântica"),
            QuestionCreate(text="Quem foi o primeiro programador da história?", difficulty=DifficultyEnum.dificil, concept_name="História da Computação"),
            QuestionCreate(text="Qual a fórmula da velocidade da luz no vácuo?", difficulty=DifficultyEnum.dificil, concept_name="Física"),
        ]
        for q in questions:
            db_question = Question(**q.dict())
            db.add(db_question)
        db.commit()

def get_assessment_questions(db: Session):
    populate_questions(db)
    return db.query(Question).all()
