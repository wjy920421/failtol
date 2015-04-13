import time
import kazoo.exceptions
from database.zookeeper import kazooclientlast

class ZookeeperClient():
    def __init__(self, zkhost, instance_name, instances_num, seq_obj_path, barrier_path):
        self.zkhost = zkhost
        self.instance_name = instance_name
        self.instances_num = instances_num
        self.seq_obj_path = seq_obj_path
        self.barrier_path = barrier_path

        self._kz = kazooclientlast.KazooClientLast(hosts=self.zkhost)
        self.seq_num = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()

    def start(self):
        print "Establishing connection to ZooKeeper"
        self._kz.start()
        # Initialize sequence numbering by ZooKeeper
        try:
            self._kz.create(path=self.seq_obj_path, value="0", makepath=True)
        except kazoo.exceptions.NodeExistsError as nee:
            self._kz.set(self.seq_obj_path, "0") # Another instance has already created the node, or it is left over from prior runs

        # Wait for all DBs to be ready
        self._kz.ensure_path(self.barrier_path)
        b = self._kz.create(self.barrier_path + '/' + self.instance_name, ephemeral=True)
        print "Waiting for other DB instances"
        while len(self._kz.get_children(self.barrier_path)) < self.instances_num:
            time.sleep(1)
        print "All DB instances are now running"

        # Create the sequence counter.
        self.seq_num = self._kz.Counter(self.seq_obj_path)

    def stop(self):
        print "Closing ZooKeeper connection"
        self._kz.stop()
        self._kz.close()
        
