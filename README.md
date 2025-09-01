# QGIS Add Parity From All Fields

Универсальный PyQGIS скрипт для обработки векторных слоев .gpkg. Автоматически находит все целочисленные поля и создает для каждого соответствующее поле четности.

## Описание

Скрипт выполняет следующие операции:
- Загружает указанный векторный слой .gpkg
- Автоматически находит все поля с целочисленными типами данных
- Для каждого целочисленного поля создает новое поле `parity-{field_name}`
- Заполняет поля четности значениями:
  - `"even"` - для четных значений
  - `"odd"` - для нечетных значений
  - `NULL` - для некорректных значений

## Требования

- QGIS 3.x установленный на системе
- Python 3.x
- PyQt5

## Установка зависимостей

Для установки PyQt5 через Poetry:

```bash
poetry install
poetry add PyQt5
```

## Запуск скрипта

### Windows

1. Откройте OSGeo4W Shell (поставляется с QGIS)
2. Перейдите в директорию проекта:
   ```cmd
   cd C:\path\to\qgis-add-parity-from-fields
   ```
3. Запустите скрипт с указанием пути к файлу:
   ```cmd
   python src/add_parity_from_all_fields.py data/city.gpkg
   python src/add_parity_from_all_fields.py C:\path\to\your\layer.gpkg
   ```

### macOS

1. Откройте Terminal
2. Перейдите в директорию проекта:
   ```bash
   cd /path/to/qgis-add-parity-from-fields
   ```
3. Запустите скрипт через Python из QGIS:
   ```bash
   /Applications/QGIS-LTR.app/Contents/MacOS/bin/python3 src/add_parity_from_all_fields.py data/city.gpkg
   /Applications/QGIS-LTR.app/Contents/MacOS/bin/python3 src/add_parity_from_all_fields.py /path/to/your/layer.gpkg
   ```

### Linux (Ubuntu/Debian)

1. Откройте Terminal
2. Перейдите в директорию проекта:
   ```bash
   cd /path/to/qgis-add-parity-from-fields
   ```
3. Запустите скрипт:
   ```bash
   python3 src/add_parity_from_all_fields.py data/city.gpkg
   python3 src/add_parity_from_all_fields.py /path/to/your/layer.gpkg
   ```

Или если QGIS установлен в нестандартном месте:
```bash
/usr/bin/python3 src/add_parity_from_all_fields.py data/city.gpkg
```

### Справка по параметрам

Для получения справки по использованию:
```bash
python src/add_parity_from_all_fields.py --help
```

## Структура проекта

```
qgis-add-parity-from-fields/
├── data/
│   ├── city.gpkg          # Входной векторный слой
│   ├── lakes.gpkg
│   ├── rastr.tif
│   └── roads.gpkg
├── src/
│   ├── process_city_layer.py      # Старый скрипт (только для city.gpkg)
│   └── add_parity_from_all_fields.py  # Универсальный скрипт
├── pyproject.toml
├── poetry.lock
└── README.md
```

## Результат работы

После успешного выполнения скрипта:
- В указанном слое будут созданы новые поля `parity-{field_name}` для каждого целочисленного поля
- Поля будут заполнены значениями на основе четности соответствующих полей
- В консоли будет выведена информация о процессе обработки

### Пример результата

Для слоя с полями `fid` и `SCALERANK` будут созданы:
- `parity-fid` - четность значений поля fid
- `parity-SCALERANK` - четность значений поля SCALERANK

## Возможные ошибки

- **"Файл не найден"** - убедитесь, что указанный файл .gpkg существует
- **"В слое не найдено целочисленных полей"** - слой не содержит полей для обработки
- **"ModuleNotFoundError: No module named 'qgis'"** - убедитесь, что используете Python из QGIS
- **"usage: add_parity_from_all_fields.py [-h] layer_path"** - не указан путь к файлу