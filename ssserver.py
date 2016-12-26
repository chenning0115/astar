# -*- coding: utf-8 -*-
# 最短成本路径服务器端
# author:cyr
from io import BytesIO
from io import StringIO
import gzip
import pika
import demjson
import logging


class Server(object):
    def __init__(self, methodname, spmethod):
        """
methodname: string, in "dijistra", "astar(0)", "ants", "pregelsssp".\n
method: function, with param list (data,start,end).\n
    data: 2d array, presents cost grid.\n start: tuple with two int,
    start point.\n end: tuple with two int, end point.
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='mq.12414.tk'))
        channel = connection.channel()
        channel.queue_declare(queue=methodname)

        channel.basic_qos(prefetch_count=1)

        def request(ch, method, properties, body):
            logging.warning('%s: start request.' % properties.correlation_id)
            # gzip解压
            reqbuffer = BytesIO(body)
            reqf = gzip.GzipFile(mode="rb", fileobj=reqbuffer)
            reqjson = reqf.read()
            # json解码
            reqpayload = demjson.decode(reqjson)

            logging.info('%s: request payload: %s' % (properties.correlation_id, reqjson))
            logging.warning('%s: start compute.' % properties.correlation_id)

            # 计算最短路径
            result = spmethod(reqpayload['data'], reqpayload['start'], reqpayload['end'])

            logging.warning('%s: start response.' % properties.correlation_id)
            logging.info('%s: response payload: %s' % (properties.correlation_id, result))

            # json编码
            respjson = demjson.encode(result)
            # gzip压缩
            respbuf = BytesIO()
            respf = gzip.GzipFile(mode="wb", fileobj=respbuf)
            respf.write(bytes(respjson,'utf-8'))
            respf.close()

            # 将计算结果发送回客户端
            ch.basic_publish(exchange='',
                             routing_key=properties.reply_to,
                             properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                             body=respbuf.getvalue())
            ch.basic_ack(delivery_tag=method.delivery_tag)

            logging.warning('%s: end request.' % properties.correlation_id)

        channel.basic_consume(request, queue=methodname)

        channel.start_consuming()

        return


def test():
    import sys
    funname = sys.argv[1]
    from astar import Astar
    def fun_astar(data, s, e):
        star = Astar(data,funname)
        star.setstarpos((s[1], s[0]))
        star.setendpos((e[1], e[0]))
        res =  star.runAstar()
        mylist = []
        for x,y in res:
            mylist.append(y)
            mylist.append(x)
        return mylist
    Server(funname, fun_astar)
    return





if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,  # WARNING,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%d %b %Y %H:%M:%S')
    test()


