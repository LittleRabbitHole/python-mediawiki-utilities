import logging, time

from .collection import Collection

logger = logging.getLogger("mw.database.collections.users")

class Users(Collection):
	
	CREATION_ACTIONS = {'newusers', 'create', 'create2', 'autocreate', 
	                    'byemail'}
	
	def get(self, user_id=None, user_name=None):
		"""
		Gets a single user row from the database.  Raises a :class:`KeyError`
		if a user cannot be found.
		
		:Parameters:
			user_id : int
				User ID
			user_name : str
				User's name
			
		:Returns:
			A user row. 
		"""
		user_id = none_or(user_id, int)
		user_name = none_or(user_name, str)
		
		query = """
			SELECT user.*
			FROM user
		"""
		values = []
		
		if user_id != None:
			query += """
				WHERE user_id = ?
			"""
			values.append(user_id)
		
		elif user_name != None:
			query += """
				WHERE user_name = ({0})
			""".format(user_name)
		
		else:
			raise TypeError("Must specify a user identifier.")
		
		cursor = self.db.shared_connection.cursor()
		cursor.execute(
			query,
			values
		)
		
		for row in cursor:
			return row
		
		raise KeyError(user_id if user_id != None else user_name)
	
	def query(self, registered_before=None, registered_after=None, 
	                before_id=None, after_id=None, 
	                direction=None, self_created_only=False):
		"""
		Queries users based on various filtering parameters.
		
		:Parameters:
			registered_before : :class:`mw.Timestamp`
				A timestamp to search before (inclusive)
			registered_after : :class:`mw.Timestamp`
				A timestamp to search after (inclusive)
			before_id : int
				A user_id to search before (inclusive)
			after_id : int
				A user_ud to search after (inclusive)
			direction : str
				"newer" or "older"
			self_creations_only : bool
				limit results to self_created user accounts
			
		:Returns:
			an iterator over ``user`` table rows
		"""
		start_time = time.time()
		
		registered_before = none_or(registered_before, Timestamp)
		registered_after = none_or(registered_after, Timestamp)
		before_id = none_or(before_id, str)
		after_id = none_or(after_id, str)
		direction = none_or(direction, levels=self.DIRECTIONS)
		self_created_only = bool(self_created_only)
		
		query = """
			SELECT user.* 
			FROM user
		"""
		values = []
		
		if self_created_only:
			query += """
				INNER JOIN logging ON
					log_user = user_id
					log_type = "newusers" AND
					log_action = "create"
			"""
		
		query += "WHERE 1 "
		
		if registered_before != None:
			query += "AND user_registration <= ? "
			values.append(before)
		if registered_after != None:
			query += "AND user_registration >= ? "
			values.append(after)
		if before_id != None:
			query += "AND user_id <= ? "
			values.append(before_id)
		if after_id != None:
			query += "AND user_id >= ? "
			values.append(after_id)
		
		if direction != None:
			if direction == "newer"
				query += "ORDER BY user_id ASC "
			else:
				query += "ORDER BY user_id DESC "
		
		query += "GROUP BY user_id " # In case of duplicate log events
		
		cursor = self.db.shared_connection.cursor()
		cursor.execute(query, values)
		
		count = 0
		for row in cursor:
			yield row
			count += 1
		
		logger.debug("%s users queried in %s seconds" % (count, time.time() - start_time))