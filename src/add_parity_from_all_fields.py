import os

os.environ['PROJ_LIB'] = '/Applications/QGIS-LTR.app/Contents/Resources/proj'

import sys
import argparse
from typing import Optional
from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFeature,
    QgsApplication,
)

from PyQt5.QtCore import QVariant


def get_integer_fields(layer: QgsVectorLayer) -> list[str]:
    """
    Возвращает список полей с целочисленными типами данных

    Args:
        layer: Векторный слой

    Returns:
        Список имен целочисленных полей
    """
    integer_fields = []
    fields = layer.fields()

    for field in fields:
        # Проверяем тип поля на целочисленные типы
        if field.type() in [
            QVariant.Int,
            QVariant.UInt,
            QVariant.LongLong,
            QVariant.ULongLong,
        ]:
            integer_fields.append(field.name())

    return integer_fields


def load_layer(layer_path: str) -> Optional[QgsVectorLayer]:
    """
    Загружает векторный слой из файла

    Args:
        layer_path: Путь к файлу .gpkg

    Returns:
        Загруженный слой или None в случае ошибки
    """
    # Проверяем существование файла
    if not os.path.exists(layer_path):
        print(f"Ошибка: Файл {layer_path} не найден!")
        return None

    # Получаем имя файла без пути для отображения
    layer_name = os.path.splitext(os.path.basename(layer_path))[0]

    # Загружаем векторный слой
    layer = QgsVectorLayer(layer_path, layer_name, "ogr")

    # Проверяем, что слой загружен корректно
    if not layer.isValid():
        print(f"Ошибка: Не удалось загрузить слой {layer_path}")
        return None

    return layer


def print_layer_info(layer: QgsVectorLayer, integer_fields: list[str]) -> None:
    """
    Выводит информацию о слое

    Args:
        layer: Векторный слой
        integer_fields: Список целочисленных полей
    """
    print(f"Слой загружен успешно: {layer.name()}")
    print(f"Количество объектов: {layer.featureCount()}")

    # Получаем список всех полей
    fields = layer.fields()
    field_names = [field.name() for field in fields]
    print(f"Все поля в слое: {field_names}")
    print(f"Целочисленные поля: {integer_fields}")


def create_parity_fields(
    layer: QgsVectorLayer, integer_fields: list[str]
) -> tuple[dict[str, int], dict[str, int]]:
    """
    Создает поля parity для каждого целочисленного поля

    Args:
        layer: Векторный слой
        integer_fields: Список целочисленных полей

    Returns:
        Кортеж (field_indices, parity_indices) - словари с индексами полей
    """
    field_indices = {}
    parity_indices = {}

    # Создаем поля parity для каждого целочисленного поля
    for field_name in integer_fields:
        parity_field_name = f"parity-{field_name}"

        # Получаем индекс исходного поля
        field_indices[field_name] = layer.fields().indexFromName(field_name)

        # Проверяем, существует ли поле parity
        parity_idx = layer.fields().indexFromName(parity_field_name)

        if parity_idx == -1:
            print(f"Создаем новое поле '{parity_field_name}'...")
            parity_field = QgsField(parity_field_name, QVariant.String, len=10)
            layer.dataProvider().addAttributes([parity_field])
            layer.updateFields()
            parity_idx = layer.fields().indexFromName(parity_field_name)
            print(f"Поле '{parity_field_name}' создано успешно")
        else:
            print(f"Поле '{parity_field_name}' уже существует, будет перезаписано")

        parity_indices[field_name] = parity_idx

    return field_indices, parity_indices


def calculate_parity(value) -> Optional[str]:
    """
    Вычисляет четность числа

    Args:
        value: Значение для проверки

    Returns:
        "even", "odd" или None для некорректных значений
    """
    if value is None:
        return None

    try:
        # Преобразуем в целое число
        int_value = int(value)

        # Определяем четность
        return "even" if int_value % 2 == 0 else "odd"

    except (ValueError, TypeError):
        return None


