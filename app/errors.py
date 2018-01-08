from discord.ext import commands


class DuplicateArtist(commands.CommandError):
    """
    Exception raised when an artist already exists in database
    """
    pass

class MissingArtist(commands.CommandError):
    """
    Exception raised when an artist doesn't exist in database
    """
    pass

class NoTagFound(commands.CommandError):
    """
    Exception raised when tag was not found
    """
    pass

class TagAlreadyExists(commands.CommandError):
    """
    Exception raised when tag already exists
    """
    pass
    