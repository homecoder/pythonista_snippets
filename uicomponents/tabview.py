# -*- coding: utf-8 -*-
"""
TabView

Copyright 2018 - Michael Ruggiero

Released under the MIT Open Source License

A clone of the iOS Tabbed Application, does not use   any objecive c bridges etc, only uses documented components.

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

TODO:
    * Options:
        * Enable/Disable Animation
        * Change animation type
    * Add better / more advanced animations
    * Either clean up the unnecessary additinal classes, OR
      continue with original idea, and set it all up so the
      develoer can subclass / customize any of the components
    * Add the option to use the objective-c bridge to use the
      original / Apple UI
      
    * Button Class:
        * Improve the button view to be a bit smarter
        * Allow text to go left/right/above or below image
        * Add inteligence for size of superview so text can
          be shrunk automatically if too big (optionally)
        * Split button class out to its own file
    
    Styling: 
        * Add styling and theming ability to all, allow 
          the use of the Pythonista themes.
        * Setup the Pythonista themespm
        * Build gradients using PIL for background(s)
        
    * Top Tabs:
        * Implement the tabs from the Pythonista editor:
            * Find examples on omz
        * Implement own version of tabs similar to the
          ones that are in Pythonista
        * Allow image backgrounds
    
    * Possible Helpful Links:
        * Composite (combine Button and Label)
            https://github.com/mikaelho/pythonista-composite/blob/master/README.md
        * ui animation franework
            https://github.com/mikaelho/scripter
        
"""

"""
Credits for some code used in this project:

https://forum.omz-software.com/topic/1935/how-can-i-convert-a-pil-image-to-a-ui-image/10

vertical line adapted from https://github.com/python-pillow/Pillow/issues/367
"""

import ui
import re
from cache import CacheView    # Cache the view state TODO:
from six import text_type
from six import BytesIO
from PIL import Image, ImageDraw

class AnimateView (object):
    """
    A set of transitional animations to be used with Pythonista's ui.View.add_subview()
    
    Use with Caution
    
    To use:
        # MainView is the superview
        MyNewView = ui.View()
        AnimateView(MyNewView).into(MainView).slide_up()
        # or
        #AnimateView(MyNewView, MainView).grow(.35) 
        # or
        av = AnimateView(MyNewView)
        av.remove_siblings=True
        av.slide_left()
        
    """

    def __init__(self, view, superview=None, remove_siblings=True):
        self.view = view
        self.superview = superview
        self.remove_siblings = remove_siblings
        self.siblings = []
    
    def into(self, superview):
        self.superview = superview
        return self
    
    def _siblings_cp(self):
        # get sublings - copy - not actual
        try:
            siblings = list(superview.subviews).copy()
        except:
            pass
            
            
    def slide_up(self, timer=0.25):
        """
        Modify the views position by taking its y coordinate
        and adding the full length of the window, then using
        the ui.Animate to bring it up.
        """
        assert isinstance(self.view, ui.View)
        assert isinstance(self.superview, ui.View)
        
        # Keeping this for a kater thought
        self._siblings_cp()
        
        self.view.y += self.superview.height
    
        self.superview.add_subview(self.view)
        
        def animation():
            self.view.y -= self.superview.height
            
        ui.animate(animation, timer)
        
        if self.remove_siblings:
            for sv in self.superview.subviews:
                if sv != self.view:
                    self.superview.remove_subview(sv)
    
    
    def slide_down(self, timer=0.25):
        assert isinstance(self.view, ui.View)
        assert isinstance(self.superview, ui.View)
        
        # Keeping this for a kater thought
        self._siblings_cp()
        
        self.view.y -= self.superview.height
    
        self.superview.add_subview(self.view)
        
        def animation():
            self.view.y += self.superview.height
            
        ui.animate(animation, timer)
        
        if self.remove_siblings:
            for sv in self.superview.subviews:
                if sv != self.view:
                    self.superview.remove_subview(sv)


    def slide_left(self, timer=0.25):
        assert isinstance(self.view, ui.View)
        assert isinstance(self.superview, ui.View)
        
        # Keeping this for a kater thought
        self._siblings_cp()
        
        self.view.x += self.superview.width
    
        self.superview.add_subview(self.view)
        
        def animation():
            self.view.x -= self.superview.width
            
        ui.animate(animation, timer)
        
        if self.remove_siblings:
            for sv in self.superview.subviews:
                if sv != self.view:
                    self.superview.remove_subview(sv)
        

    def slide_right(self, timer=0.25):
        assert isinstance(self.view, ui.View)
        assert isinstance(self.superview, ui.View)
        
        # Keeping this for a kater thought
        self._siblings_cp()
        
        self.view.x -= self.superview.width
    
        self.superview.add_subview(self.view)
        
        def animation():
            self.view.x += self.superview.width
            
        ui.animate(animation, timer)
        
        if self.remove_siblings:
            for sv in self.superview.subviews:
                if sv != self.view:
                    self.superview.remove_subview(sv)
        

    def fade_in(self, timer=0.5):
        assert isinstance(self.view, ui.View)
        assert isinstance(self.superview, ui.View)
        
        # Keeping this for a kater thought
        self._siblings_cp()
        
        # Set alpha to 0, then load subview
        
        self.view.alpha = 0.0
        self.superview.add_subview(self.view)
        
        def animation():
            self.view.alpha = 1.0
        
        ui.animate(animation, timer)
        
        if self.remove_siblings:
            for sv in self.superview.subviews:
                if sv != self.view:
                    self.superview.remove_subview(sv)



