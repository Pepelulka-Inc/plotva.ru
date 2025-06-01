import asyncio
from src.plotva.plugins.s3 import plugin_init, get_or_create_bucket
from src.plotva.plugins.s3 import CephStorageProvider


async def test_ceph_operations():
    """Тестовая функция для проверки всех операций с Ceph хранилищем"""
    print("🚀 Начинаем тестирование Ceph хранилища...")

    # Тестовые параметры (замените на свои)
    TEST_BUCKET = "plotva"
    TEST_FILE = "test.txt"
    TEST_CONTENT = "meow meow meow"

    # Конфигурация Ceph
    ENDPOINT_URL = "https://s3.ru-7.storage.selcloud.ru "  # Удалены лишние пробелы
    ACCESS_KEY = "ef4a9dcfc2b04d9f95fe7c4b43dfe356"
    SECRET_KEY = "52e2ff3ef0c547f1966be1b57978c0cd"

    try:
        # 1. Инициализируем подключение
        print("🔌 Инициализируем подключение...")
        init_gen = plugin_init(
            endpoint_url=ENDPOINT_URL,
            is_secure=True,  # Установлено в True для HTTPS
            access_key=ACCESS_KEY,
            secret_key=SECRET_KEY,
        )

        s3_client = next(init_gen)  # Получаем клиент
        next(init_gen)  # Пропускаем Type[CephAdapterProvider]
        next(init_gen)  # Пропускаем Type[CephStorageProvider]

        # 2. Создаем/получаем бакет
        print(f"📂 Создаем/получаем бакет {TEST_BUCKET}...")
        get_or_create_bucket(s3_client, TEST_BUCKET)  # Убедитесь, что

        # 3. Создаем провайдер хранилища
        storage_provider = CephStorageProvider(s3_client, TEST_BUCKET)
        storage = storage_provider.get_storage()

        # 4. Проверяем начальное состояние
        print("🔍 Проверяем начальное состояние...")
        exists_before = await storage.exists(TEST_FILE)
        print(f"Файл {TEST_FILE} существует до теста: {exists_before}")

        # 5. Записываем файл
        print(f"💾 Записываем файл {TEST_FILE}...")
        await storage.write_file(TEST_FILE, TEST_CONTENT)

        # 6. Проверяем существование после записи
        exists_after = await storage.exists(TEST_FILE)
        print(f"Файл {TEST_FILE} существует после записи: {exists_after}")

        # 7. Читаем файл
        content = await storage.read_file(TEST_FILE)
        print(f"Полученный контент: {content}")
        assert content == TEST_CONTENT, "❌ Контент не совпадает с ожидаемым"
        print("✅ Контент успешно совпадает")

        # 8. Проверяем список файлов
        files = await storage.list_all_filenames()
        print(f"Список файлов в бакете: {files}")
        assert TEST_FILE in files, "❌ Файл не найден в списке файлов"

        # 9. Тестируем снимок
        print("📸 Создаем снимок состояния бакета...")
        snapshot = await storage.get_snapshot()
        print(f"Снимок содержит {len(snapshot._snapshot)} объектов")

        # 10. Удаляем тестовый файл
        print(f"🗑️ Удаляем тестовый файл {TEST_FILE}...")
        await storage.remove_file(TEST_FILE)

        # 11. Проверяем удаление
        exists_after_delete = await storage.exists(TEST_FILE)
        print(f"Файл {TEST_FILE} существует после удаления: {exists_after_delete}")
        assert not exists_after_delete, "❌ Файл не удален"

        print("🎉 Все тесты успешно пройдены!")

    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(test_ceph_operations())
