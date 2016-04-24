#coding=utf-8
"""
TODO:
	* 命令帮助文本生成
	* 检查__doc__和函数参数两种声明的一致性
	* 运行命令processor前，转换参数至声明时所指定的类型 (removed)
	* 命令行中，同参数重复赋值的处理
	* 子命令可接受无前缀赋值 (done. using FREE_MODE)
	* entry函数为子命令提供环境变量env
	* processor更名
	* 多次赋值
	* 从processor函数参数列表获得选项信息，无需定义__doc__
"""

import sys
import re
import types
import inspect

KEY_VALUE_SEPARATOR = '='
NO_SUCH_COMMAND = '_no_such_cmd'

class CmdError(Exception):
		pass

def name(name_to_replace):
	pass

class Command(object):
	OPT_DOC_PATTERN = r'@(=)?([\w\s\-,]+)\s*(#.+)?'
	FREE_MODE = True
	_env = {}


	def __init__(self, processor):
		self.processor = processor
		self.option_list = []
		self.roster = {}

		self._init_processor()
		self._init_options()

	def _init_processor(self):
		"""检查并获得命令主函数信息"""
		p = self.processor

		if not callable(p):
			raise CmdError, "Command processor '%s' is not callable" % p

		if type(p) is not types.FunctionType:
			raise CmdError, "Command processor '%s' must be function type" % p

		self.name = p.__name__

		argspec = inspect.getargspec(p)
		self.exactly_argsname = argspec.args
		self.defaultvalues = {}
		if argspec.defaults:
			self.defaultvalues = dict(zip(argspec.args[0-len(argspec.defaults):], argspec.defaults))

		# print self.defaultvalues

	def _init_options(self):
		"""解析processor.__doc__, 生成选项列表option_list"""
		docpat = re.compile(self.OPT_DOC_PATTERN)
		comment = ''
		option_define = []

		#筛出参数定义行
		for line in re.split('\n', self.processor.__doc__ or ''):
			r = docpat.findall(line)
			if r:
				option_define.extend(r)
			else:
				comment += line + '\n'

		self.comment = comment

		# print option_define

		#处理参数定义
		for o in option_define:
			is_keyvalue, aliases, comment = o
			aliases = [a.strip() for a in aliases.split(',')]

			opt = Option(is_keyvalue == '=', aliases, comment)
			self.option_list.append(opt)

			for alias in aliases:
				self.roster[alias] = opt

		# print self.option_list
		# print self.roster

	def parse_args(self, argv):
		"""将命令列表解析成键值对列表, 遇到不可解析参数立即停止"""
		option, free_args = [], []

		while argv:
			a = argv.pop(0)

			if a.startswith('-'):
				#正常带前缀参数
				if a.startswith('--'):
					k, sptr, v = a[2:].partition(KEY_VALUE_SEPARATOR)
					perfix = '--'
				else:
					k, v = a[1], a[2:]
					perfix = '-'
					
				o = self.roster.get(k)

				if o is None : 
					raise CmdError, "option %s%s not recognized" % (perfix, k)
				
				if o.is_keyvalue:
					if not v:
						if not argv:
							raise CmdError, "option %s%s requires value" % (perfix, k)
						v = argv.pop(0)
				else:
					if v:
						raise CmdError, "option %s%s must not have value" % (perfix, k)
					v = True

				option.append((o.name, v))
			
			elif KEY_VALUE_SEPARATOR in a:
				#无前缀,等号赋值的键值对.直接解析不检查选项是否已定义
				k, sptr, v = a.partition(KEY_VALUE_SEPARATOR)
				option.append((k, v))
			
			else:
				#遇到无参数名的选项时,分两种情况处理
				if not self.FREE_MODE:
					argv.insert(0, a)
					break
				
				free_args.append(a)

		return option, argv, free_args

	def run(self, opt = {}, argv = [], env = {}):
		if not opt:
			opt, argv, free_args = self.parse_args(argv)
			#todo 检查是否有重复赋值
			opt = dict(opt)

		#将命令行选项对应到processor函数参数
		exactly_args = []
		for arg_name in self.exactly_argsname:
			o = self.roster[arg_name]
			aliases = o.aliases #todo check the key
			args_in_opt = [opt.pop(a) for a in aliases if a in opt]
			
			if args_in_opt:
				arg = args_in_opt[0] 
			elif self.FREE_MODE and free_args:
				arg = free_args.pop(0)
 			elif arg_name in self.defaultvalues:
 					arg = self.defaultvalues[arg_name]
 			else:
				raise CmdError, "option --%s must be set" % arg_name

			exactly_args.append(arg)

		# print exactly_args
		self.processor(*exactly_args, **opt)

	def set_environ(self, env = {}):
		self._env = env

class Option(object):
	def __init__(self, is_keyvalue, aliases, option_comment):
		self.aliases = aliases
		self.name = aliases[0]
		self.option_comment = option_comment
		self.is_keyvalue = is_keyvalue

	def __repr__(self):
		if self.is_keyvalue:
			return "<KV Option '%(name)s>" % self.__dict__
		else: 	
			return "<Option '%(name)s'>" % self.__dict__

def run(entry, argv = sys.argv[1:], cmdfuncs = [], noexit = False):
	if cmdfuncs:
		run_with_subcommand(entry, argv, cmdfuncs, noexit)
	else:
		Command(entry).run(argv = argv)

def run_with_subcommand(entry, argv, cmdfuncs = [], noexit = False):

	cmd_dict = dict([(cmd.name, cmd) for cmd in map(Command, cmdfuncs)])

	environ = {}

	if entry:
		entry = Command(entry)
		entry.FREE_MODE = False
		opt, argv, _ = entry.parse_args(argv)
		environ = entry.run(opt = dict(opt))

	entry_name = entry.name if entry else ''
	if not argv:
		exit(0)

	cmd, argv = argv[0], argv[1:]

	#子命令不存在，尝试交给错误处理命令
	if cmd not in cmd_dict:
		hdlr = cmd_dict.get(NO_SUCH_COMMAND)
		if hdlr:
			hdlr.run(env = environ)
		else:
			
			print "'%s' is not a %s command" % (cmd, entry_name)
		exit(1)

	#print "Run %s command: %s" % (entry_name, cmd)
	cmd_dict[cmd].run(argv = argv, env = environ)

