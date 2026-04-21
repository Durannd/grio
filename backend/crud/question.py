from sqlalchemy.orm import Session
from models.question import Question, Option, DifficultyEnum

def populate_questions(db: Session):
    if db.query(Question).count() == 0:
        questions_data = [
            {
                "text": "Qual a capital da França?",
                "difficulty": DifficultyEnum.facil,
                "concept_name": "Geografia",
                "options": ["Londres", "Paris", "Roma", "Madri"],
                "correct_option": "Paris",
            },
            {
                "text": "Quanto é 2+2?",
                "difficulty": DifficultyEnum.facil,
                "concept_name": "Matemática",
                "options": ["3", "4", "5", "6"],
                "correct_option": "4",
            },
            {
                "text": "Qual a cor do céu?",
                "difficulty": DifficultyEnum.facil,
                "concept_name": "Conhecimentos Gerais",
                "options": ["Verde", "Azul", "Vermelho", "Amarelo"],
                "correct_option": "Azul",
            },
        ]
        for q_data in questions_data:
            db_question = Question(
                text=q_data["text"],
                difficulty=q_data["difficulty"],
                concept_name=q_data["concept_name"],
            )
            db.add(db_question)

            options = []
            for option_text in q_data["options"]:
                db_option = Option(text=option_text, question=db_question)
                db.add(db_option)
                options.append(db_option)

            db.flush()

            correct_option = next(o for o in options if o.text == q_data["correct_option"])
            db_question.correct_option = correct_option

        db.commit()

def get_assessment_questions(db: Session):
    populate_questions(db)
    return db.query(Question).all()
