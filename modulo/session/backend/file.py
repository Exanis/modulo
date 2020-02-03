try:
    import aiofiles
except ImportError:
    raise ImportError("File session backend requires aiofiles library")
from os.path import join, isfile
from json import loads, dumps
from .abstract import Abstract


class File(Abstract):
    _session_path = None

    @staticmethod
    def get_path() -> str:
        if File._session_path is None:
            from modulo.conf import settings

            File._session_path = settings.SESSION_OPTIONS['folder']
        return File._session_path

    async def load(self: File) -> None:
        path = join(File.get_path(), self._key)
        if isfile(path):
            async with aiofiles.open(path, mode='r') as f:
                content = await f.read()
                self._data = loads(content)
    
    async def save(self: File) -> None:
        path = join(File.get_path(), self._key)
        async with aiofiles.open(path, mode='w+') as f:
            await f.write(dumps(self._values))
