"""Extract raw data from a single IRC message."""

import datetime
import re
from typing import Optional

# precompiled regexes
_ANSI_ESCAPE = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
_TAB = re.compile("\t")


def escape_ansi(line: str) -> str:
    """Remove ANSI escape sequences logged by WeeChat."""
    return _ANSI_ESCAPE.sub("", line)


class IRCMessage:
    """A single IRC message with its metadata."""

    def __init__(self, msgstring: str):
        """Initialize the object."""
        try:
            self._timestr, self._prefix, self.body = _TAB.split(
                escape_ansi(msgstring), 2
            )
        except ValueError:
            raise ValueError(f"failed to parse line:\n{msgstring}")

    @property
    def timestamp(self) -> datetime.datetime:
        """Get the timestamp of the IRC message."""
        # timestamp_match = _TIMESTAMP_REGEX.match(self._timestr)
        try:
            return datetime.datetime.strptime(
                # mypy false positive: we handle the match being None
                self._timestr,  # type: ignore[union-attr]
                "%Y-%m-%d %H:%M:%S",
            )
        except AttributeError:
            raise ValueError(f"Failed to parse date string {self._timestr}")

    @property
    def msg_type(self) -> str:
        """Type of IRC message.

        See WeeChat Plugin API docs for prefixes and their meanings.
        """
        # if the prefix string isn't a nick, it's a special kind of message.
        # otherwise, it's a regular message
        try:
            return {
                "=!=": "error",
                "--": "network",
                " *": "action",
                "-->": "join",
                "<--": "quit",
                "": "other",
            }[self._prefix]
        except KeyError:
            return "message"

    @property
    def nick(self) -> Optional[str]:
        """Message nick, if one exists."""
        try:  # return the already-found nick if it exists
            return self._nick
        except AttributeError:  # extract nick from message and save it
            self._nick: Optional[str] = None
            if self.msg_type == "message":
                self._nick = self._prefix
            # the first word of an action's body is the nick
            elif self.msg_type == "action":
                self._nick = self.body.split(" ")[0]
            else:
                return None
            # remove the nick prefix if it exists
            if self._nick[0] in {"+", "%", "@", "~", "&"}:
                self._nick = self._nick[1:]
            # make nick lowercase since IRC nicks with different case
            # usually represent the same user.
            self._nick = self._nick.lower()
            return self._nick
