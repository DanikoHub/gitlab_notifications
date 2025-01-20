from sqlalchemy import select
import json

with open('./mysite/secret_var.json', 'r') as file:
    secret_var = json.load(file)

def create_obj(obj, session) -> None:
	session.add(obj)

def select_all(session, class_name):
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
    try:
    	statement = select(class_name).where(class_field == value)
    	db_object = session.scalars(statement).all()
    	session.close()
    	return db_object
    except:
        pass

def select_filtered_rows(session, class_name, filters):
    try:
        query = session.query(class_name)
        for field, value in filters.items():
            query = query.filter(class_name.c[field] == value)
        results = query.all()
        session.close()
        return results
    except:
        pass

def select_all_from_list(session, class_name, class_field, list_vals, return_field = None):
    try:
        if return_field is None:
    	    statement = select(class_name).where(class_field.in_(list_vals))
        else:
            statement = select(return_field).where(class_field.in_(list_vals))
        db_object = session.scalars(statement).all()
        session.close()
        return db_object
    except Exception as e:
        bot.send_message(secret_var["telegram_id"], e)




