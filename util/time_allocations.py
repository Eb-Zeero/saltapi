from flask import g
from data import sdb_connect
from util.action import Action
from util.multipartner import multipartner_ids


def check_time_allocations(allocations, partner, semester):
    if not g.user.may_perform(Action.UPDATE_TIME_ALLOCATIONS, partner, semester):
        raise Exception('You are not allowed to update the time allocations.')


def update_time_allocations(time_allocations, partner, semester):
    """
    Update the database with a list of time allocations.

    Parameters
    ----------
    time_allocations : iterable
        The list of time allocations. Each time allocation must be a dictionary with a proposal code, a priority
        and a time in seconds, such as `{'proposal_code': '2017-2-SCI-042', 'priority': 2, 'time': 2400}`.
    partner : str
        The partner code of the partner for whom the time allocations are updated.
    semester : str
        The semester, such as `2017-2` or `2018-1`, for which the time allocations are updated.

    """

    proposal_codes = [alloc['proposal_code'] for alloc in time_allocations]
    multipartner_id_map = multipartner_ids(proposal_codes, partner, semester)

    # TODO: Perform checks!
    check_time_allocations(time_allocations, partner, semester)

    # FIXME: hard-coded id
    moon_id = 6

    # list of values in the form '(proposal code, priority, time in seconds)
    values_list = ['({multipartner_id}, {priority}, {time}, {moon_id})'
                       .format(multipartner_id=int(multipartner_id_map[alloc['proposal_code']]),
                               priority=int(alloc['priority']),
                               time=int(alloc['time']),
                               moon_id=int(moon_id))
                   for alloc in time_allocations
                   if alloc['proposal_code'] in multipartner_id_map.keys()]
    sql = '''INSERT INTO PriorityAlloc (MultiPartner_Id, Priority, TimeAlloc, Moon_Id)
                    VALUES {values}
                    ON DUPLICATE KEY UPDATE
                        MultiPartner_Id=VALUES(MultiPartner_Id),
                        Priority=VALUES(Priority),
                        TimeAlloc=VALUES(TimeAlloc),
                        Moon_Id=VALUES(Moon_Id)'''.format(values=', '.join(values_list))

    comment_list = ['({multipartner_id}, {tac_comment})'
                        .format(multipartner_id=int(multipartner_id_map[alloc['proposal_code']]),
                                tac_comment=str(alloc['priority']))
                    for alloc in time_allocations
                    if alloc['proposal_code'] in multipartner_id_map.keys()]
    print("tac Comment", comment_list)

    tac_comment_sql = '''INSERT INTO TacProposalComment (MultiPartner_Id, TacComment)
                        VALUES {values}
                        ON DUPLICATE KEY UPDATE
                            MultiPartner_Id=VALUES(MultiPartner_Id),
                            TacComment=VALUES(TacComment)'''.format(values=', '.join(comment_list))
    connection = sdb_connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()
    finally:
        connection.close()

    return True