## Utility classes/functions for MSMController

## Copyright 2013 James Crooks
## Released under the MIT License

class DictDiff(object):
    def __init__(self, old_dict, new_dict):
        self._old_dict = old_dict
        self._new_dict = new_dict
        self._keys_added = []
        self._keys_removed = []
        self._values_changed = []
        for key in old_dict:
            if key not in new_dict:
                self._keys_removed.append(key)
        for key in new_dict:
            if key not in old_dict:
                self._keys_added.append(key)
        for key in old_dict:
            self._current_key_value = new_dict.get(key,None)
            if self._current_key_value and old_dict[key] == self._current_key_value:
                self._values_changed.append((key, old_dict[key], new_dict[key]))
        
    @property
    def changes(self):
        self._changes = []
        for key in self._keys_added:
            self._changes.append(("Added", str(key), str(self._new_dict[key])))
        for key in self._keys_removed:
            self._changes.append(("Removed", str(key)))
        for entry in self._values_changed:
            self._changes.append("Changed", str(entry[0]), str(entry[1]), str(entry[2]))
    return self._changes

# Functional interface to DictDiff, using scoping rules to clean up the DictDiff object
# after it's no longer needed.
def dict_diff(old_dict, new_dict):
    comparer = DictDiff(old_dict, new_dict)
    return comparer.changes
