from mysite.src.notifications import NotificationFactory
from mysite.src.table_factory import TableFactory

class Record:
    def __init__(self, Session, request = "", bot = None):
        self.Session = Session
        self.request = request
        self.bot = bot

    def create_new_record(self, class_name, **args):
        TableFactory.create_table(class_name, self.Session, self.request, **args)
        if self.bot is not None:
            NotificationFactory.notify(class_name, self.Session, self.request, self.bot)

    def delete_record(self, class_name):
        TableFactory.delete_record(class_name, self.Session, self.request)
    