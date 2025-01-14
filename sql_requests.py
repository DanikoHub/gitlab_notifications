from sqlalchemy import select

def create_obj(obj, session) -> None:
	session.add(obj)

def get_all_objs(session, class_name):
	statement = select(class_name)
	db_object = session.scalars(statement).all()
	return db_object

def update_obj(new_object, session) -> None:
	session.merge(new_object)

def add_composed_obj(Session,composed_obj):
    try:
        with Session() as session:
            try:
                create_obj(composed_obj, session)
            except:
                session.rollback()
            else:
                session.commit()
    except:
        pass

def select_by_field(session, class_name, class_field, value):
	statement = select(class_name).where(class_field == value)
	db_object = session.scalars(statement).all()
	return db_object




