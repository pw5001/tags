#!/usr/local/bin/python3
"""
================================================================================

   This script will build a set of Obsidian compatible files, one for each tag
   that it finds in the files in the vault that is reads.

Bugs:

Bugs Fixed:

Missing functionality:
   None

Parameters:
   1. name of the config file

Versions:
   1.0.0    2023-12-23  Github release

================================================================================
"""

import os
import re
import sys
import json
import urllib.parse
import yaml
from datetime import datetime, date


VERSION        = '1.0.0'
JOBTAG         = 'tags.py %s' % VERSION

MAXFILES       = 100

# keys in the config file

DEBUG          = 'debug'
CLOSEDVOCAB    = 'closedvocab'
CODEDIR        = 'codedir'
LIVEMETADATA   = 'livemetadata'
REPORTFILE     = 'reportfile'
TAGDIR         = 'tagdir'
VAULT          = 'vault'
VAULTNAME      = 'vaultname'
#
#
#
DEFAULTREPORTFILE = '/tmp/tags.report.txt'
#
# Header YAML block for the tag file
#
Header         = '---\ntitle: %s\ndate_created: %s\n---\n\n'
#
# Unwanted sub-directories
#
Unwanted       = ['archive', 'attachments', 'MOC', 'Queries', 'tags', 'templates']
#
# Obsidian template. Examples :
#
# obsidian://open?vault=Obsidian&file=me%20and%20here%2FIn-house%20Geek%2FProjects%2FEDMS
# obsidian://open?vault=Article-vault&file=2023%2F2023-06-05%20Barbarian%20in%20space%20-%20the%20secret%20space-laser%20battle%20station%20of%20the%20Cold%20War
#
OURL           = 'obsidian://open?vault=%s&file=%s'


"""
================================================================================
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
================================================================================
"""

class Util ():
   def __init__ (self, Debug=False):

      self.Debug = Debug

# --------------------------------------------------------------------------------
# DebugPrint:
#    In:      string to print
#    Out:     nothing

   def DebugPrint (self, S):
      if self.Debug:
         print (S)

# --------------------------------------------------------------------------------
# Error:
#    In:      string to print
#    Out:     nothing

   def Error (self, S):
      print ("E: %s" % (S,))

# --------------------------------------------------------------------------------
# MD5File:
#    In:      file name
#    Out:     MD5 as a string

   def MD5File (self, File):

      with open (File, 'rb') as fh:
         data = fh.read ()

      S = hashlib.md5(data).hexdigest ()

      return str (S)

# --------------------------------------------------------------------------------
# ReadConfig:
#    In:      name of the file holding config data
#    Out:     config data as a dictionary
#

   def ReadConfig (self, FileName):

      Config = {}

      with open (FileName, 'r') as fh:
         line = fh.readline ()
         while line:
            line = line.replace ('\n', '').replace ('\r', '')
            m = re.search ("(\w+)\s+(.*)", line)
            if m:
               Name, Value = [m.group (1), m.group (2)]
               Name = Name.lower ().strip ()
               Config [Name] = Value.lstrip ().rstrip ()

            line = fh.readline ()

      return Config

# --------------------------------------------------------------------------------
# Debug switches
#    In:      nothing
#    Out:     nothing

   def DebugOff (self):
      self.Debug = False

   def DebugOn (self):
      self.Debug = True

# --------------------------------------------------------------------------------
# Output:
#    In:      string to output (print at this version)
#    Out:     nothing

   def Output (self, S):
      print (S)

# --------------------------------------------------------------------------------
# PrepareName:
#    In:      name
#    Out:     name normalised

   def PrepareName (self, Name):

      S = Name.lower ()
      S1 = re.sub (r'[^a-zA-Z0-9]', '', S)

      return S1.lstrip ().rstrip ()

"""
================================================================================
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
================================================================================
"""

