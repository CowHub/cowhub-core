#!/usr/bin/env ruby
require 'fileutils'

abort 'Invalid entry point of arguments.' if __FILE__ != $0 or ARGV.length == 0

mode = ARGV.first

FileUtils::cp "lib/#{mode}/handler.py", 'lib/'
system 'zip -r lib{.zip,}'
FileUtils::rm 'lib/handler.py'

