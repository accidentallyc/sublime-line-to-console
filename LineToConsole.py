import sublime
import sublime_plugin
import warnings
import re
from os.path import basename

line_regex = re.compile('(\s*)(.*)')

class LineToConsoleCommand(sublime_plugin.TextCommand):
	def __init__(self,edit):
		super().__init__(edit)
		class JsFactory():
			rxPattern = re.compile('console.log\((.*?)\,(.*)\)')
			def console(filename,linenum,txt):
				return 'console.log(\"' + filename + '::' + linenum + '\",' + txt +')'
			def isConsoled(txt):
				return JsFactory.rxPattern.match(txt)
			def deconsole(isConsoledOutput):
				return isConsoledOutput.group(2).strip()

		class PyFactory():
			rxPattern = re.compile('print\((.*?)\,(.*)\)')
			def console(filename,linenum,txt):
				return 'print(\"' + filename + '::' + linenum + '\",' + txt +')'
			def isConsoled(txt):
				return PyFactory.rxPattern.match(txt)
			def deconsole(isConsoledOutput):
				return isConsoledOutput.group(2).strip()

		class UnknownFactory():
			rxPattern = re.compile('/*Cannot Determine \((.*?)\,(.*)\)')
			def console(filename,linenum,txt):
				return 'print(\"' + filename + '::' + linenum + '\",' + txt +')'
			def isConsoled(txt):
				return PyFactory.rxPattern.match(txt)
			def deconsole(isConsoledOutput):
				return isConsoledOutput.group(2).strip()

		self.factories = {
			'js':JsFactory,
			'coffee':JsFactory, # JsFactory also works with coffee
			'py':PyFactory,
		}

	def run(self, edit):
		fullpath = self.view.file_name()
		filename =  basename(fullpath)
		ext = fullpath.split('.')[-1]
		factory = self.factories[ext] if ext in self.factories else None
		if factory == None:
			warnings.warn('Unsupported extension ' + ext)
			return


		view = self.view
		sel = self.view.sel()
		for region in sel:
			full_line = view.line(region)
			predicate = view.substr(full_line)
			line = line_regex.match(predicate)

			tabs = line.group(1)
			txt = line.group(2)
			new_text = None

			isConsoled = factory.isConsoled(txt)
			if isConsoled:
				new_text = tabs + factory.deconsole(isConsoled)
			else :
				linenum = str(view.rowcol(full_line.begin())[0] + 1)
				new_text = tabs + factory.console(filename,linenum,txt)
			view.replace(edit, full_line, new_text)