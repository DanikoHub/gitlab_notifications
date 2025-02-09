from typing import List, Any, Dict
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import sessionmaker
from mysite.src.tables.base import Base

from sqlalchemy import select

from mysite.src.log_tools import log_error

class SQLRequest:
	"""Class for making requests to db using SQLAlchemy module"""

	def __init__(self, Session : sessionmaker, class_name : Base):
		self.Session = Session
		self.class_name = class_name

	def create_obj(self, composed_obj, filter_dict : Dict[str, Any]) -> None:
		"""
		This method is used to create a new record in the database

		:param composed_obj: The composed object is instance of class that inheretes class Base, Example - class Users(Base)

		:param filter_dict : Filter is dictionary of unque fields and their values used to prevent creation of duplicate records
		"""
		try:
			obj_in_db = self.select_with_filter(filters = filter_dict) if self.class_name is not None and filter_dict is not None else []

			if obj_in_db is None or obj_in_db == []:
				with self.Session() as session:
					try:
						session.add(composed_obj)
					except Exception as e:
						log_error(e)
						session.rollback()

					else:
						session.commit()

		except Exception as e:
			log_error(e)

	def update_obj(self, filter_class_field : Mapped[Any], filter_value, update_dict : Dict[str, Any]) -> None:
		"""
		This method is used to update a record in the database

		:param filter_class_field: The field of the class that is used to filter the record

		:param filter_value: The value of the field that is used to filter the record

		:param update_dict: The dictionary of the fields and their new values
		"""
		with self.Session() as session:
			try:
				obj_to_update = session.query(self.class_name).filter(filter_class_field == filter_value)
				obj_to_update.update(update_dict)

			except Exception as e:
				session.rollback()
				log_error(e)

			else:
				session.commit()

	def select_all(self, return_field : Mapped[Any] = None) -> List[Any]:
		"""
		This method is used to select all records from the database

		:param return_field: The field of the class that will be returned
		"""
		try:
			statement = select(self.class_name if return_field is None else return_field)

			with self.Session() as session:
				db_object = session.scalars(statement).all()

			return db_object

		except Exception as e:
			log_error(e)
			return []


	def select_by_field(self, filter_class_field : Mapped[Any], filter_value, return_field : Mapped[Any] = None) -> List[Any]:
		"""
		This method is used to select a record from the database by a field

		:param filter_class_field: The field of the class that is used to filter the record

		:param filter_value: The value of the field that is used to filter the record

		:param return_field: The field of the class that will be returned
		"""
		try:
			with self.Session() as session:
				db_object = session.query(self.class_name if return_field is None else return_field)\
				.filter(filter_class_field == filter_value).all()

			return db_object

		except Exception as e:
			log_error(e)
			return []


	def select_with_filter(self, filters : Dict[str, Any], return_field : Mapped[Any] = None) -> List[Any]:
		"""
		This method is used to select a record from the database by a filter

		:param filters: The filter of the class that will be used to select the record

		:param return_field: The field of the class that will be returned
		"""
		try:
			results = None
			with self.Session() as session:
				query = session.query(self.class_name if return_field is None else return_field)

				for field, value in filters.items():
					query = query.filter(getattr(self.class_name, field) == value)
				results = query.all()

				return results

		except Exception as e:
			log_error(e)
			return []


	def select_from_list(self, filter_class_field : Mapped[Any], filter_list_values : List[Any], return_field : Mapped[Any] = None) -> List[Any]:
		"""
		This method is used to select a record from the database by a list of values

		:param filter_class_field: The field of the class that is used to filter the record

		:param filter_list_values: The list of values that are used to filter the record
		"""
		try:
			with self.Session() as session:
					db_object = session.query(self.class_name if return_field is None else return_field).filter(filter_class_field.in_(filter_list_values)).all()

			return db_object

		except Exception as e:
			log_error(e)
			return []


	def delete_obj(self, filters : Dict[str, Any]) -> None:
		"""
		This method is used to delete a record from the database

		:param filters: The filter of the class that is used to delete the record
		"""
		with self.Session() as session:
			try:
				obj = self.select_with_filter(filters)
				if len(obj) != 0:
					session.delete(obj[0])

			except Exception as e:
				log_error(e)
				session.rollback()

			else:
				session.commit()




