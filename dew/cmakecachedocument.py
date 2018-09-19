import re
from typing import List, Dict, Iterable, Optional


cache_entry_pattern = re.compile(r'^\s*([^:]*)(?::(.*))?=(.*?)(\s*/{2}.*)?$')


class CMakeCacheEntry(object):
    def __init__(self) -> None:
        self.source_line = -1
        self.name = ''
        self.type = ''
        self.value = ''
        self.comment = ''


class CMakeCacheDocument(object):

    def __init__(self, lines: Iterable[str], entries: Iterable[CMakeCacheEntry]) -> None:
        self._lines: List[str] = list(lines)
        self._entries: Dict[str, CMakeCacheEntry] = {}
        for entry in entries:
            self._entries[entry.name] = entry

    def set_value(self, name: str, cmake_type: str, value: str) -> None:
        entry = self._entries.get(name)
        if entry is None:
            entry = CMakeCacheEntry()
            entry.source_line = len(self._lines)
            entry.name = name
            self._lines.append('')
            self._entries[name] = entry

        entry.type = cmake_type
        entry.value = value
        self._apply_entry(entry)

    def _apply_entry(self, entry: CMakeCacheEntry) -> None:
        text = '{0}:{1}={2}'.format(entry.name, entry.type, entry.value)
        self._lines[entry.source_line] = text

    @property
    def lines(self) -> List[str]:
        return list(self._lines)


def parse_cmake_cache(lines: Iterable[str]) -> Optional[CMakeCacheDocument]:
    entries: List[CMakeCacheEntry] = []

    for line_index, line in enumerate(lines):
        if line.strip().startswith('#'):
            continue

        match = cache_entry_pattern.match(line)
        if match is None:
            continue

        entry = CMakeCacheEntry()
        entry.source_line = line_index
        entry.name = match.group(1)
        entry.type = match.group(2)
        if entry.type is None:
            entry.type = ''
        entry.value = match.group(3)
        entry.comment = match.group(4)
        if entry.comment is None:
            entry.comment = ''

        entries.append(entry)

    doc = CMakeCacheDocument(lines, entries)
    return doc
