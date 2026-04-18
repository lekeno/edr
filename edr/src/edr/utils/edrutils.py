from edr.core.edri18n import _
import re


def pretty_print_number(number):
    """
    Format a number into a human-readable string with units (b, m, k).

    Args:
        number (int/float): The number to format.

    Returns:
        str: A localized string representation.
    """
    if number is None:
        return _("N/A")

    abs_number = abs(number)
    sign = "-" if number < 0 else ""

    if abs_number >= 1000000000:
        # Billions
        if abs_number >= 10000000000:
            return sign + _("{} b").format(int(abs_number // 1000000000))
        return sign + _("{:.1f} b").format(abs_number / 1000000000.0)

    if abs_number >= 1000000:
        # Millions
        if abs_number >= 10000000:
            return sign + _("{} m").format(int(abs_number // 1000000))
        formatted = _("{:.1f} m").format(abs_number / 1000000.0)
        if formatted.endswith(".0 m"):
             return sign + _("{} m").format(int(round(abs_number / 1000000.0)))
        return sign + formatted

    if abs_number >= 1000:
        # Kilos
        if abs_number >= 10000:
            return sign + _("{} k").format(int(abs_number // 1000))
        formatted = _("{:.1f} k").format(abs_number / 1000.0)
        if formatted.endswith(".0 k"):
            return sign + _("{} k").format(int(round(abs_number / 1000.0)))
        return sign + formatted

    return sign + _("{}").format(int(abs_number) if isinstance(abs_number, float) and abs_number.is_integer() else abs_number)


def simplified_body_name(star_system, body_name, empty_name_overrider=None):
    """
    Simplify a body name by removing the system name prefix.

    Args:
        star_system (str): Name of the star system.
        body_name (str): Full name of the body.
        empty_name_overrider (str, optional): Value to return if the simplified name is empty.

    Returns:
        str: Simplified body name string.
    """
    if star_system is None or body_name is None:
        return None
    if body_name.lower().startswith(star_system.lower()):
        # Example: Pleione A 1 A => a 1 a
        # Remove prefix + space
        return body_name[len(star_system) + 1:].lower() or (empty_name_overrider if empty_name_overrider else body_name)
    return body_name.lower()


def compare_versions(version1, version2):
    """
    Compare two version strings.

    Args:
        version1 (str): First version string (e.g., "1.0.0").
        version2 (str): Second version string.

    Returns:
        int: 1 if v1 > v2, -1 if v1 < v2, 0 if equal.
    """
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$', '', v).split(".")]

    return (normalize(version1) > normalize(version2)) - (normalize(version1) < normalize(version2))


def is_valid_semver(version):
    """
    Checks if the version string follows strict Semantic Versioning (Major.Minor.Patch).

    Args:
        version (str): The version string to check.

    Returns:
        bool: True if valid, False otherwise.
    """
    semver_pattern = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
    return bool(semver_pattern.match(version))
