from sqlalchemy import select
from typing import List, Any

from mysite.src.debug_tools import send_e

class SQLRequest:
	"""Class for making requests to db using SQLAlchemy module"""

	def __init__(self, Session, class_name):
		self.Session = Session
		self.class_name = class_name

	def close_session(self):
		self.Session().close()

	def create_obj(self, composed_obj, filter_) -> None:
		"""
		This method is used to create a new record in the database

		:param composed_obj: The composed object is instance of class that inheretes class Base, Example - class Users(Base)

		:param filter_ : Filter is dictionary of unque fields and their values used to prevent creation of duplicate records
		"""
		try:
			self.close_session()
			obj_in_db = self.select_with_filter(filters = filter_) if self.class_name is not None and filter_ is not None else []

			if obj_in_db is None or obj_in_db == []:
				with self.Session() as session:
					try:
						session.add(composed_obj)
					except Exception as e:
						send_e(e)
						session.rollback()

					else:
						session.commit()

		except Exception as e:
			send_e(e)

	def update_obj(self, class_update_field, update_value, update_dict) -> None:
		self.close_session()
		with self.Session() as session:
			try:
				obj_to_update = session.query(self.class_name).filter(class_update_field == update_value)
				obj_to_update.update(update_dict)

			except Exception as e:
				session.rollback()
				send_e(e)

			else:
				session.commit()

	def select_all(self, return_field = None) -> List[Any]:
		try:
			self.close_session()
			statement = select(self.class_name if return_field is None else return_field)

			with self.Session() as session:
				db_object = session.scalars(statement).all()

			return db_object

		except Exception as e:
			send_e(e)
			return []


	def select_by_field(self, class_field, value, return_field = None) -> List[Any]:
		try:
			self.close_session()
			with self.Session() as session:
				db_object = session.query(self.class_name if return_field is None else return_field)\
				.filter(class_field == value).all()

			send_e("db_object - " + str(db_object))
			return db_object

		except Exception as e:
			send_e(e)
			return []


	def select_with_filter(self, filters, return_field = None) -> List[Any]:
		try:
			results = None

			self.close_session()
			with self.Session() as session:
				query = session.query(self.class_name if return_field is None else return_field)

			for field, value in filters.items():
				query = query.filter(getattr(self.class_name, field) == value)
			results = query.all()

			return results

		except Exception as e:
			send_e(e)
			return []


	def select_from_list(self, class_field, list_vals, return_field = None) -> List[Any]:
		try:
			self.close_session()
			with self.Session() as session:
					db_object = session.query(self.class_name if return_field is None else return_field).filter(class_field.in_(list_vals)).all()

			return db_object

		except Exception as e:
			send_e(e)
			return []


	def delete_obj(self, filters) -> None:
		self.close_session()
		with self.Session() as session:
			try:
				obj = self.select_with_filter(self, filters)
				if len(obj) != 0:
					session.delete(obj[0])

			except Exception as e:
				send_e(e)
				session.rollback()

			else:
				session.commit()




