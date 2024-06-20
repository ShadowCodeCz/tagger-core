import copy
import re


class ReFilterRule:
    def __init__(self):
        self.included = [[]]
        self.excluded = [[]]


class NoFilter:
    def filter(self, items):
        return items


class ReFilter:
    def __init__(self, rules):
        self.rules = rules

    def filter(self, items):
        included = self.include(items)
        return self.exclude(included)

    def include(self, items):
        result = []
        for item in items:
            for re_tags_and_group in self.rules.included:
                if all([self.match(tag_expression, item.tags) for tag_expression in re_tags_and_group]):
                    if not item in result:
                        result.append(item)
                        continue
        return result

    def exclude(self, items):
        if self.rules.excluded == [[]]:
            return items

        result = []
        for item in items:
            exclude = False
            for re_tags_and_group in self.rules.excluded:
                if all([self.match(tag_expression, item.tags) for tag_expression in re_tags_and_group]):
                    exclude = True
            if not exclude:
                if not item in result:
                    result.append(item)
        return result

    def match(self, tag_expression, tags):
        for tag in tags:
            if re.search(tag_expression, tag):
                return True
        return False


# class TaggedItem:
#     def __init__(self, path, tags):
#         self.path = path
#         self.tags = tags
#
#     @property
#     def mag(self):
#         for t in self.tags:
#             if "mag@" in t:
#                 return t


# items = [
#     TaggedItem("", ["mag@A", "proj@X"]), # IN
#     TaggedItem("", ["mag@B", "proj@Z"]),
#     TaggedItem("", ["mag@C", "proj@X", "abc@def"]), # IN
#     TaggedItem("", ["mag@D", "proj@X", "exclude"]),
#     TaggedItem("", ["mag@E", "proj@X", "ex1", "ex2"]),
#     TaggedItem("", ["mag@F", "proj@X", "ex1"]), # IN
#     TaggedItem("", ["mag@G", "proj@X", "ex3"]), # IN
#     TaggedItem("", ["mag@H", "proj@Y", "camp@U", "incl"]), # IN
#     TaggedItem("", ["mag@I", "proj@Y", "camp@U", "incl", "ex1", "ex2"]),
#     TaggedItem("", ["mag@J", "proj@Y", "camp@U"]),
# ]
#
# rule = ReFilterRule()
#
# # rule.included = [["proj@X"], ["proj@Y", "camp@U", "incl"]]
# # rule.excluded = [["exclude"], ["ex1", "ex2"]]
#
# rule.included = [[".*"]]
# rule.excluded = [[]]
#
# tag_filter = ReFilter(rule)
# result = tag_filter.filter(items)
# print("\n".join([r.mag for r in result]))


