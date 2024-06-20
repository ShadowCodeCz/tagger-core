
class TagParser:
    def parse(self, raw_tag):
        parts = raw_tag.split("@")
        return Tag(parts[0], parts[1] if len(parts) > 1 else None)


class TagsParser:
    # TODO: Multiple tags jira.ticket@
    tag_parser = TagParser()

    def parse(self, raw_tags):
        index = {}

        for raw_tag in raw_tags:
            t = self.tag_parser.parse(raw_tag)
            index[t.name] = t

        return index


class TagsReader:
    # TODO: Multiple tags jira.ticket@
    def __init__(self, parsed_tags):
        self.tags_index = parsed_tags

    def read_tag_value(self, tag_name):
        if tag_name in self.tags_index:
            return self.tags_index[tag_name].value
        else:
            return None


class Tag:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f"{self.name}@{self.value}"