import zmq

import gen_ports


class PubSubManager():
    def __init__(self, instance_name, instances, proxied_instances, sub_to_name, base_port):
        self.instance_name = instance_name
        self.sub_to_name = sub_to_name
        self.pub_port, self.sub_ports = gen_ports.gen_ports(base_port, instances, proxied_instances, instance_name)
        
        self._zmq_context = None

    def __enter__(self):
        self.start()

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()

    def start(self):
        '''
        Set up the publish and subscribe connections.
        '''
        self._zmq_context = zmq.Context.instance()

        # Open a publish socket.
        pub_socket = self._zmq_context.socket(zmq.PUB)
        pub_socket.bind("tcp://*:{0}".format(self.pub_port))
        print "instance {0} binded on {1}".format(self.instance_name, self.pub_port)

        # Open subscribe sockets.
        sub_sockets = []
        for sub_port in self.sub_ports:
            sub_socket = self._zmq_context.socket(zmq.SUB)
            sub_socket.setsockopt(zmq.SUBSCRIBE, "")
            sub_socket.connect("tcp://{0}:{1}".format(self.sub_to_name, sub_port))
            sub_sockets.append(sub_socket)
            print "instance {0} connected to {1} on {2}".format(self.instance_name, self.sub_to_name, sub_port)

    def stop(self):
        print "Closing sockets"
        self._zmq_context.destroy(0)



