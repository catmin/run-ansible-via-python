#!/usr/bin/python3

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager

from ansible.playbook.helpers import load_list_of_tasks

class CustomRunner:

	def __init__(self, user="ansible", private_key_file="ansiblekey.pem", host_list):
		self.user = user
		self.private_key_file = private_key_file
		
	def run(self, play_source)

		Options = namedtuple('Options', ['connection','module_path', 'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check'])
		# initialize needed objects
		variable_manager = VariableManager()
		# TODO load vars
		loader = DataLoader()
		options = Options(
			connection='ssh', 
			module_path='modules', 
			forks=100, 
			remote_user=self.user, 
			private_key_file=self.private_key_file, 
			ssh_common_args=None, 
			ssh_extra_args=None, 
			sftp_extra_args=None, 
			scp_extra_args=None, 
			become=True, 
			become_method="sudo", 
			become_user="root", 
			verbosity=None, 
			check=False)
		passwords = dict(vault_pass='secret')

		# create inventory and pass to var manager
		inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=host_list)
		variable_manager.set_inventory(inventory)
		
		play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

		# actually run it
		tqm = None
		try:
			tqm = TaskQueueManager(
					  inventory=inventory,
					  variable_manager=variable_manager,
					  loader=loader,
					  options=options,
					  passwords=passwords,
					  # TODO callback must be an instance of CallbackBase or the name of a callback plugin
					  stdout_callback='default',
				  )
			result = tqm.run(play)
		finally:
			if tqm is not None:
				tqm.cleanup()
		

host_list = ['192.168.56.212', '192.168.56.123']
runner = CustomRunner(user="ansible", private_key_file="ansiblekey.pem", host_list=host_list)

# create play with tasks
play_source =  dict(
        name = "Ansible Play",
        hosts = '192.168.56.212',
        gather_facts = 'no',
        tasks = [ dict(
            action=dict(module='sysctl', args=dict(name='net.ipv4.ip_forward', value=1, state='present'))
        )]
    )
	
runner.run(play_source)