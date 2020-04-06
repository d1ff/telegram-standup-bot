from umongo import Instance, Document, fields

from .app import dp

db = dp.storage.get_db()

instance =  Instance(db)

@instance.register
class Report(Document):
    user = fields.StrField()
    date = fields.DateTimeField()
    feel = fields.StrField()
    yesterday = fields.StrField()
    today = fields.StrField()
    block = fields.StrField()
    absences = fields.StrField()

    class Meta:
        collection = db.reports
