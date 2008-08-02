#file: listbox.py
#Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
#This file is part of Endgame: Singularity.

#Endgame: Singularity is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#Endgame: Singularity is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Endgame: Singularity; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#This file contains generic listbox code.

import pygame
import g
import scrollbar
from buttons import void, exit, always, Return, maybe_return, show_buttons

class listbox(object):
    def __init__(self, xy, size, viewable_items, lines_per_item, bg_color,
                    sel_color, out_color, font_color, font):
        self.xy = xy
        self.size = (size[0], size[1]-1)
        self.viewable_items = viewable_items
        self.lines_per_item = lines_per_item
        self.bg_color = bg_color
        self.sel_color = sel_color
        self.out_color = out_color
        self.font_color = font_color
        self.font = font


        self.list_surface = pygame.Surface((self.size[0], self.size[1]+1))

        #create outline
        self.list_surface.fill(out_color)


        #create inner containers:
        for i in range(viewable_items):
            self.list_surface.fill(bg_color,
                    (1, 1+i*self.size[1]/self.viewable_items,
                    self.size[0]-2, self.size[1]/self.viewable_items-1))

    def refresh_listbox(self, selected, lines_array):
        if len(lines_array) != self.viewable_items:
            print "CRASH WARNING: len(lines_array)="+str(len(lines_array))
            print "CRASH WARNING: self.viewable_items="+str(self.viewable_items)
            return False

        if selected >= self.viewable_items:
            print "Error in refresh_listbox(). selected =" + str(selected)
            selected = 0

        if len(lines_array) % (self.viewable_items*self.lines_per_item) != 0:
            print "Error in refresh_listbox(). len(lines_array)="+ \
                                str(len(lines_array))
            return False

        g.screen.blit(self.list_surface, self.xy)

        #selected:
        g.screen.fill(self.sel_color, (self.xy[0]+1,
                    self.xy[1]+1+selected*self.size[1]/self.viewable_items,
                    self.size[0]-2, self.size[1]/self.viewable_items-1))


        #text:
        txt_y_size = self.font.size("")
        for i in range(self.viewable_items):
            for j in range(self.lines_per_item):
                g.print_string(g.screen, lines_array[i*self.lines_per_item + j],
                        self.font, -1, (self.xy[0]+4, self.xy[1] +
                        (i*self.size[1]) / self.viewable_items +
                        j*(txt_y_size[1]+2)), self.font_color)
        return True

    def is_over(self, xy):
        if xy[0] >= self.xy[0] and xy[1] >= self.xy[1] and \
                    xy[0] <= self.xy[0] + self.size[0] \
                    and xy[1] < self.xy[1] + self.size[1]:
            return (xy[1]-self.xy[1])*self.viewable_items / self.size[1]

        return -1

    def key_handler(self, keycode, cur_pos, input_array):
        array_length = len(input_array)
        lastpos = cur_pos
        refresh = False
        if keycode == pygame.K_DOWN:
            cur_pos += 1
        elif keycode == pygame.K_UP:
            cur_pos -= 1
        elif keycode == pygame.K_HOME:
            cur_pos = 0
        elif keycode == pygame.K_END:
            cur_pos = array_length-1
        elif keycode == pygame.K_PAGEUP:
            cur_pos -= self.viewable_items
        elif keycode == pygame.K_PAGEDOWN:
            cur_pos += self.viewable_items

        if cur_pos >= array_length:
            cur_pos = array_length-1
        elif cur_pos <= 0:
            cur_pos = 0

        if input_array[cur_pos] == "" and (keycode == pygame.K_PAGEDOWN or
                keycode == pygame.K_END):
            for i in range(cur_pos, -1, -1):
                cur_pos = i
                if input_array[i] != "": 
                    break

        if lastpos != cur_pos: 
            refresh = True
        return cur_pos, refresh


