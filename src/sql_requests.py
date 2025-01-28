from sqlalchemy import select
import json

with open('./mysite/secret_var.json', 'r') as file:
	secret_var = json.load(file)


def send_e(bot, e, line = ''):
	if bot is not None:
		bot.send_message(secret_var["telegram_id"], line + str(e))


def create_obj(Session, composed_obj, class_name = None, filter_ = None, bot = None):
	try:
		obj_in_db = select_filtered_rows(Session, class_name, filter_, bot = bot) \
		if class_name is not None and filter_ is not None \
		else []

		with Session() as session:
			try:
				if obj_in_db is None or obj_in_db == []:
					session.add(composed_obj)
			except:
				session.rollback()
			else:
				session.commit()

	except Exception as e:
	    send_e(bot, e, line = 'sql29 ')


def update_obj(Session, class_name, class_update_field, update_value, update_json, bot = None):
	with Session() as session:
		try:
			obj_to_update = session.query(class_name).filter(class_update_field == update_value)
			obj_to_update.update(update_json)

		except Exception as e:
			session.rollback()
			send_e(bot, e, line = 'sql40 ')

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


def select_filtered_rows(Session, class_name, filters, return_field = None, bot = None):
	try:
		results = None

		with Session() as session:
			query = session.query(class_name if return_field is None else return_field)

			results = [query.filter(getattr(class_name, field) == value) for field, value in filters.items()][-1].all()

		return results

	except Exception as e:
	    send_e(bot, e, line = 'sql80 ')


def select_all_from_list(Session, class_name, class_field, list_vals, return_field = None):
	try:
		statement = select(class_name if return_field is None else return_field).where(class_field.in_(list_vals))

		with Session() as session:
			db_object = session.scalars(statement).all()

		return db_object
	except:
		pass




