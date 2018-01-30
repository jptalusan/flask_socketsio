from sockets import db

class Masternode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nodename = db.Column(db.String(64), index=True, unique=True)
    datafile = db.Column(db.String(64), index=True)
    status   = db.Column(db.String(64))
    ipaddress = db.Column(db.String(64))
    slaves = db.relationship('Slavenode', backref='masternode', lazy=True)

    def __repr__(self):
        return 'Master: nodename:{0}, ipaddress:{1}, status:{2}, datafile:{3}'.format(self.nodename, self.ipaddress, self.status, self.datafile)

class Slavenode(db.Model):
    __tablename__ = 'slavenode'
    id = db.Column(db.Integer, primary_key=True)
    nodename = db.Column(db.String(64), index=True, unique=True)
    datafile = db.Column(db.String(64), index=True)
    status   = db.Column(db.String(64))
    ipaddress = db.Column(db.String(64))
    masternode_name = db.Column(db.String(64))
    masternode_id = db.Column(db.Integer, db.ForeignKey('masternode.id'))

    def __repr__(self):
        return 'Slave: nodename:{0}, ipaddress:{1}, status:{2}, datafile:{3}, masternode:{4}'.format(self.nodename, self.ipaddress, self.status, self.datafile, self.masternode)