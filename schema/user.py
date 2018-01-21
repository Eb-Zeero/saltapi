from graphene import Enum, ObjectType, String, List, Field
from util.action import Action

class RoleType(Enum):
    """
    An enumeration of all the available roles a user can have.
    """

    ADMINISTRATOR = 1
    SALT_ASTRONOMER = 2
    TAC_MEMBER = 3
    TAC_CHAIR = 4

    @property
    def description(self):
        if self == RoleType.ADMINISTRATOR:
            return 'Site administrator'
        elif self == RoleType.SALT_ASTRONOMER:
            return 'SALT Astronomer'
        elif self == RoleType.TAC_MEMBER:
            return 'Member of a Time Allocation Committee'
        elif self == RoleType.TAC_CHAIR:
            return 'Chair of a Time Allocation Committee'
        else:
            return str(self)


class Role(ObjectType):
    type = RoleType()
    partners = Field(List(String))

    def resolve_type(self, *args, **kwargs):
        return self.type.value


class UserModel(ObjectType):
    first_name = String()
    last_name = String()
    email = String()
    username = String()
    role = Field(List(Role))

    def has_role(self, role, partner):
        """
        Check whether this user has a role for a partner.

        Parameters
        ----------
        role : RoleType or int
            The role, such as `TAC_CHAIR` or `SALT_ASTRONOMER`.
        partner
            The partner for which the role is checked.

        Returns
        -------
        hasrole: bool
            Bool indicating whether this user has the role for the partner.
        """

        return any(r.type == role and partner in r.partners for r in self.role)

    def may_perform(self, action, **kwargs):
        """
        Check whether this user may perform an action.

        Parameters
        ----------
        action : util.Action
            The action.
        kwargs : kwargs
            Any additional required arguments, which depend on the action.

        Returns
        -------
        mayperform : bool
            Bool indicating whether this user may perform the action.
        """

        partner = kwargs.get('partner')

        if action == Action.UPDATE_TIME_ALLOCATIONS:
            return self.has_role(RoleType.ADMINISTRATOR, partner)\
                   or self.has_role(RoleType.TAC_CHAIR, partner)

        return False
