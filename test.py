#!/usr/bin/env python

import sys
sys.path.append('/usr/share/terminator')



import os
try:
    ORIGCWD = os.getcwd()
except OSError:
    ORIGCWD = os.path.expanduser("~")

# Check we have simple basics like Gtk+ and a valid $DISPLAY
try:
    import pygtk
    pygtk.require ("2.0")
    # pylint: disable-msg=W0611
    import gtk, pango, gobject

    if gtk.gdk.display_get_default() == None:
        print('You need to run terminator in an X environment. ' \
              'Make sure $DISPLAY is properly set')
        sys.exit(1)

except ImportError:
    print('You need to install the python bindings for ' \
           'gobject, gtk and pango to run Terminator.')
    sys.exit(1)

import terminatorlib.optionparse
from terminatorlib.terminator import Terminator
from terminatorlib.factory import Factory
from terminatorlib.version import APP_NAME, APP_VERSION
from terminatorlib.util import dbg, err

if __name__ == '__main__':
    dbus_service = None

    dbg ("%s starting up, version %s" % (APP_NAME, APP_VERSION))

    OPTIONS = terminatorlib.optionparse.parse_options()

    # Attempt to import our dbus server. If one exists already we will just
    # connect to that and ask for a new window. If not, we will create one and
    # continue. Failure to import dbus, or the global config option "dbus"
    # being False will cause us to continue without the dbus server and open a
    # window.
    try:
        if OPTIONS.nodbus:
            dbg('dbus disabled by command line')
            raise ImportError
        from terminatorlib import ipc
        import dbus
        try:
            dbus_service = ipc.DBusService()
        except ipc.DBusException:
            dbg('Unable to become master process, operating via DBus')
            # get rid of the None and True types so dbus can handle them (empty
            # and 'True' strings are used instead), also arrays are joined
            # (the -x argument for example)
            optionslist = {}
            for opt, val in OPTIONS.__dict__.items():
                if type(val) == type([]):
                    val = ' '.join(val)
                if val == True:
                    val = 'True'
                optionslist[opt] = val and '%s'%val or ''
            optionslist = dbus.Dictionary(optionslist, signature='ss')
            if OPTIONS.new_tab:
                dbg('Requesting a new tab')
                ipc.new_tab(optionslist)
            else:
                dbg('Requesting a new window')
                ipc.new_window(optionslist)
            sys.exit()
    except ImportError:
        dbg('dbus not imported')
        pass

    MAKER = Factory()
    TERMINATOR = Terminator()
    TERMINATOR.set_origcwd(ORIGCWD)
    TERMINATOR.set_dbus_data(dbus_service)
    TERMINATOR.reconfigure()
    try:
        dbg('Creating a terminal with layout: %s' % OPTIONS.layout)
        TERMINATOR.create_layout(OPTIONS.layout)
    except (KeyError,ValueError), ex:
        err('layout creation failed, creating a window ("%s")' % ex)
        TERMINATOR.new_window()
    TERMINATOR.layout_done()

    if OPTIONS.debug > 2:
        import terminatorlib.debugserver as debugserver
        # pylint: disable-msg=W0611
        import threading

        gtk.gdk.threads_init()
        (DEBUGTHREAD, DEBUGSVR) = debugserver.spawn(locals())
        TERMINATOR.debug_address = DEBUGSVR.server_address



    """
    Steve's stuff here!
    """
    terminator = TERMINATOR
    window = TERMINATOR.windows[0]

    t1 = window.get_children()[0]
    window.split_vert(t1)

    hp = window.get_children()[0]

    # Resizing tabs:
    # divider_x = hp.get_position()
    # hp.set_position(divider_x)
    # width = hp.get_length()
    # window.tab_change(window, num=1)

    # Renaming tabs:


    # tl = notebook.get_tab_label(notebook.get_children()[i]) i = 0, 1, ...
    # tl.label.set_custom()
    # tl.label.set_text('Hi there')
    # or even better:
    # tl.set_custom_label('Hi there')


    t2 = hp.get_child2()

    t1.feed('T1')
    t2.feed('T2')

    # You can do other trickery to create new tabs!
    window.tab_new()

    notebook = window.get_child()
    t3 = notebook.get_children()[1]

    t3.feed('T3')

    import IPython; IPython.embed()



    try:
        gtk.main()
    except KeyboardInterrupt:
        pass
