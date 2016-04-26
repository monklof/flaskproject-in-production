flaskproject-in-production
=====
FIP(Flaskproject-in-production)

## FIP是什么？

这是一个较小的Flask Demo，集成了一些在基于Flask开发部署Web应用时非常有用的功能，基于它，你可以快速开始写一个Flask应用并应用到生产环境下。

Flask本身是一个轻量级的Web框架，提供了Web请求处理的基本框架，能帮助开发者解决许多在HTTP请求处理层面上的许多问题。但在实际的工程中，我们往往需要做更多的工作来使得基于Flask的应用能够应用到生产环境下。譬如：

* 用户认证: 有些资源/页面访问时需要进行认证，而这个过程其实是比较通用的，能否把这个功能集成好呢？
* 程序配置管理: 线下开发和线上部署时程序往往要使用不同的配置（比如常见的情况就是线下开发需要指向线下数据库，而线上需要指向线上数据库），能否提供一种通用的配置方式呢？使得程序可以方便的进行配置切换？
* 生产环境下的部署: Flask自带的调试server是单线程的，一个请求阻塞后之后的请求都会被卡住，在生产环境下肯定不能使用这个server。通常我们会选择使用[Gunicorn][gunicorn]这样的服务器来作为生产环境下的并发方案，这个功能也可以集成起来。
* 日志文件管理: 在生产环境下，往往要记录程序的访问日志、出错日志、应用日志以方便进行问题定位。而Flask是没有提供这样的机制的，往往还需要开发者再去开发这样的功能。

我相信这些功能，是一个健康成熟的线上生产应用的通用需求。FIP将这些功能集成起来，以方便开发者开发时，不再需要再关注这些通用性的问题，而将关注点切换至更高层次上解决问题，提高开发效率。

## 功能特性

目前技术栈大体构成是：

1. [SQLAlchemy][sqla]: 用来作为关系型数据库的ORM。
2. [npm][npm] + [webpack][webpack]: 用来进行前端依赖管理和前端js资源打包
3. [gunicorn][gunicorn]: 一个以pre-fork worker模型作为并发策略的WSGI server，用来作为生产服务器。

### 用户认证

FIP集成了用户认证功能，实现上采用Flask插件[Flask-Login][f-login]作为认证管理工具。

具体功能包括： 用户登录、用户注册、用户认证。

[f-login]: https://flask-login.readthedocs.org/en/latest/

相关实现代码在`src/auth.py`中。

#### 用户认证

假设页面`/home`需要登录后的用户在才能访问，那么你可以这样使用，当用户未登录时，会自动跳转到登录页面`/login`中:

```python
from auth import flask_login
...

@app.route("/home")
@flask_login.login_required
def home():
    return render_template("home.html")
```

#### 用户登录与用户注册

FIP简单实现了一个用户登录和注册功能，你可以在`src/auth.py`中进行自定义。

* `/login`: 登录
* `/register`: 注册

### 多版本配置管理

FIP使用一个多版本配置工具[Swing][swing]来管理配置，在`src/settings.py`中，可以很方便的配置多个版本的配置。

* 在`DevleopmentConfig`类中配置开发环境的配置
* 在`ProductionConfig`中配置生产环境配置
* 通过`swing.config`的属性，能访问对应的配置项。
* 使用管理脚本`src/manage.py`的命令行参数便能很方便的控制程序运行在哪个配置上。这个会在后面说明。

```python
from swing import ConfigBase

class CommonConfig(ConfigBase):

    SECRET_KEY = "the secret key (you should change this!)"
    DEBUG = True
    DB_CONNECTION = "sqlite:///flask.db"
    # ... 

class DevelopmentConfig(CommonConfig):
    __confname__ = "dev"

class ProductionConfig(CommonConfig):
    __confname__ = "prod"
    DEBUG = False
    DB_CONNECTION = "sqlite:///flask.prod.db"
```

### 集成部署方案

内嵌[Gunicorn][gunicorn]的部署方案，[Gunicorn][gunicorn]使用pre-fork worker模型来作为并发策略。部署时，他会启动多个Worker进行来接收处理请求。使得服务能力远比Flask自带的调试服务器能力强。

### 集成日志管理

对Web请求访问日志、出错日志、程序出错日志都做了对应的集成，你只需要在`src/settings.py`中更改这些日志的位置，或者通过`bin/manage.py`启动应用时显示指定日志位置就可以将日志打到指定的位置。

### 其他特性

1. 支持静态文件链接带hash tag: 构建静态文件url时，会对文件进行hash处理，将tag加到url参数中，这样方便进行静态文件更新而无需手动更新文件hash tag。

## 快速开始

### 安装环境

```bash
$ git clone https://github.com/monklof/flaskproject-in-production.git
$ cd flaskproject-in-production
$ sudo pip install -r requirements.txt
```

### manage.py

`manage.py`是程序的命令行接口，提供了控制程序运行方式的功能。有两个子命令，

* `debug_server`: 启动一个Flask内置的调试服务器。
* `gunicorn_server`: 启动gunicorn_server

```bash
$ ./bin/manage.py debug_server
```

这样便会启动一个5000端口的Flask内嵌Server，运行在Debug模式，使用开发环境下的配置。访问 http://localhost:5000/ 便可以浏览一个简单支持登录注册权限验证的demo。

如果在生产环境下，需要更加健壮的并发策略时，可以这样使用:

```bash
$ ./bin/manage.py gunicorn_server accesslog=/path/to/accesslog/access.log errorlog=/path/to/errorlog 
```

这样，会默认启动2*N + 1个worker进程数来接收请求处理，N为CPU核数。使用gunicron_server会默认使用生产环境配置。

### 命令行参数

`manange.py`支持以下参数:

* `manange.py debug_server`

    * --config=${CONFIG}: 使用程序的哪个配置, 默认是dev
    * --host=${HOST}: server绑定在哪个IP上，默认是0.0.0.0
    * --port=${PORT}: server端口

* `manage.py gunicorn_server`

    * --config=${CONFIG}: 使用程序的哪个配置, 默认是prod
    * --host=${HOST}: server绑定在哪个IP上，默认是0.0.0.0
    * --port=${PORT}: server端口
    * --workers=${WORKERS}: 启动worker进程数，默认是2*N+1，N为CPU核心数。
    * --accesslog=${ACCESSLOG}: Web访问日志文件。
    * --errorlog=${ERRORLOG}: 出错日志

## 内部实现

### 目录结构

* `bin/manage.py`: 运行应用的命令接口。
* `package.json`: 前端框架依赖
* `requirements.txt`: Python依赖包
* `webpack.config.js`: 前端js打包的webpack配置
* `src/`: 主代码目录

    * `main.py`: 程序入口
    * `fe-src/js`: js源代码
    * `static/`: 静态文件
    * `templates/`: 模板
    * `auth.py`: 认证相关代码
    * `model.py`: 程序使用的一些数据库实体
    * `api.py`: 提供了一个用于演示的api接口
    * `settings.py`: 程序使用的配置
    * `utils/`: 使用的一些工具

## 参考

* [Swing][swing] by @monklof , 在此项目中用来进行配置管理。
* [docopt][docopt] by @ekayxu , 在此项目中用来进行命令行解析。

## 作者

* Monklof (monklof@gmail.com)
* ekayxu
* liyouyang

## License

MIT

[swing]: https://github.com/monklof/swing
[docopt]: https://github.com/ekayxu/docstring-option
[sqla]: http://sqlalchemy.org
[npm]: https://www.npmjs.com/
[webpack]: http://webpack.github.io
[gunicorn]: http://docs.gunicorn.org/en/stable/index.html


