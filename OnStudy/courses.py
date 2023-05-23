from redbot.core import commands, Config, checks
from redbot.core.utils.chat_formatting import error
from redbot.core.utils.predicates import MessagePredicate
from .logger import logger

import discord
import re
import random


class Courses(commands.Cog):
    """Manages courses for Server McServerface."""
    utility_roles = {
        "staff": {
            "id": 492382906241777678,
            "ref": None
        }
    }
    
    restricted_courses = [
      {
        "id": None,
        "name": None
      }
    ]

    def __init__(self, bot, args):
        """
        Initialize the CourseAssignment object
        """
        self.bot = bot
        self.roles = args["roles"]
        self.logic = args["logic"]
        self.guild_id = args["guild_id"]
        self.channels = args["channels"]
        # self.utility = args["utility"]

        self.db = Config.get_conf(self, identifier=8748107325)
        # self.courseList = self.bot.get_channel(514518408122073116)
        self.emoji = "\N{WHITE HEAVY CHECK MARK}"
        
        # await self.bot.wait_until_ready()
        # self.utility_roles["staff"]["ref"] = self.bot.get_guild(self.guild_id).get_role(
        #     self.utility_roles["staff"]["id"]
        # )

        default_guild = {
            "registered_courses": {}
        }

        self.db.register_guild(**default_guild)

    # Helper methods
    async def getStaffRole(self):
        """
        Retrieves the staff role from the cache
        """
        staffRole = self.utility_roles["staff"]["ref"]

        if staffRole is None:
            staffRole = self.utility_roles["staff"]["ref"] = self.bot.get_guild(self.guild_id).get_role(
                self.utility_roles["staff"]["id"]
            )

        if staffRole is None:
            logger.error("Something went wrong. StaffRole is still None")        

        return staffRole
        

    @commands.group(name="courses")
    @checks.admin()
    async def _courses(self, ctx):
        """
        The course group of commands.
        """
        pass        

    def _courses_create_record(self, course_role: discord.Role, course_category: discord.CategoryChannel):
        """
        Builds a course dictionary object
        """
        return {
            "course_name": course_role.name,
            "role_id": course_role.id,
            "category_id": course_category.id
        }

    @_courses.command(name="create", aliases=["add"])
    @checks.admin()
    async def _courses_create(self, ctx, *, roles: str):
        """
        Creates a category based on the course name supplied.

        If the role for the course doesn't exist it will
        query to user if it should be created as well.

        roles can be a single course or a string of space delimitated courses 
        ex. "cs2003 cs2004 cs2005"
        """
        if roles is None:
            return await ctx.send(error("Role cannot be blank"))

        roles = roles.split(" ")

        # register the course with the database
        for role in roles:
            await self._courses_register(ctx, role.lower(), sort=False)

        # sort courses after all courses have been added
        await ctx.invoke(self._courses_sort)

        await ctx.channel.send("Done.")
        pass        

    async def _course_create_channel(self, ctx, course_role, *, sections_num: int = 0):
        """
        Creates a course channel group if it doesn't already exists
        """
        # this point on needs to be updated
        for course_category in self.bot.get_guild(self.guild_id).categories:
            # BUG: course_role is NoneType here but we shouldn't even be here.
            # It could also be course_category that is NoneType
            if course_category.name.lower() == course_role.name.lower():
                logger.info(f"Skipping channel creation for {course_role.name} as it already exists.")
                return course_category

        logger.info(f"Creating channel for {course_role.name}.")
        # sets permissions for role objects
        staffRole = await self.getStaffRole()
        overwrites = {
            self.bot.get_guild(self.guild_id).default_role: discord.PermissionOverwrite(read_messages=False),
            course_role: discord.PermissionOverwrite(read_messages=True),
            staffRole: discord.PermissionOverwrite(read_messages=True)
        }

        # create the category
        course_category = await self.bot.get_guild(self.guild_id).create_category(name=f"{course_role.name.upper()}", overwrites=overwrites)
        # create the general chat for the course
        await self.bot.get_guild(self.guild_id).create_text_channel(name=course_role.name, category=course_category)
        # create any requested section channels
        for i in range(1, sections_num):
            await self.bot.get_guild(self.guild_id).create_text_channel(name=f"section-00{i}", category=course_category)
        # create the voice channels
        voice_channel_name = re.sub(
            r"^[A-Za-z]+(?P<courseNum>[\d]+)$",
            r"\g<courseNum>",
            course_role.name
        )

        await self.bot.get_guild(self.guild_id).create_voice_channel(name=f"{voice_channel_name}-gen", category=course_category)
        await self.bot.get_guild(self.guild_id).create_voice_channel(name=f"{voice_channel_name}-school", category=course_category)

        return course_category

    @_courses.command(name="create_section", aliases=["cs"])
    async def _courses_create_section(self, ctx, section_number: str, *, topic: str = ""):
        """
        Creates a course section for the parent course

        section_number **required**: The section number of the course.
        topic: if supplied, will set the topic of the channel to this
        """
        if not section_number:
            return

        parent_course = self.bot.get_guild(self.guild_id).get_channel(ctx.channel.category_id)
        channel = await self.bot.get_guild(self.guild_id).create_text_channel(name=f"section-{section_number}", category=parent_course)

        if topic:
            await channel.edit(topic=topic)
        

    async def _courses_create_courseList_entry(self, ctx, course_role):
        """
        Creates the message and applies the emoji for the users click on
        """

        # check to make sure that the course isn't already in the course list
        async for message in self.channels.courseList.history():
            if message.content == course_role.name:
                logger.warning(f"Skipping creation course list entry for {course_role.name} as it already exists.")
                return message.id

        # create the course role message
        message = await self.channels.courseList.send(f"{course_role.name}")
        await self.add_reaction_to_message(ctx, message, self.emoji)

        logger.info(f"Created course list entry for {course_role.name}")

        return message.id

    @_courses.command(name="delete", aliases=["del"])
    async def _courses_delete(self, ctx, msg_id: int):
        """
        Removes a course. **NO UNDO!**

        msg_id: the id of the course you want to remove
        """
        confirm = await self.logic.confirm(ctx, msg="Are you sure you wish to delete this course? There is no undo.")
        if not confirm:
            return await ctx.send("Canceling.")

        async with self.db.guild(ctx.guild).registered_courses() as courses:
            course = courses.pop(str(msg_id), None)
            await self.remove_course_channel(course["category_id"])
            await self.remove_course_role(course["role_id"])
            await self.remove_courseList_entry(msg_id)
        await ctx.channel.send("Done.")
        

    async def remove_course_channel(self, category_id):
        """
        Removes the category and it's children that matches the 'category_id' from the server.
        """
        category = self.bot.get_guild(self.guild_id).get_channel(category_id)
        if category is None:
            return logger.error("category is empty.")

        for channel in category.channels:
            await channel.delete(reason=f"removing parent category")

        await category.delete()
        

    async def remove_course_role(self, role_id):
        """
        Removes the role that matches the 'role_id' from the server.
        """
        role = self.bot.get_guild(self.guild_id).get_role(role_id)
        if role is None:
            return logger.error("role is empty.")

        await role.delete()
        

    async def remove_courseList_entry(self, msg_id):
        """
        Removes the course list entry that matches the 'msg_id' from the courseList channel.
        """
        msg = await self.channels.courseList.get_message(msg_id)
        if msg is None:
            return logger.error("msg is empty")

        await msg.delete()
        

    async def _courses_does_course_exist(self, course_role_name: str):
        """
        Checks to see if the course exists on the server
        """
        course_role_found = None
        # get the role from the list of server roles
        for guild_role in self.bot.get_guild(self.guild_id).roles:
            if (guild_role.name == course_role_name):
                course_role_found = guild_role
                break
        return course_role_found

    async def _courses_register_from_courseListing(self, ctx, message: discord.Message, create_interaction: bool = False):
        """
        Registers a course from a course listing in the courseList channel.
        """
        await self._courses_register(ctx, message.content, create_interaction=create_interaction, message_id=message.id)

    async def _courses_register(self, ctx, role_name: str, *, sections_num: int = 0, create_interaction: bool = True, message_id: int = 0, sort: bool = False):
        """
        Registers a course.
        msg_id: the id of the message which will trigger the course to be applied.
        course: a dict object in format of {"course_name": str, "role_id": int}
        """

        # get the role from the list of server roles
        course_role = await self._courses_does_course_exist(role_name)

        if course_role is None:
            new_role = await self.roles.create_role(ctx, role_name)
            logger.info(f"new role `{new_role}`")
            if new_role is not None:
                course_role = new_role
            else:
                return logger.info(f"Declined to create role `{role_name}`")
        elif course_role is False:
            await ctx.channel.send(f"Skipping course {role_name}")
            pass

        course_channel = await self._course_create_channel(ctx, course_role, sections_num=sections_num)

        if create_interaction:
            # create the message that users will react to
            message_id = await self._courses_create_courseList_entry(
                ctx, course_role
            )

        if message_id == 0:
            return logger.error("Invalid message id")

        course_record = self._courses_create_record(
            course_role,
            course_channel
        )

        async with self.db.guild(ctx.guild).registered_courses() as courses:
            courses.update({
                str(message_id): course_record
            })

        if sort:
            await ctx.invoke(self._courses_sort)

        

    @_courses.command(name="remove_member", aliases=["rm"])
    async def _courses_remove_member(self, ctx, member: discord.Member):
        """
        Removes a member's reactions for the courses in course list.
        """
        async with ctx.channel.typing():
            try:
                await ctx.send("Removing member from courses.")
                async for message in self.channels.courseList.history():
                    await message.remove_reaction(self.emoji, member)
                await ctx.send("Done.")
            except discord.Forbidden:
                logger.exception("Insufficient permissions to remove reaction.")
            except discord.NotFound:
                logger.exception("The member or emoji you specified was not found.")
            except discord.InvalidArgument:
                logger.exception("The emoji parameter is invalid.")
            except discord.HTTPException:
                logger.exception("Removing the reaction failed.")
        

    @_courses.command(name="reset")
    async def _courses_reset(self, ctx):
        """
        Clears all registered courses. **NO UNDO**!
        """
        pred = await self.logic.confirm("Are you sure you wish to clear all registered courses? There is **no undo option**.")
        if pred is False:
            return await ctx.channel.send("Canceling.")

        async with ctx.channel.typing():
            await ctx.channel.send("Clearing registered courses.")
            async with self.db.guild(ctx.guild).registered_courses() as courses:
                courses.clear()
        await ctx.channel.send("Done.")
        

    @_courses.command(name="show")
    async def _courses_show(self, ctx):
        """
        Displays each course known to the bot.
        """
        courses = await self.db.guild(ctx.guild).get_raw("registered_courses")
        await ctx.channel.send(f"Displaying {len(courses)} courses.")
        courseNum = 1
        async with ctx.channel.typing():
            for key, val in courses.items():
                await ctx.channel.send(
                    f"Course {courseNum}:\n"
                    "```\n"
                    f"msg_id: {key}\n"
                    f"course: {val}\n"
                    "```"
                )
                courseNum += 1
        

    @_courses.command(name="sort")
    async def _courses_sort(self, ctx):
        """
        Sorts the course channels in alphabetical order
        """
        
        # Goals:
        # TODO: Add restricted list
        # TODO: Remove restricted courses from the list of sortable courses
        # TODO: Sort courses by name
        await ctx.send("Sorting courses.")

        start_index = 5

        category_list = self.bot.get_guild(self.guild_id).categories[start_index:]

        def take_name(elem):
            return elem.name.upper()

        category_list.sort(key=take_name)

        async with ctx.typing():
            for index, category in enumerate(category_list):
                new_position = index + start_index
                try:
                    await category.edit(name=category.name.upper(), position=new_position)
                except discord.InvalidArgument:
                    logger.exception(f"Invalid attempt to change the position of category {category.name} to position {new_position}")
                    await ctx.send(error(f"Invalid attempt to change the position of category {category.name} to position {new_position}"))
                except discord.Forbidden:
                    logger.exception(f"Forbidden from modifying category {category.name}")
                    await ctx.send(error(f"Forbidden from modifying category {category.name}"))
                except discord.HTTPException:
                    logger.exception(f"Failed to edit category {category.name}")
                    await ctx.send(error(f"Failed to edit category {category.name}"))

        await ctx.send("Done Sorting.")

        

    @_courses.command(name="sync")
    async def _courses_sync(self, ctx):
        """
        Syncs the course list channel with the bot and the users.

        **Warning:** May take some time to complete.
        """
        async with ctx.channel.typing():
            try:
                await ctx.send("Syncing courses. This may take a while. Please be patient.")
                async for message in self.channels.courseList.history():
                    if message.type != discord.MessageType.default:
                        continue
                    
                    # syncs courses with the bot's database
                    await self._courses_register_from_courseListing(ctx, message, create_interaction=False)

                    # syncs users with the courses they have signed up for
                    await self._courses_sync_roles(ctx, message)
                await ctx.send("Done.")
            except discord.Forbidden:
                logger.exception("discord.Forbidden error.")
            except discord.HTTPException:
                logger.exception("discord.HTTPException error.")
        

    async def _courses_sync_roles(self, ctx, message: discord.Message):
        """
        Updates users and courses in #course-list to make sure they match
        """
        for react in message.reactions:
            if str(react.emoji) == self.emoji:
                has_bot_reacted = False
                async for user in react.users():
                    if user.bot and user == self.bot.get_guild(self.guild_id).me:
                        has_bot_reacted = True
                        continue
                    await self.process_course_assignment_from_call(react, user)

                if not has_bot_reacted:
                    await self.add_reaction_to_message(ctx, message, self.emoji)
        

    @_courses.group(name="roles")
    async def _courses_roles(self, ctx):
        """
        Commands that revolve around creating and managing course roles.
        """
        pass

    @_courses_roles.command(name="add")
    @checks.mod_or_permissions(manage_roles=True)
    async def _courses_roles_add(self, ctx, user: discord.Member = None, *, requested_roles):
        """
        Adds any number of roles to a user
        """
        if user is None:
            return

        requested_roles = requested_roles.split(" ")

        # save a copy of the guild reols so that we're not calling it a lot
        guild_roles = ctx.guild.roles

        # create a list of the roles that are already roles in the guild
        roles_to_add = [role for role in guild_roles if role.name in requested_roles]

        # create a list of roles which are not found in the guild.
        # compare the list of requested_roles against a list of the names of the roles from the guild roles
        roles_not_found = [requested_role for requested_role in requested_roles if requested_role not in [role.name for role in guild_roles]]

        # Ask if the missing riles should be created
        for role in roles_not_found:
            new_role = await self.roles.create_role(ctx, role)
            if new_role is not None:
                roles_to_add.append(new_role)

                # create channel group
                self._courses_create(ctx, roles=new_role.name)

        if roles_to_add:
            await user.add_roles(*roles_to_add, reason=f"{ctx.message.author} requested it.")

        await ctx.channel.send("Done.")
        

    @_courses_roles.command(name="check")
    @checks.mod()
    async def _courses_roles_check(self, ctx, user: discord.Member = None):
        """
        Shows the roles the user has
        Defaults to author
        """
        if user is None:
            user = ctx.author
        roles = self.roles.getRolesForUser(user)
        formattedRoles = "\n".join(roles)
        await ctx.send(f"User: **{user.display_name}** has the following roles: \n{formattedRoles}")
        

    async def add_reaction_to_message(self, ctx, message: discord.Message, emoji):
        """
        Adds the specified emoji as a reaction to the specified message
        """
        try:
            # add initial reaction to the course to make it easier on users to add it
            await message.add_reaction(emoji)
        except discord.InvalidArgument:
            logger.exception(f"Emoji was not a valid emoji.")
        except discord.Forbidden:
            logger.exception("Forbidden action")
        except discord.NotFound:
            logger.exception(f"The requested emoji was not found on the server.")
        except discord.HTTPException:
            logger.exception(f"There was an issue with the webserver.")
        
    @commands.Cog.listener("on_raw_reaction_add")
    async def reaction_added(self, payload):
        """
        Member agrees to the rules.
        """
        logger.debug("Saw the reaction add")
        await self.process_course_assignment_from_trigger(payload, add=True)
        

    @commands.Cog.listener("on_raw_reaction_remove")
    async def reaction_removed(self, payload):
        """
        Member no longer agrees to the rules.
        """
        logger.debug("Saw the reaction remove")
        await self.process_course_assignment_from_trigger(payload, add=False)
        

    async def process_course_assignment(self, member: discord.Member, emoji, message_id: int, add: bool):
        """
        Handles building the required products to register a student with a course
        """
        if member is None:
            return logger.error("member is none!")
        elif member.bot:
            return logger.debug("member is bot")
        elif str(emoji) != self.emoji:
            return logger.debug("incorrect emoji")

        # get the dict courses from the db
        courses = await self.db.guild(self.bot.get_guild(self.guild_id)).get_raw("registered_courses")

        # default course to None so that we know for sure if we found something
        course = None

        # get the course that has a msg_id which matches our payload
        # then set its value to course
        for key, val in courses.items():
            if key == str(message_id):
                course = val
                break

        # ensure that we actually got a course
        if course is None:
            logger.error("course wasn't found!")
            return

        # get the role from the guild that matches the course
        role = self.bot.get_guild(self.guild_id).get_role(course["role_id"])
        
        # update the status of the role for the member
        await self.roles.update_member(member, role, add)
        

    async def process_course_assignment_from_call(self, reaction: discord.Reaction, member: discord.Member):
        """
        Handles the processing of the reaction from an internal call.
        """
        await self.process_course_assignment(member, reaction.emoji, reaction.message.id, True)
        

    async def process_course_assignment_from_trigger(self, payload, *, add: bool):
        """
        Handles the processing of the reaction from a trigger.
        """
        # get the member from the guild using the user_id in the payload
        member = self.bot.get_guild(payload.guild_id).get_member(payload.user_id)
        if member is None:
            error_msg = (
                f"Unable to add user with id #{payload.user_id} to their requested "
                "course as they were not found to be a member of the guild."
            )
            logger.error(error_msg)            
            return await self.channels.log.send(error(error_msg))
        await self.process_course_assignment(member, payload.emoji, payload.message_id, add)
        
