# -*- coding: utf-8 -*-

"""
PageView

Copyright 2018 - Michael Ruggiero

Released under the MIT Open Source License

[description goes here]


License Note:
    
    This code has a very open license, purposefully. It has
    very few limitations. However, I do ask as a courtesy if
    you do end up using this code in any way, be it in an
    open source or commercial project, that you let me know.
    
    If you are selling your project commercially and feel
    like making a donation, I certainly won't object, but -
    I would ask that you make a donation to a childrens 
    charity of your choice. If you have a limited capacity
    to donate, then donate to the charity before me.
    
    If you are using Pythonista, you have certain luxuries 
    that many cannot afford, and children are chiefly among
    those who need our help the most.
    
    None of this is required, so its up to you.
    
    Thank you.
    
"""

"""
Where to start looking:
    
    https://gist.github.com/omz/b39519b877c07dbc69f8
"""

import ui
import console

from collections import namedtuple
#from cache import CacheView

from six import text_type


# Constants
TAB_CLOSE_BUTTON_IMAGE_DEFAULT=0
TAB_CLOSE_BUTTON_IMAGE_CIRCLE=1
TAB_CLOSE_BUTTON_IMAGE_CIRCLE_FILLED=2


class TabPageStyle (object):
    """
    Tab Page Style Object
    
    Setup all style options for the TabPageView.
    
    This is testing right now.
    """
    class tab (object):
        close_button_options = [
            ui.Image.named('iob:close_24'),
            ui.Image.named('iob:ios7_close_outline_24'),
            ui.Image.named('iob:close_circled_24'),
        ]
        
        _close_button_image = ui.Image.named('iob:close_24')
        
        # close button image
        @property
        def close_button_image(self):
            return self._close_button_image
        
        @close_button_image.setter
        def close_button_image(self, value):
            # If they are using one of the internal one
            if isinstance(value, int):
                if value < len(self.close_button_tabs):
                    self._close_button_image = self.close_button_tabs[value]
                    return self
            
            if isinstance(value, ui.Image):
                self._close_button_image = value
                return self
            
            try:
                return ui.Image.named(value)
            except Exception:
                raise AttributeError('invalid argument for value {}.\n Must be one of:\n'\
                                    '* pageview.TAB_CLOSE* \n'\
                                    '* ui.Image \n'\
                                    '* Pythonista Image string \n' \
                                    '* Path to image file'
                )
                
        

class TabPageItem (object):
    
    def __init__(self, title, view, id, locked=False, tab_close_action=None, bypass_close_action=False):
        """
        Class Initializer - Using this as a single validation  point.
        """
        if not isinstance(title, text_type):
            raise AttributeError('title must be string')
        
        if not isinstance(view, ui.View) and view is not None:
            raise AttributeError('view must be type ui.View or None.')
        
        # id is kind of open.. for now.
        
        if not isinstance(locked, bool):
            raise AttributeError('locked must be bool')
        
        self.title = title
        self.view = view
        self.id = id
        self.locked = locked
        self.close_tab_action=tab_close_action,
        self.bypass_close_action = bypass_close_action
        