class Tags (Util):
   def __init__ (self, ConfigFile, Debug=False):

      super ().__init__ (Debug)

      self.ConfigData = self.ReadConfig (ConfigFile)
      self.TagData = []
      self.TagCount = {}
      self.TagDict = {}

      if VAULT in self.ConfigData:
         self.ArticleDir = self.ConfigData [VAULT]
         m = re.search (".*Dropbox/(.*)", self.ArticleDir, re.I)
         self.PartVaultName = m.group (1)
      else:
         self.Error ("[%s] not found in config file" % (VAULT,))
         exit (1)

      if REPORTFILE in self.ConfigData:
         self.ReportFile = self.ConfigData [REPORTFILE]
      else:
         self.ReportFile = DEFAULTREPORTFILE

      if CLOSEDVOCAB in self.ConfigData:
         with open (self.ConfigData [CLOSEDVOCAB], 'r') as fh:
            self.MasterTagsList = json.load (fh)
      else:
         self.MasterTagsList = {}

      if VAULTNAME in self.ConfigData:
         self.VaultName = self.ConfigData [VAULTNAME]
      else:
         self.VaultName = 'unspecified'

      self.DebugRequest = False
      self.MaxFiles = 9999999

      if DEBUG in self.ConfigData:
         if self.ConfigData [DEBUG].lower () == 'y':
            self.DebugRequest = True

      self.FileCount = 0

      self.MetaData = {}
      self.MetaData ['_system'] = {}
      self.MetaData ['_system']['hostname'] = os.uname()[1]
      self.MetaData ['_system']['script_name'] = os.path.basename(__file__)
      self.MetaData ['_system']['script_version'] = VERSION
      self.MetaData ['_system']['vault_name'] = self.VaultName

      if CODEDIR in self.ConfigData:
         self.MetaData ['_system']['script_location'] = self.ConfigData [CODEDIR]
      else:
         self.MetaData ['_system']['script_location'] = 'UNKNOWN'

      self.DebugPrint ("====> Tags")
      self.DebugPrint ("====> max files = %d" % (self.MaxFiles,))

# --------------------------------------------------------------------------------
# ProcessSingleFile :
#    In:      directory name
#             name of the MD file
#    Out:     nothing
#

   def ProcessSingleFile (self, Dir, File):

      FileName = Dir + File

      self.DebugPrint ("ProcessSingleFile 1: [%s]" % (FileName,))

      S = ''
      State = 0

      with open (FileName, 'r') as fh:
         line = fh.readline ()
         while line:
            line = line.replace ('\n', '').replace ('\r', '')
            if line.startswith ('---'):
               State += 1
            elif State == 1:
               if line.startswith ('title'):
                  line = line.replace (': ', ' - ').replace ('title -', 'title:')
               S += line + '\n'
            if State > 1:
               line = ''
            else:
               line = fh.readline ()

      Y = yaml.safe_load (S)
      TagList = Y ['tags']
      if isinstance (TagList, str):
         Tags = TagList
      else:
         Tags = ','.join (TagList)

      self.DebugPrint ("ProcessSingleFile 1: " + str (type (TagList)))
      self.ProcessTags (Tags, FileName)

# --------------------------------------------------------------------------------
# ProcessTags :
#    In:      list of tags from the file
#             name of the file being processed
#    Out:     nothing
#

   def ProcessTags (self, TagList, FileName):

      self.DebugPrint ("ProcessTags 1: TagList [%s]" % (TagList,))

      if 'Dropbox' in FileName:
         m = re.search (".*Dropbox/(.*)", FileName)
         PartName = m.group (1)
      else:
         PartName = FileName

      ObsidianFile = self.ReturnObsidianFile (FileName)
      URL = OURL % (self.VaultName, ObsidianFile)

      m = re.search (".*/(.*?).md", FileName)
      TerminalFile = m.group (1)

      tags = []
      TagList = TagList.lower ().replace ('[', '').replace (']', '').replace ('.', ',') + ','

      for item in TagList.split (','):
         item = item.rstrip ().lstrip ()
         if item:
            lcitem = item.lower ()
            if item in self.MasterTagsList:
               item = self.MasterTagsList [lcitem]
            tags.append (item.lstrip ().rstrip ())

            if item not in self.TagDict:
               self.TagDict [item] = []
            self.TagDict [item].append (TerminalFile)

      for item in tags:
         H = {}
         H ['base']           = 'DROPBOX'
         H ['system']         = 'obsidian'
         H ['file']           = PartName
         H ['thistag']        = item
         H ['vault']          = self.PartVaultName
         H ['obsidian_url']   = URL
         H ['taglist']        = TagList
         H ['terminalfile']   = TerminalFile
         
         self.TagData.append (H)
         if item not in self.TagCount:
            self.TagCount [item] = 1
         else:
            self.TagCount [item] += 1

