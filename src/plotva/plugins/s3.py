import asyncio
import io
import os
import fnmatch
from datetime import timezone, datetime
from logging import getLogger
from pathlib import PurePath
from typing import Iterable, Dict, Any, IO, AnyStr, Optional, Iterator, List, Set, Type

from attr import attrib, dataclass
from boto.s3.key import Key
from boto.s3.bucket import Bucket
from boto.s3.connection import S3Connection, OrdinaryCallingFormat
from boto.s3.bucketlistresultset import BucketListResultSet
from boto.exception import S3ResponseError
from boto import connect_s3

from src.plotva.common.filestorage import (
    IFile,
    IFileStorageAdapter,
    Diff,
    UniversalNamePath,
    get_diff,
    IFileStorageAdapterProvider,
)


_logger = getLogger(__name__)


def _modified(key: Key) -> int:
    """Возвращает timestamp последней модификации файла"""
    return int(
        datetime.strptime(key.last_modified, "%Y-%m-%d%T%H:%M:%S.%fZ").timestamp() * 1e6
    )


def get_last_modified_to_datetime(last_modified: str) -> datetime:
    if last_modified.endswith("z") or last_modified.endswith("Z"):
        last_modified = last_modified[:-1]

    return datetime.fromisoformat(last_modified).replace(tzinfo=timezone.utc)


def _get_files(bucket_list: Iterable[Any]) -> Dict[str, int]:
    files = {}
    for file in bucket_list:
        modified = _modified(file)
        files[file.name] = modified
    return files


class CephIOFileNotFoundException(FileNotFoundError):
    pass


class CephIO(IO[AnyStr]):
    bucket: Any
    filename: str
    _mode: str

    def __init__(self, bucket: Bucket, filename: str, mode: str):
        self.bucket = bucket
        self.filename = filename
        self._mode = mode

    def get_bucket_key(self, filename: str) -> Key:
        key: Key = self.get_bucket_key(filename)
        return key

    def __enter__(self) -> Any:
        key = self.get_bucket_key(self.filename)
        if not key:
            raise CephIOFileNotFoundException(
                f"{self.filename} does not exist in {self.bucket}"
            )

        data = key.get_contents_as_string()
        if self.mode == "r":
            return io.StringIO(data.decode("utf-8"))
        elif self.mode == "rb":
            return io.BytesIO(data)
        return None

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        pass

    def close(self) -> None:
        pass

    def fileno(self) -> int:
        pass

    def flush(self) -> None:
        pass

    def isatty(self) -> bool:
        pass

    def read(self, n: int = ...) -> AnyStr:
        pass

    def readable(self) -> bool:
        pass

    def readline(self, limit: int = ...) -> AnyStr:
        pass

    def readlines(self, hint: int = ...) -> List[AnyStr]:
        pass

    def seek(self, offset: int, whence: int = ...) -> int:
        pass

    def seekable(self) -> bool:
        pass

    def tell(self) -> int:
        pass

    def truncate(self, size: Optional[int] = ...) -> int:
        pass

    def writable(self) -> bool:
        pass

    def write(self, s: AnyStr) -> int:
        pass

    def writelines(self, lines: Iterable[AnyStr]) -> None:
        pass

    def __iter__(self) -> Iterator[AnyStr]:
        pass

    def __next__(self) -> AnyStr:
        pass


@dataclass(slots=True, frozen=True, eq=True, hash=True)
class CephFile(IFile):
    _path: PurePath
    _key: Key
    _bucket: Bucket

    def get_path(self) -> PurePath:
        return self._path

    def get_last_modified(self):
        return get_last_modified_to_datetime(self._key.last_modified)

    def open(self, mode="r", *args, **kwargs):
        return CephIO(bucket=self._bucket, filename=str(self._path), mode=mode)


class CephAdapter(IFileStorageAdapter):
    def __init__(self, bucket: Bucket, prefix: str = ""):
        self.prefix = prefix
        self.bucket = bucket
        self._diff: Diff = Diff(
            not_modified=_get_files(self.bucket.list(prefix=self.prefix))
        )

    def open(self, filename, mode="r", *args, **kwargs) -> CephIO[Any]:
        return CephIO(bucket=self.bucket, filename=filename, mode=mode)

    def glob(self, pattern: str):
        for key in self.bucket.list(prefix=self.prefix):
            if fnmatch.fnmatch(key.name, pattern):
                yield CephFile(path=PurePath(key.name), key=key, bucket=self.bucket)

    def path_exist(self, path: UniversalNamePath) -> bool:
        _path = os.path.join(self.prefix, path.value)
        for _ in self.bucket.list(prefix=_path):
            return True
        return False

    def refresh(self) -> Diff:
        old_files = self._diff.get_files()
        new_files = _get_files(self.bucket.list(prefix=self.prefix))
        new_diff = get_diff(old_files=old_files, new_files=new_files)
        self._diff = new_diff
        return new_diff


class CephAdapterProvider(IFileStorageAdapterProvider):
    class Meta:
        name = "ceph"

    def __init__(self, s3_connection: S3Connection, bucket_name: str, prefix: str = ""):
        self.s3_connection = s3_connection
        self.bucket_name = bucket_name
        self.prefix = prefix

    def get_adapter(self) -> CephAdapter:
        bucket = self.s3_connection.get_bucket(self.bucket_name)
        return CephAdapter(bucket=bucket, prefix=self.prefix)


