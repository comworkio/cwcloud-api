from unittest import TestCase

from utils.list import unmarshall_list_array, marshall_list_string

class TestTransformRole(TestCase):
    def test_marshall_list_string_nominal(self):
        # Given
        roles = ["role1", "role2"]

        # When
        roles_str = marshall_list_string(roles)

        # Then
        self.assertEqual("role1;role2", roles_str)

    def test_marshall_list_string_already_string(self):
        # Given
        roles = "role1;role2"

        # When
        roles_str = marshall_list_string(roles)

        # Then
        self.assertEqual("role1;role2", roles_str)

    def test_marshall_list_string_node(self):
        # Given
        roles = None

        # When
        roles_str = marshall_list_string(roles)

        # Then
        self.assertEqual("", roles_str)

    def test_unmarshall_list_array_nominal(self):
        # Given
        roles = "role1;role2"

        # When
        roles_array = unmarshall_list_array(roles)

        # Then
        self.assertEqual(["role1", "role2"], roles_array)

    def test_unmarshall_list_array_comma(self):
        # Given
        roles = "role1,role2"

        # When
        roles_array = unmarshall_list_array(roles)

        # Then
        self.assertEqual(["role1", "role2"], roles_array)

    def test_unmarshall_list_array_single(self):
        # Given
        roles = "role1"

        # When
        roles_array = unmarshall_list_array(roles)

        # Then
        self.assertEqual(["role1"], roles_array)

    def test_unmarshall_list_array_array(self):
        # Given
        roles = ["role1", "role2"]

        # When
        roles_array = unmarshall_list_array(roles)

        # Then
        self.assertEqual(["role1", "role2"], roles_array)

    def test_unmarshall_list_array_none(self):
        # Given
        roles = None

        # When
        roles_array = unmarshall_list_array(roles)

        # Then
        self.assertEqual([], roles_array)
