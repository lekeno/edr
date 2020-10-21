from __future__ import absolute_import

from sys import platform
import os.path

import utils2to3

if platform == 'darwin':

    from AppKit import NSSound

    class AudioFeedback(object):

        def __init__(self):
            self.snd_warn = NSSound.alloc().initWithContentsOfFile_byReference_(utils2to3.abspathmaker(__file__, 'sounds', 'snd_warn.wav'), False)
            self.snd_notify = NSSound.alloc().initWithContentsOfFile_byReference_(utils2to3.abspathmaker(__file__, 'sounds', 'snd_notify.wav'), False)

        def soft(self):
            self.snd_warn = NSSound.alloc().initWithContentsOfFile_byReference_(utils2to3.abspathmaker(__file__, 'sounds', 'snd_warn_soft.wav'), False)
            self.snd_notify = NSSound.alloc().initWithContentsOfFile_byReference_(utils2to3.abspathmaker(__file__, 'sounds', 'snd_notify_soft.wav'), False)

        def loud(self):
            self.snd_warn = NSSound.alloc().initWithContentsOfFile_byReference_(utils2to3.abspathmaker(__file__, 'sounds', 'snd_warn.wav'), False)
            self.snd_notify = NSSound.alloc().initWithContentsOfFile_byReference_(utils2to3.abspathmaker(__file__, 'sounds', 'snd_notify.wav'), False)

        def warn(self):
            self.snd_warn.play()

        def notify(self):
            self.snd_notify.play()


elif platform == 'win32':
    import winsound

    class AudioFeedback(object):
        def __init__(self):
            self.snd_warn = utils2to3.abspathmaker(__file__, 'sounds', 'snd_warn.wav')
            self.snd_notify = utils2to3.abspathmaker(__file__, 'sounds', 'snd_notify.wav')


        def soft(self):
            self.snd_warn = utils2to3.abspathmaker(__file__, 'sounds', 'snd_warn_soft.wav')
            self.snd_notify = utils2to3.abspathmaker(__file__, 'sounds', 'snd_notify_soft.wav')


        def loud(self):
            self.snd_warn = utils2to3.abspathmaker(__file__, 'sounds', 'snd_warn.wav')
            self.snd_notify = utils2to3.abspathmaker(__file__, 'sounds', 'snd_notify.wav')


        def warn(self):
            winsound.PlaySound(self.snd_warn, winsound.SND_ASYNC)


        def notify(self):
            winsound.PlaySound(self.snd_notify, winsound.SND_ASYNC)


else:
    class AudioFeedback(object):
        def soft(self):
            pass

        def loud(self):
            pass

        def warn(self):
            pass

        def notify(self):
            pass
