Fyyur
-----

## 项目简介
Fyyur是一个音乐场馆和音乐人预订网站，有助于发现和预订当地音乐场馆和音乐人之间的表演。此网站允许您查看并发现新的音乐场馆和音乐人，并以音乐人的身份列出作为某音乐场馆的节目。


## 概述

在此应用程序中定义了视图、控制器、模型和模型交互，使用PostgreSQL 数据库检索和更新数据。其具体功能如下：

* 创建新的音乐场馆、音乐人和演出show。
* 搜索音乐场馆和音乐人。
* 了解有关特定音乐人或音乐场馆的详细信息。

希望Fyyur成为音乐场馆和音乐人可以用来寻找彼此并合作新演出的一个新平台。

## 技术栈

### 1. 后端
 * 使用 **virtualenv** 作为创建独立Python虚拟环境的工具
 * 使用 **SQLAlchemy ORM** 作为ORM库
 * 使用 **PostgreSQL** 作为数据库
 * 使用基于**Python3**语言的**Flask**作为服务器框架
 * 使用 **Flask-Migrate** 创建和运行数据库架构迁移

### 2. 前端
 * 使用基于**HTML**、**CSS** 和 **Javascript**和Javascript的[Bootstrap3]框架用于搭建网站前端
 

## 主要文件与项目结构

  ```sh
  ├── README.md
  ├── app.py *** the main driver of the app. Includes your SQLAlchemy models.
                    "python app.py" to run after installing dependencies
  ├── config.py *** Database URLs, CSRF generation, etc
  ├── error.log
  ├── forms.py *** Your forms
  ├── requirements.txt *** The dependencies we need to install with "pip3 install -r requirements.txt"
  ├── static
  │   ├── css 
  │   ├── font
  │   ├── ico
  │   ├── img
  │   └── js
  └── templates
      ├── errors
      ├── forms
      ├── layouts
      └── pages
  ```

MVC架构：
* Models在文件 `models.py` 中.
* Controllers 在文件 `app.py` 中.
* Web前端动态资源位于 `templates/` ,静态资源位于 `static/`文件夹.
* 用于创建数据的 Web 表单位于 `form.py`文件夹.


## 关于表单
起始代码使用名为 [Flask-WTF](https://flask-wtf.readthedocs.io/) 的交互式表单构建器库，这个库可以提供表单验证和错误处理等功能。为了管理 Flask-WTF 表单的请求，表单中的每个字段都有一个 `data` 属性，其中包含来自用户输入的值。比如；要处理“场地”表单中的venue_id数据，使用：`show = Show(venue_id=form.venue_id.data)`, 而不使用 `request.form['venue_id']`


## 项目开发运行配置
1. **初始化一个虚拟环境:**
```
python -m virtualenv env
source env/Scripts/activate
```
>**Note：** - IOS和Linux系统中使用这个指令：
```
source env/bin/activate
```

2. **安装项目依赖的库:**
```
pip install -r requirements.txt
```
3. **安装前端bootstrap需要的软件**
安装[Node.js](https://nodejs.org/en/download/). Windows用户安装完需要重启电脑。在命令行运行下列代码验证是否安装成功
```
node -v
npm -v
```
安装 [Bootstrap 3](https://getbootstrap.com/docs/3.3/getting-started/):
```
npm init -y
npm install bootstrap@3
```

4. **运行服务器**
```
export FLASK_APP=myapp
export FLASK_ENV=development # enables debug mode
python3 app.py
```

5. **在浏览器上验证**<br>
导航到项目主页 [http://127.0.0.1:5000/](http://127.0.0.1:5000/) 

