# 政务局黑名单信息对比客户端
## 项目结构

```
alive-check-client/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖列表
├── src/
│   ├── core/               # 核心模块
│   │   ├── api_client.py   # 接口调用客户端
│   │   ├── config_manager.py # 配置管理
│   │   ├── crypto.py       # SM3/SM4加密
│   │   ├── file_parser.py  # ZJPV/ZJPC解析
│   │   └── processor.py    # 批量处理
│   ├── gui/                # GUI界面
│   │   ├── app.py          # 主窗口
│   │   ├── config_panel.py # 配置面板
│   │   ├── process_panel.py # 处理面板
│   │   └── result_dialog.py # 结果对话框
│   └── utils/
│       └── logger.py       # 日志记录
└── README.md
```

## 功能特性

- 配置管理：支持保存接口配置（`appId`、`appSecret`、接口地址、保存目录）
- 批量处理：自动遍历文件夹中所有 ZJPV 文件
- 进度显示：实时显示处理进度、已处理人数、已故人数
- 结果输出：自动生成符合规范的 ZJPC 文件
- 国密加密：SM3 签名 + SM4 加密
- 跨平台：支持 Windows、macOS、Linux

## 运行要求

- Python 3.9+
- 已启动生存认证模拟服务端（Spring Boot）

## 安装依赖

```bash
python3 -m pip install -r requirements.txt
```

## 运行应用

```bash
cd alive-check-client
python3 main.py
```

## 使用流程

### Step 1: 配置页面

填写接口配置信息：
- 应用 ID（`appId`）
- 应用密钥（`appSecret`）
- Token接口地址
- 比对接口地址
- 保存目录

点击"测试连接"验证配置是否正确，点击"下一步"进入处理页面。

### Step 2: 处理页面

选择待校验文件夹（包含ZJPV文件），点击"开始比对"。

进度显示：
- 进度条
- 当前文件名
- 已处理人数
- 已故人数
- 实时日志

### Step 3: 结果提示

比对完成后显示友好提示：
- 总处理人数
- 已故人员数量
- 输出文件位置

点击"查看文件"可直接打开文件夹。

## 文件格式

### 输入文件 (ZJPV)

```
文件名: ZJPV + YYYYMMDD + 序号(10位)
示例: ZJPV202604140000000001
内容:
  第1行: 文件标识
  第2行: 记录数标识
  第3行+: 姓名 + 空格 + 身份证号
```

### 输出文件 (ZJPC) - 仅已故人员

```
文件名: ZJPC + YYYYMMDD + 序号(10位)
内容:
  第1行: 文件标识
  第2行: 记录数标识
  第3行+: 姓名 + 空格 + 身份证号
```

## 打包发布

使用PyInstaller打包为独立应用：

```bash
# Windows
pyinstaller --onefile --windowed main.py

# macOS
pyinstaller --onefile --windowed --osx-bundle-identifier com.example.alivecheck main.py

# Linux
pyinstaller --onefile main.py
```

## 配置文件

配置保存在用户目录：`~/.alive-check/config.json`

```json
{
    "appId": "APP001",
    "appSecret": "secret001abcdef",
    "tokenUrl": "http://localhost:8080/openapi/stoken",
    "compareUrl": "http://localhost:8080/openapi/aliveCompare",
    "saveDir": "/Users/xxx/Documents/生存比对结果"
}
```

---

## 对接真实接口注意事项

本客户端是基于模拟后端开发测试的，对接真实的生存认证库接口时，需要注意以下关键点：

### 1. 加密算法兼容性 ⚠️ 重要

不同国密库的实现可能存在差异，对接时需要重点验证：

#### SM4密钥处理
- **密钥长度**：SM4要求128位（16字节）密钥
- **填充方式**：不同库对短密钥的处理不同
  - 本实现：不足16字节时末尾补0
  - 其他实现：可能使用不同的填充算法或直接报错
- **验证方法**：用相同密钥加密同一明文，对比密文是否一致

#### SM4加密输出格式
- **Hex格式**：十六进制字符串（如 `d20152c586d2...`）
- **Base64格式**：Base64编码（如 `0gFSxYbS9SiO...`）
- 本实现支持两种格式的**加密输出**和**解密输入**
- 真实接口可能只支持其中一种，需要确认文档要求

#### PKCS7填充
- 加密时需要PKCS7填充，解密时需要正确去填充
- gmssl库的`crypt_ecb`函数返回bytes时已自动处理填充，但如果返回list需要手动处理
- 真实接口可能使用不同的填充策略（PKCS5/PKCS7/ZeroPadding）

### 2. 签名规则验证

签名规则需要严格匹配：
```
签名数据 = appSecret + encryptData
签名结果 = SM3(签名数据)
```

需要注意：
- `encryptData`是加密后的密文（Hex或Base64字符串）
- 签名结果通常是Hex格式
- 真实接口可能使用不同的签名规则（如加入timestamp、appId等）

### 3. 接口响应格式

真实接口的响应可能存在差异：
- **成功标识**：`respCode`为0表示成功，其他值表示失败
- **错误信息**：`respMsg`可能包含详细错误描述
- **加密数据**：响应的`encryptData`格式需要与解密函数匹配

### 4. 验证步骤

对接真实接口时的建议验证顺序：

1. **单独测试加密解密**
   ```python
   # 使用真实接口提供的密钥加密明文
   # 与真实接口返回的密文对比验证
   
   plain = '{"appId":"xxx","appSecret":"xxx"}'
   encrypted = encrypt_data(plain, app_secret)
   # 发送到真实接口，观察是否通过签名验证
   ```

2. **单独测试签名**
   ```python
   # 验证签名算法是否一致
   sign = sign_data(app_secret, encrypt_data)
   # 与真实接口期望的签名对比
   ```

3. **测试Token获取**
   ```python
   # 获取Token后解密验证内容是否正确
   token_response = client.generate_token()
   print(token_response)  # 检查返回内容
   ```

4. **测试生存比对**
   ```python
   # 用少量测试数据验证比对流程
   results = client.alive_compare([{"idcard": "test", "username": "test"}])
   # 检查返回格式是否符合预期
   ```



### 5. `crypto.py` 需要修改的位置

如果真实接口与本实现不兼容，可能需要修改：

```python
# src/core/crypto.py

# 1. 加密输出格式（第40-45行）
if output_format == 'base64':
    return base64.b64encode(cipher_bytes).decode('utf-8')
else:
    return cipher_bytes.hex()

# 2. 密钥填充方式（第20-30行）
key_list = func.bytes_to_list(key_bytes[:16])
while len(key_list) < 16:
    key_list.append(0)  # 改为其他填充方式

# 3. 签名规则（第85-90行）
sign_data = app_secret + encrypt_data  # 可能需要加入其他参数
```

---




