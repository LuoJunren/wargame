#!/usr/bin/env python3

import pygame

from wargame.nodes import ImageNode
from wargame.loader import Resources
from wargame.gui.helpers import add_border


class BorderWidget(ImageNode):
    """
    A border widget is a widget that contains something (like a window)
    It must handle setting the x/y coords relative to itself
    """
    border_config = 'WindowBorder'

    def __init__(self, contents, xpos=-1, ypos=-1):
        self.container = contents
        # get the contents to render themselves
        self.container.build_image()
        border = Resources.configs.get(self.border_config)
        image = self.build_widget_display(border, self.container.image)
        if xpos < 0:
            xpos, ypos = Resources.get_centre(image.get_width(), image.get_height())
        rect = pygame.Rect(xpos, ypos, image.get_width(), image.get_height())
        super().__init__(rect, image)

    def update(self, time_delta):
        # we need to collect all of the dirty rects in all the nodes
        rects = self.get_dirty_rects(self.container, time_delta)
        # all of these rects are local to our node, and they
        # need to be reltive to the screen
        for rect in rects:
            rect.x += self.rect.x
            rect.y += self.rect.y
        return rects

    def get_dirty_rects(self, parent, time_delta):
        root = []
        try:
            nodes = parent.nodes
            # right, we have a tree, so we need to call
            # this function again for all those nodes
            for node in nodes:
                root.extend(self.get_dirty_rects(node, time_delta))
            return root
        except AttributeError:
            # this is a single node
            # we need to update OUR image if there is an update,
            # because the scene will ask us to draw, not this node
            rects = parent.update(time_delta)
            return self.update_widget_image(parent, rects)

    def update_widget_image(self, node, rects):
        # given a list of rects relative to the child node, update OUR image
        # return the rects relative to this border container
        border_coords = []
        for dirty in rects:
            # coords are relative based on the widget
            # add the nodes offsets to get the offset into our image
            tmp_rect = dirty.copy()
            tmp_rect.x += node.offset.x
            tmp_rect.y += node.offset.y
            self.image.blit(node.image, tmp_rect, dirty)
            border_coords.append(tmp_rect)
        return border_coords

    def handle(self, message):
        # pass the message to the container object, unless we
        # want to do something with this message first
        # we will need to adjust any coords against the window though:
        # widget co-ords are relative
        self.container.handle(message, self.rect)

    def build_widget_display(self, border, base_image):
        # base image has already been built at this point
        image = add_border(base_image, border, Resources.get_image(border.image))
        # only relative to the window
        # have to add widths and border AND screen position
        border_size = border.border_size
        deltax = border.rects.middle_left[2] + border_size
        deltay = border.rects.top_left[3] + border_size
        self.container.update_position(deltax, deltay)
        return image

    def build_image(self):
        pass


class Window(BorderWidget):
    """
    A gui widget with the border of a window
    """
    border_config = 'WindowBorder'
