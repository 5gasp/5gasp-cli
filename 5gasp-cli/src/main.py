# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-02-01 16:31:36
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-04-20 13:45:18

# Python
from typing import List, Optional
import os
from helpers import constants as Constants
from helpers.CICDManagerAPIClient import apli_client as CICD_API_Client
from helpers.Prompt.prompts import Prompts
from helpers.beatiful_prints import PrintAsTable, PrintAsPanelColumns
from rich.prompt import Prompt, Confirm
# Typer
import typer

from TestingDescriptorGenerator.descriptor_generator import TestingDescriptorGenerator

app = typer.Typer(pretty_exceptions_show_locals = False)
state = {"verbose": False}


@app.command()
def create_tests(
    config_file: str = typer.Option(None, 
                                        help = "Name of the config file \
                                        containing the desired test' names"),
    output_filename: str = typer.Option("../../generated_descriptor/testing-descriptor.yaml", 
                                        help = "Output filename"),
    clear_executions: bool = typer.Option(False, 
                                        help = "Clear executions"),
    infer_tags_from_nsd: Optional[List[str]] = typer.Option(None)
    ):
    descriptor_generator = TestingDescriptorGenerator(state)
    descriptor_generator.create_testing_descriptor(
                            config_file, 
                            output_filename, 
                            clear_executions, 
                            infer_tags_from_nsd
                        )


@app.command()
def list_testbeds():
    '''
    List available testbeds
    '''
    ApiClient = CICD_API_Client.CICDManagerAPIClient()
    testbeds = ApiClient.get_all_testbeds()

    # Print table with the available testbeds
    table = PrintAsTable(
        header=["ID", "Name", "Description"],
        rows=[
            [t["id"], t["name"], t["description"]]
            for t
            in testbeds
        ]
    )
    table.print()

    # Ask the user if he wishes to list the available test cases in each of
    # the available testbeds
    should_list_tests = Confirm.ask(
        "\nDo you wish to list the available tests for one of these testbeds?",
    )

    # If the answer is 'yes'
    if should_list_tests:
        testbed_id = Prompt.ask(
            "\nFor which testbed do you wish to list the available tests",
            choices=[t["id"] for t in testbeds]
        )

        print(f"\nAvailable tests in testbed '{testbed_id}':\n")

        tests = ApiClient.get_tests_per_testbed(testbed_id)
        pannels = PrintAsPanelColumns(
            pannels=[t.to_pannel() for t in tests]
        )
        pannels.print()


@app.command()
def list_available_tests():
    '''
    List available tests to developer
    '''
    descriptor_generator = TestingDescriptorGenerator(state)
    descriptor_generator.list_available_tests()


@app.callback()
def main(
    verbose: bool = False,
    ci_cd_manager_url: str = typer.Option(
        default=Constants.CI_CD_SERVICE_URL,
        help="CI/CD Manager URL to override the default one.")
):
    """
    5GASP CLI
    """
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True
    # Set the ci_cd_manager_url
    Constants.CI_CD_SERVICE_URL = ci_cd_manager_url


if __name__ == "__main__":

    app()
