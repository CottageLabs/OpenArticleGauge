"""
Contains the open access policy functions, which define what "open_access" is
based on the rights / requirements of an individual license.
"""

from copy import deepcopy
from openarticlegauge.licenses import LICENSES

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

    Example usage:
    license_info = {'BY': True, 'NC': True, 'SA': False, 'ND': False,
                        'type': 'cc-nc', 'name': 'Creative Commons NonComm.'}
    is_it_oa = oa_from_rights(**license_info)
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
    oa_from_rights. It just selects the appropriate license from the
    licenses module.
    """
    try:
        lic_info = deepcopy(LICENSES[lic_type])
    except KeyError:
        lic_info = {'NC': None, 'SA': None, 'ND': None}

    # we could *find* a license in LICENSES, but one with no rights defined at all
    # which would still break
    lic_info.setdefault('NC')
    lic_info.setdefault('SA')
    lic_info.setdefault('ND')

    return oa_from_rights(**lic_info)
