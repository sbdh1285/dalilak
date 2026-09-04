"""محتوى المقالات الموسّع لمراجعة الجودة."""
from .knowledge import BODIES as KNOWLEDGE
from .home import BODIES as HOME
from .recipes import BODIES as RECIPES
from .tech import BODIES as TECH

BODIES = {}
BODIES.update(KNOWLEDGE)
BODIES.update(HOME)
BODIES.update(RECIPES)
BODIES.update(TECH)
