# md-nlp
## Background

I use Obsidian a lot, but don't link between notes as much as I could, and tags are useful although they can be bogged down with typos and involuntary use of alternate terms. Hence this package.

It is written in Python and runs on MacOS and Ubuntu Linux. Not Windows because I don't use Windows for serious work. The only needed package outside the standard install is `pyyaml`.

It reads files in the vault, butt does not change them.

## Files
### In the package

- `code/run.sh` - the bash script that defines variables and creates the config file;
- `code/tags.py` - the Python script that does the work;
- `data/Convert-tags.json` - a JSON formatted file with key/value data;

### Generated

By default these files will go into the `tmp` folder, but this can be configured differently:

- `tmp/TagsReport.txt` - an alphabetic list of tags with occurrence counts;
- `tmp/config.txt` - generated configuration file
- `tmp/obsidian.json` - a metadata file in JSON format
- `tmp/output-1` - diagnostic file, currently holds a copy of the config
- `tmp/output-2` - diagnostic file, currently unused
- `tmp/output-3` - diagnostic file, progress messages from the Python code
- `tmp/output-4` - diagnostic file, currently unused

## Hints

Install the YAML package:
```python
pip3 install pyyaml
```

Check `run.sh` and adjust the locations as needed (there are helpful comments included). The only oddity is a call to a bash function which overcomes the MacOS shell not honouring case in directory names. By that I mean '/user/paul` and `/user/Paul` will be treated as identical by the shell, but not by the Python script. I haven't included `wheresmyhome.sh` because it's written for my environment and won't be helpful for most other people.

In my environment everything lives in Dropbox. That includes code, static data and the Obsidian vault. This may be different for you.

Just set the bash variables accordingly and everything will be fine.

I would recommend running the bash script in test mode the first time:
```bash
./run.sh -t
```
This will create the index files in whatever temporary directory you specify. Check that everything looks OK and then run it against the Obsidian vault.

## Detail

Tags are pulled from the YAML block at the start of the note, but not if they are defined elsewhere. Each is reduced to lowercase and then matched against the key/value data loaded from `Convert-tags.json`. If the tag matches a key, it is replaced by the value. If not, the key is retained with it's original case.

_Missing fucntionality_:

- I have considered a threshold for tags, below which files would not be generated. This would be controlled via a configuration item and a parameter to the bash script `run.sh`. Currently this isn't important enough to implement (but this is likely to change in the near future). However, sort the `tmp/TagsReport.txt` file and look at the occurrence counts to see how much it would help you;
- Recognising tags defined outside the YAML block. I don't write notes like that, but with a little more effort it could be done. Performance would degrade somewhat as the note content would have to be parsed;
- Tidy the diagnostic messages. Too many get generated even without the flag being set. Clumsy but not critical - it helps me identify poorly constructed notes (and there have been a few);

## Performance

Development and testing take place on either a MacBook Pro or an iMac, both vintage. Run times are acceptable on either machine :

5 seconds reading _2602_ notes giving _539_ unique tags on a 2012 Macbook Retina Pro

Obviously, 539 unique tags will generate 539 index files.

