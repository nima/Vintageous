from Vintageous.vi.constants import MODE_NORMAL


class CmdData(dict):
    # vi_cmd_data is a key data structure that drives the action/motion execution.
    # Keys and values must be valid JSON data types, because the data structure ends up being an
    # argument to an ST command.
    def __init__(self, state):
        self['pre_motion'] = None
        self['motion'] = {}
        # Whether the user needs to provide a motion. If there is no user-provided motion, a
        # motion specified by an action could still be run before the action.
        self['motion_required'] = True
        self['action'] = {}
        self['post_action'] = None
        self['count'] = state.count
        # Helps to disambiguate between invocations that behave differently depending on whether
        # the user provided a count or not (for example, %).
        self['_user_provided_count'] = state.user_provided_count
        self['pre_every_motion'] = None
        self['post_every_motion'] = None
        # This is the only hook that takes a list of commands to execute.
        # Specify commands as a list of [command, args] elements (don't use tuples).
        self['post_motion'] = []
        # Set to True if the command must be able to populate the registers. This will cause
        # Vintageous to propagate copied text to the unnamed register as needed.
        self['can_yank'] = False
        # Some commands operate CHARACTERWISE but always yank LINEWISE, so we need this.
        self['yanks_linewise'] = False
        # We set this to the user-supplied information.
        self['register'] = state.register
        self['mode'] = state.mode
        self['reposition_caret'] = None
        self['follow_up_mode'] = None
        # Some digraphs can be computed on their own, like cc and dd, but others require an
        # explicit "wait for next command name" status, like gU, gu, etc. This property helps
        # with that.
        self['is_digraph_start'] = False
        # User input, such as arguments to the t and f commands.
        # TODO: Try to unify user-input collection (both for registers and this kind of
        # argument).
        self['user_input'] = state.user_input
        # TODO: Interim solution to avoid problems with this step. Many commands don't need
        # this and it's causing quite some trouble. Let commands specify an explicit command
        # to reorient the caret as occurs with other hooks.
        self['__reorient_caret'] = False
        # Whether the motion is considered a jump.
        self['is_jump'] = False
        # Some actions must be cancelled if the selections didn't change after the motion.
        # Others, on the contrary, must always go ahead.
        self['cancel_action_if_motion_fails'] = False
        # Some commands that don't take motions need to be repeated, but currently ViRun only
        # repeats the motion, so tell global state to repeat the action. An example would be
        # the J command.
        self['_repeat_action'] = False
        # Search string used last to find text in the buffer (like the / command).
        self['last_buffer_search'] = state.last_buffer_search
        # Search character used last to find text in the line (like the f command).
        self['last_character_search'] = state.last_character_search
        # Whether we want to save the original selections to restore them after the command.
        self['restore_original_carets'] = False
        # We keep track of the caret's x position so vertical motions like j, k can restore it
        # as needed. This item must not ever be reset. All horizontal motions must update it.
        # Vertical motions must adjust the selections .b end to factor in this data.
        self['xpos'] = state.xpos
        # Indicates whether xpos needs to be updated. Only vertical motions j and k need not
        # update xpos.
        self['must_update_xpos'] = True,       
        # Whether we should make sure to show the first selection.
        self['scroll_into_view'] = True
        # If not None, the corresponding mode will be entered before runnig ViRun.
        # It's basically used as a way to change to NORMALMODE and be able to capture further
        # key strokes for INSERTMODE chords. Use sparingly.
        # Used, for example, by CTRL+R,= in INSERTMODE.
        self['_change_mode_to'] = None
        # If not None, the corresponding mode will be entered during the full run of a command, in
        # some cases. Used to know which mode to transition to after a failed composite command.
        # Note this is mainly useful to exit from bad corrupted states; successful commands should
        # instead specify their 'follow_up_mode' hook.
        # For example, in INSERTMODE, Ctrl+R,j would cause VintageState to use this.
        self['_exit_mode'] = None
        self['must_blink_on_error'] = False
        # Mode to transition to on success.
        self['next_mode'] = MODE_NORMAL
