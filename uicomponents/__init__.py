# -*- coding: utf-8 -*-
"""
Copyright 2017-2018 Michael Ruggiero <michael@ruggiero.co>

Custom Pythonista ui view types:
  * "Drop Down" Style list box
  * Checkbox

Planned ui view types:
  * Combo box
  * Auto Suggest

  * Radio Group / 

  * Status Bar View 
  * Toolbar / Status Bar View
  * Tabbar View

View Helpers
  * BoxSizer (Horiz/Vert)
  * Spacer

"""
try:
    import ui
except ImportError:
    from .mobile_bridge import ui
    pass

from six import text_type

# TODO: Put all this into a module already

# TODO: Setup Simple (no bg button) style
# TODO: Figure out how to set styles
# TODO: Setup so it can drop UP instead if low on screen
# TODO: Allow user to click text box (optionally) to drop up/down
# TODO: Setup button to 'clear' results

"""
  * Make it able to drop "up" if the button is below 50%
"""

# Import other files

from tabview import TabView, TabButton
from cache import CacheView, CacheJSONEncoder


class TouchPanelView(ui.View):
    """
    Hack attempt at creating an overlay strictly for touch events
  
    Important: Remember to move views which you want to interact with in FRONT of this one!
    """

    def __init__(self, touch_action=None):
        self.background_color = None
        w, h = ui.get_screen_size()
        self.frame = (0, 0, w, h)
        self.alpha = .1

        self.touch_action = touch_action
        self.touch_args = []
        self.touch_kwargs = {}

    def touch_began(self, touch):
        # Called when a touch begins.
        if not isinstance(self.touch_args, list):
            self.touch_args = [self.touch_args]

        if self.touch_action is not None:
            self.touch_action(
                *self.touch_args,
                **self.touch_kwargs,
            )


class DropdownListData(ui.ListDataSource):
    def __init__(self, items):
        super(DropdownListData, self).__init__(items)
        self.move_enabled = False
        self.delete_enabled = False
        self.accessory_action = None

    def mkitem(self, item):
        self.items.append(item)
        self.reload()

    def rmitem(self, item):
        if item in self.items:
            return bool(self.items.pop(item, False))


class DropdownListView(ui.View):
    arrow_image = None

    def __init__(self, items, **kwargs):

        self.items = items

        self.name = 'dropdown'
        self.width = 200
        self.height = 32
        self.button_overlay = 4
        # self.background_color = '#fff'
        self.dropdown_presented = False

        self.touch_panel = TouchPanelView(self.hide_dropdown)

        # action
        self.action = None

        # Setup keyword args

        # self.value = kwargs.pop('default', None)
        self.arrow_style = kwargs.pop('arrow_style', None)
        self.dropdown_style = kwargs.pop('dropdown_style', None)

        # defaults

        # Default dropdown arrow image
        self.dropdown_arrow(
            'iob:arrow_down_b_24',
            dict(

            )
        )

        # Create Button
        self.dropdown_button = ui.Button()
        self.dropdown_button_style = dict(
            name='{0}_button'.format(self.name),
            width=32,
            height=32,
            background_color='#666',
            tint_color='#f7f7f7',
            # border_width=0.5,
            corner_radius=2,
            border_color='#d3d3d3',
            action=self.toggle_dropdown,
        )

        # Create TextField

        self.dropdown = ui.TextField()
        # self.dropdown.clear_button_mode='always'

        self.dropdown_tf_style = dict(
            name='{0}_field'.format(self.name),
            width=self.width,
            flex='WH',
            height=32,
            x=0,
            y=0,
            spellchecking_type=False,
            autocapitalization_type=False,
            enabled=False,
        )

        # Allow to override anything
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Setup TableView
        self.items_delegate = DropdownListData(self.items)
        self.items_delegate.action = self.select_item

        tv = ui.TableView()
        tv.allows_multiple_selection = False
        tv.row_height = 32
        tv.separator_color = self.dropdown.background_color
        tv.background_color = self.dropdown.background_color
        tv.delegate = self.items_delegate
        tv.data_source = self.items_delegate
        tv.corner_radius = 4

        self.list_view = tv

        self.add_subview(self.dropdown)
        self.add_subview(self.dropdown_button)

    def toggle_dropdown(self, sender):
        """
        Toggle the dropdown. Steps happening here:
    
        """
        if self.dropdown_presented:
            self.superview.remove_subview(self.touch_panel)
            self.superview.remove_subview(self.list_view)
            self.dropdown_presented = False
            self.update_interval = 0.0
        else:
            self.list_view.flex = 'T'
            self.list_view.border_width = 1
            self.list_view.border_color = '#eee'
            self.list_view.background_color = '#fff'
            # TODO: Move styling
            self.dropdown_presented = True
            self.update_interval = 0.3
            self.superview.add_subview(self.touch_panel)
            self.superview.add_subview(self.list_view)

        pass

    @property
    def text(self):
        return self.dropdown.text

    @text.setter
    def text(self, value):

        self.dropdown.text = value

    def hide_dropdown(self, sender=None):
        if self.dropdown_presented:
            self.toggle_dropdown(sender)
        pass

    @staticmethod
    def _set_style(view, style):
        assert isinstance(style, dict)

        try:
            for key, value in style.items():
                setattr(view, key, value)
        except AttributeError:
            pass

    def select_item(self, sender):
        val = self.items_delegate.items[sender.selected_row]
        if isinstance(val, str):
            self.dropdown.text = val
        elif isinstance(val, dict):
            self.dropdown.text = val['title']
        self.toggle_dropdown(sender)
        if callable(self.action):
            self.action(val)
        pass

    def reload(self, sender=None):
        self.list_view.reload()

    def draw(self):
        self._set_style(self.dropdown, self.dropdown_tf_style)
        self._set_style(
            self.dropdown_button,
            self.dropdown_button_style
        )
        self.dropdown_button.x = (
            self.width - self.dropdown_button.width
        )
        self.dropdown_button.image = self.arrow_image
        self.dropdown.width = (
            self.width - self.dropdown_button.width + self.button_overlay
        )

    def update(self):
        """
        Since I can't redraw based on layout change / rotation since it won't be the superview, I am checking on half second intervals, IF the dropdown is presented - it will refresh the layout
    
        The check here is just because I am too lazy to check performance. Setting the interval to 
        """

        if self.dropdown_presented:
            self.set_needs_display()

    def layout(self):
        # set the frame for the dropdown

        # calculate width
        w, h = ui.get_screen_size()

        # Max width, leave 10px from end of screen
        max_item_length = max(
            (len(i) for i in self.items_delegate.items)
        )

        max_width = min(
            ((w - self.x - 10), max_item_length)
        )

        max_height = min(
            self.list_view.row_height * len(self.items),
            (h - self.y - self.height - 75),
        )

        # set frame
        self.list_view.frame = (
            self.x,
            (self.y + self.height),
            max((self.width, max_width)),
            max_height
        )

    def dropdown_arrow(self, arrow, styles=None):
        if isinstance(arrow, ui.Image):
            self.arrow_image = arrow
        elif isinstance(arrow, text_type):
            self.arrow_image = ui.Image.named(arrow)

        if isinstance(styles, dict):
            for key, value in styles.items():
                setattr(self.arrow_image, key, value)

        return self


