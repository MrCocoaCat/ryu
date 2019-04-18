# -*- coding: UTF-8 -*-


import logging
import os
from ryu.lib import ip


# We don't bother to use cfg.py because monkey patch needs to be
# called very early. Instead, we use an environment variable to
# select the type of hub.
HUB_TYPE = os.getenv('RYU_HUB_TYPE', 'eventlet')

# Return a logger with the specified name, creating it if necessary
LOG = logging.getLogger('ryu.lib.hub')

if HUB_TYPE == 'eventlet':
    import eventlet
    # HACK:
    # sleep() is the workaround for the following issue.
    # https://github.com/eventlet/eventlet/issues/401
    eventlet.sleep()
    import eventlet.event
    import eventlet.queue
    import eventlet.semaphore
    import eventlet.timeout
    import eventlet.wsgi
    from eventlet import websocket
    import greenlet
    import ssl
    import socket
    import traceback

    getcurrent = eventlet.getcurrent
    # 在全局中为指定的系统模块打补丁，补丁后的模块是“绿色线程友好的”，关键字参数指示哪些模块需要被打补丁，
    patch = eventlet.monkey_patch
    # 暂停当前greenthread，允许其他线程处理
    sleep = eventlet.sleep
    listen = eventlet.listen
    connect = eventlet.connect

    # 类似一个装饰器函数，增加了异常处理功能，装饰eventlet.spawn
    def spawn(*args, **kwargs):
        # **kwargs 为字典类型，删除其‘raise_error ’，如果无键值，则返货False
        raise_error = kwargs.pop('raise_error', False)

        def _launch(func, *args, **kwargs):
            # Mimic gevent's default raise_error=False behaviour
            # by not propagating an exception to the joiner.
            try:
                return func(*args, **kwargs)
            # TaskExit - greenlet.GreenletExit
            except TaskExit:
                pass
            except BaseException as e:
                if raise_error:
                    raise e
                # Log uncaught exception.
                # Note: this is an intentional divergence from gevent
                # behaviour; gevent silently ignores such exceptions.
                LOG.error('hub: uncaught exception: %s',
                          traceback.format_exc())

        return eventlet.spawn(_launch, *args, **kwargs)

    # 类似一个装饰器函数，增加了异常处理功能，装饰eventlet.spawn_after
    def spawn_after(seconds, *args, **kwargs):
        raise_error = kwargs.pop('raise_error', False)

        def _launch(func, *args, **kwargs):
            # Mimic gevent's default raise_error=False behaviour
            # by not propagating an exception to the joiner.
            try:
                return func(*args, **kwargs)
            except TaskExit:
                pass
            except BaseException as e:
                if raise_error:
                    raise e
                # Log uncaught exception.
                # Note: this is an intentional divergence from gevent
                # behaviour; gevent silently ignores such exceptions.
                LOG.error('hub: uncaught exception: %s',
                          traceback.format_exc())

        return eventlet.spawn_after(seconds, _launch, *args, **kwargs)

    def kill(thread):
        thread.kill()

    # join 列表中的线程
    def joinall(threads):
        for t in threads:
            # This try-except is necessary when killing an inactive
            # greenthread.
            try:
                t.wait()
            # TaskExit 为强制退出异常
            except TaskExit:
                pass

    # http://eventlet.net/doc/modules/semaphore.html
    #
    # This is a variant of Queue that behaves mostly like the standard Stdlib_Queue.
    # It differs by not supporting the task_done or join methods,
    # and is a little faster for not having that overhead.
    # Queue的变体，类似于标准的Stdlib_Queue。
    # 但不支持task_done或join方法，速度更快。
    Queue = eventlet.queue.LightQueue
    # Return True if the queue is empty, False otherwise.
    QueueEmpty = eventlet.queue.Empty
    # An unbounded semaphore.有限信号量
    Semaphore = eventlet.semaphore.Semaphore
    # A bounded semaphore checks to make sure its current value doesn’t exceed its initial value.
    # 有限信号量，即信号量总数不得超过设定值
    BoundedSemaphore = eventlet.semaphore.BoundedSemaphore
    # 强制退出异常
    TaskExit = greenlet.GreenletExit

    #
    class StreamServer(object):
        def __init__(self, listen_info, handle=None, backlog=None,
                     spawn='default', **ssl_args):
            assert backlog is None
            assert spawn == 'default'

            if ip.valid_ipv6(listen_info[0]):
                self.server = eventlet.listen(listen_info,
                                              family=socket.AF_INET6)
            elif os.path.isdir(os.path.dirname(listen_info[0])):
                # Case for Unix domain socket
                self.server = eventlet.listen(listen_info[0],
                                              family=socket.AF_UNIX)
            else:
                self.server = eventlet.listen(listen_info)

            if ssl_args:
                def wrap_and_handle(sock, addr):
                    ssl_args.setdefault('server_side', True)
                    handle(ssl.wrap_socket(sock, **ssl_args), addr)

                self.handle = wrap_and_handle
            else:
                self.handle = handle

        def serve_forever(self):
            while True:
                sock, addr = self.server.accept()
                spawn(self.handle, sock, addr)

    class StreamClient(object):
        def __init__(self, addr, timeout=None, **ssl_args):
            assert ip.valid_ipv4(addr[0]) or ip.valid_ipv6(addr[0])
            self.addr = addr
            self.timeout = timeout
            self.ssl_args = ssl_args
            self._is_active = True

        def connect(self):
            try:
                if self.timeout is not None:
                    client = socket.create_connection(self.addr,
                                                      timeout=self.timeout)
                else:
                    client = socket.create_connection(self.addr)
            except socket.error:
                return None

            if self.ssl_args:
                client = ssl.wrap_socket(client, **self.ssl_args)

            return client

        def connect_loop(self, handle, interval):
            while self._is_active:
                sock = self.connect()
                if sock:
                    handle(sock, self.addr)
                sleep(interval)

        def stop(self):
            self._is_active = False

    class LoggingWrapper(object):
        def write(self, message):
            LOG.info(message.rstrip('\n'))

    class WSGIServer(StreamServer):
        def serve_forever(self):
            self.logger = LoggingWrapper()
            eventlet.wsgi.server(self.server, self.handle, self.logger)

    WebSocketWSGI = websocket.WebSocketWSGI

    Timeout = eventlet.timeout.Timeout

    class Event(object):
        def __init__(self):
            self._ev = eventlet.event.Event()
            self._cond = False

        def _wait(self, timeout=None):
            while not self._cond:
                self._ev.wait()

        def _broadcast(self):
            self._ev.send()
            # Since eventlet Event doesn't allow multiple send() operations
            # on an event, re-create the underlying event.
            # Note: _ev.reset() is obsolete.
            self._ev = eventlet.event.Event()

        def is_set(self):
            return self._cond

        def set(self):
            self._cond = True
            self._broadcast()

        def clear(self):
            self._cond = False

        def wait(self, timeout=None):
            if timeout is None:
                self._wait()
            else:
                try:
                    with Timeout(timeout):
                        self._wait()
                except Timeout:
                    pass

            return self._cond
