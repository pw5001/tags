#!/bin/bash
# ================================================================================
#
#  VERSION 3 GitHub:
#
#  Recommendation:
#     Run the script with "-t" (`run.sh -t`) the first time and have the *.md files
#     created in the temp directory. Check that what you have is what you want before
#     running the script live.
#
#  Description
#    Runner script for V3 of the Obsidian tools
#
#  Parameters:
#     -t    switch on test mode
#
#  Maintnance:
#     3.0.0    2023-12-23  Github release
#
# ================================================================================

if [ "$1" == '-t' ];then
   TestMode=y
else
   TestMode=n
fi

if [ $TestMode == 'y' ];then
   set -x
fi

VERSION=1.0.0
JobTag="run.sh v.${VERSION}"
Home=xx

#
# This allows for the MacOS shell not honouring case in directory names!
#
Home=`/usr/local/bin/wheresmyhome.sh`

if [ "$Home" == 'xx' ];then
   echo "No home directory found!"
   exit 1
fi

#
# Ths works for me on a Linux server and MacOS dev machine. YMMV !
#
# Hints:
#     Everything lives in ~/Dropbox/Live/Git/<git-project>     $BaseDir
#     Name of the Obsidian vault (which is a folder)           $VaultLocation
#     The terminal part of the vault name                      $VaultName
#     A JSON file with tag data is created                     $LiveMetaDataFile
#     An alphabetic list of tags with counts                   $ReportFile
#     Directory where the tag index files are created          $TagDir
#

GitProject=md-nlp

DropboxDir=${Home}Dropbox
BaseDir=${DropboxDir}/Live/Git/$GitProject/
CodeDir=${BaseDir}code
DataDir=${BaseDir}data
TmpDir=${BaseDir}tmp
ReportDir=${BaseDir}reports
LOGDIR=$TmpDir
LiveData=$DataDir
LiveMetaDataDir=$ReportDir

JSON=${LiveData}/Convert-tags.json

#
# Make sure that the directory for new tags exists
#
TagDir=${DropboxDir}/PKM/Tags
mkdir -p $TagDir

TmpFile1=${TmpDir}/output-1 ; >$TmpFile1
TmpFile2=${TmpDir}/output-2 ; >$TmpFile2
TmpFile3=${TmpDir}/output-3 ; >$TmpFile3
TmpFile4=${TmpDir}/output-4 ; >$TmpFile4

Today="`date +%Y-%m-%d` at `date +%H:%M`"

# --------------------------------------------------------------------------------
# There's a single vault now
#

ConfigFile=${TmpDir}/config.txt

VaultName=Obsidian
ArticleDir=${DropboxDir}/PKM/$VaultName
VaultLocation=$ArticleDir
#
# This file will have an alphabetic list of tags with counts
#
ReportFile=${TmpDir}/TagsReport.txt
#
# This is a JSON dump originally intended for another system
#
LiveMetaDataFile=${TmpDir}/obsidian.json

if [ $TestMode == 'y' ];then
   TagDir=$TmpDir
   Debug=y
else
   Dubug=n
fi

echo "# $Today"                            > $ConfigFile
echo "#"                                  >> $ConfigFile
echo "debug          $Debug"              >> $ConfigFile
echo "tagdir         $TagDir"             >> $ConfigFile
echo "reportfile     $ReportFile"         >> $ConfigFile
echo "closedvocab    $JSON"               >> $ConfigFile
echo "livemetadata   $LiveMetaDataFile"   >> $ConfigFile
echo "vault          $VaultLocation"      >> $ConfigFile
echo "vaultname      $VaultName"          >> $ConfigFile
echo "#"                                  >> $ConfigFile
echo "codedir        $CodeDir"            >> $ConfigFile
echo "tmpopfile      $TmpFile2"           >> $ConfigFile

echo '' >>$TmpFile1
cat $ConfigFile >>$TmpFile1
echo '' >>$TmpFile1

# --------------------------------------------------------------------------------
# Build the files based on tags
#

cd $CodeDir

./tags.py $ConfigFile >>$TmpFile3
Summary=`grep ^R: $TmpFile3 | sed -e 's/R: //'`
Err=$?

echo '' >>$TmpFile3
echo "$Summary" >>$TmpFile3
echo '==========================================================' >>$TmpFile3
echo '' >>$TmpFile3

# --------------------------------------------------------------------------------
# Keep a count of the number of MD files in Obsidian
# 

MDFileCount=${ReportDir}/md-file-counts.n

cd $ArticleDir

N=`ls -lR | grep ".md$" | wc -l`
Today=`date +%y-%m-%d`

echo "$Today $N" >>$MDFileCount

# --------------------------------------------------------------------------------
# Sends a message back to the caller
#
echo "${JobTag};${Summary}"

exit $Err

