import graphene
from flask import g
from schema.partner import *
from schema.selectors import Selectors
from schema.proposal import *
from data.proposal import get_proposals
from data.partner import get_partners
from data.targets import get_targets
from data.selectors import get_selectors_data
from schema.instruments import *
from schema.user import UserModel
from schema.mutations import Mutations


class Query(graphene.ObjectType):
    proposals = Field(List(Proposals), semester=String(), partner_code=String(),
                      all_proposals=Boolean(), description="List of proposals per semester. Can be reduced to per "
                                                           "partner or per proposal. Semester must be provided in all "
                                                           "cases"
                      )
    targets = Field(List(Target), semester=String(), partner_code=String(), proposal_code=String(),
                    description="List of targets per semester can be reduced to per partner or per proposal. " 
                                " Semester must be provided in all cases")
    partner_allocations = Field(List(PartnerAllocations), semester=String(), partner_code=String(),
                                description="List of all allocations of SALT Partners")
    user = Field(UserModel)

    def resolve_proposals(self, info, semester=None, partner_code=None, all_proposals=False):
        if semester is None:
            raise ValueError("please provide argument \"semester\"")
        return get_proposals(semester=semester, partner_code=partner_code, all_proposals=all_proposals)

    def resolve_targets(self, info, semester=None, partner_code=None,):
        if semester is None:
            raise ValueError("please provide argument \"semester\"")
        return get_targets(semester=semester, partner_code=partner_code)

    def resolve_partner_allocations(self, info, semester=None, partner_code=None):
        if semester is None:
            raise ValueError("please provide argument \"semester\"")
        return get_partners(semester=semester, partner=partner_code)

    def resolve_user(self, info):
        return g.user


schema = graphene.Schema(query=Query, mutation=Mutations, types=[HRS, RSS, BVIT, SCAM])
