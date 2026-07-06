def diff_dicts(new_dict: dict, old_dict: dict):
    diff = {}
    # find all things in new that were different in old.
    # we will *not* check the case where something from old is missing from new, we assume
    # that in this case we don't want to change it.
    for k, v in new_dict.items():
        try:
            if isinstance(v, list):
                for entry in v:
                    if entry not in old_dict[k]:
                        diff[k] = v
                        continue
            if v != old_dict[k]:
                if v == '' and old_dict[k] is None or v is None and old_dict[k] == '':
                    continue
                diff[k] = v
        except KeyError:
            diff[k] = v
    return diff