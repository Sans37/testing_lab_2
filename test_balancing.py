import requests
import time
from collections import Counter

BASE_URL = "http://localhost"


def test_load_balancing():
    """Тестирование балансировки нагрузки"""
    instances = Counter()
    errors = []

    print("🧪 Тестирование балансировки GET запросов (2:1:1)...")

    # 100 GET запросов
    for i in range(100):
        try:
            response = requests.get(f"{BASE_URL}/instance-info")
            if response.status_code == 200:
                instance = response.json().get("instance", "unknown")
                instances[instance] += 1
            else:
                errors.append(f"GET {i}: {response.status_code}")
        except Exception as e:
            errors.append(f"GET {i}: {str(e)}")

        time.sleep(0.01)

    print("\n📊 Распределение GET запросов:")
    for instance, count in instances.items():
        percentage = (count / 100) * 100
        print(f"  {instance}: {count} запросов ({percentage:.1f}%)")

    # Тестирование записи (только master)
    print("\n🧪 Тестирование POST запросов (только master)...")
    write_instances = Counter()

    for i in range(10):
        try:
            response = requests.post(f"{BASE_URL}/api/v2/test-write")
            if response.status_code == 200:
                instance = response.json().get("instance", "unknown")
                write_instances[instance] += 1
            elif response.status_code == 403:
                print(f"✅ POST {i}: Correctly rejected (read-only instance)")
            else:
                errors.append(f"POST {i}: {response.status_code}")
        except Exception as e:
            errors.append(f"POST {i}: {str(e)}")

    print("\n📊 Распределение POST запросов:")
    for instance, count in write_instances.items():
        print(f"  {instance}: {count} запросов")

    # Тестирование mirror
    print("\n🧪 Тестирование mirror приложения...")
    try:
        response = requests.get(f"{BASE_URL}/mirror/instance-info")
        if response.status_code == 200:
            instance = response.json().get("instance", "unknown")
            print(f"✅ Mirror instance: {instance}")
        else:
            errors.append(f"Mirror: {response.status_code}")
    except Exception as e:
        errors.append(f"Mirror: {str(e)}")

    # Вывод ошибок
    if errors:
        print(f"\n❌ Ошибки ({len(errors)}):")
        for error in errors[:5]:
            print(f"  {error}")
        if len(errors) > 5:
            print(f"  ... и еще {len(errors) - 5} ошибок")

    print(f"\n{'=' * 50}")
    print("Ожидаемое распределение GET: master ~50%, replica-1 ~25%, replica-2 ~25%")
    print("Ожидаемое распределение POST: master 100%")
    print("Mirror: всегда api-mirror")


if __name__ == "__main__":
    test_load_balancing()