# Pythonista Snippets

This repository contains snippets of code that I have created for Pythonista.

I've had full intentions of wrapping this stuff into a module, however work has been a little busy, so I figured I would start to release what I can.

Many of these snippets are a work-in-progress and have been developed to server a particular purpose for myself; however if anyone is interested in seeing something developed further please create an issue and I will be happy to prioritize it.

## Contents

**github_downloader**

Simple ui script which accepts a GitHub username and repository name to download the repo as a zip file.

**uicomponents**

Dropdown / Checkbox

A *very* early stage implemention of a "Drop Down" / List Box for Pythonista, add it as a subview to your main view - don't create a container view restricted to the size of the drop down, else it won't work as it stands.

Note: It creates a transparent view which covers the entire superview of the combo box, to allow the user to tap outside of the drop down to dismiss, and not accidently tap another function.

Example provided at the bottom of the file.

The checkbox class is also quite simple, it is a view which wraps a button which switches between two images (unchecked, and checked) with access methods to get the state.

## License

The code here is licensed under the MIT License.  See the LICENSE file for more information.

## Open Source Word

I love open source, if you profit from any of my code at any point, and you can't release or contribute back to the open source community, please make a donation to a charity in need.

You are under absolutely no obligation to; and I have chosen the MIT license for that very reason, no obligation. However, you should, and you know it.