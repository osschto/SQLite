from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, select

app = FastAPI()

class Teacher(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    subject: str
    experience : int

def validate_experience(teacher : Teacher):
    if teacher.experience < 0:
        raise HTTPException(status_code=400, detail="Стаж не может быть меньше 0")
    return teacher
    
engine = create_engine("sqlite:///teachers.db")
SQLModel.metadata.create_all(engine)

@app.post("/teachers", tags=["CRUD"], summary="Добавить учителя")
def add_teacher(teacher : Teacher = Depends(validate_experience)):
    with Session(engine) as session:
        session.add(teacher)
        session.commit()
        session.refresh(teacher)
        return {"message" : f"{teacher.name} был(а) успешно добавлен(а)"}

@app.get("/teachers",tags=["CRUD"], summary="Получить список учителей")
def get_teacher():
    with Session(engine) as session:
        teachers = session.exec(select(Teacher)).all()
        return teachers
    
@app.put("/teachers/{teacher_id}", tags=["CRUD"], summary="Изменить по id")
def edit_by_id(teacher_id : int, updated : Teacher = Depends(validate_experience)):
    with Session(engine) as session:
        teacher = session.get(Teacher, teacher_id)
        if not teacher:
            return HTTPException(status_code=404, detail="Учитель не найден")
        
        teacher.name = updated.name
        teacher.subject = updated.subject
        teacher.experience = updated.experience
        
        session.add(teacher)
        session.commit()

        return {"message" : "Данные обновлены"}

@app.delete("/teachers/{teacher_id}", tags=["CRUD"], summary="Удалить по id")
def delete_by_id(teacher_id : int):
    with Session(engine) as session:
        teacher = session.get(Teacher, teacher_id)
        if not teacher:
            return HTTPException(status_code=404, detail="Учитель не найден")
        
        session.delete(teacher)
        session.commit()

        return {"message" : "Данные удалены"}
        