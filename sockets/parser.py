from sockets import db
from sockets.models import Slavenode, Masternode

from json import dumps, loads

class Parser:
    def __init__(self):
        self.x = 0

    def test(self):
        # print('Hello world {0}, {1}!'.format(self.x, json_str))
        # data = json.loads(json_str)
        # print(data['node'])
        # print(data['ipaddress'])

        # snodes = Slavenode.query.all()
        # for node in snodes:
        #     db.session.delete(node)

        # mnodes = Masternode.query.all()
        # for node in mnodes:
        #     db.session.delete(node)

        # db.session.commit()

        # snode = Slavenode.query.filter_by(nodename='node0').first()

        # if snode is None:
        #     print('not existing, inserting')
        #     mn = Masternode(nodename="master0", datafile='empty', status='available', ipaddress='1234')
        #     db.session.add(mn)
        #     sn = Slavenode(nodename=data['node'], datafile='empty', status=data['availability'], ipaddress=data['ipaddress'], masternode=mn)
        #     sn1 = Slavenode(nodename='node1', datafile='empty1', status=data['availability'], ipaddress=data['ipaddress'], masternode=mn)
        #     sn2 = Slavenode(nodename='node2', datafile='empty2', status=data['availability'], ipaddress=data['ipaddress'], masternode=mn)
        #     db.session.add(sn)
        #     db.session.add(sn1)
        #     db.session.add(sn2)
        #     db.session.commit()
        # else:
        #     print('already here!{0}'.format(snode))
        #     #updating
            
        #     snode.status = 'busy!'
        #     db.session.commit()

        # snodes = Slavenode.query.all()
        # for snode in snodes:
        #     print(snode)
            #updating
        #     db.session.execute("UPDATE {0} SET status='{2}' WHERE nodename='{1}'".format(Slavenode.__tablename__, snode.nodename, 'HELLO'))
        #     db.session.commit()
        # print(snodes)
        # print(Slavenode.__tablename__)
        # cols = db.session.execute("PRAGMA table_info('{0}')".format(Slavenode.__tablename__))


        sns = db.session.execute('SELECT * FROM slavenode')
        for r in sns:
            print(r)

        mns = db.session.execute('SELECT * FROM masternode')
        for r in mns:
            print(r)

    def updateEverything():
        pass

    def deleteDB(self):
        snodes = Slavenode.query.all()
        for node in snodes:
            db.session.delete(node)

        mnodes = Masternode.query.all()
        for node in mnodes:
            db.session.delete(node)

        db.session.commit()

    def insert_or_update(self, json_str):
        data = loads(json_str)
        # print(data)
        if 'master' in data['nodename']:
            mn = Masternode.query.filter_by(nodename=data['nodename']).first()
            #insert to master table (what if slaves arrive first? just update after...)
            if mn is None:
                #insert
                masternode = Masternode(nodename=data['nodename'], datafile='empty', status=data['status'], ipaddress=data['ipaddress'])
                db.session.add(masternode)
                # db.session.commit()
            else:
                mn.status = data['status']
                mn.datafile = 'will_add_soon'
                mn.ipaddress = data['ipaddress']
                # db.session.commit()
            db.session.commit()
            # TODO: Maybe add string to slave so that i can iterate through them here and add the masternode to them
            snodes = Slavenode.query.filter_by(masternode_name=data['nodename'])
            mn = Masternode.query.filter_by(nodename=data['nodename']).first()
            for snode in snodes:
                snode.masternode = mn
            db.session.commit()
        elif 'node' in data['nodename']:
            snode = Slavenode.query.filter_by(nodename=data['nodename']).first()
            slaveMaster = data['master']
            mn = Masternode.query.filter_by(nodename=slaveMaster).first()
            if snode is None:
                #insert
                if mn is not None:
                    #check if master node placed in master key exists if yes, get it and then add
                    sn = Slavenode(nodename=data['nodename'], datafile='empty', status=data['status'], ipaddress=data['ipaddress'], masternode=mn, masternode_name=data['master'])
                else:
                    #no master node entry yet
                    sn = Slavenode(nodename=data['nodename'], datafile='empty', status=data['status'], ipaddress=data['ipaddress'], masternode_name=data['master'])
                db.session.add(sn)
                db.session.commit()
            else:
                if mn is not None:
                    #check if master node placed in master key exists if yes, get it and then add
                    snode.masternode = mn
                snode.status = data['status']
                snode.datafile = 'will_add_soon'
                snode.ipaddress = data['ipaddress']
                db.session.commit()
            #for slave nodes
        else:
            pass

    def generateJSON(self):
        snodes = Slavenode.query.all()
        mnodes = Masternode.query.all()
        
        l = []
        for snode in snodes:
            d = {}
            print(snode.nodename)
            d['nodename'] = snode.nodename
            d['status'] = snode.status
            d['ipaddress'] = snode.ipaddress
            d['datafile'] = snode.datafile
            d['masternode_name'] = snode.masternode_name
            l.append(d)

        d = {}
        for mnode in mnodes:
            d['nodename'] = mnode.nodename
            d['status'] = mnode.status
            d['ipaddress'] = mnode.ipaddress
            d['datafile'] = mnode.datafile
            d['masternode_name'] = 'none'
            l.append(d)

        json_str = dumps(l)
        print(json_str)
        return json_str

    def check_node_availability(self):
        pass
        
