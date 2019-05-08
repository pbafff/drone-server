from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
import json
from drone import connectToDrone, handleInput, defineAttitudeListenerCallback

class MyServerProtocol(WebSocketServerProtocol):
    connections = list()
    
    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        self.connections.append(self)
        #defineAttitudeListenerCallback(MyServerProtocol.broadcast_message)
        

    def onOpen(self):
        print("WebSocket connection open.")      

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
	    
        else:
            # print("Text message received: {0}".format(payload.decode('utf8')))
	        cmd = json.loads(json.loads(payload.decode('utf8'))['msg'])
                handleInput(cmd)

    def onClose(self, wasClean, code, reason):
	    print("WebSocket connection closed: {0}".format(reason))

    @classmethod
    def broadcast_message(cls, data):
        payload = json.dumps(data, ensure_ascii = True).encode('utf8')
        for c in set(cls.connections):
            reactor.callFromThread(cls.sendMessage, c, payload)
    

if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)
    
    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = MyServerProtocol
    defineAttitudeListenerCallback(factory.protocol.broadcast_message)
    reactor.listenTCP(9000, factory)

reactor.callInThread(connectToDrone)
reactor.run()
