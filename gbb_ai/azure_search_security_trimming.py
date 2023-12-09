from typing import Dict, Optional

class SecurityGroupManager:
    def __init__(self):
        # Initialize the mapping of customer groups to security groups
        self.group_mapping = {
            "Contoso Dev": "Group_medium",  # Example mapping
            "Contoso Manager": "Group_critical"
        }

    def set_group_association(self, customer_group: str, security_group: str):
        """
        Associate a customer group with a specific security group.

        :param customer_group: The name of the customer group.
        :param security_group: The security group to associate.
        """
        self.group_mapping[customer_group] = security_group

    def get_security_group(self, customer_group: str) -> Optional[str]:
        """
        Retrieve the security group associated with a customer group.

        :param customer_group: The name of the customer group.
        :return: The associated security group, or None if no association exists.
        """
        return self.group_mapping.get(customer_group)