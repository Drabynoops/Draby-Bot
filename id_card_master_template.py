import discord
from discord.ext import commands

##########################################################################################
### GLOBALS/CONSTANTS                                                                  ###
##########################################################################################
# Main Server
BOT_TOKEN ='BotToken'
GUILD_ID = None
CATEGORY_ID = None
GUILD_MASTER = None
ADMIN_CHAT = None
ADMIN_ROLE = None

# Test Server
#BOT_TOKEN ='Bot Token'
#GUILD_ID = None
#CATEGORY_ID = None

client = commands.Bot(command_prefix = '.')

##########################################################################################
### EVENTS                                                                             ###
##########################################################################################
@client.event
async def on_ready():
	''' Notifies that the bot has successfully logged in.'''
	print('We have logged in as ', client.user)
	
@client.event
async def on_message(message):
	''' Respond to user messages.
	
	As of 5/28/2019 there is no use here
	'''
	if message.author == client.user:
		return
		
	await client.process_commands(message)

@client.event
async def on_member_join(member):
	''' Create an id_card text channel whenever a member joins.'''
	if not member.bot:
		await create_id_card(member)

##########################################################################################
### BOT COMMANDS                                                                      ###
##########################################################################################
@client.command()
async def add_id_card(context, name, discriminator = None):
	''' Create an in_card text channel based on name/discriminator.
	
	This command exists for times when the bot is offline or
	there was an error.
	'''
	if is_admin(context.author):
		member_to_search = await find_member(name, discriminator)
		if member_to_search:
			await create_id_card(member_to_search)
	else:
		await context.send('Apologies, {0}. You lack the rights to use that command.'.format(context.author.name))
		
##########################################################################################
### GENERIC/HELPER FUNCTIONS                                                           ###
##########################################################################################
async def find_member(name, discriminator = None):
	''' Finds a member of a guild based on name and discriminator.
	
	If duplicates are found and a discriminator exists,
	test against the duplicates.
	'''
	guild = client.get_guild(GUILD_ID)
	results = list()
	
	# Append all matching names
	for member in guild.members:
		if member.name == name:
			results.append(member)
	
	# No results found	
	if len(results) == 0:
		return False
	# Exactly one match
	elif len(results) == 1:
		return results[0]
	# Two or more matches, but no discriminator
	elif discriminator is None:
		return False
	# Two or more matches and a discriminator
	else:
		match = None
		# Loops through duplicates looking for matching discriminator
		for duplicate in results:
			if duplicate.discriminator == discriminator:
				match = duplicate
		
		if match is None:
			return False
		else:
			return match
					
async def create_id_card(member):
	''' Create an id card based on member that joined.'''
	
	# Get guild and Category Channel
	guild = client.get_guild(GUILD_ID)
	id_category = client.get_channel(CATEGORY_ID)
	
	# Assign properties that are needed to create the channel
	channel_name = member.name + '-id-card'
	overwrites = {
		guild.default_role: discord.PermissionOverwrite(send_messages=False),
		member: discord.PermissionOverwrite(send_messages=True)
	}
	
	# Check for duplicates
	duplicate = False
	index = 0
	existing_id_cards = id_category.text_channels
	
	# Runs until all channels have been checked or a duplicate is found
	while not duplicate and index < len(existing_id_cards):
		if existing_id_cards[index].name.lower() == channel_name.lower():
			duplicate = True
		index += 1
	
	if not duplicate:
		await id_category.create_text_channel(channel_name, overwrites = overwrites)
	else:
		admin_chat = guild.get_channel(ADMIN_CHAT)
		channel.send('Attention admins. Unable to create id-card for {0} due to duplicate name. Please resolve'.format(member.name))

def is_admin(member):
	admin_status = False
	index = 0
	member_roles = member.roles
	
	print(member.roles)
	while not admin_status and index < len(member.roles):
		if member_roles[index].id == ADMIN_ROLE:
			admin_status = True
		index += 1
	return admin_status
##########################################################################################
### RUN THE BOT                                                                        ###
##########################################################################################
client.run(BOT_TOKEN)
