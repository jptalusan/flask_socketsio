from sockets import db

class MasterNode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nodename = db.Column(db.String(64), index=True, unique=True)
    datafile = db.Column(db.String(64), index=True, unique=True)
    status   = db.Column(db.String(64))
    ipaddress = db.Column(db.String(64))

    def __repr__(self):
        return 'Master: name:{0}, ip:{1}, status:{2}, data:{3}'.format(self.nodename, self.ipaddress, self.status, self.datafile)