class TabButton(ui.View):
    """
    A ui.Button clone where the text appears below the image
    
    Contains:
        ui.Image
        ui.Label
    
    Set the frame or width/height, and optionally the space
    between the image and title, the image will be sized
    automatically.
    
    Initially designed to be used with the TabView class (below),
    but will create an Image Button and work exactly like a normal button.
    
    At this juncture I am too lazy lets see
    """

    def __init__(self,
                 render_mode=ui.CONTENT_SCALE_ASPECT_FIT,
                 **kwargs):

        self.action_valid = False

        self._image = ui.ImageView(y=5)
        self._image.content_mode = render_mode
        self._title = ui.Label(font=('<System>', 12))
        self._action = None
        self._enabled = True
        self.view = None

        self.render_mode = render_mode
        self.image = kwargs.pop('image', None)
        self.alpha = kwargs.pop('alpha', 1)
        # Used for enable/disable
        self._save_alpha = self.alpha
        self.enabled = kwargs.pop('enabled', True)
        self.action = kwargs.pop('action', None)
        # self.background_image = kwargs.pop('background_image', None)
        self.font = kwargs.pop('font', ('<system>', 12,))
        self.title = kwargs.pop('title', 'Button')

        self.width = kwargs.pop('width', 70)
        self.height = kwargs.pop('height', 70)

        # Set Padding, T, R, B, L ?
        # self.padding = (5,5,5,5,)

        self.title_pad = 5

        self.image_width = kwargs.pop(
            'image_width',
            self.width
        )

        self.image_height = kwargs.pop(
            'image_height',
            self.height
        )

        for k, v in kwargs.items():
            try:
                setattr(self, k, v)
            except AttributeError:
                pass

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        """
        Using a setter/property to easily validate that action is callable
        """
        if callable(value) or value is None:
            self._action = value
        else:
            raise AttributeError('action must be callable or None')

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        if self._enabled:
            self.alpha = self._save_alpha
            self.touch_enabled = True
        else:
            self.alpha = 0.4
            # noinspection PyAttributeOutsideInit
            self.touch_enabled = False

    @property
    def image_width(self):
        return self._image.width

    @image_width.setter
    def image_width(self, value):
        self._image.width = value

    @property
    def image_height(self):
        return self._image.height

    @image_height.setter
    def image_height(self, value):
        self._image.height = value

    @property
    def title(self):
        return self._title.text

    @title.setter
    def title(self, value):
        if value:
            self._title.text = value
        self._add_title()

    @property
    def image(self):
        return self._image.image

    @image.setter
    def image(self, value):
        # assert isinstance(value, ui.Image)
        if value:
            self._image.image = value.with_rendering_mode(self.render_mode)
        self._add_image()

    # noinspection PyPep8
    def _add_image(self):
        # remove any existing images
        try:
            for s in self.subviews:
                if isinstance(s, ui.Image):
                    self.remove_subview(s)
        except:
            pass

            # We have an image
        if isinstance(self._image, ui.ImageView):
            self.add_subview(self._image)

        self.set_needs_display()
        return

    def _add_title(self):
        try:
            for s in self.subviews:
                if isinstance(s, ui.Label):
                    self.remove_subview(s)
        except:
            pass

        # We have an image
        if isinstance(self._title, ui.Label):
            if self._title.text is not None:
                self.add_subview(self._title)
                pass

        self.set_needs_display()
        return

    def draw(self):
        # set the button height - hack for now
        try:
            self.height = (self.superview.height - 5)
        except:
            pass

        # set the image height without text
        if self.image:
            self._image.width = self.width
            self._image.height = self.height

        if self.title:
            w, h = ui.measure_string(self._title.text,
                                     font=self.font,
                                     alignment=ui.ALIGN_CENTER, )

            self._title.frame = (0, (self.height - h), self.width, h)
            try:
                self._image.height -= (h + self.title_pad)
            except:
                print('failed to set image height')
                pass

            try:
                # Setup the Text to center in the view
                self._title.width = self.width
                self._title.alignment = ui.ALIGN_CENTER
            except:
                pass

    def touch_began(self, touch):
        _ = touch  # Shadap IDE
        self.alpha = 0.3
        pass

    def touch_ended(self, touch):
        self.alpha = 1
        lw, lh = touch.location
        if 0 <= lw <= self.width and 0 <= lh <= self.height:
            self.action(self.view)


