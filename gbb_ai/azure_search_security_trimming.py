from typing import Dict, List, Optional

from utils.ml_logging import get_logger

# Initialize logging
logger = get_logger()


class SecurityGroupManager:
    def __init__(self):
        # Initialize the mapping of customer groups to security groups
        self.group_mapping = {
            "Contoso Owners": "Group_critical",
            "Contoso Visitors": "Group_medium",
            "Contoso Members": "Group_low",
            # Add other default mappings here
        }

    def set_group_association(self, customer_group: str, security_group: str):
        """
        Associate a customer group with a specific security group.

        :param customer_group: The name of the customer group.
        :param security_group: The security group to associate.
        """
        self.group_mapping[customer_group] = security_group
        logger.info(f"Associated {customer_group} with {security_group}")

    def get_highest_priority_group(
        self, users_by_role: Dict[str, List[str]]
    ) -> Optional[str]:
        """
        Retrieve the highest priority security group based on the provided user roles.

        :param users_by_role: Dictionary categorizing user roles into 'owner', 'read', and 'write'.
        :return: The highest priority security group or None if no relevant groups are found.
        """
        priority_order = ["Group_critical", "Group_medium", "Group_low"]
        found_groups = set()

        for category in ["owner", "read"]:
            user_groups = users_by_role.get(category, [])
            for user_group in user_groups:
                security_group = self.group_mapping.get(user_group)
                if security_group:
                    found_groups.add(security_group)
                    logger.debug(f"Found {security_group} for {user_group}")

        for priority_group in priority_order:
            if priority_group in found_groups:
                logger.info(f"Returning highest priority group: {priority_group}")
                return priority_group

        logger.warning(
            "No relevant security group found for the given user roles, defaulting to Group_medium"
        )
        return "Group_medium"
