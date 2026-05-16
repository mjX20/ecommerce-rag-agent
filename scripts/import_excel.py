import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_loader import DataLoader

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法：python scripts/import_excel.py <excel文件路径> <输出json文件路径>")
        print("示例：python scripts/import_excel.py data/my_products.xlsx data/my_products.json")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    json_path = sys.argv[2]
    
    DataLoader.excel_to_json(excel_path, json_path)