## 简介

将单词批量转换为 Anki 卡片，数据来源：

- [剑桥词典](https://dictionary.cambridge.org/zhs/%E8%AF%8D%E5%85%B8/%E8%8B%B1%E8%AF%AD-%E6%B1%89%E8%AF%AD-%E7%AE%80%E4%BD%93/)

  macOS 端预览：

   <img src="https://raw.githubusercontent.com/qianbinbin/dict2anki/master/images/mac-preview.png" width = "500" align=center />

  手机端预览：

   <img src="https://raw.githubusercontent.com/qianbinbin/dict2anki/master/images/mobile-preview.png" width = "300" align=center />

## 使用环境

- [Python3](https://www.python.org/)

## 使用方法

### 一、准备单词文件

以换行分隔，`#`开头的行将被忽略，例如`vocabulary.txt`:

```
dread
dreadful
handicap
competitor
competition
competitive
competitiveness
adhere to sth
fulfill
# account
# list
in terms of
reflect on
abbreviate
cater for sb/sth
```

### 二、运行脚本

#### 方式一：通过 [pip](https://pip.pypa.io/en/stable/installing/) 安装

```sh
$ pip3 install dict2anki
$ dict2anki -i /path/to/vocabulary.txt
```

#### 方式二：下载源码

```sh
$ git clone https://github.com/qianbinbin/dict2anki.git && cd dict2anki
$ # git clone git@github.com:qianbinbin/dict2anki.git && cd dict2anki
$ # wget https://github.com/qianbinbin/dict2anki/archive/master.zip && unzip master.zip && cd dict2anki-master
$ python3 -m dict2anki -i /path/to/vocabulary.txt
```

使用 `-i` 参数指定输入单词文件。

默认在当前目录下生成。

`cards.txt` 以追加形式增加内容，可以多次运行脚本以便输入到同一 `cards.txt` 文件。

### 三、导入

#### 1. 新建模板

打开桌面版 Anki，`工具` -> `管理笔记类型` -> `添加` -> `基础`，输入名称，例如 `基础单词`，选中 `基础单词`，点击右侧 `卡片`，

- 将 `front_template.txt` 中的内容复制到 `正面模板`，
- 将 `styling.txt` 中的内容复制到 `格式刷`，
- 将 `back_template.txt` 中的内容复制到 `背面模板`，

以上“复制”指完全替换，不是粘贴到原始内容后。

#### 2. 复制媒体文件

将 `collection.media` 文件夹中的文件全部复制到 [Anki 文件夹](https://docs.ankiweb.net/files.html#file-locations) 对应用户的 `collection.media` 文件夹下。

#### 3. 导入卡片

创建所需记忆库，例如 `英语单词`。

`文件` -> `导入`，选择 `cards.txt`，`类型` 选择刚刚新建的笔记类型 `基础单词`，`牌组` 选择 `英语单词`，勾选 `允许在字段中使用 HTML`，点击 `导入`。

### 四、导出（macOS、Linux 等类 Unix 系统）

要还原为[第一步](#一准备单词文件)中的单词文件，打开桌面版 Anki，`文件` -> `导出...`，导出格式选择 `纯文本格式的笔记`，牌组选择 `英语单词`，取消勾选 `包含标签` 和 `包括HTML和引用的媒体`，并点击`导出`。

假设导出文件名为 `notes.txt`，使用以下命令：

```sh
awk -F '\t' '{print $1}' notes.txt >out.txt
```

此时单词已经还原到 `out.txt` 中。
