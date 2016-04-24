flaskproject-in-production
=====

持续开发中，未经过单元测试，未最终发版，文档还在补充中。

## 这个项目是什么？

一个集成了很多有用的基础工具和功能的Flask Web应用框架，基于这个项目，你可以快速开始写一个Flask应用并应用到生产环境下。

Flask本身是一个轻量级的Web框架，提供了Web请求处理的基本框架，能帮助开发者解决许多在HTTP请求处理层面上的许多问题。但在实际的工程中，我们往往需要做更多的工作来使得基于Flask的应用能够应用到生产环境下。譬如：

* 用户认证: 有些请求是需要授权之后才能访问的。
* 数据库访问
* 程序配置管理: 线上部署和线下开发时程序往往要使用不同的配置。
* 多进程部署: Flask自带的调试server是单线的，一个请求阻塞后之后的请求都会被卡住，在生产环境下肯定不能使用这个server。
* 日志文件管理: 在生产环境下，往往要记录程序的访问日志、出错日志、应用日志以方便进行问题定位。
* 等等

我相信这些功能，是一个健康成熟的线上生产应用的通用需求，既然是个通用需求，那我们干脆整理一个比较合理的解决方案，把基础设施搭好（把工具集成，代码写好），并分享出来。那么之后我们再需要新起一个项目时，基于已有方案（代码）再来构建就能更加专注业务和架构了。才能更好更快的拿KPI （逃

（当然不是为了KPI :P, 如果关注低层次的问题花的时间多了，高层次的时间就少了。我们尽量完善基础设施，在较高的层次来解决技术问题。）


## 功能特性

如前所述，这个项目是为了给Flask 应用提供基础解决方案和基础工具。目前技术栈大体构成是：

1. [SQLAlchemy][sqla]: 用来作为关系型数据库的ORM。
2. [npm][npm] + [webpack][webpack]: 用来进行前端依赖管理和前端js资源打包
3. [gunicorn][gunicorn]: 一个以pre-fork worker模型作为并发策略的WSGI server，用来作为生产服务器。

目前此项目提供的功能支持有：

1. 支持用户认证: 提供了登录、注册、认证功能。
2. 支持静态文件链接带hash tag: 构建静态文件url时，会对文件进行hash处理，将tag加到url参数中，这样方便进行静态文件更新而无需手动更新文件hash tag。
3. 支持多版本配置切换: 提供方便的多版本配置定义方式，以及基于命令行的配置切换功能。
4. 支持pre-fork worker并发策略的服务端部署方式。
5. 集成日志管理: 提供了可以按照日期进行格式化文件日志记录的功能。

## 快速开始

```bash
$ git clone https://github.com/monklof/flaskproject-in-production.git
$ cd flaskproject-in-production
$ sudo pip install -r requirements.txt
$ ./bin/manage.py debug_server
```

这样便会启动一个5000端口的Flask内嵌Server，运行在Debug模式。访问 http://localhost:5000/ 便可以浏览一个简单支持登录注册权限验证的demo。

### 生产环境

如果在生产环境下，可以这样使用:

```bash
$ ./bin/manage.py gunicorn_server accesslog=/path/to/accesslog/access.log errorlog=/path/to/errorlog 
```

这样，会默认启动2*N + 1个worker进程数，N为CPU核数。

`manage.py`是程序的命令行接口，提供了控制程序运行方式的功能。有两个子命令，

* `debug_server`: 启动一个Flask内置的调试服务器。
* `gunicorn_server`: 启动gunicorn_server


### 命令行参数

`manange.py`支持以下参数:

* `manange.py debug_server`

    * --config=${CONFIG}: 使用程序的哪个配置, 默认是dev
    * --host=${HOST}: server绑定在哪个IP上，默认是0.0.0.0
    * --port=${PORT}: server端口

* `manage.py gunicorn_server`

    * --config=${CONFIG}: 使用程序的哪个配置, 默认是dev
    * --host=${HOST}: server绑定在哪个IP上，默认是0.0.0.0
    * --port=${PORT}: server端口
    * --workers=${WORKERS}: 启动worker进程数，默认是2*N+1，N为CPU核心数。
    * --accesslog=${ACCESSLOG}: Web访问日志文件。
    * --errorlog=${ERRORLOG}: 出错日志

## 内部实现

### 目录结构

* bin/manage.py: 命令行接口
* package.json: 前端框架依赖
* requirements.txt: Python依赖包
* webpack.config.js: 前端js打包的webpack配置
* src/: 主代码目录

    * main.py: 程序入口
    * fe-src/js: js源代码
    * static/: 静态文件
    * templates/: 模板
    * auth.py: 认证相关代码
    * model.py: 程序使用的一些数据库实体
    * api.py: 提供了一个用于演示的api接口
    * settings.py: 程序使用的配置
    * utils/: 使用的一些工具

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


