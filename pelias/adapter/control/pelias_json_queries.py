"""
query the response json from Pelias for various elements
"""


def has_features(rec):
    """
    check to see whether the call to pelias has any features
    NOTE: wrap with try except, since we might get funky 500 response objects from Pelias
    """
    ret_val = False
    try:
        if rec is not None and 'features' in rec and len(rec['features']) > 0:
            ret_val = True
    except Exception as e:
        log.debug(e)
        ret_val = False
    return ret_val


def get_element_value(dict, *prop_names):
    """ return value of first named element from a dictionary """
    ret_val = None
    for n in prop_names:
        v = dict.get(n)
        if v and len(v) > 0:
            ret_val = v
            break
    return ret_val


def append(str1, str2, sep=', '):
    """ append """
    if str1:
        if str2 and str2 not in str1:
            ret_val = "{}{}{}".format(str1, sep, str2)
        else:
            ret_val = str1
    else:
        ret_val = str2

    return ret_val


def append3(str1, str2, str3, sep1=', ', sep2=', '):
    ret_val = append(str1, str2, sep1)
    ret_val = append(ret_val, str3, sep2)
    return ret_val


def street_name(pelias_json, include_number=True, def_val=None):
    ret_val = def_val

    street = pelias_json.get('street')
    if street:
        ret_val = street

        if include_number:
            num = pelias_json.get('housenumber')
            if num:
                ret_val = "{} {}".format(num, street)

    return ret_val


def neighborhood_and_city(pelias_json, sep=', ', def_val=None):
    ret_val = def_val

    neighbourhood = pelias_json.get('neighbourhood')
    city = pelias_json.get('locality')
    if neighbourhood and city and city not in neighbourhood:
        ret_val = "{}{}{}".format(neighbourhood, sep, city)
    elif neighbourhood:
        ret_val = neighbourhood
    elif city:
        ret_val = city

    return ret_val


def city_neighborhood_or_county(properties, def_val=None):
    ret_val = def_val
    r = get_element_value(properties, 'locality', 'neighborhood', 'county')
    if r:
        ret_val = r
    return ret_val


def is_region_record(pelias_json):
    ret_val = False
    layer = pelias_json.get('layer')
    if layer in ('locality', 'neighbourhood', 'region', 'county'):
        ret_val = True
    return ret_val


def break_query_string_at_region(pelias_json, query_string, min_len=3):
    """
    Pelias Query string of 'text=834 SE Lambert St, WA' could return
    elements with 'WA', 'Washington', "Whatcom County", etc...
    """
    ret_val = query_string
    if query_string and len(query_string) > min_len:
        for n in ['name', 'locality', 'region_a', 'label', 'county_a', 'county']:
            val = pelias_json.get(n)
            if val in query_string:
                s = query_string.split()
                if s and len(s) > 1:
                    ret_val = s[0]
                    break
    return ret_val


def strip_region_from_query(pelias_json, query_string, min_len=3):
    """
    strip city (and state and zip) from query string
    idea is if you get region records, you'll strip region data out of your query string
    """
    ret_val = query_string
    if is_region_record(pelias_json):
        new_qs = break_query_string_at_region(pelias_json, query_string, min_len)
        if new_qs and len(new_qs) >= min_len:
            ret_val = query_string
    return ret_val