# --------------------------------------------------------------------------------
# ReadArticleDir :
#    In:      name of the directory
#    Out:     nothing
#

   def ReadArticleDir (self, Dir):

      if not Dir.endswith ('/'):
         Dir = Dir + '/'

      self.DebugPrint ("ReadArticleDir: reading %s" % (Dir,))

      for item in os.listdir (Dir):
         if item.startswith ('.'):
            pass

         elif os.path.isfile (Dir + item) and item.endswith ('.md'):

            if self.FileCount >= self.MaxFiles:
               return

            self.FileCount += 1
            self.ProcessSingleFile (Dir, item)

         elif os.path.isdir (Dir + item):
            if item in Unwanted:
               pass
            else:
               self.ReadArticleDir (Dir + item)

# --------------------------------------------------------------------------------
# ReturnObsidianFile:
#    In:      full file name
#    Out:     nothing
#

   def ReturnObsidianFile (self, FileName):

      LocalFileName = FileName.replace (self.ConfigData [VAULT], '')

      return urllib.parse.quote (LocalFileName, safe='')

# --------------------------------------------------------------------------------
# TagsReport:
#    In:      nothing
#    Out:     nothing
#

   def TagsReport (self):

      When = datetime.now () .strftime ("%Y-%m-%d %H:%M")

      with open (self.ReportFile, 'w') as fh:
         fh.write ("#\n# Created %s\n#\n" % (When,))

         Tags = list (self.TagCount.keys ())
         Tags.sort ()

         for tag in Tags:
            N = self.TagCount [tag]
            fh.write ("%5d  %s\n" % (N, tag))

# --------------------------------------------------------------------------------
# WriteLiveMetaData :
#    In:      nothing
#    Out:     nothing
#

   def WriteLiveMetaData (self):

      When = datetime.now () .strftime ("%Y-%m-%d %H:%M")
      self.MetaData ['_system']['created_at']   = When
      self.MetaData ['_system']['file_count']   = self.FileCount

      self.MetaData ['data'] = []
      self.MetaData ['data'] = self.TagData

      with open (self.ConfigData [LIVEMETADATA], 'w') as fh:
         json.dump (self.MetaData, fh, indent=3)

# --------------------------------------------------------------------------------
# WriteTagFiles:
#    In:      directory to hold the tag files
#    Out:     nothing
#

   def WriteTagFiles (self, Dir):

      if self.DebugRequest:
         print ("===================\nCollected tags as a dictionary\n")
         for key in self.TagDict:
            print ("%s : %s" % (key, ','.join (self.TagDict [key])))

      When = datetime.now () .strftime ("%Y-%m-%d %H:%M")

      if not Dir.endswith ('/'):
         Dir = Dir + '/'

# self.TagDict [item].append (TerminalFile)

      for tag in self.TagDict:
         NewFile = Dir + tag + '.md'

         with open (NewFile, 'w') as fh:
            fh.write (Header % ('tag ' + tag, When))
            List = self.TagDict [tag]
            List.sort ()
            for title in List:
               link = '[[' + title + ']]'
               fh.write (link + '\n')
            fh.write ('\n')

# ================================================================================
# ================================================================================

DiagWanted = True
# DiagWanted = False

ConfigFile = sys.argv [1]

Obj = Tags (ConfigFile, DiagWanted)
Obj.ReadArticleDir (Obj.ArticleDir)

Obj.TagsReport ()
Obj.WriteLiveMetaData ()
Obj.WriteTagFiles (Obj.ConfigData [TAGDIR])

Summary = "R: %s - found %d files in %s" % (JOBTAG, Obj.FileCount, Obj.VaultName)
print (Summary)

exit (0)


