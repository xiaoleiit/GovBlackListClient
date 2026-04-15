"""
生存人员比对客户端应用
用于批量处理ZJPV文件，调用生存认证接口比对，输出已故人员ZJPC文件
"""

import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.app import AliveCheckApp

def main():
    """主程序入口"""
    app = AliveCheckApp()
    app.run()

if __name__ == '__main__':
    main()