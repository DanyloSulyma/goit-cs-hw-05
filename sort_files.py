import argparse
import asyncio
import logging
import shutil
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

async def copy_file(file_path: Path, output_folder: Path):
    """
    Асинхронно копіює файл у підпапку на основі його розширення.
    """
    try:
        ext = file_path.suffix.lstrip('.')
        if not ext:
            ext = 'no_extension'
        
        target_dir = output_folder / ext
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = target_dir / file_path.name
        
        await asyncio.to_thread(shutil.copy2, file_path, target_path)
        logging.info(f"Скопійовано: {file_path.name} -> {target_dir}")
        
    except Exception as e:
        logging.error(f"Помилка при копіюванні файлу {file_path}: {e}")

async def read_folder(source_folder: Path, output_folder: Path):
    """
    Рекурсивно читає всі файли у вихідній папці та планує їх копіювання.
    """
    try:
        tasks = []
        for item in source_folder.iterdir():
            if item.is_dir():
                tasks.append(read_folder(item, output_folder))
            elif item.is_file():
                tasks.append(copy_file(item, output_folder))
        
        if tasks:
            await asyncio.gather(*tasks)
            
    except Exception as e:
        logging.error(f"Помилка при читанні папки {source_folder}: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Асинхронне сортування файлів за розширенням.")
    parser.add_argument("-s", "--source", type=str, required=True, help="Шлях до вихідної папки (source folder)")
    parser.add_argument("-o", "--output", type=str, default="sorted_files", help="Шлях до цільової папки (output folder)")
    
    args = parser.parse_args()
    
    source = Path(args.source)
    output = Path(args.output)
    
    if not source.exists() or not source.is_dir():
        logging.error(f"Вихідна папка '{source}' не існує або не є директорією.")
        return
    
    logging.info(f"Початок сортування з '{source}' в '{output}'")
    await read_folder(source, output)
    logging.info("Сортування завершено.")

if __name__ == "__main__":
    asyncio.run(main())