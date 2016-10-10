__author__ = 'jaime'
import sys
import threading
import time

# Third party imports.
import wx

class ProgressThread(threading.Thread):
    """A thread that does the work represented by a wx.ProgressDialog.
    It does the work and sends updates to the UI, so the end user can
    have some idea what the program is doing.
    To use, subclass and override the do_work generator.
    """

    # GRIPE A wx.ProgressDialog cannot adjust its number of steps after
    # creation. However, being able to create the dialog before we know how
    # many steps there actually are is very convenient - some threads might not
    # actually know how many steps they involve until a lot of processing has
    # been done. Thus, we assume that there are one million steps in any thread,
    # then internally subdivide it based on the number of actual steps do_work()
    # calculates.
    _max_num_steps = 1000000

    # Minimum time in milliseconds between attempts to update the progress
    # dialog. Set it to another value if you need to. If it's much lower,
    # you'll lock the main thread by flooding the dialog with update attempts.
    min_update_wait = 34

    def __init__(self, parent, title, msg, *args, **kwargs):
        """Create a thread tied to a progress dialog.
        The dialog is spawned when the thread starts running.
        `parent` is the window this subtask belongs to.
        `title` is the dialog's title.
        `msg` is the dialog's starting message.
        `args` and `kwargs` will be passed to self.do_work() as *args
        and **kwargs, allowing you to pass params to your background
        thread easily.
        """

        threading.Thread.__init__(self)

        self._parent = parent
        self._dialog = wx.ProgressDialog(title, msg, self._max_num_steps,
                                         style=wx.PD_CAN_ABORT)
        self._dialog.Center()
        self._dialog.Pulse()

        self._args = args
        self._kwargs = kwargs

        self._cancel_signal = False
        self._num_steps = None
        self._cur_step = None

        # The rate at which we step through the self._max_num_steps points
        # of progress available to us.
        self._stride = None
        # How far we are through the self._max_num_steps units in the progress
        # bar.
        self._cur_progress = None

        self._update_timestamp = None

        self._dialog.Bind(wx.EVT_BUTTON, self.handle_cancel_click)

    def _close_dialog(self, retCode):
        """Close this thread's dialog safely.
        `retCode` is required by ProgressDialog.EndModal(). I think it
        sets the result code returned by ShowModal(), but the docs don't
        actually make it clear.
        """

        wx.CallAfter(self._dialog.EndModal, retCode)
        wx.CallAfter(self._dialog.Destroy)

    def _success_cleanup(self):
        """Close the progress dialog and call do_success."""

        self.update_dialog(self._max_num_steps)
        self._close_dialog(wx.ID_OK)

        self.do_success(self._parent)

    def _cancel_cleanup(self):
        """Handle any post-cancellation cleanup.
        We hide the dialog and call the implemented cleanup method.
        """

        self._close_dialog(wx.ID_CANCEL)

        self.do_cancel(self._parent)

    def set_num_steps(self, num_steps):
        """Set the number of steps in this thread to `num_steps`.
        Sets self._cur_step to 0.
        """

        self._num_steps = num_steps
        self._cur_step = 0

        self._stride = int(self._max_num_steps / self._num_steps)
        self._cur_progress = 0

    def do_work(self, *args, **kwargs):
        """Generator that yields a summary of its next action as a str.
        Override this to implement your thread's innards.
        This is a good place to call self.set_num_steps() from.
        """

        raise Exception('This generator is not implemented.')

    def run(self):
        """Run this thread."""

        try:
            for next_step in self.do_work(*self._args, **self._kwargs):
                if self._cancel_signal:
                    self._cancel_cleanup()
                    return

                self._cur_step += 1
                self._cur_progress += self._stride
                self.update_dialog(self._cur_progress, next_step)

            self._success_cleanup()
        except Exception as exc:
            # GRIPE I'm not sure wx.ID_ABORT is a good way to say "we crashed".
            self._close_dialog(wx.ID_ABORT)

            # Rethrow this exception in the GUI thread, so our handler can
            # deal with it.
            exc_info = sys.exc_info()
            def rethrow(exc_info):
                raise exc_info[1], None, exc_info[2]
            wx.CallAfter(rethrow, exc_info)

    def update_dialog(self, step_num, msg=None):
        """Set this thread's progress to `step_num` and show `msg`.
        If `msg` is not passed, the message is not updated.
        If it has not been at least self.min_update_wait milliseconds
        since the last update to the dialog, the new update will be
        silently dropped.
        Otherwise, we may flood the GUI thread with events, and cause
        everything to freeze until this thread is done running. That
        would defeat the purpose of running things in a thread.
        This behavior is admittedly iffy - it might be better to look
        at how many updates are as yet unprocessed, and decide whether
        the current one should be sent based on that.
        That's harder, though, and might run too slowly to be usable.
        This appears to work.
        """

        cur_timestamp = time.time() * 1000
        if self._update_timestamp is not None:
            if cur_timestamp - self._update_timestamp < self.min_update_wait:
                return

        self._update_timestamp = cur_timestamp

        args = [self._dialog.Update, step_num]
        if msg is not None:
            args.append(msg)

        wx.CallAfter(*args)

    def do_cancel(self):
        """Perform any cleanup needed to properly cancel this thread.
        Subclasses should override this.
        For computations without side effects, `pass` is sufficient.
        Operations that modify the environment should use this to ensure
        the environment is left in the initial state.
        """

        raise Exception('This method is not implemented.')

    def handle_cancel_click(self, event):
        """Handle clicks on the dialog's Cancel button."""

        self.cancel()

    def cancel(self):
        """Ask this thread to stop running.
        A canceled thread should leave the environment as it was before it
        started. It is up to self.do_cancel() to ensure this is true.
        """

        self._cancel_signal = True

class Counter(ProgressThread):
    """A thread that counts to n slowly.
    This is meant as a simple example and test case - it has no use that
    I am aware of.
    """

    def do_work(self, n, cause_exception=False):
        """Count to `n` slowly.
        `cause_exception` can be set to True if you want to test
        exception handling.
        """

        self.n = n

        self.set_num_steps(n)
        for i in range(n):
            yield str(i + 1)

        if cause_exception is True:
            raise Exception('I am crashing on purpose.')

    def do_cancel(self, parent):
        """Explain what happened."""

        dialog = wx.MessageDialog(parent, 'You stopped me! Why?',
                                  'Not %s' % self.n)
        dialog.ShowModal()

    def do_success(self, parent):
        """Display a dialog."""

        dialog = wx.MessageDialog(parent, 'I counted to %s!' % self.n,
                                  'I Did It')
        dialog.ShowModal()


class ProgressFrame(wx.Frame):
    """Primitive demo of ProgressThread."""

    def __init__(self, parent, id):
        """Create the ProgressFrame."""

        wx.Frame.__init__(self, parent, id, 'Thread Test')

        self.btn = wx.Button(self, wx.ID_ANY, 'Start', pos=(0,0))

        self.btn.Bind(wx.EVT_BUTTON, self.OnStart)

    def OnStart(self, event):
        """Handle clicks on the Start button."""

        thread = Counter(self, 'Counting...', 'Initializing...', 1000000)
        thread.start()

class ProgressApp(wx.App):
    """App to demonstrate my ProgressThread."""

    def OnInit(self):
        """Initialize app."""

        self.frame = ProgressFrame(None, -1)
        self.frame.Show(True)
        self.frame.Center()
        self.SetTopWindow(self.frame)

        return True

def main():
    """Simple demo of using ProgressThread."""

    app = ProgressApp(0)
    app.MainLoop()

if __name__ == '__main__':
    main()