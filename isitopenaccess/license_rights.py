"""
Lists what licenses grant what rights:
BY - Attribution required
NC - NonCommercial restriction
SA - ShareAlike requirement
ND - NoDerivatives restriction
"""

LICENSES_RIGHTS = {
    'cc-by': {
        'BY': True,
        'NC': False,
        'SA': False,
        'ND': False
    },
    'cc-nc': {
        'BY': True,
        'NC': True,
        'SA': False,
        'ND': False
    },
    'plos-who': {
        'BY': True,
        'NC': None, # unknown - we can't decide
        'SA': False,
        'ND': False
    },
    'cc-zero': {
        'BY': False,
        'NC': False,
        'SA': False,
        'ND': False
    },
    'uk-ogl': {
        'BY': True,
        'NC': False,
        'SA': False,
        'ND': False
    },
}

def oa_from_rights(NC, SA, ND, **kwargs):
    """
    Determine whether a license is Open Access from the rights it grants or
    denies.
    :param NC: NonCommercial restriction
    :param SA: ShareAlike requirement
    :param ND: NoDerivatives restriction
    
    The additional keyword arguments are ignored. They are accepted simply for
    the caller's convenience - because the definition of NC, SA and ND usually
    comes with other information, such as the definition of BY (the Attribution
    requirement).
    """
    if NC is None or SA is None or ND is None:
    # just can't make a decision without knowing all of these, assume not OA
        return False

    return not NC and not SA and not ND

def oa_for_license(lic_type):
    """
    Determine whether a license is Open Access-compliant according to the
    known rights it grants / restricts.

    This function is essentially a convenience wrapper around
    oa_from_rights which just selects the appropriate license from the
    LICENSES_RIGHTS dictionary.
    """
    return oa_from_rights(**LICENSES_RIGHTS[lic_type])
