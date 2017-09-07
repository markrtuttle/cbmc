/*******************************************************************\

Module:

Author: Daniel Kroening, kroening@kroening.com

\*******************************************************************/

#ifndef CPROVER_UTIL_PLATFORM_TYPES_H
#define CPROVER_UTIL_PLATFORM_TYPES_H

#include "std_types.h"

// in brief, the blow correspond to 'int'
signedbv_typet signed_word_type();
unsignedbv_typet unsigned_word_type();

// size of any object held
unsignedbv_typet size_type();

pointer_typet pointer_type(const typet &);

#endif // CPROVER_UTIL_PLATFORM_TYPES_H
