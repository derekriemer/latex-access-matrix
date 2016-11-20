# settings.py
#    A part of the latex-access project at http://latex-access.sourceforge.net/
#    Author: Daniel Dalton <daniel.dalton10@gmail.com>
#    Copyright (C) 2011,2012,2013 Daniel Dalton/latex-access Contributors
#
#    This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation;
#    either version 2 of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#    See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with this program; if not, visit <http://www.gnu.org/licenses>

import os
import ueb
import nemeth

globals
# Global settings for latex-access, these are the default values
settings={"brailledollars":"True","speakdollars":"True","brailletable":"nemeth","capitalisation":"6dot","preprocessorfile":"~/.latex-access-preprocessor.strings", "speechfile":"","nemethfile":"","uebfile":""}

def loadSettings (file):
    """Read settings from file.

    This function reads the setting values from file. The settings are
    saved in the public dict settings. The file should be in the form
    settingname value

    Where settingname is a valid setting and value is the value of that
    setting. The file may be commented by use of ; but only at the start
    of a line! Blank lines are ignored."""
    f=None
    try:
        f=open(file, "r")
    except:
        return False
    else:
        for line in f.readlines ():
            if line[0] == "\n" or line[0] == ";": # Skip some irrelevant stuff
                continue
            words = line.split()
            if not words: # Ignore lines with spaces
                continue
            if len(words) < 2:
                continue
            settings[words[0]] = words[1].lower()
        return True
    finally:
        if f:
            f.close()

def activateSettings (instances):
    """Activate settings stored in a file.

    This function activates the settings in a file, which for the emacs
    module is ~/.latex-access.

    It also sets up the settings for active instances such as those as a
    result of the nemeth class eg. nemeth.nemeth () and sets those active
    sessions to the values specified in the config file. Note the
    activation or deactivation of speech and Braille must be controlled by
    each module independently, i.e. not here."""

    # points to our custom speech strings file
    speechfile =os.path.expanduser(settings["speechfile"])
    # Decide what file holds Braille strings based on what table is in use.
    if settings["brailletable"].lower() == "ueb":
        bfile =os.path.expanduser(settings["uebfile"])
    else:
        bfile =os.path.expanduser(settings["nemethfile"])

    if 'speak' in instances.keys():
        instances["speak"].remove_dollars = not booleaniseSetting("speakdollars")
        if os.path.exists(speechfile) and os.path.isfile (speechfile):
            instances["speak"].load_file(speechfile)
    if 'braille' in instances.keys():
        instances["braille"].remove_dollars = not booleaniseSetting("brailledollars")
        instances["braille"].capitalisation=settings["capitalisation"]
        if os.path.exists(bfile) and os.path.isfile (bfile):
            instances["braille"].load_file(bfile)
    if 'preprocessor' in instances.keys () and os.path.exists(os.path.expanduser (settings["preprocessorfile"])):
        instances["preprocessor"].read(os.path.expanduser (settings["preprocessorfile"]))

    return True # Settings activated

def booleaniseSetting (setting):
    """Turn a setting value into a boolean type.

    As settings read from the config file are of type string, return a
    boolean representation of this. 'true' or 'True' = True, while any
    other string is False."""
    if str(settings[setting]).lower () == 'true':
        return True
    else:
        return False

def getSetting (setting):
    """Get the value of setting.

    This function searches for the particular setting in the settings
    dict, and if found, returns the settings' value."""

    if setting in settings.keys():
        return booleaniseSetting(setting)
    else: # setting not found
        return False

def brailleTableToUse ():
    """Return the instance of the braille module to use.

    This function return the instance of the Braille table that should be
    used."""
    if settings["brailletable"].lower() == "ueb":
        return ueb.ueb()
    else:
        return nemeth.nemeth()