def refresh_list(listbox, scrollbar, list_pos, list_array):
    success=listbox.refresh_listbox(list_pos%listbox.viewable_items,
        list_array[(list_pos/listbox.viewable_items)*
        listbox.viewable_items:(list_pos/listbox.viewable_items)*
        listbox.viewable_items+ listbox.viewable_items])
    if not success:
        print list_array
    if scrollbar:
        scrollbar.refresh_scroll(list_pos,
        ((len(list_array)/listbox.viewable_items)+1)*listbox.viewable_items-1)
    pygame.display.flip()

def resize_list(list, list_size = 10):
    if len(list) > 0:
        padding_needed = (-len(list) % list_size)
    else:
        padding_needed = list_size
    list += [""] * padding_needed

def sane_index(index, max_value, min_value = 0):
    """Return the closest int i to index such that min <= i < max."""
    if max_value <= min_value + 1:
        return min_value
    return min(max_value - 1, max(min_value, int(index + .5)))

def show_listbox(*args, **kwargs):
    # Set defaults.
    options = dict(
                 list_pos = 0, 
                 list_size = 10, 
                 lines_per_item = 1, 

                 loc = (g.screen_size[0]/2 - 300, 50),
                 box_size = (250,300), 

                 bg_color = g.colors["dark_blue"], 
                 sel_color = g.colors["blue"], 
                 out_color = g.colors["white"], 
                 font_color = g.colors["white"], 

                 font = g.font[0][18],

                 pos_callback = void, 
                 return_callback = void, 
                 button_callback = void,

                 escape_exit_code = -1
               )

    # Use any arguments given.
    options.update(kwargs)

    # Pass it on to _show_listbox, using the Return exception from the buttons
    # module.
    try:
        _show_listbox(*args, **options)
    except Return, e:
        return e.args[0]

# Lets us access a dict d by creating an object a such that:
# a.some_property == d["some_property"]
# a.some_property = 0  ->  d["some_property"] = 0
class Args(object):
    def __init__(self, dict):
        self.__dict__ = dict

def _show_listbox(list, buttons, **kwargs):
    kw = Args(kwargs)
    resize_list(list, kw.list_size)

    box = listbox(kw.loc, kw.box_size, kw.list_size, kw.lines_per_item, kw.bg_color, kw.sel_color, kw.out_color, kw.font_color, kw.font)
    scroll = scrollbar.scrollbar((kw.loc[0]+kw.box_size[0], kw.loc[1]), kw.box_size[1], kw.list_size, kw.bg_color, kw.sel_color, kw.out_color)

    def handle_key(event):
        key = event.key
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            maybe_return( kw.return_callback(kw.list_pos) )
        elif key in (pygame.K_ESCAPE, pygame.K_q):
            maybe_return( kw.escape_exit_code )

        kw.list_pos, refresh = box.key_handler(key, kw.list_pos, list)

    # Happily, using kw.list_pos instead of a local variable list_pos means that
    # we can safely assign to it from within a subfuction.
    def handle_click(event):
        if event.button == 1:
            selection = box.is_over(event.pos)
            if selection != -1:
                selection += kw.list_pos - (kw.list_pos % kw.list_size)
            else:
                selection = scroll.adjust_pos(event, kw.list_pos, list)

            if selection != -1:
                kw.list_pos = selection
        elif event.button == 4:  # Mouse wheel scroll down
            kw.list_pos -= 1
        elif event.button == 5:  # Mouse wheel scroll up
            kw.list_pos += 1

        kw.list_pos = sane_index(kw.list_pos, len(list))

    def give_list_pos():
        return (kw.list_pos,)

    def do_refresh():
        kw.pos_callback(kw.list_pos)
        refresh_list(box, scroll, kw.list_pos, list)

    raise Return, show_buttons(buttons, key_callback=handle_key, 
                               click_callback=handle_click, 
                               button_callback=kw.button_callback, 
                               button_args=give_list_pos, 
                               refresh_callback=do_refresh)