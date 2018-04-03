# -*- coding: utf-8 -*-
# https://gist.github.com/omz/f3886441053d0ea79f39

# Updated to work on python2/3

import ui
import sys

# Mapping based on http://www.upsidedowntext.com/unicode
CHARMAP = {
    '!': b'\xc2\xa1',
    '"': b',,',
    "'": b',',
    '&': b'\xe2\x85\x8b',
    ')': b'(',
    '(': b')',
    ',': b"'",
    '.': b'\xcb\x99',
    '1': b'\xc6\x96',
    '0': b'0',
    '3': b'\xc6\x90',
    '2': b'\xe1\x84\x85',
    '5': b'\xcf\x9b',
    '4': b'\xe3\x84\xa3',
    '7': b'\xe3\x84\xa5',
    '6': b'9',
    '9': b'6',
    '8': b'8',
    '<': b'>',
    '?': b'\xc2\xbf',
    '>': b'<',
    'A': b'\xe2\x88\x80',
    'C': b'\xc6\x86',
    'B': b'B',
    'E': b'\xc6\x8e',
    'D': b'D',
    'G': b'\xd7\xa4',
    'F': b'\xe2\x84\xb2',
    'I': b'I',
    'H': b'H',
    'K': b'K',
    'J': b'\xc5\xbf',
    'M': b'W',
    'L': b'\xcb\xa5',
    'O': b'O',
    'N': b'N',
    'Q': b'Q',
    'P': b'\xd4\x80',
    'S': b'S',
    'R': b'R',
    'U': b'\xe2\x88\xa9',
    'T': b'\xe2\x94\xb4',
    'W': b'M',
    'V': b'\xce\x9b',
    'Y': b'\xe2\x85\x84',
    'X': b'X',
    '[': b']',
    'Z': b'Z',
    ']': b'[',
    '_': b'\xe2\x80\xbe',
    'a': b'\xc9\x90',
    '`': b',',
    'c': b'\xc9\x94',
    'b': b'q',
    'e': b'\xc7\x9d',
    'd': b'p',
    'g': b'\xc6\x83',
    'f': b'\xc9\x9f',
    'i': b'\xe1\xb4\x89',
    'h': b'\xc9\xa5',
    'k': b'\xca\x9e',
    'j': b'\xc9\xbe',
    'm': b'\xc9\xaf',
    'l': b'l',
    'o': b'o',
    'n': b'u',
    'q': b'b',
    'p': b'd',
    's': b's',
    'r': b'\xc9\xb9',
    'u': b'n',
    't': b'\xca\x87',
    'w': b'\xca\x8d',
    'v': b'\xca\x8c',
    'y': b'\xca\x8e',
    'x': b'x',
    '{': b'}',
    'z': b'z',
    '}': b'{',
    '-': b'-'
}

class TextViewDelegate(object):
    def textview_should_change(self, tv, rng, repl):
        if repl == '':
            return True
        ud = ''.join(reversed([CHARMAP.get(x, x).decode('utf-8') for x in repl])) 
        text_len = len(tv.text)
        tv.replace_range(rng, ud)
        tv.selected_range = rng[0], rng[0]
        return False


tv = ui.TextView()


def copy_action(sender):
    import clipboard
    import console
    clipboard.set(tv.text)
    console.hud_alert('Copied')


copy_button = ui.ButtonItem(title='Copy', action=copy_action)
tv.right_button_items = [copy_button]
tv.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
tv.autocorrection_type = False
tv.spellchecking_type = False

tv.font = ('HelveticaNeue', 36)
tv.delegate = TextViewDelegate()
tv.name = 'Upside-Down Text'
tv.present('sheet')

