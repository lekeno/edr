def pretty_print_number(number):
    readable = u""
    if number is None:
        return _(u"N/A")
    if number >= 10000000000:
        # Translators: this is a short representation for a bounty >= 10 000 000 000 credits (b stands for billion)  
        readable = _(u"{} b").format(number // 1000000000)
    elif number >= 1000000000:
        # Translators: this is a short representation for a bounty >= 1 000 000 000 credits (b stands for billion)
        readable = _(u"{:.1f} b").format(number / 1000000000.0)
    elif number >= 10000000:
        # Translators: this is a short representation for a bounty >= 10 000 000 credits (m stands for million)
        readable = _(u"{} m").format(number // 1000000)
    elif number >= 1000000:
        # Translators: this is a short representation for a bounty >= 1 000 000 credits (m stands for million)
        readable = _(u"{:.1f} m").format(number / 1000000.0)
    elif number >= 10000:
        # Translators: this is a short representation for a bounty >= 10 000 credits (k stands for kilo, i.e. thousand)
        readable = _(u"{} k").format(number // 1000)
    elif number >= 1000:
        # Translators: this is a short representation for a bounty >= 1000 credits (k stands for kilo, i.e. thousand)
        readable = _(u"{:.1f} k").format(number / 1000.0)
    else:
        # Translators: this is a short representation for a bounty < 1000 credits (i.e. shows the whole bounty, unabbreviated)
        readable = _(u"{}").format(number)
    return readable

def simplified_body_name(star_system, body_name, empty_name_overrider=None):
    if star_system is None or body_name is None:
        return None
    if body_name.lower().startswith(star_system.lower()):
        # Example: Pleione A 1 A => a 1 a
        # Remove prefix + space
        return body_name[len(star_system)+1:].lower() or (empty_name_overrider if empty_name_overrider else body_name)
    return body_name.lower()
