class TerraformPlanParser:

    def find_changes(self, before, after, prefix=""):
        """
        Recursively compare two dictionaries and return all differences.
        """

        changes = []

        keys = set(before.keys()) | set(after.keys())

        for key in keys:

            old_value = before.get(key)
            new_value = after.get(key)

            current_path = f"{prefix}.{key}" if prefix else key

            # Compare nested dictionaries recursively
            if isinstance(old_value, dict) and isinstance(new_value, dict):

                changes.extend(
                    self.find_changes(
                        old_value,
                        new_value,
                        current_path
                    )
                )

            else:

                if old_value != new_value:

                    changes.append({
                        "property": current_path,
                        "azure": old_value,
                        "terraform": new_value
                    })

        return changes