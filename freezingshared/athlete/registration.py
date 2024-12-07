from freezing.model import meta, orm



def register_athlete_team(strava_athlete, athlete_model):
    """
    Updates db with configured team that matches the athlete's teams.

    Updates the passed-in Athlete model object with created/updated team.

    :param strava_athlete: The Strava model object for the athlete.
    :type strava_athlete: :class:`stravalib.orm.Athlete`

    :param athlete_model: The athlete model object.
    :type athlete_model: :class:`bafs.orm.Athlete`

    :return: The :class:`bafs.orm.Team` object will be returned which matches
             configured teams.
    :rtype: :class:`bafs.orm.Team`

    :raise MultipleTeamsError: If this athlete is registered for multiple of
                               the configured teams.  That won't work.
    :raise NoTeamsError: If no teams match.
    """
    # TODO: This is redundant with freezingsaddles/freezing-sync which has a
    # very similar method in freezing/sync/data/athlete.py
    # Figure out how to DRY (Don't Repeat Yourself) for this code.

    all_teams = config.COMPETITION_TEAMS
    try:
        if strava_athlete.clubs is None:
            raise NoTeamsError(
                "Athlete {0} ({1} {2}): No clubs returned- {3}. {4}.".format(
                    strava_athlete.id,
                    strava_athlete.firstname,
                    strava_athlete.lastname,
                    "Full Profile Access required",
                    "Please re-authorize",
                )
            )
        matches = [c for c in strava_athlete.clubs if c.id in all_teams]
        athlete_model.team = None
        if len(matches) > 1:
            # you can be on multiple teams
            # as long as only one is an official team
            matches = [c for c in matches if c.id not in config.OBSERVER_TEAMS]
        if len(matches) > 1:
            raise MultipleTeamsError(matches)
        if len(matches) == 0:
            # Fall back to main team if it is the only team they are in
            matches = [c for c in strava_athlete.clubs if c.id == config.MAIN_TEAM]
        if len(matches) == 0:
            raise NoTeamsError(
                "Athlete {0} ({1} {2}): {3} {4}".format(
                    strava_athlete.id,
                    strava_athlete.firstname,
                    strava_athlete.lastname,
                    "No teams matched ours. Teams defined:",
                    strava_athlete.clubs,
                )
            )
        else:
            club = matches[0]
            # create the team row if it does not exist
            team = meta.scoped_session().query(Team).get(club.id)
            if team is None:
                team = Team()
            team.id = club.id
            team.name = club.name
            team.leaderboard_exclude = club.id in config.OBSERVER_TEAMS
            athlete_model.team = team
            meta.scoped_session().add(team)
            return team
    finally:
        meta.scoped_session().commit()
