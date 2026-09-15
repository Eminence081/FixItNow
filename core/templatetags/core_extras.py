from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_STROKE = 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'

_ICONS_INNER = {
    "plumbing": '''<path d="M8 3v4a2 2 0 0 0 2 2h1v3"/>
        <path d="M15 8h3a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2h-1"/>
        <path d="M11 12v6a3 3 0 0 0 3 3h1"/>
        <circle cx="6" cy="5" r="2"/>
        <path d="M17 12v3"/>''',
    "electrical": '''<path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z"/>''',
    "cleaning": '''<path d="M9 3 6 6l9 9 3-3Z"/>
        <path d="M6 6 3 9l9 9 9-9-3-3"/>
        <path d="M12 15 6 21"/>''',
    "moving": '''<path d="M3 8h13l4 4v6H3Z"/>
        <path d="M3 8V5h9v3"/>
        <circle cx="7.5" cy="18.5" r="1.5"/>
        <circle cx="17.5" cy="18.5" r="1.5"/>''',
    "painting": '''<rect x="4" y="3" width="10" height="6" rx="1"/>
        <path d="M9 9v4a2 2 0 0 0 2 2h1"/>
        <rect x="12" y="14" width="4" height="7" rx="1"/>''',
    "appliance-repair": '''<path d="M14.7 6.3a1 1 0 0 0 1.4 0l1.6-1.6a4 4 0 0 1-5.4 5.4L4 18.4V20h1.6l8.3-8.3a4 4 0 0 1 5.4-5.4l-1.6 1.6a1 1 0 0 0 0 1.4Z"/>''',
    "gardening": '''<path d="M12 21c-4-1-7-4-7-9 5 0 8 3 9 7"/>
        <path d="M12 21c4-1 7-5 7-10-5 0-8 4-9 8"/>
        <path d="M12 21v-9"/>''',
    "carpentry": '''<path d="m4 15 8-8 3 3-8 8Z"/>
        <path d="m13 9 3-3 3 3-3 3"/>
        <path d="M4 15v5h5"/>''',
}

_ICONS = {
    slug: f'<svg viewBox="0 0 24 24" {_STROKE}>{inner}</svg>'
    for slug, inner in _ICONS_INNER.items()
}

_DEFAULT_ICON_INNER = '''<circle cx="12" cy="12" r="9"/>
    <path d="M12 8v4l3 2"/>'''
_DEFAULT_ICON = f'<svg viewBox="0 0 24 24" {_STROKE}>{_DEFAULT_ICON_INNER}</svg>'


@register.filter
def category_icon(slug):
    return mark_safe(_ICONS.get(slug, _DEFAULT_ICON))


@register.filter
def category_icon_paths(slug):
    """Inner <path>/<circle>/<rect> elements only, for embedding inside a
    caller-sized <svg> (e.g. positioned pins inside a larger illustration)."""
    return mark_safe(_ICONS_INNER.get(slug, ""))