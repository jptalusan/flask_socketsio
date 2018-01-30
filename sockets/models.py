from sockets import db
import json

class Masternode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nodename = db.Column(db.String(64), index=True, unique=True)
    datafile = db.Column(db.String(64), index=True)
    status   = db.Column(db.String(64))
    ipaddress = db.Column(db.String(64))
    slaves = db.relationship('Slavenode', backref='masternode', lazy=True)

    def __repr__(self):
        output = {}
        output['nodename'] = self.nodename
        output['ipaddress'] = self.ipaddress
        output['status'] = self.status
        output['datafile'] = self.datafile
        output['masternode_name'] = "none"
        return json.dumps(output)

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
        output = {}
        output['nodename'] = self.nodename
        output['ipaddress'] = self.ipaddress
        output['status'] = self.status
        output['datafile'] = self.datafile
        output['masternode_name'] = self.masternode_name
        
        return json.dumps(output)