def process_feature(
    feature: QgsFeature,
    field_indices: dict[str, int],
    parity_indices: dict[str, int],
    integer_fields: list[str],
    layer: QgsVectorLayer,
) -> bool:
    """
    Обрабатывает один объект слоя

    Args:
        feature: Объект слоя
        field_indices: Индексы исходных полей
        parity_indices: Индексы полей parity
        integer_fields: Список целочисленных полей
        layer: Векторный слой

    Returns:
        True если объект был обновлен
    """
    feature_updated = False

    # Обрабатываем каждое целочисленное поле
    for field_name in integer_fields:
        field_idx = field_indices[field_name]
        parity_idx = parity_indices[field_name]

        # Получаем значение поля
        field_value = feature[field_idx]

        # Вычисляем четность
        parity_value = calculate_parity(field_value)

        if parity_value is not None:
            # Обновляем значение в поле parity
            layer.changeAttributeValue(feature.id(), parity_idx, parity_value)
            feature_updated = True

            print(
                f"Объект ID {feature.id()}: {field_name}={int(field_value)}, parity-{field_name}={parity_value}"
            )
        else:
            # Устанавливаем NULL для некорректных значений
            layer.changeAttributeValue(feature.id(), parity_idx, None)

            if field_value is None:
                print(
                    f"Предупреждение: Значение поля '{field_name}' равно NULL для объекта ID {feature.id()}"
                )
            else:
                print(
                    f"Предупреждение: Не удалось преобразовать значение '{field_value}' поля '{field_name}' в число для объекта ID {feature.id()}"
                )

    return feature_updated


def process_all_features(
    layer: QgsVectorLayer,
    field_indices: dict[str, int],
    parity_indices: dict[str, int],
    integer_fields: list[str],
) -> int:
    """
    Обрабатывает все объекты в слое

    Args:
        layer: Векторный слой
        field_indices: Индексы исходных полей
        parity_indices: Индексы полей parity
        integer_fields: Список целочисленных полей

    Returns:
        Количество обновленных объектов
    """
    features = layer.getFeatures()
    total_updated = 0

    for feature in features:
        if process_feature(
            feature, field_indices, parity_indices, integer_fields, layer
        ):
            total_updated += 1

    return total_updated


def save_changes(
    layer: QgsVectorLayer, total_updated: int, integer_fields_count: int
) -> bool:
    """
    Сохраняет изменения в слое

    Args:
        layer: Векторный слой
        total_updated: Количество обновленных объектов
        integer_fields_count: Количество созданных полей parity

    Returns:
        True если сохранение прошло успешно
    """
    if layer.commitChanges():
        print(f"Изменения сохранены успешно! Обработано объектов: {total_updated}")
        print(f"Создано полей parity: {integer_fields_count}")
        return True
    else:
        print("Ошибка при сохранении изменений:")
        for error in layer.commitErrors():
            print(f"  - {error}")
        return False


def process_vector_layer(layer_path: str) -> bool:
    """
    Основная функция для обработки векторного слоя
    Создает поля parity для всех целочисленных полей

    Args:
        layer_path: Путь к файлу .gpkg

    Returns:
        True если обработка прошла успешно, False в случае ошибки
    """
    # Загружаем слой
    layer = load_layer(layer_path)
    if layer is None:
        return False

    # Находим все целочисленные поля
    integer_fields = get_integer_fields(layer)

    # Выводим информацию о слое
    print_layer_info(layer, integer_fields)

    if not integer_fields:
        print("Предупреждение: В слое не найдено целочисленных полей для обработки!")
        return True

    # Начинаем редактирование слоя
    layer.startEditing()

    try:
        # Создаем поля parity
        field_indices, parity_indices = create_parity_fields(layer, integer_fields)

        # Обрабатываем все объекты
        total_updated = process_all_features(
            layer, field_indices, parity_indices, integer_fields
        )

        # Сохраняем изменения
        return save_changes(layer, total_updated, len(integer_fields))

    except Exception as e:
        print(f"Ошибка при обработке слоя: {str(e)}")
        layer.rollBack()
        return False


def main() -> None:
    """
    Главная функция для запуска скрипта
    """
    qgs = QgsApplication([], False)
    qgs.initQgis()

    try:
        parser = argparse.ArgumentParser(
            description="Добавляет поля parity для всех целочисленных полей в векторном слое",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Примеры использования:
  python add_parity_from_all_fields.py data/city.gpkg
  python add_parity_from_all_fields.py /path/to/your/layer.gpkg
            """,
        )

        parser.add_argument("layer_path", help="Путь к файлу .gpkg для обработки")

        args = parser.parse_args()

        print("=== Обработка векторного слоя ===")
        print(f"Файл: {args.layer_path}")
        print(
            "Создание полей 'parity-{field_name}' на основе четности значений всех целочисленных полей"
        )
        print()

        success = process_vector_layer(args.layer_path)

        if success:
            print("\n=== Обработка завершена успешно! ===")
        else:
            print("\n=== Обработка завершена с ошибками! ===")
            sys.exit(1)

    finally:
        qgs.exitQgis()


# Запуск скрипта
if __name__ == "__main__":
    main()
