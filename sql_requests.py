from sqlalchemy import select
import json

with open('./mysite/secret_var.json', 'r') as file:
    secret_var = json.load(file)

def create_obj(Session, composed_obj, class_name = None, filter_ = None, bot = None):
    try:
        if class_name is not None and filter_ is not None:
            obj_in_db = select_filtered_rows(Session, class_name, filter_, bot = bot)
        else:
            obj_in_db = []
        with Session() as session:
            try:
                if obj_in_db is None or obj_in_db == []:
                    session.add(composed_obj)
            except:
                session.rollback()
            else:
                session.commit()
    except Exception as e:
        if bot is not None:
            bot.send_message(secret_var["telegram_id"], 'sql22 ' + str(e))

def update_obj(new_object, session) -> None:
	session.merge(new_object)

def select_all(Session, class_name, return_field = None):
    if return_field is None:
        statement = select(class_name)
    else:
        statement = select(return_field)

    with Session() as session:
        db_object = session.scalars(statement).all()

    return db_object

def select_by_field(Session, class_name, class_field, value, return_field = None):
    try:
        if return_field is None:
            statement = select(class_name).where(class_field == value)
        else:
            statement = select(return_field).where(class_field == value)

        with Session() as session:
            db_object = session.scalars(statement).all()

        return db_object
    except:
        pass

def select_filtered_rows(Session, class_name, filters, return_field = None, bot = None):
	try:
		results = None

		with Session() as session:
			if return_field is None:
				query = session.query(class_name)
			else:
				query = session.query(return_field)

			for field, value in filters.items():
					query = query.filter(getattr(class_name, field) == value)

			results = query.all()

		return results

	except Exception as e:
		if bot is not None:
			bot.send_message(secret_var["telegram_id"], 'sql69 ' + str(e))

def select_all_from_list(Session, class_name, class_field, list_vals, return_field = None):
    try:
        if return_field is None:
    	    statement = select(class_name).where(class_field.in_(list_vals))
        else:
            statement = select(return_field).where(class_field.in_(list_vals))

        with Session() as session:
            db_object = session.scalars(statement).all()

        return db_object
    except:
        pass




