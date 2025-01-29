from sqlalchemy import select

from mysite.src.debug_tools import send_e

def create_obj(Session, composed_obj, class_name = None, filter_ = None, bot = None):
	try:
		obj_in_db = select_with_filter(Session, class_name, filter_, bot = bot) \
		if class_name is not None and filter_ is not None else []

		with Session() as session:
			try:
				if obj_in_db is None or obj_in_db == []:
					session.add(composed_obj)

			except:
				session.rollback()

			else:
				session.commit()

	except Exception as e:
	    send_e(e)


def update_obj(Session, class_name, class_update_field, update_value, update_json, bot = None):
	with Session() as session:
		try:
			obj_to_update = session.query(class_name).filter(class_update_field == update_value)
			obj_to_update.update(update_json)

		except Exception as e:
			session.rollback()
			send_e(e)

		else:
			session.commit()


def select_all(Session, class_name, return_field = None):
	statement = select(class_name if return_field is None else return_field)

	with Session() as session:
		db_object = session.scalars(statement).all()

	return db_object


def select_by_field(Session, class_name, class_field, value, return_field = None):
	try:
		statement = select(class_name if return_field is None else return_field).where(class_field == value)

		with Session() as session:
			db_object = session.scalars(statement).all()
		return db_object

	except:
		pass


def select_with_filter(Session, class_name, filters, return_field = None, bot = None):
	try:
		results = None

		with Session() as session:
			query = session.query(class_name if return_field is None else return_field)
			results = [query.filter(getattr(class_name, field) == value) for field, value in filters.items()][-1].all()

		return results

	except Exception as e:
	    send_e(e)


def select_from_list(Session, class_name, class_field, list_vals, return_field = None):
	try:
		statement = select(class_name if return_field is None else return_field).where(class_field.in_(list_vals))

		with Session() as session:
			db_object = session.scalars(statement).all()

		return db_object

	except:
		pass

def delete_obj(Session, class_name, filters):
    with Session() as session:
        try:
            obj = select_with_filter(session, class_name, filters)
            if len(obj) != 0:
                session.delete(obj[0])

        except:
            session.rollback()

        else:
            session.commit()