class TextFieldSuggest(ui.View):
    """
    Coming Soon - Auto-complete on ui.TextField()
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


"""
Checkbox
"""

import ui
from dialogs import _FormContainerView
from base64 import b64decode


class uiCheckbox(ui.View):
    checkboxes = {
        'checked': [
            'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYA',
            'AACqaXHeAAADoUlEQVR42u2bO4hTQRSG4xvf',
            'iA+00EICoiFx8yYGJDaCBATFKGIjVotbLIKN',
            'hbqoWFhYWPjARrFRtFqsRAvBQhDZtRAFQQQx',
            'rroLEcVH3Gz8f9C9IUySewibufckgcMuyZy5',
            '5//m3Jm5c2cC1Wq1oUUikTXxeDwfi8VOJxKJ',
            'YfxfhFU9bkXGypgZOzU002j8Eo7zUMkQ/pZZ',
            'qc+tTBjU5ApAMpnsQ+FROiuz0Wg0urUpABQ6',
            '6rS6SitToxEAW96F+Aqs5HGrtIJQmwnT93yT',
            'tP8IGwSgbehQFrO8l40xMlbGzNgb3Q7UPA2A',
            'HZ6pIL6/nUqlVrKMH42xU0MDbUMs83+oK5vE',
            's4AGawChTO1M/7wp7U0t7+dMaHA75AMcIw0/',
            'DNJRk1FTvU5qZ3oM1//ATkQbAGqq10ntAcP0',
            'tuKH3h5D2RbEehatuDeTySx0MzoYhshiwJD+',
            'Ja+Lh+j9iPNXTcyv0JqpVn7UVq/XbwCYyusN',
            'QmiTAHMuFArN1wyA8T5oMdMbSafTyzQCYKz9',
            'JtGGzu2aNgBM/Y2I7ZvLh57nqgDgMxut+til',
            'eI7vV1UBgPhjgkfeEjtKLQAofhNi+iFo/cNq',
            'RoFCoTAH8Tx1K54zO03zAMZ2QpD640j9tVoA',
            'MK4w7Lcg9Q/omAk6K1Qjgta/Qz9NAM4IxI/x',
            'eV8NAKRyHJ8/go5vN/1UAAgGgwtw/ZeC1r9B',
            'PzUA0JoXBOLfw5brAOCs2FQEAHbSTwMAxrAI',
            '9kYg/gr9NAG4JBD/FoseS+wCcOboDPwU19fb',
            'EL8DNuVS/BTWArfTzyYAit9XN1R9hoWlAWWz',
            '2aXweyeY7V2kny0AZvGOfUGAEWFA1wWp/5qr',
            'vx0BIBYvh8C6dgnET8LS9LMFgAFHXc7Qxp3X',
            'z2YLh8MrUO6DAMB5+tkEwHI3jcHJIRDmLUFd',
            'L7jU7S8AzvN5n2Guv0eyo8NQh/1bQGATtQKQ',
            'Favx3SeB/0mjGLudoBwC4f1r/XuCp7xnuVxu',
            'rkcAtA+Br60E5X+i/GaBOHsToRmy47yOVQAW',
            'ITzhixDrACxB+I7UD7Ju6wBsQID4AdbpCQCd',
            'hoA6HiL1Z3kGQIchfIVtYD0+BNA+BPgdob8/',
            'AbQP4T79dACQQ5iArVMCQA4BZQ6yrA4Acgh3',
            'WcY2gLY2SgpWfsbqrvFoZjZjyjdKdmKrLCGv',
            'gvXDLmOyc4ivwLyyVba3Wbrrt8t3/YGJrj8y',
            '0zs01Ts21zs42Ts62zs83cXH5/8CllkxCviA',
            'RtIAAAAASUVORK5CYII='],

        'unchecked': [
            'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAMA',
            'AACdt4HsAAAAQlBMVEX///8zMzMzMzMyMjIz',
            'MzMuLi4zMzMuLi4zMzM2NjYzMzMzMzM1NTUz',
            'MzM0NDQzMzM0NDQ0NDQxMTEzMzM1NTUzMzM6',
            '7LBrAAAAFXRSTlMA8Pp/SxbmCwUT0G86/bLn',
            'qIAvajBGafPqAAAAwElEQVR4Xu2XSw6DMAxE',
            'h/whaYBC7n/Vyi5IXZJ4V/ltsponR954cOGd',
            'raE9JFTrPH5Ju2mdGJtwg3NpAyxvXBymDWEO',
            'MOedf00Ped0GniF9519ziXhILHnl0JIA7Jzf',
            'ZnQxbxzbAW84j27YYDwczz+jm5l/4WDpyRgg',
            'U9Ki0lMwQKFkRaD9RQwQaZsBpJkwxETZvxSo',
            'QAUqUIEKVKACFahAfGiKT13xsS0+98WFQ1p5',
            'xKVLWvvExVNefeXlW1z/P5ukTB0BVFA1AAAA',
            'AElFTkSuQmCC']
    }

    def __init__(self, key, value=False, text=None, imgsize=26, **kwargs):

        def b64i(data):
            if isinstance(data, list):
                data = ''.join(data)

            d = b64decode(data)
            return ui.Image.from_data(d)

        # Strictly to make it fit in Pythonista
        def c(which):
            return self.checkboxes[which]

        def getopt(opt):
            pass

        unchecked = b64i(c('unchecked'))
        checked = b64i(c('checked'))

        # Checkbox Options


        self.value = value
        button = ui.Button()
        button.width = imgsize
        button.height = imgsize
        button.value = value
        button.flex = 'TBR'
        button.name = key
        button.tint_color = '#000'
        button.text = text

        state = {True: checked, False: unchecked}
        button.image = state[value]

        def chgbtn(sender):
            self.value = not self.value
            sender.image = state[self.value]

        button.action = chgbtn

        self.add_subview(button)

        if text:
            t = ui.Label()
            t.text = text
            tw = ui.measure_string(t.text, font=t.font)
            t.flex = 'W'
            bw = (imgsize + tw[0] + 5)
            t.x = imgsize + 5
            t.height = imgsize - round(imgsize / 10)
            self.add_subview(t)
            self.frame = (5, 5, bw, imgsize)
            self.height = 26


if __name__ == '__main__':
    # Drop Down
    v = ui.View()
    v.name = 'picker'
    v.flex = 'WH'
    v.background_color = '#fff'
    items = ['one', 'two', 'three', 'four', 'five', 'six',
             'seven', 'eight', 'none', 'ten']
    items = items + items
    dd = DropdownListView(items)
    dd.frame = (15, 10, 220, 32)
    
    # Add checkbox
    
    w, _ = ui.get_window_size()
    check1 = uiCheckbox('love_python',text='I love Python')
    check2 = uiCheckbox('is_nerdy', text='I am kind of nerdy..')
    check3 = uiCheckbox('hate_coding', text='I Hate Coding')
    check2.y = (check1.height + 10)
    check3.y = (check2.y + check2.height + 5)
    
    checkbox_holder = ui.View(
        frame=(5, 100, (w-10), 250),
        border_width=.5,
        background_color='#eeeeee'
    )
    checkbox_holder.add_subview(check1)
    checkbox_holder.add_subview(check2)
    checkbox_holder.add_subview(check3)
    
    v.add_subview(checkbox_holder)
    v.add_subview(dd)
    v.present()
