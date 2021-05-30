## 简介

![](images/usage.svg)

将单词批量生成为 Anki 卡片。

当前支持的词典：

- [剑桥词典](https://dictionary.cambridge.org/zhs/%E8%AF%8D%E5%85%B8/%E8%8B%B1%E8%AF%AD-%E6%B1%89%E8%AF%AD-%E7%AE%80%E4%BD%93/)

  ![](images/mac-preview.png)

## 使用环境

- [Python3](https://www.python.org/)

## 安装

### 方式一：通过 [pip](https://pip.pypa.io/en/stable/installing/) 安装

```sh
$ pip3 install dict2anki
```

### 方式二：下载源码

```sh
$ git clone https://github.com/qianbinbin/dict2anki.git && cd dict2anki
$ # 或者
$ git clone git@github.com:qianbinbin/dict2anki.git && cd dict2anki
$ # 或者
$ wget https://github.com/qianbinbin/dict2anki/archive/master.zip && unzip master.zip && cd dict2anki-master
```

## 使用

### 一、准备单词文件

以换行分隔，`#` 开头的行将被忽略，例如 `list.txt`:

```
abandon
abbreviate
abduct
abide
abide by sth
abject
abolish
abort
abortion
abound
# this line will be ignored
```

### 二、生成


```sh
$ # pip 方式
$ dict2anki -i /path/to/list.txt
$ # 源码方式
$ python3 -m dict2anki -i /path/to/list.txt
```

使用 `-i` 参数指定输入单词文件，默认生成在当前目录。

生成的卡片文件 `cards.txt` 是以追加形式写入的，如果单词被放在多个文件中，就可以多次运行脚本以输出到同一 `cards.txt`。

### 三、导入

#### 1. 新建模板

打开桌面版 Anki，`工具` -> `管理笔记模板` -> `添加` -> `问答题`，输入名称，例如 `单词模板`，选中 `单词模板`，点击右侧 `卡片`，

- 将 `front-template.txt` 中的内容复制到 `正面模板`，
- 将 `back-template.txt` 中的内容复制到 `背面模板`，
- 将 `styling.txt` 中的内容复制到 `样式`。

以上“复制”指完全替换，不是粘贴到原始内容后。

#### 2. 复制媒体文件

将 `collection.media` 文件夹中的内容（如果有的话），复制到 [Anki 文件夹](https://docs.ankiweb.net/files.html#file-locations) 对应用户的 `collection.media` 文件夹下。

#### 3. 导入卡片

创建所需牌组，例如 `单词牌组`。

`文件` -> `导入`，选择 `cards.txt`，`模板` 选择刚刚新建的笔记类型 `单词模板`，`牌组` 选择 `单词牌组`，勾选 `允许在字段中使用 HTML`，点击 `导入`。

### 四、还原为单词文件（类 Unix 系统）

要还原为 [第一步](#一准备单词文件) 中的单词文件，打开桌面版 Anki，`文件` -> `导出...`，导出格式选择 `纯文本格式的笔记`，牌组选择 `单词牌组`，取消勾选 `包含标签` 和 `包括 HTML 和引用的媒体`，并点击 `导出`，设置文件名，例如 `notes.txt`，并保存。

再使用以下命令将单词还原到 `out.txt` 中：

```sh
awk -F '\t' '{print $1}' notes.txt >out.txt
```

