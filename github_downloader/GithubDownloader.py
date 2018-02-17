#!python3
# -*- coding: utf-8 -*-

"""
Created on Sun Mar 08 15:29:00 2015

Prompt for a GitHub user name, the name of a repo, and download it.
Please note: this is *NOT* a cloning tool! It simply downloads the files in the repo.

Note: This is based on a script found on the Pythonista Tools page, but the gist link now is 404.

Pythonista tools page: https://github.com/Pythonista-Tools/Pythonista-Tools/blob/master/GitHub%20Tools.md

The original script was a console application which downloaded ad-hoc repositories from GitHub (via Zip download)

Changes:
    + Python 3 Support
    + Added ui views
    + Added the ability to save repos
    + Added save repo without download

TODO:
    + Ability to choose download location
    + Clean-up code & Comment code
    + Option to Remove the '-master' from folder
    + Option (rather than forcefully) over-write
      destination contents
    + Save last download date & check for updates 
      optionally, on a per-repo basis   
"""

import os
import zipfile
import random
import ui
import dialogs
import json
import six
import sys
from six.moves import urllib
from urllib.request import urlretrieve



class GetRepo (object):
    """
    Applications Main Class
    """
    
    infopopup = None
    popuptext = None
    
    def __init__(self):
        """
        Class Initializer

        Creates a file to track which repos you have saved, called 'repo_downloader.json'        
        """
        
        self.saved_file = 'repo_downloader.json'
        
        try:
            with open(self.saved_file) as f:
                self.saved = json.load(f)
        except:
                self.saved = []

    def main(self): 
        """
        Application's main entry point
        """
        tv = ui.TableView()
        w, h = ui.get_window_size()
        tv.width = w
        tv.height = h
        tv.name = "Download Repo"
        ds = ui.ListDataSource(self.saved)
        ds.action = self.download
        ds.move_enabled = False
        ds.edit_action = self.delrepo
        tv.data_source = ds
        tv.delegate = ds
        
        add = ui.ButtonItem(action=self.add_repo, image=ui.Image.named('iob:ios7_plus_empty_32'))
        
        tv.right_button_items = [add]
        self.tv = tv
        
        self.tv.present()
    
    def add_repo(self, sender):
        """
        Add a new repo to be downloaded and/or saved.
        """
        q = [{
            'title' : "Github User",
            'icon' : 'iob:ios7_person_32',
            'key' : 'user',
            'value' : '',
            'type' : 'text' },
        {
            'title' : 'Repo Name',
            'icon' : 'iob:code_working_32',
            'key' : 'repo',
            'type' : 'text' },
        {
            'title' : 'Save',
            'icon' : 'iob:briefcase_32',
            'key' : 'save',
            'value' : True,
            'type' : 'switch' },
        {
            'title' : 'Download Now',
            'icon' : 'iob:code_download_32',
            'key' : 'download',
            'value' : True,
            'type' : 'switch'
        }]
        new = dialogs.form_dialog('Add Repo',q)
        
        
        if new:
            user = new['user']
            repo = new['repo']
            url_format = 'https://www.github.com/{user}/{repo}/archive/master.zip'
            url = url_format.format(user=user, repo=repo)
            title = '{}/{}'.format(user,repo)
            item = {
                'title' : title,
                'image' : 'iob:code_download_32',
                'accessory_type' : 'disclosure_indicator',
                'url' : url
            }
            if new['save']:
                self.saved.append(item)
                self.save_saved()
                self.tv.data_source = ui.ListDataSource(self.saved)
                self.tv.reload()
            
            if new['download']:
                self.download_now(url)
            
    def save_saved(self):
        """
        Add the repo selected to be saved to the 'repo_downloader.json' file.
        """
        with open(self.saved_file, 'w') as f:
            json.dump(self.saved, f)
    
    def delrepo(self, sender):
        saved_id = sender.tapped_accessory_row
        item = self.saved[saved_id]
        #print(item)
        self.saved.pop(saved_id)
        self.save_saved()
        self.tv.reload()
        pass
    
    @ui.in_background    
    def do_download(self):
        """
        Method to download the zip file.
        """
        
        url = self.get_url
        
        # Create a random name to prevent over-writing an existing archive, just in case.
        downloadname = str(random.randint(0x000000, 0xFFFFFF)) + "_master.zip"
        
        self.add_popup_text('Downloading as {}...'.format(downloadname))
        
        urlretrieve(url, downloadname)
        
        self.add_popup_text('Download Complete!')
        zipped = zipfile.ZipFile(downloadname, 'r')
        
        
        self.add_popup_text('Extracting Zip...')
        zipped.extractall()
        
        zipped.close()
        
        self.add_popup_text("Cleaning up...")
        os.remove(downloadname)
        self.add_popup_text('Deleted {}'.format(downloadname))
        
        self.add_popup_text('Done!')
        self.add_popup_text('')
        self.add_popup_text('Closing Window in 3 seconds...')
        if self.get_url:
            self.get_url = None
            
        ui.delay(self.closepop, 3)
        
        
    def download(self, sender):
        """
        Setup the UI to show the file downloading, then call the actual download code.
        """
        dl_id = sender.selected_row
        item = self.saved[dl_id]
        url = item['url']
        self.get_url = url
        self.infopop()
        self.add_popup_text('Starting...')
        ui.delay(self.do_download,2)
        
    def download_now(self, url):
        """
        To Be Completely honest, I forget.
        """
        self.get_url = url
        self.infopop()
        self.add_popup_text('Starting...')
        ui.delay(self.do_download,2)
        
    def closepop(self, sender=None):
        """
        Close the pop-up
        """
        def close_animate():
            self.infopopup.alpha = 0
        
        def do_close(sender=None):
            self.tv.remove_subview(self.infopopup)
        
        ui.animate(close_animate, 1)
        ui.delay(do_close,1)
        
    def add_popup_text(self, text):
        """
        Add text to the popup created during download
        """
        self.popuptext.text += ' ' + text + '\n'
        #^self.t.content_offset = self.tv.o
        self.infopopup.content_offset = self.infopopup.content_size

    def infopop(self):        
        """
        Modal style pop-up.
        """
        w,h = ui.get_window_size()
        width = round((w*0.8),0)
        height = round((h*0.8/1.5),0)
        
        if not self.infopopup:
            # Outer          
            p = ui.ScrollView()
            p.border_color = '#ccc'
            p.border_width = 1

            p.width = width
            p.height = height
            p.corner_radius = 10
            
            t = ui.TextView()
            t.width = width
            t.height = height
            t.font = ('<System>',12)
            t.content_inset = (5,5,5,5)
            
            b = ui.Button()
            b.action = self.closepop
            b.image = ui.Image.named('iob:ios7_close_outline_24')
            b.width = 24
            b.height = 24
            b.x = (width - 29)
            b.y = 5
            
            t.editable = False
            
            t.add_subview(b)
            
            self.popuptext = t
            
            p.y = (((h - height) / 2) - 40)
            p.x = ((w - width) / 2)
            
            p.add_subview(self.popuptext)
            self.infopopup = p
            p.height = 0
        
        
        
        def animate_popup():
            """
            Method to animate the the popup, because its prettier.
            """
            self.infopopup.height = height
            
        self.infopopup.height = 0
        self.tv.add_subview(self.infopopup)
        ui.animate(animate_popup,1)

        
GetRepo().main()