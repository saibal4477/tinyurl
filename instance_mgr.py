from kazoo.client import KazooClient
from kazoo.exceptions import NodeExistsError, KazooException
from piddy_exception import PiddyurlException
import logging
import os


class InstanceManager:
    def __init__(self):
        self.zk = None
        self.instance_id = -1
        self.latest = ''
        self.zkpath = '/piddyurl/frontend/1.0/instance'
        self.host_name = os.environ.get('ZK_HOST', '127.0.0.1')

    def connect(self):
        try:
            logging.basicConfig()

            self.zk = KazooClient(hosts=self.host_name)
            self.zk.start()
        except KazooException as ex:
            raise PiddyurlException('The web server is not initialized properly [' + str(ex) + ']', status_code=410)

    def getInstanceID(self):
        # if not connected then reconnect
        if self.zk and self.zk.connected and self.instance_id != -1:
            return self.instance_id

        if not self.zk:
            self.connect()

        if not self.zk.connected:
            self.connect()

        # create the node for the first time
        try:
            self.zk.create(path=self.zkpath, ephemeral=False, sequence=False, makepath=True)
        except NodeExistsError:
            pass

        # check which instance is available
        for i in range(62):
            # do we have the node for the instance ?
            if not self.zk.exists(path=self.zkpath + str(i)):
                try:
                    # create it
                    self.zk.create(path=self.zkpath + '/' + str(i), ephemeral=False, sequence=False, makepath=True)
                except NodeExistsError:
                    pass

            # do we have a live
            if not self.zk.exists(path=self.zkpath + '/' + str(i) + '/live'):
                try:
                    self.zk.create(path=self.zkpath + '/' + str(i) + '/live', ephemeral=True, sequence=False,
                                   makepath=True)
                    self.instance_id = i

                    # read the latest value
                    if not self.zk.exists(path=self.zkpath + '/' + str(i) + '/latest'):
                        self.zk.create(path=self.zkpath + '/' + str(i) + '/latest', ephemeral=False, sequence=False,
                                       makepath=True)

                        if 0 <= i < (26 * 2):
                            val = chr(ord('a') + i)
                        else:
                            val = chr(ord('0') + i)
                        val += 'aaaaa'

                        self.updateLatest(val)
                    break
                except NodeExistsError:
                    pass

        # if we haven't found any instance then let go this instance
        if self.instance_id == -1:
            raise PiddyurlException('The web server is not initialized properly [all 62 instances are running] ', status_code=410)

        return self.instance_id

    def getLatest(self):
        if self.zk and self.zk.connected and self.latest != '':
            return self.latest

        self.connect()
        try:
            data, _ = self.zk.get(path=self.zkpath + '/' + str(self.instance_id) + '/latest')
            self.latest = data.decode('utf-8')
            return self.latest
        except KazooException as ex:
            raise PiddyurlException('Cannot get the latest field from the ZooKeeper [', str(ex) + ']')

    def updateLatest(self, latest):
        try:
            self.latest = latest
            self.zk.set(path=self.zkpath + '/' + str(self.instance_id) + '/latest', value=self.latest.encode('ascii'))
        except KazooException as ex:
            raise PiddyurlException('Cannot get the latest field from the ZooKeeper [' + str(ex) + ']')

