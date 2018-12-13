# 建立資料表欄位
from app import db
class Todo(db.Model):
    # __table__name = 'user_table'，若不寫則看 class name
    # 設定 primary_key
    # id = db.Column(db.Integer, primary_key=True)
    # content = db.Column(db.String(80))
    Id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(64))
    Dataset = db.Column(db.String(64))
    Max_batch = db.Column(db.Integer)
    Batch_size = db.Column(db.Integer)
    Subdivisions = db.Column(db.Integer)
    Learning_rate = db.Column(db.Integer)

    def __init__(self, name, Dataset, Max_batch, Batch_size, Subdivisions, Learning_rate):
        self.name = name
        self.Dataset = Dataset
        self.Max_batch = Max_batch
        self.Batch_size = Batch_size
        self.Subdivisions = Subdivisions
        self.Learning_rate = Learning_rate
    def __repr__(self):
        return '<Todo %r>' % self.name