class TabPageView (ui.View):
    
    def __init__(self, **kwargs):
        """
        Class Initializer
        
        Todo:
            * Figure out how to use themes
            * configurable close button
            * 
        
        Keyword Arguments:
            height: tab height, default 30
            use_editor_theme: False?
            background_color: default '#cccccc'
        """
        self.tab_height = kwargs.pop('height', 30)
        
        self.use_editor_theme = kwargs.pop('use_editor_theme', False)
        self.background_color = kwargs.pop('background_color', '#ffffff')
        self.frame = kwargs.pop('frame', (0,0, 320, 460))
        
        # confirm
        self.confirm_close = kwargs.pop('confirm_close', False)
        
        self.confirm_heading = kwargs.pop('confirm_headinn', 'Are you sure you wish to close?')
        
        self.confirm_message = kwargs.pop('confirm_message', 'Any unsaved changes will be lost.')
        
        # global custom close action
        self.close_action = kwargs.pop('close_action', None)
        self.close_action_check_return = bool(kwargs.pop('close_action_check_return', True))
        
        # tab defaults
        self.tab_font = kwargs.pop('tab_font', ('<System>', 12))
        
        self.tab_view = ui.View(
            frame=(0, 0, 320, self.tab_height),
            flex='WB',
            background_color='#eee',
            border_color='#ccc',
            border_width=0.5,
        )
        
        self.content_view = ui.View(
            frame=(0, self.tab_height, 320, 460),
            flex='WH',
            background_color=self.background_color,
        )
        
        # Setup Tab specs
        
        self.tabs = []
        
        # Add the subviewa
        self.add_subview(self.tab_view)
        self.add_subview(self.content_view)
        
        # Check close action
        if self.close_action and not callable(self.close_action):
            raise AttributeError('close_action must be callable or None.')
            
    def get_tab_by_id(self, id):
        for tab in self.tabs:
            try:
                if tab.id == id:
                    return tab
            except:
                pass
        
        return None
    
    def add(self, *args, title=None, view=None, id=None, locked=False, tab_close_action=None, bypass_close_action=False):
        if args:
            _allowed_arg = (dict, TabPageItem,)
            if any((not isinstance(i, _allowed_arg) for i in args)):
                raise AttributeError('Positinal arguments for add must be dict.')
            
            for tab in args:
                if isinstance(tab, TabPageItem):
                    self.tabs.append(tab)
                else:
                    self.tabs.append(TabPageItem(**tab))
        
        if all((title, view, id)):
            self.tabs.append(
                TabPageItem(
                    title=title,
                    view=view,
                    id=id,
                    locked=locked,
                    tab_close_action=tab_close_action,
                    bypass_close_action=bypass_close_action,
                )
            )
        elif not args:
            raise AttributeError('You must either provide dict as positional argument(s), or provide title, view, and id as keyword arguments.')
    
    def remove(self, id):
        for idx, tab in enumerate(self.tabs):
            if tab.id == id:
                self.tabs.pop(idx)
                self._draw_tabs()
    
    def close_tab(self, sender):
        id = sender.tab_id
        bypass = sender.bypass_close_action
        if self.close_action and not bypass: # Global Close Action
            tab = self.get_tab_by_id(id)
            ret = self.close_action(tab)
            # Get out if checking the return is req'd
            if self.close_action_check_return and not ret:
                return
                
        if self.confirm_close:
            if self.confirm():
                self.remove(id)
        else:
            self.remove(id)
        
    def confirm(self):
        return console.alert(self.confirm_heading, self.confirm_message, 'Ok')
    
                
    def _draw_tabs(self, sender=None):
        for tab in self.tab_view.subviews:
            self.tab_view.remove_subview(tab)
            pass
        
        if len(self.tabs) <= 0:
            return 
            
        tab_width = int(self.width / len(self.tabs))
        count = 0
        for tab in self.tabs:
            x = int(count * tab_width)
            
            self.tab_view.add_subview(
                self._mktab(tab, tab_width, x),
            )
            count += 1
            
    def _mktab(self, tab, width, tab_x=None, tab_close_action=None, bypass_close_action=False):
        assert isinstance(tab, TabPageItem), 'Invalid tab provided'
        
        t = ui.View(
            height=self.tab_height+2,
            width=width,
            x=0,
            y=-1, 
            border_width=0.5,
            border_color='#ccc',
        )
        
        if tab.id == 1:
            t.background_color='white'
        
        if tab_x:
            t.x = tab_x
        
        tab_label = ui.Label(
            font=self.tab_font,
            text=tab.title,
            #frame=t.frame,
            x=5,
            height=self.tab_height,
            alignment=ui.ALIGN_CENTER,
            flex='RTB',
            
        )
        
        close_image=ui.Image.named('iob:close_24')
        
        close_button = ui.Button(
            background_image=close_image,
            frame=((t.width-18), ((t.height-16)/2), 16, 16),
            flex='LTB',
            action=self.close_tab,
            
            # tab specific
            tab_id=tab.id,             # Used for closing
            tab_close_action=tab_close_action, # Run when closing
            bypass_close_action=bypass_close_action,
            
        )
        #tab_label.present()
        t.add_subview(tab_label),
        t.add_subview(close_button)
        
        return t
    
    def draw(self):
        self._draw_tabs()
        pass

if __name__ == '__main__':
    # Example of custom script when closing
    def custom_close(sender=None):
        console.hud_alert('Klikkity Klick Bitch!')
    
    def custom_tab_close(sender=None):
        console.hud_alert('You like this tab eh..')
    
    tpv = TabPageView(
        use_editor_theme=True, 
        confirm_close=True,
        close_action=custom_close,
        close_action_check_return=False,
    )
    tabs = [
        dict(
            title='Tab one',
            view=None,
            id=1
        ),
        dict(
            title='Tab Two',
            view=None,
            id=2
        ),
        dict(
            title='Tab Three',
            view=None,
            id=3
        )
    ]
    
    # Custom Tab
    tab4 = TabPageItem(
        title='Settings',
        view=None,
        id='settings',
        locked=False,
        tab_close_action=custom_close,
        bypass_close_action=True,
    )
    tpv.add(*tabs)
    tpv.add(tab4)
    tpv.present('sheet', title_bar_color='#eee')
