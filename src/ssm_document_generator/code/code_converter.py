import json
from pathlib import Path


class CodeConverter(object):
    """
    Defines a generic class used to convert scripts to SSM documents.
    Child classes provide implementation for language specific functions.
    """
    DEFAULT_TEMPLATE_PATH = str(Path(__file__).parent / "../templates/run_command_template.json")
    SHEBANG = '#!/usr/bin/env bash'
    DEFINITION_KEYS_TO_FILTER = ('command_type', 'command_file', 'name', 'parameters')

    def convert(self, definition, code_file_path):
        """
        Converts given command definition into the SSM document.
        :param definition: Command definition
        :param code_file_path: Path to the code of the command.
        :return:
        """
        ssm_document = self.read_template()
        self.merge_definition_into_template(ssm_document, definition)

        command_list = ssm_document['mainSteps'][0]['inputs']['runCommand']
        command_list.extend(self.get_prefix_code())
        command_list.extend(self.generate_parameters_code(ssm_document['parameters']))
        command_list.extend(self.process_code(code_file_path))
        command_list.extend(self.get_postfix_code())

        return ssm_document

    def generate_parameters_code(self, parameter_definition):
        """
        From given parameter definition - generate code to pass the parameters to the command implementation
        :param parameter_definition:
        :return:
        """
        return []

    def process_code(self, code_file_path):
        with Path(code_file_path).open() as code_stream:
            return code_stream.readlines()

    def get_prefix_code(self):
        """
        Returns code that should be added at the beginning of the generated script before the main body of code.
        :return:
        """
        return [self.shebang()]

    def get_postfix_code(self):
        """
        Returns code that should be added at the end of the generated script after the main body of code.
        :return:
        """
        # todo consider reading this from file
        return []

    @staticmethod
    def merge_definition_into_template(template, definition, keys_to_filter=DEFINITION_KEYS_TO_FILTER):
        """
        Application specific dict merge - merge definition into document template, overriding parameters that
        are not filtered out.
        :param template:
        :param definition:
        :param keys_to_filter: List of keys to ignore during the merge.
        """
        template.update({k: v for k, v in definition.items() if k not in keys_to_filter})
        # consider doing deep merge if there would be more special cases then params.
        if 'parameters' in definition:
            template['parameters'].update(definition['parameters'])

        return template

    @classmethod
    def shebang(cls):
        return cls.SHEBANG

    @staticmethod
    def read_template(template_path=DEFAULT_TEMPLATE_PATH):
        return json.loads(Path(template_path).read_text())