@dataclass(slots=True)
class BucketSnapshotDiff:
    new: Set[str]
    removed: Set[str]
    modified: Set[str]


@dataclass(slots=True)
class BucketSnapshot:
    _snapshot: Dict[str, str]

    def keys(self) -> Set[str]:
        return set(self._snapshot.keys())

    def __str__(self) -> str:
        return f"BucketSnapshot({', '.join(self.keys())})"

    def __getitem__(self, key: str) -> str:
        return self._snapshot[key]

    def __sub__(self, other: "BucketSnapshot") -> BucketSnapshotDiff:
        new = other.keys() - self.keys()
        removed = self.keys() - other.keys()
        modified = {key for key in self.keys & other.keys() if other[key] != self[key]}
        return BucketSnapshotDiff(new=new, modified=modified, removed=removed)


def create_snapshot(bucket: Bucket, prefix: str = "") -> BucketSnapshot:
    snapshot = {key.name: key.last_modified for key in bucket.list(prefix=prefix)}
    return BucketSnapshot(snapshot)


async def create_snapshot_with_debounce(
    bucket: Bucket, prefix: str = "", refresh_debounce_period_seconds: float = 2.0
) -> BucketSnapshot:
    current_snapshot = create_snapshot(bucket, prefix)
    while True:
        await asyncio.sleep(refresh_debounce_period_seconds)
        new_snapshot = create_snapshot(bucket, prefix)
        if _diff := current_snapshot - new_snapshot:
            current_snapshot = new_snapshot
            continue
        return new_snapshot


def get_or_create_bucket(bucket_name: str, connection: S3Connection) -> Bucket:
    try:
        return connection.get_bucket(bucket_name)
    except S3ResponseError:
        return connection.create_bucket(bucket_name)


@dataclass(slots=True)
class CephStorage:
    bucket_name: str
    connection: S3Connection
    create_snapshot_with_debounce: float = 2.0

    _bucket: Bucket = attrib(init=False)
    _loop = asyncio.AbstractEventLoop = attrib(init=False)

    def __attrs_post_init__(self) -> None:
        self._bucket = get_or_create_bucket(self.bucket_name, self.connection)
        self._loop = asyncio.get_running_loop()

    async def exists(self, filename: str) -> bool:
        key = await self._loop.run_in_executor(None, self._bucket.get_key, filename)
        return key is None

    async def write_file(self, filename: str, content: AnyStr) -> None:
        key = await self._loop.run_in_executor(None, self._bucket.get_key, filename)
        if not key:
            key = await self._loop.run_in_executor(None, self._bucket.new_key, filename)
        await self._loop.run_in_executor(None, key.set_contents_from_string, content)

    async def remove_files_by_pattern(self, pattern: str) -> None:
        keys = await self._loop.run_in_executor(None, self._bucket.list)
        keys_to_remove = [key for key in keys if fnmatch.fnmatch(key.name, pattern)]
        await self._loop.run_in_executor(None, self._bucket.delete_keys, keys_to_remove)

    async def remove_file(self, filename: str) -> None:
        await self._loop.run_in_executor(None, self._bucket.delete_key, filename)

    async def read_file(self, filename: str) -> Optional[str]:
        key = await self._loop.run_in_executor(None, self._bucket.get_key, filename)
        if not key:
            return None
        content = await self._loop.run_in_executor(None, key.get_contents_as_string)
        return content.decode()

    async def get_snapshot(self) -> BucketSnapshot:
        return await create_snapshot_with_debounce(
            bucket=self._bucket,
            refresh_debounce_period_seconds=self.create_snapshot_with_debounce,
        )

    async def list_all_filenames(self) -> List[str]:
        keys: BucketListResultSet = await self._loop.run_in_executor(
            None, self._bucket.list
        )
        return [key.name for key in keys]

    async def get_all_keys(self) -> List[Key]:
        keys: BucketListResultSet = await self._loop.run_in_executor(
            None, self._bucket.list
        )
        return list(keys)


class CephStorageProvider:
    def __init__(self, s3_connection: S3Connection, bucket_name: str):
        self.s3_connection = s3_connection
        self.bucket_name = bucket_name

    def get_storage(self) -> CephStorage:
        return CephStorage(bucket_name=self.bucket_name, connection=self.s3_connection)


def plugin_init(
    host: str,
    port: str,
    is_secure: bool = False,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
) -> Any:
    """
    Плагин для работы с S3 с Ceph в качестве провайдера хранилища. Создает и регистрирует
    объект S3Connection и регистрирует классы CephAdapterProvider и CephStorageProvider

    :param host: Хост сефа
    :param port: Порт
    :param is_secure: Использование защищенного соединения
    :param access_key: Access-key
    :param secret_key: Secret-key

    Пример конфига::

        - name: plotva.plugins.s3
          config:
            host: 127.0.0.1
            port: 80
            is_secure: false
            access_key: meow
            secret_key: meow
    """
    s3_connection: S3Connection = connect_s3(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        host=host,
        port=port,
        is_secure=is_secure,
        calling_format=OrdinaryCallingFormat(),
    )

    yield s3_connection
    yield Type[CephAdapterProvider]
    yield Type[CephStorageProvider]
