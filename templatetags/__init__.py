from docutils.parsers import rst

import docutils_extensions

rst.roles.register_local_role('sci', docutils_extensions.sci_role)
rst.roles.register_local_role('atm', docutils_extensions.atm_role)
rst.roles.register_local_role('jargon', docutils_extensions.jargon_role)

# rst.roles.register_local_role('ref', docutils_extensions.ref_role)
# rst.roles.register_local_role('eqn', docutils_extensions.ref_role)
# rst.roles.register_local_role('tbl', docutils_extensions.ref_role)
# rst.roles.register_local_role('fig', docutils_extensions.ref_role)
# rst.roles.register_local_role('plt', docutils_extensions.ref_role)
# rst.roles.register_local_role('ani', docutils_extensions.ref_role)

rst.directives.register_directive('tbl', docutils_extensions.tbl_directive)
rst.directives.register_directive('fig', docutils_extensions.fig_directive)
rst.directives.register_directive('plt', docutils_extensions.plt_directive)
rst.directives.register_directive('ani', docutils_extensions.plt_directive)

# rst.directives.register_directive('tog', docutils_extensions.tog_directive)

