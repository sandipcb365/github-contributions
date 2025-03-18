#!/usr/bin/env python
import argparse
import os
from datetime import datetime, timedelta
from random import randint
from subprocess import Popen
import sys


def main(def_args=sys.argv[1:]):
    args = arguments(def_args)
    curr_date = datetime.now()
    directory = 'repository-' + curr_date.strftime('%Y-%m-%d-%H-%M-%S')
    repository = args.repository
    user_name = args.user_name
    user_email = args.user_email

    if repository is not None:
        start = repository.rfind('/') + 1
        end = repository.rfind('.')
        directory = repository[start:end]

    no_weekends = args.no_weekends
    frequency = args.frequency
    days_before = args.days_before
    if days_before < 0:
        sys.exit('days_before must not be negative')
    days_after = args.days_after
    if days_after < 0:
        sys.exit('days_after must not be negative')

    os.mkdir(directory)
    os.chdir(directory)
    run(['git', 'init', '-b', 'main'])

    if user_name is not None:
        run(['git', 'config', 'user.name', user_name])

    if user_email is not None:
        run(['git', 'config', 'user.email', user_email])

    start_date = curr_date.replace(hour=20, minute=0) - timedelta(days_before)
    for day in (start_date + timedelta(n) for n in range(days_before + days_after)):
        if (not no_weekends or day.weekday() < 5) and randint(0, 100) < frequency:
            for commit_time in (day + timedelta(minutes=m) for m in range(contributions_per_day(args))):
                contribute(commit_time)

    if repository is not None:
        run(['git', 'remote', 'add', 'origin', repository])
        run(['git', 'branch', '-M', 'main'])
        run(['git', 'push', '-u', 'origin', 'main'])

    print('\nRepository generation \x1b[6;30;42mcompleted successfully\x1b[0m!')


def contribute(date):
    with open(os.path.join(os.getcwd(), 'README.md'), 'a') as file:
        file.write(message(date) + '\n\n')
    run(['git', 'add', '.'])
    run(['git', 'commit', '-m', '"%s"' % message(date), '--date', date.strftime('"%Y-%m-%d %H:%M:%S"')])


def run(commands):
    Popen(commands).wait()


def message(date):
    return date.strftime('Contribution: %Y-%m-%d %H:%M')


def contributions_per_day(args):
    max_c = args.max_commits
    return randint(1, min(max_c, 20))


def arguments(argsval):
    parser = argparse.ArgumentParser()
    parser.add_argument('-nw', '--no_weekends', required=False, action='store_true', default=False,
                        help="Do not commit on weekends")
    parser.add_argument('-mc', '--max_commits', type=int, default=10, required=False,
                        help="Defines the maximum number of commits per day (1 to 20). Default is 10.")
    parser.add_argument('-fr', '--frequency', type=int, default=80, required=False,
                        help="Percentage of days to commit (0-100). Default is 80%.")
    parser.add_argument('-r', '--repository', type=str, required=False,
                        help="A link to an empty, non-initialized remote Git repository. Example: "
                             "git@github.com:user/repo.git or https://github.com/user/repo.git.")
    parser.add_argument('-un', '--user_name', type=str, required=False,
                        help="Overrides git user.name config.")
    parser.add_argument('-ue', '--user_email', type=str, required=False,
                        help="Overrides git user.email config.")
    parser.add_argument('-db', '--days_before', type=int, default=365, required=False,
                        help="Number of past days to generate commits. Default is 365.")
    parser.add_argument('-da', '--days_after', type=int, default=0, required=False,
                        help="Number of future days to generate commits. Default is 0.")
    return parser.parse_args(argsval)


if __name__ == "__main__":
    main()
