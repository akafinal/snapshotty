import boto3
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances

@click.group()
def instances():
    """Commands for instances"""

@instances.command('list')
@click.option('--project', default=None,
help='Only instances for project (tag Project:<name>)')
def list_instances(project):
    'List EC2 instances'
    instances = filter_instances(project)
    for i in instances:
        tags = {t['Key']:t['Value'] for t in i.tags or []}
        print (', '.join((
            i.id,
            i.placement['AvailabilityZone'],
            i.public_dns_name,
            i.state['Name'],
            tags.get('Project','<no project>')
        )))
    return
@instances.command('stop')
@click.option('--project', default=None,
help='Only instances for project (tag Project:<name>)')
def stop_instances(project):
    'Stop EC2 instances'
    instances = filter_instances(project)
    for i in instances:
        print('Stopping {0}...'.format(i.id))
        i.stop()
        i.wait_until_stopped()
        print("Job's done!")
    return
@instances.command('start')
@click.option('--project', default=None,
help='Only instances for project (tag Project:<name>)')
def start_instances(project):
    'Stop EC2 instances'
    instances = filter_instances(project)
    for i in instances:
        print('Starting {0}...'.format(i.id))
        i.start()
        i.wait_until_running()
        print("Job's done!")
    return
@instances.command('snapshot')
@click.option('--project', default=None,
help='Only instances for project (tag Project:<name>)')
def create_snapshots(project):
    'Create EC2 snapshots'
    instances = filter_instances(project)
    ins = []
    for i in instances:
        if i.state['Name'] == 'running': ins.append(i)

        print('Stopping {0}'.format(i.id))
        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            print('Making snapshots of {0}'.format(i.id))
            v.create_snapshot(Description='Created by snapshotty')

        for j in ins:
            print('Starting {0} that were running before'.format(j.id))
            j.start()
            j.wait_until_running()
    print("Job's done!")
    return

if __name__ == '__main__':
        instances()
