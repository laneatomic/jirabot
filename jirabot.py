import os
from datetime import datetime
import csv
import click
import colorama
from jira import JIRA


# JIRABOT interface machine go!
JIRABOT = JIRA(os.environ['JIRA_URL'], basic_auth=(os.environ['JIRA_USER'], os.environ['JIRA_PASS']))

@click.group()
def cli():
    pass

@click.command()
@click.argument('issue')
def view(issue):
    """View a single issue"""
    data = JIRABOT.issue(issue)
    click.secho('%s - %s' % (data, data.fields.summary), fg='green')
    click.secho('Reporter: ', fg='blue', nl=False)
    click.echo(data.fields.reporter)
    click.echo()
    click.secho('Description:', fg='blue')
    click.echo(data.fields.description)
    if data.fields.customfield_13332:
        click.echo()
        click.secho('Business reason:', fg='blue')
        click.echo(data.fields.customfield_13332)
    click.echo()
    if data.fields.comment.comments:

        click.secho('COMMENTS:', fg='blue')
        for comment in data.fields.comment.comments:
            click.secho('%s ' % comment.author, fg='yellow', nl=False)
            click.echo('(%s)' % datetime.strptime(comment.updated, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d %H:%M:%S"))
            click.echo(comment.body)
            click.secho('---', fg='red')

@click.command()
@click.option('-c', '--csv', 'dest', help='Output to a CSV')
@click.argument('jql')
@click.option('-d', '--description', is_flag=True, help='Show description field for each issue')
def search(jql, dest, description):
    """Search for issues with arbitrary JQL"""
    data = JIRABOT.search_issues(jql, maxResults=0)
    parse_search(data, description, dest)

def parse_search(data, description=False, dest=None):
    if dest:
        with click.open_file(dest, 'w') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(['ISSUE', 'REPORTER', 'SUMMARY', 'ASSIGNEE'])
            for issue in data:
                csvwriter.writerow([issue, issue.fields.reporter, issue.fields.summary, issue.fields.assignee])

    else:
        for issue in data:
            click.secho('%s - ' % issue, fg='red', nl=False)
            click.secho('%s' % issue.fields.reporter, fg='green', nl=False)
            click.echo(': %s - ' % issue.fields.summary, nl=False)
            click.secho('%s' % issue.fields.assignee, fg='yellow')
            if description:
                click.echo(issue.fields.description)

@click.command()
@click.option('-p', '--project', help='The project to open the issue', required=True)
@click.option('-s', '--summary', help='The summary of the issue', required=True)
@click.option('-d', '--description', help='The description of the issue')
@click.option('-t', '--type', 'issue_type', help='The issue type (Story, Bug, etc.), default: Story', default='Story')
@click.option('-f', '--field', help='Custom field (field:value)', multiple=True)
def issue(project, summary, description, issue_type, field):
    """Create an issue in Jira"""
    if description is None:
        description = click.edit()
        if description is None:
            click.echo('Description is required!')
            return

    issue_type = issue_type.capitalize()

    issue_dict = {
        'project': {'key': project},
        'summary': summary,
        'description': description,
        'issuetype': {'name': issue_type},
    }

    if field:
        for f in field:
            name,value = f.split(':', 1)
            if name.lower() == 'business reason':
                name = 'customfield_13332'
            issue_dict.update({name: value})

    new_issue = JIRABOT.create_issue(fields=issue_dict)
    click.echo('Issue: %s' % new_issue)

@click.command()
@click.argument('filter_id')
@click.option('-c', '--csv', 'dest', help='Output to a CSV')
@click.option('-d', '--description', is_flag=True, help='Show description field for each issue')
def fsearch(filter_id, description, dest):
    """Search for issues with a saved filter"""
    filter_data = JIRABOT.filter(filter_id)
    data = JIRABOT.search_issues(filter_data.jql, maxResults=0)
    parse_search(data, description, dest)

cli.add_command(view)
cli.add_command(search)
cli.add_command(fsearch)
cli.add_command(issue)