class TabControllerItem(object):
    _image = None
    _title = None
    _view = None
    _name = None

    def __init__(self, **kwargs):
        """
        Class Initializer
        """

        # Allow setting of properties via keyword arg
        self.image = kwargs.pop('image', None)
        self.title = kwargs.pop('title', None)
        self.view = kwargs.pop('view', None)
        self.name = kwargs.pop('name', None)
        self.action = kwargs.pop('action', None)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        if not any((isinstance(image, text_type),
                    isinstance(image, ui.Image),
                    image is None)):
            raise AttributeError('image must be one of: str, ui.Image, None')
        if isinstance(image, text_type):
            image = ui.Image.named(image)

        self._image = image

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        if title is not None and not isinstance(title, text_type):
            raise AttributeError('title must be one of: string or None')
        self._title = title

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, view):
        if not isinstance(view, ui.View) and view is not None:
            raise AttributeError('view must be a Pythonista View')

        self._view = view

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if name is not None:
            self._name = name
        elif self.title is not None:
            # Setup stuff here
            self._name = re.sub(r'([^\s\w_])+', '', self.title)
            self.name = self._name.replace(' ', '_')
        elif isinstance(self.image, ui.Image):
            self.name = id(self.image)
        else:
            self.name = id(self)

    @property
    def button(self):
        """
        Provide a button
        """
        button = TabButton(
            title=self.title,
            image=self.image,
            view=self.view,
            name=self.name,
            action=self.action,
        )
        return button


class TabController(object):
    """
    Tab Controller
    
    This is a helper class designed to further simplify the tab buttons. 
    """

    def __init__(self, action, *args, **kwargs):
        self.tabs = []
        self.action = action
        if args:
            for tab in args:
                if isinstance(tab, dict):
                    self.add(**tab)

        if kwargs:
            if 'tabs' in kwargs:
                tabs = kwargs['tabs']
                if isinstance(tabs, list):
                    for tab in tabs:
                        self.add(**tab)
        pass

    def add(self, image, title, view, name=None, order=0):
        """
        Add a(n) Button/Option to the Tab Controller.
        :param (str|ui.Image|None) image: The Image you wish to use
        :param (str|None) title: The title / text below the image - None for blank
        :param ui.View view: Pythonista View you wish to associate with the button
        :param str name: Name of the tab, See Below:
                         The name is used as an identifier, if it is not set, then it will automatically be set as:
                             1. The ui.View name, if not None
                             2. The title, lower(), with _ instead of spaces, punctuation removed, i.e.
                                Title: "Fav Thing's", Name: fav_things; if not None.                                
                             3. The image objects "id" - if not None; see Python's id()
                             4. The TabControllerItem's id; see Python's id()
        :param int order: Button Order, left to right. default is automatic
        :return self: Returns self to enable method chaining
        """
        item = TabControllerItem(
            image=image,
            title=title,
            view=view,
            name=name,
            action=self.action)

        self.tabs.append({
            'button': item,
            'order': order,
        })

        return self

    def remove(self, name=None, view=None):
        """
        This is not tested.
        """
        assert any((name, view,))
        for tab in self.tabs:
            if (name and tab.name == name) or (view and tab.view == view):
                self.tabs.pop(self.tabs.index(tab))


