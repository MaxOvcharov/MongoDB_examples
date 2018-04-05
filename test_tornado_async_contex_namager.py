from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from functools import partial


class MyLock:

    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.open_file = None
        self.is_context_manager = False

    @coroutine
    def acquire(self):
        self.open_file = open(self.filename, self.mode)
        self.is_context_manager = True
        return self.open_file

    @coroutine
    def release(self):
        if self.is_context_manager and self.open_file is not None:
            self.open_file.close()
            self.is_context_manager = False

    @coroutine
    def locked(self):
        return self.is_context_manager

    def __enter__(self):
        raise RuntimeError(
            "Use Lock like 'with (yield lock)', not like 'with lock'")

    __exit__ = __enter__

    @coroutine
    def __aenter__(self):
        return (yield self.acquire())

    @coroutine
    def __aexit__(self, typ, value, tb):
        yield self.release()


@coroutine
def test_context_manager1():
    lock = MyLock('test.txt', 'r')

    with (yield lock.acquire()) as f:
        for line in f:
            print(line)

        print((yield lock.locked()))

    print((yield lock.locked()))


@coroutine
def test_context_manager2():
    lock = MyLock('test.txt', 'r')

    with (yield lock) as f:
        for line in f:
            print(line)

        print((yield lock.locked()))

    print((yield lock.locked()))


async def test_context_manager3():
    lock = MyLock('test.txt', 'r')

    async with lock as f:
        for line in f:
            print(line)

        res = await lock.locked()
        print(res)

    res = await lock.locked()
    print(res)


class MyLockAsync:

    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.open_file = None
        self.is_context_manager = False

    async def acquire(self):
        self.open_file = open(self.filename, self.mode)
        self.is_context_manager = True
        return self.open_file

    async def release(self):
        if self.is_context_manager and self.open_file is not None:
            self.open_file.close()
            self.is_context_manager = False
        self.is_context_manager = False

    async def locked(self):
        return self.is_context_manager

    def __enter__(self):
        raise RuntimeError(
            "Use Lock like 'with (yield lock)', not like 'with lock'")

    __exit__ = __enter__

    async def __aenter__(self):
        res = await self.acquire()
        return res

    async def __aexit__(self, typ, value, tb):
        await self.release()


async def test_context_manager_async():
    lock = MyLockAsync('test.txt', 'r')

    async with lock as f:
        for line in f:
            print(line)

        res = await lock.locked()
        print(res)

    res = await lock.locked()
    print(res)


@coroutine
def start(ver):
    if ver == 1:
        yield test_context_manager1()
    elif ver == 2:
        yield test_context_manager2()
    elif ver == 3:
        yield test_context_manager3()
    else:
        yield test_context_manager_async()


if __name__ == '__main__':
    IOLoop.current().run_sync(partial(start, 1))
    # IOLoop.current().run_sync(partial(start, 2))
    # IOLoop.current().run_sync(partial(start, 3))
    # IOLoop.current().run_sync(partial(start, 4))