class TabView(ui.View):
    """
    A TabView Controller - This is a clone of the "iOS Tabbed Application" Layout
    
    This sets up a set of Tab Icons which can be used to switch views.
    """

    def __init__(self, tabs=None, height=75, **kwargs):
        w, h = ui.get_window_size()
        self.flex = 'WH'
        self.frame = (0, 0, w, h)
        self.tab_height = height
        self.name = 'Select Drink'
        self.view_index = []

        self.content_view = ui.View(
            name='content',
            frame=(0, 0, w, (h - height)),
            flex='WB',
        )

        self.tab_view = ui.View(
            background_color='#eee',
            frame=(0, (h - height), w, height),
            border_color='#ccc',
            border_width=0.5,
            flex='WT'
        )

        controller_options = dict(
            action=self.load_view,
        )

        if isinstance(tabs, list):
            controller_options['tabs'] = tabs

        self.controller = TabController(**controller_options)
        self.background_color = kwargs.pop('background_color', '#ffffff')

        # Add buttons

        button_width = int(self.width / len(self.controller.tabs))

        count = 0
        for tab in self.controller.tabs:
            vv = tab['button'].view
            self.view_index.append(vv)
            button = tab['button'].button
            button.x = (count * button_width)
            button.width = button_width
            button.y += 3
            self.tab_view.add_subview(button)

            if 0 < count < len(self.controller.tabs):
                sep = ui.ImageView(
                    image=self.separator(),
                    frame=((count * button_width), 0, 3, 70)
                )
                self.tab_view.add_subview(sep)
            count += 1

        # add components as subviews
        if len(self.controller.tabs) > 0:
            # Use first tab as default view for now
            default_view = self.controller.tabs[0]['button'].view
            self.content_view.add_subview(
                default_view

            )

        self.add_subview(self.content_view)
        self.add_subview(self.tab_view)

    def draw(self):
        w, h = self.width, self.height
        height = self.tab_height
        self.content_view.frame = (0, 0, w, (h - height))
        for view in self.content_view.subviews:
            view.frame = self.content_view.frame

    def load_view(self, view):
        """
        Remove other subviews and plug in requested one
        """
        last_subview = None
        for v in self.content_view.subviews:
            if v == view:
                return
                
            last_subview = v
            #self.content_view.remove_subview(v)
        

        view.frame = self.content_view.frame
        self.name = view.name
        
        if last_subview:
            if last_subview == view:
                return 
            
            lsi = self.view_index.index(last_subview)
            csv = self.view_index.index(view)
            
            if lsi < csv:
                AnimateView(
                    view
                ).into(
                    self.content_view
                ).slide_left()
            else:
                AnimateView(
                    view
                ).into(
                    self.content_view
                ).slide_right()
        else:
            AnimateView(
                view
            ).into(
                self.content_view
            ).slide_right()
            
        #self.content_view.add_subview(view)

    def separator(self):
        img = Image.new('RGB', (4, 80), self.hex_to_rgb('#eeeeee'))
        draw = ImageDraw.Draw(img)
        draw.line((1.5, 10, 1.5, 75), self.hex_to_rgb('#dedede'), 1)
        return self.pil_to_ui_image(img)

    @staticmethod
    def hex_to_rgb(value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    @staticmethod
    def rgb_to_hex(rgb):
        return '#%02x%02x%02x' % rgb

    @staticmethod
    def pil_to_ui_image(ip):
        with BytesIO() as bIO:
            ip.save(bIO, 'PNG')
            img = ui.Image.from_data(bIO.getvalue())
            img = img.with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
            return img


if __name__ == '__main__':
    """
    Main View App
    """


    def viewlabel(label_text):
        w, h = ui.get_window_size()
        lh = (h - 60) / 2 - 5
        lbl = ui.Label(
            x=0,
            y=lh,
            text=label_text,
            name=label_text,
            alignment=ui.ALIGN_CENTER,
        )

        return lbl


    beer = viewlabel('Beer')
    wine = viewlabel('Wine')
    beaker = viewlabel('Beaker')

    tabs = [{
        'name': 'beer',
        'title': 'Beer',
        'image': ui.Image.named('iob:beer_32'),
        'view': beer,
    }, {
        'name': 'wine',
        'title': 'Wine',
        'image': ui.Image.named('iob:wineglass_32'),
        'view': wine,
    }, {
        'name': 'beaker',
        'title': 'Beaker',
        'image': ui.Image.named('iob:beaker_32'),
        'view': beaker,
    }]

    main = TabView(tabs=tabs, height=65)
    main.present()
